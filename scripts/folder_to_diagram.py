"""Import a folder into the open Gaphor model. Load with runpy.run_path()."""

import math
from pathlib import Path

from gaphor import UML
from gaphor.core.modeling import StyleSheet
from gaphor.diagram.event import DiagramOpened
from gaphor.diagram.group import change_owner
from gaphor.transaction import Transaction
from gaphor.UML.classes.package import PackageItem
from gaphor.UML.deployments.artifact import ArtifactItem


def _model_path(element):
    parts, seen = [], set()
    while element is not None and element.id not in seen:
        seen.add(element.id)
        parts.append(element.name or str(element.id))
        element = (
            element.element
            if isinstance(element, UML.Diagram)
            else getattr(element, "owner", None)
        )
    return "/".join(reversed(parts))


def list_targets(service):
    """Return IDs and paths usable as parent= or diagram= arguments."""
    factory = service("element_factory")
    return {
        label: sorted(
            ({"id": str(e.id), "path": _model_path(e)} for e in factory.select(kind)),
            key=lambda row: row["path"],
        )
        for label, kind in (("packages", UML.Package), ("diagrams", UML.Diagram))
    }


def _resolve(factory, selector, kind):
    candidates = list(factory.select(kind))
    by_id = [e for e in candidates if str(e.id) == selector]
    matches = by_id or [
        e for e in candidates if _model_path(e) == selector or e.name == selector
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Destino inexistente o ambiguo: {selector!r}. "
            "Consulta list_targets(service) y utiliza el ID."
        )
    return matches[0]


def _scan(folder, exclude, max_items):
    """Read names and filesystem types only; finish before touching the model."""
    path = Path(folder).expanduser()
    if not path.is_absolute() or not path.is_dir():
        raise ValueError("folder debe ser la ruta absoluta de una carpeta existente.")
    if isinstance(exclude, str):
        raise ValueError("exclude debe ser una secuencia, por ejemplo ('.git',).")
    if not isinstance(max_items, int) or max_items < 1:
        raise ValueError("max_items debe ser un entero positivo.")
    excluded = set(exclude)
    counts = {"folders": 0, "files": 0}
    skipped = []

    def visit(entry, depth):
        if depth > 60:
            raise ValueError("La carpeta supera los 60 niveles de profundidad.")
        if entry.is_symlink() or entry.is_junction():
            skipped.append(str(entry))
            return None
        directory = entry.is_dir()
        if not directory and not entry.is_file():
            skipped.append(str(entry))
            return None
        counts["folders" if directory else "files"] += 1
        if sum(counts.values()) > max_items:
            raise ValueError(
                f"Más de {max_items} archivos/carpetas: usa exclude o max_items."
            )
        children = None
        if directory:
            children = []
            for child in sorted(entry.iterdir(), key=lambda p: (p.name.casefold(), p.name)):
                if child.name in excluded:
                    skipped.append(str(child))
                elif (node := visit(child, depth + 1)) is not None:
                    children.append(node)
            children.sort(key=lambda node: node[1] is None)
        return entry.name or entry.anchor, children

    tree = visit(path, 0)
    if tree is None:
        raise ValueError("Usa la ruta real de la carpeta, no un enlace o junction.")
    return tree, counts, skipped


def _position_after_existing(diagram):
    points = [
        item.matrix_i2c.transform_point(*handle.pos)
        for item in diagram.get_all_items()
        for handle in item.handles()
    ]
    if not points:
        return 40, 40
    return max(x for x, _ in points) + 100, min(y for _, y in points)


def _layout(item):
    """Size containers from their children, using Gaphor's measured text sizes."""
    children = list(item.children)
    for child in children:
        _layout(child)
    if not isinstance(item, PackageItem):
        item.width = max(220, float(item.min_width) + 20)
        item.height = max(72, float(item.min_height) + 16)
        return
    padding, gap = 24, 24
    header = max(64, float(item.min_height) + 16)
    target_width = max(
        [260]
        + [child.width for child in children]
        + [math.sqrt(sum((c.width + gap) * (c.height + gap) for c in children)) * 1.4]
    )
    x, y, row_height, right = padding, header, 0, 0
    for child in children:
        if x > padding and x + child.width > target_width + padding:
            x, y, row_height = padding, y + row_height + gap, 0
        child.matrix.set(1, 0, 0, 1, x, y)
        right = max(right, x + child.width)
        row_height = max(row_height, child.height)
        x += child.width + gap
    item.width = max(260, float(item.min_width) + 20, right + padding)
    item.height = max(100, y + row_height + padding)


