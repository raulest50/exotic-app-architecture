"""Read-only reference text from native model elements and graphical nesting."""

from gaphor import UML


class ReferenceError(ValueError):
    """A reference cannot be copied from the current diagram context."""


def element_name(element, model):
    if element is None or model.lookup(element.id) is not element:
        raise ReferenceError("El elemento ya no está disponible en este proyecto.")
    name = getattr(element, "name", None)
    if not isinstance(name, str) or not name.strip():
        raise ReferenceError("El elemento no tiene nombre para copiar.")
    return name


def diagram_path(item, diagram, model):
    if (diagram is None or model.lookup(diagram.id) is not diagram
            or item.diagram is not diagram
            or not any(candidate is item for candidate in diagram.get_all_items())):
        raise ReferenceError("La figura ya no está disponible en el diagrama.")
    parts = [element_name(item.subject, model)]
    seen = {id(item)}
    parent = item.parent
    while parent is not None:
        if id(parent) in seen or parent.diagram is not diagram:
            raise ReferenceError("No se pudo determinar el anidamiento de la figura.")
        seen.add(id(parent))
        if isinstance(parent.subject, UML.Package):
            parts.append(element_name(parent.subject, model))
        parent = parent.parent
    return "/".join(reversed(parts))


def tree_path(element, diagram, model):
    element_name(element, model)
    if diagram is None or model.lookup(diagram.id) is not diagram:
        raise ReferenceError("Abre un diagrama que muestre este elemento para copiar su ruta.")
    paths = {diagram_path(item, diagram, model)
             for item in diagram.get_all_items() if item.subject is element}
    if not paths:
        raise ReferenceError("El elemento no aparece en el diagrama activo. Copia la ruta desde su figura en otro diagrama.")
    if len(paths) > 1:
        raise ReferenceError("El elemento tiene varias rutas en este diagrama. Copia desde la figura correspondiente.")
    return paths.pop()
