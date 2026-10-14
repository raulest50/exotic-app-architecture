"""Validated per-element CSS, applied in memory with isolated figure boundaries."""

import logging
import math
from functools import lru_cache

import tinycss2
from gi.repository import GLib
from gaphor import UML
from gaphor.core import event_handler
from gaphor.core.modeling import Diagram, StyleSheet
from gaphor.core.modeling.diagram import StyledItem
from gaphor.core.modeling.event import (
    ElementDeleted, ElementUpdated, ModelFlushed, ModelReady, StyleSheetUpdated,
)
from gaphor.core.styling import INHERITED_DECLARATIONS, PrefersColorScheme, merge_styles
from gaphor.core.styling.declarations import declarations, parse_value

from .model import DocumentationError, read_css, target_element

log = logging.getLogger(__name__)
_runtimes = {}
_original_compute_style = None
SUPPORTED_PROPERTIES = frozenset({
    "background-color", "border-radius", "color", "dash-style", "padding",
    "font-family", "font-size", "font-style", "font-weight", "justify-content",
    "line-width", "min-width", "max-width", "min-height", "opacity",
    "text-decoration", "text-align", "text-color", "vertical-align",
    "vertical-spacing", "white-space",
})
TEXT_PROPERTIES = frozenset(INHERITED_DECLARATIONS) | {"text-decoration"}


class CssError(DocumentationError):
    pass


def _invalid(token, reason):
    return CssError(f"CSS, línea {token.source_line}, columna {token.source_column}: {reason}")


def _check_tokens(tokens):
    for token in tokens:
        if token.type == "error":
            raise _invalid(token, token.message)
        if token.type in ("{} block", "[] block", "() block", "url", "at-keyword"):
            raise _invalid(token, "solo se admiten declaraciones de estilo del elemento.")
        if token.type == "function":
            if token.lower_name not in ("rgb", "rgba", "hsl", "hsla"):
                raise _invalid(token, "solo se admiten funciones de color; las variables no están disponibles.")
            _check_tokens(token.arguments)
        if token.type in ("number", "dimension", "percentage") and not math.isfinite(token.value):
            raise _invalid(token, "el número debe ser finito.")
        if token.type == "dimension" and token.lower_unit != "px":
            raise _invalid(token, "utiliza números sin unidad o píxeles (px).")


@lru_cache(maxsize=256)
def _parse_css(text):
    result = {}
    for token in tinycss2.parse_declaration_list(text, skip_comments=True, skip_whitespace=True):
        if token.type != "declaration":
            raise _invalid(token, "escribe propiedad: valor; sin selectores, bloques ni directivas.")
        name = token.lower_name
        if name not in SUPPORTED_PROPERTIES:
            raise _invalid(token, f"propiedad no admitida: {name}.")
        if token.important:
            raise _invalid(token, "!important no es necesario: este estilo ya tiene prioridad.")
        _check_tokens(token.value)
        meaningful = [part for part in token.value if part.type not in ("whitespace", "comment")]
        if not meaningful:
            raise _invalid(token, f"falta un valor para {name}.")
        if name == "font-family" and any(
            part.type not in ("ident", "string") and not (part.type == "literal" and part.value == ",")
            for part in meaningful
        ):
            raise _invalid(token, "font-family requiere nombres de fuentes; revisa los puntos y coma.")
        try:
            value = declarations(name, parse_value(token.value))
            valid = value is not None
            if name == "padding" and valid:
                raw = parse_value(token.value)
                parts = raw if isinstance(raw, tuple) else (raw,)
                valid = 1 <= len(parts) <= 4 and all(v >= 0 for v in value)
            elif name == "dash-style" and valid:
                valid = all(v >= 0 for v in value) and (not value or any(value))
        except (TypeError, ValueError, AttributeError, OverflowError):
            valid = False
        if not valid:
            raise _invalid(token, f"valor no válido para {name}.")
        result[name] = value
    return result


def parse_css(text):
    """Return a fresh parsed mapping, never expose the cached mutable value."""
    return dict(_parse_css(text))