def import_folder(
    service,
    folder,
    *,
    mode="new",
    name=None,
    parent=None,
    diagram=None,
    exclude=(),
    max_items=1000,
):
    """Create a packaged diagram, or append a folder package to an existing one.

    service: the function provided by Gaphor's Python console.
    mode='new': name names the new wrapper package and diagram; parent is optional.
    mode='existing': diagram identifies a diagram owned by a UML Package.
    Select existing targets by ID, full model path, or unambiguous name.
    This imports a snapshot, never synchronizes/deletes existing elements or saves.
    """
    if mode not in ("new", "existing"):
        raise ValueError("mode debe ser 'new' o 'existing'.")
    if mode == "new" and diagram is not None:
        raise ValueError("diagram solo se utiliza con mode='existing'.")
    if mode == "existing" and (diagram is None or name is not None or parent is not None):
        raise ValueError("El modo existing necesita diagram; no acepta name ni parent.")
    factory = service("element_factory")
    event_manager = service("event_manager")
    service("undo_manager")  # Required for rollback and one-step Undo in the console.
    if Transaction.in_transaction():
        raise ValueError("Ejecuta el importador fuera de otra transacción.")
    sheet = next(factory.select(StyleSheet), None)
    if sheet is None:
        raise ValueError("Abre un modelo de Gaphor con su hoja de estilo antes de importar.")

    tree, counts, skipped = _scan(folder, exclude, max_items)
    folder_name = tree[0]
    if mode == "new":
        if parent is not None:
            owner = _resolve(factory, parent, UML.Package)
        else:
            roots = [e for e in factory.select(UML.Package) if not e.owner]
            if len(roots) > 1:
                raise ValueError("Hay varios paquetes raíz: especifica parent.")
            owner = roots[0] if roots else None
        name = folder_name if name is None else name
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name debe ser un nombre no vacío.")
        siblings = owner.nestedPackage if owner else factory.select(UML.Package)
        if any(e.name == name and e.owner is owner for e in siblings):
            raise ValueError(f"Ya existe el paquete {name!r}; elige otro name.")
        target = None
        position = (40, 40)
    else:
        target = _resolve(factory, diagram, UML.Diagram)
        owner = target.element
        if not isinstance(owner, UML.Package):
            raise ValueError("El diagrama existente debe pertenecer a un paquete UML.")
        if any(e.name == folder_name for e in owner.nestedPackage):
            raise ValueError(
                f"Ya existe el paquete {folder_name!r} en este destino. "
                "La importación no sobrescribe ni sincroniza; usa un diagrama nuevo."
            )
        position = _position_after_existing(target)

    created_items = []

    def create_tree(node, package, parent_item):
        node_name, children = node
        element = factory.create(UML.Package if children is not None else UML.Artifact)
        element.name = node_name
        if not change_owner(package, element):
            raise ValueError(f"No se pudo asignar el paquete de {node_name!r}.")
        item = target.create(
            PackageItem if children is not None else ArtifactItem,
            parent=parent_item,
            subject=element,
        )
        created_items.append(item)
        for child in children or ():
            create_tree(child, element, item)
        return item

    with Transaction(event_manager):
        if mode == "new":
            container = factory.create(UML.Package)
            container.name = name
            if owner is not None:
                container.nestingPackage = owner
            owner = container
            target = factory.create(UML.PackageDiagram)
            target.name = name
            target.element = container
        root_item = create_tree(tree, owner, None)
        # A package's default centered caption would overlap its nested boxes.
        # Scope this rule to the new presentation subtree, including in existing diagrams.
        selector = f'package[id="{root_item.id}"]'
        sheet.styleSheet += (
            f"\n/* folder_to_diagram: {root_item.id} */\n"
            f"{selector}, {selector} package {{ justify-content: start; }}\n"
        )
        target.update(created_items)
        _layout(root_item)
        root_item.matrix.set(1, 0, 0, 1, *position)
        target.update(created_items)

    result = {
        "diagram": _model_path(target),
        "diagram_id": str(target.id),
        "package": _model_path(root_item.subject),
        "folders": counts["folders"],
        "artifacts": counts["files"],
        "created_packages": counts["folders"] + (mode == "new"),
        "skipped": skipped,
    }
    event_manager.handle(DiagramOpened(target))
    return result
