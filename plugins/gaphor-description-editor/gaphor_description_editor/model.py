"""Persist documentation using standard UML profile/slot objects only."""

from dataclasses import dataclass

from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.modeling import Presentation

PROFILE = "DocumentacionArquitectura"
STEREOTYPE = "Describible"
PROPERTY = "descripcion"
CSS_PROPERTY = "css"
_UNSET = object()


class DocumentationError(ValueError):
    """A recoverable selection, stale editor, or profile conflict."""


def target_element(element):
    if isinstance(element, Presentation):
        element = element.subject
    # UML does not permit applying stereotypes to other stereotypes.
    return element if isinstance(element, UML.Element) and not isinstance(element, UML.Stereotype) else None


def _one(values, label):
    values = list(values)
    if len(values) > 1:
        raise DocumentationError(f"Hay varios elementos para {label}. Corrige la duplicación antes de editar.")
    return values[0] if values else None


@dataclass(frozen=True)
class Definition:
    profile: object
    stereotype: object
    attribute: object


def definition(model, property_name=PROPERTY):
    profile = _one((p for p in model.select(UML.Profile) if p.name == PROFILE), PROFILE)
    stereotype = _one(
        (s for s in model.select(UML.Stereotype) if s.package is profile and s.name == STEREOTYPE),
        STEREOTYPE,
    ) if profile else None
    attribute = _one(
        (p for p in stereotype.ownedAttribute if p.name == property_name and not p.association),
        property_name,
    ) if stereotype else None
    return Definition(profile, stereotype, attribute)


def _application(subject, stereotype):
    return _one(
        (a for a in subject.appliedStereotype if stereotype in a.classifier),
        "la aplicación de Describible",
    ) if stereotype else None


def _slot(application, attribute):
    return _one(
        (s for s in application.slot if s.definingFeature is attribute),
        f"el valor de {attribute.name}",
    ) if application and attribute else None


def read_description(subject):
    return _read_value(subject, PROPERTY)


def read_css(subject):
    return _read_value(subject, CSS_PROPERTY)


def _read_value(subject, property_name):
    spec = definition(subject.model, property_name)
    slot = _slot(_application(subject, spec.stereotype), spec.attribute)
    if slot and slot.value:
        if not isinstance(slot.value, UML.LiteralString):
            raise DocumentationError(f"{property_name} contiene un valor que no es texto.")
        return slot.value.value or ""
    return ""


def _ensure_definition(model, property_name=PROPERTY):
    spec = definition(model, property_name)
    profile = spec.profile
    if profile is None:
        profile = model.create(UML.Profile)
        profile.name = PROFILE
    stereotype = spec.stereotype
    if stereotype is None:
        stereotype = model.create(UML.Stereotype)
        stereotype.name = STEREOTYPE
        stereotype.package = profile
    metaclass = _one(
        (c for c in profile.ownedType if type(c) is UML.Class and c.name == "Element"),
        "la metaclase Element",
    )
    if metaclass is None:
        metaclass = model.create(UML.Class)
        metaclass.name = "Element"
        metaclass.package = profile
    extensions = [e for e in metaclass.extension if e.ownedEnd and e.ownedEnd.type is stereotype]
    if not _one(extensions, "la extensión de Element"):
        extension = UML.recipes.create_extension(metaclass, stereotype)
        extension.package = profile
    attribute = spec.attribute
    if attribute is None:
        attribute = model.create(UML.Property)
        attribute.name = property_name
        stereotype.ownedAttribute = attribute
    if attribute.type is None:
        string = _one(
            (t for t in profile.ownedType if isinstance(t, UML.PrimitiveType) and t.name == "String"),
            "el tipo String",
        )
        if string is None:
            string = model.create(UML.PrimitiveType)
            string.name = "String"
            string.package = profile
        attribute.type = string
    elif not isinstance(attribute.type, UML.PrimitiveType) or attribute.type.name != "String":
        raise DocumentationError(f"La propiedad {property_name} existente no tiene tipo String.")
    return Definition(profile, stereotype, attribute)


def save_documentation(subject, description, note, event_manager, expected=None):
    """Compatibility API: preserve CSS when only documentation is being edited."""
    return _save(subject, description, note, event_manager, expected)


def save_properties(subject, description, note, css, event_manager, expected=None):
    from .styles import parse_css

    parse_css(css)  # Validate every declaration before opening a transaction.
    return _save(subject, description, note, event_manager, expected, css)


def _write_value(subject, property_name, text):
    spec = _ensure_definition(subject.model, property_name)
    instance = _application(subject, spec.stereotype)
    if instance is None:
        instance = UML.recipes.apply_stereotype(subject, spec.stereotype)
    slot = _slot(instance, spec.attribute)
    if slot is None:
        slot = UML.recipes.add_slot(instance, spec.attribute)
    if slot.value is None:
        UML.recipes.set_slot_value(slot, text)
    else:
        # Reuse the literal, preserving identifiers across edits and Git diffs.
        slot.value.value = text


def _save(subject, description, note, event_manager, expected=None, css=_UNSET):
    """Commit all supplied fields atomically; an unchanged save creates no data."""
    if target_element(subject) is None:
        raise DocumentationError("Selecciona un elemento UML compatible.")
    try:
        model = subject.model
    except TypeError as error:
        raise DocumentationError("El elemento ya no pertenece al modelo.") from error
    if model.lookup(subject.id) is not subject:
        raise DocumentationError("El elemento ya no pertenece al modelo.")
    current = (read_description(subject), subject.note or "")
    updated = (description, note)
    if css is not _UNSET:
        current += (read_css(subject),)
        updated += (css,)
    if expected is not None and current != expected:
        raise DocumentationError("El contenido cambió mientras editabas. Copia tu texto y vuelve a abrir el editor.")
    if current == updated:
        return False
    with Transaction(event_manager):
        if description != current[0]:
            _write_value(subject, PROPERTY, description)
        if note != current[1]:
            subject.note = note
        if css is not _UNSET and css != current[2]:
            _write_value(subject, CSS_PROPERTY, css)
    return True