class IsolatedStyles:
    """Use the unmodified native cascade at every presentation boundary.

    Only CSS nodes belonging to a figure inherit that figure's custom layer.
    A nested presentation starts again from the native cascade, then applies
    its own subject's declarations. No flattened native styles are merged
    twice, which would compound opacity and relative font sizes.
    """

    def __init__(self, native, runtime):
        self.native = native
        self.runtime = runtime

    def compute_style(self, node):
        parent = node.parent()
        custom = {}
        if isinstance(node, StyledItem):
            parent_style = self.native.compute_style(parent) if parent else {}
            custom = self.runtime.for_subject(node.item.subject)
        else:
            parent_style = self.compute_style(parent) if parent else {}
            owner = parent
            while owner and not isinstance(owner, StyledItem):
                owner = owner.parent()
            if owner:
                declared = self.runtime.for_subject(owner.item.subject)
                if declared:
                    resolved = self.compute_style(owner)
                    custom = {key: resolved[key] for key in declared.keys() & TEXT_PROPERTIES if key in resolved}
        return merge_styles(
            {key: value for key, value in parent_style.items() if key in INHERITED_DECLARATIONS},
            *(values for selector, values in self.native.rules if selector(node)),
            custom,
            {"-gaphor-style-node": node, "-gaphor-compiled-style-sheet": self},
        )


def _compute_style(sheet, node, prefers_color_scheme=PrefersColorScheme.NONE):
    ancestor = node
    while ancestor is not None:
        if diagram := getattr(ancestor, "diagram", None):
            runtime = _runtimes.get(diagram.model)
            if runtime:
                native = sheet.compile_style_sheet(prefers_color_scheme)
                return IsolatedStyles(native, runtime).compute_style(node)
            break
        ancestor = ancestor.parent()
    return _original_compute_style(sheet, node, prefers_color_scheme)


class StyleRuntime:
    def __init__(self, model, event_manager):
        global _original_compute_style
        self.model = model
        self.events = event_manager
        self.cache = {}
        self.pending = 0
        self.alive = True
        _runtimes[model] = self
        if _original_compute_style is None:
            _original_compute_style = StyleSheet.compute_style
            StyleSheet.compute_style = _compute_style
        for handler in (self._changed, self._reset, self._stylesheet_changed):
            self.events.subscribe(handler)

    def for_subject(self, subject):
        if target_element(subject) is None:
            return {}
        if subject not in self.cache:
            try:
                self.cache[subject] = parse_css(read_css(subject))
            except (DocumentationError, TypeError) as error:
                # Native stereotype editing can bypass the dialog validator.
                # Preserve the text and render normally until it is corrected.
                log.warning("CSS no aplicado a %s: %s", getattr(subject, "name", subject.id), error)
                self.cache[subject] = {}
        return self.cache[subject]

    @event_handler(ElementUpdated, ElementDeleted)
    def _changed(self, event):
        if isinstance(event.element, (UML.LiteralString, UML.Slot, UML.InstanceSpecification,
                                      UML.Property, UML.Stereotype, UML.Profile, UML.PrimitiveType)) or (
            getattr(getattr(event, "property", None), "name", "") == "appliedStereotype"
        ):
            self.cache.clear()
            self._schedule()

    @event_handler(ModelReady, ModelFlushed)
    def _reset(self, _event):
        self.cache.clear()
        self._schedule()

    @event_handler(StyleSheetUpdated)
    def _stylesheet_changed(self, _event):
        self._schedule()

    def _schedule(self):
        if self.alive and not self.pending:
            self.pending = GLib.idle_add(self._refresh)

    def _refresh(self):
        self.pending = 0
        if self.alive:
            # Request native asynchronous updates instead of creating a second
            # transaction or rewriting positions/sizes in this service.
            for diagram in self.model.select(Diagram):
                for item in diagram.get_all_items():
                    diagram.request_update(item)
        return GLib.SOURCE_REMOVE

    def shutdown(self):
        global _original_compute_style
        self.alive = False
        if self.pending:
            GLib.source_remove(self.pending)
            self.pending = 0
        for handler in (self._changed, self._reset, self._stylesheet_changed):
            self.events.unsubscribe(handler)
        self.cache.clear()
        if _runtimes.get(self.model) is self:
            del _runtimes[self.model]
        if not _runtimes and _original_compute_style is not None:
            if StyleSheet.compute_style is _compute_style:
                StyleSheet.compute_style = _original_compute_style
            _original_compute_style = None
