"""Native UML snapshot creation and measured, bottom-up nested layout."""

from dataclasses import dataclass
import math

from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.modeling import StyleSheet
from gaphor.core.modeling.diagram import StyledItem, UpdateContext
from gaphor.UML.classes.package import PackageItem
from gaphor.UML.deployments.artifact import ArtifactItem

MARGIN = 32
GAP = 24


class ImportError(ValueError):
    pass


@dataclass(frozen=True)
class Capture:
    package: object
    elements: object
    diagram: object
    root_item: object


def nearest_package(element):
    if hasattr(element, "subject"):
        element = element.subject
    seen = set()
    while element is not None and id(element) not in seen:
        seen.add(id(element))
        if type(element) is UML.Package:
            return element
        element = getattr(element, "owner", None)
    return None


def package_path(package):
    parts, seen = [], set()
    while package is not None and id(package) not in seen:
        seen.add(id(package))
        parts.append(package.name or "(sin nombre)")
        package = package.nestingPackage
    return " / ".join(reversed(parts))


def _capture_name(model, destination, root_name):
    occupied = {p.name for p in model.select(UML.Package) if p.nestingPackage is destination}
    base = f"Lectura {root_name}"
    name, count = base, 2
    while name in occupied:
        name = f"{base} ({count})"
        count += 1
    return name


def _measure(item, style_sheet):
    item.update_shapes()
    context = UpdateContext(style=style_sheet.compute_style(StyledItem(item)))
    width, height = item.shape.size(context)
    return math.ceil(width), math.ceil(height)


def _arrange(diagram, root):
    style_sheet = diagram.model.style_sheet or StyleSheet()
    style_sheet.clear_caches()
    items = list(diagram.get_all_items())
    headers = {}
    for item in reversed(items):
        label_width, label_height = _measure(item, style_sheet)
        children = list(item.children)
        if isinstance(item, ArtifactItem):
            item.width = max(180, label_width + 8)
            item.height = max(64, label_height + 8)
            continue
        header = max(48, label_height + 8)
        headers[item.id] = header
        if not children:
            item.width = max(200, label_width + 2 * MARGIN)
            item.height = header + 2 * MARGIN
            continue
        target = max(
            max(c.width for c in children),
            math.sqrt(sum((c.width + GAP) * (c.height + GAP) for c in children)) * 1.4,
        )
        x, y, row_height, used_width = MARGIN, header + MARGIN, 0, 0
        for child in children:
            if x > MARGIN and x + child.width > MARGIN + target:
                x, y, row_height = MARGIN, y + row_height + GAP, 0
            child.matrix.set(1, 0, 0, 1, x, y)
            used_width = max(used_width, x + child.width)
            row_height = max(row_height, child.height)
            x += child.width + GAP
        item.width = max(200, label_width + 2 * MARGIN, used_width + MARGIN)
        item.height = y + row_height + MARGIN
    root.matrix.set(1, 0, 0, 1, MARGIN, MARGIN)
    diagram.update(items)
    validate_layout(diagram, headers)


def validate_layout(diagram, headers=None):
    """Check the actual solved rectangles, not merely the proposed positions."""
    headers = headers or {}
    tolerance = 0.1
    for parent in diagram.get_all_items():
        if parent.width <= 0 or parent.height <= 0:
            raise ImportError("No se pudo calcular el tamaño de una figura.")
        children = list(parent.children)
        rectangles = []
        for child in children:
            a, b, c, d, x, y = child.matrix
            if (a, b, c, d) != (1, 0, 0, 1):
                raise ImportError("Se encontró una transformación inesperada en el diagrama.")
            if (x < MARGIN - tolerance or y < headers.get(parent.id, 0) + MARGIN - tolerance
                or x + child.width > parent.width - MARGIN + tolerance
                or y + child.height > parent.height - MARGIN + tolerance):
                raise ImportError("Una figura no cabe dentro de su paquete. La captura se canceló.")
            rectangles.append((x, y, x + child.width, y + child.height))
        # Sweep in x to avoid comparing every pair for ordinary row layouts.
        active = []
        for rect in sorted(rectangles):
            left, top, right, bottom = rect
            active = [other for other in active if other[2] + GAP > left + tolerance]
            if any(other[3] + GAP > top + tolerance and bottom + GAP > other[1] + tolerance for other in active):
                raise ImportError("Las figuras no tienen suficiente separación. La captura se canceló.")
            active.append(rect)


def create_capture(model, event_manager, snapshot, destination=None):
    if destination is not None and (type(destination) is not UML.Package or model.lookup(destination.id) is not destination):
        raise ImportError("El paquete destino ya no está disponible. Vuelve a abrir la herramienta.")
    with Transaction(event_manager):
        container = model.create(UML.Package)
        container.name = _capture_name(model, destination, snapshot.root.name)
        if destination is not None:
            container.nestingPackage = destination
        elements = model.create(UML.Package)
        elements.name = "elements"
        elements.nestingPackage = container
        diagram = model.create(UML.ComponentDiagram)
        diagram.name = f"{snapshot.root.name} — componente en crudo"
        diagram.element = container
        pending = [(snapshot.root, elements, None)]
        root_item = None
        while pending:
            entry, owner, visual_parent = pending.pop()
            if entry.is_directory:
                subject = model.create(UML.Package)
                subject.name = entry.name
                subject.nestingPackage = owner
                item = diagram.create(PackageItem, subject=subject, parent=visual_parent)
                pending.extend((child, subject, item) for child in reversed(entry.children))
            else:
                subject = model.create(UML.Artifact)
                subject.name = entry.name
                subject.package = owner
                item = diagram.create(ArtifactItem, subject=subject, parent=visual_parent)
            if root_item is None:
                root_item = item
        _arrange(diagram, root_item)
    return Capture(container, elements, diagram, root_item)
