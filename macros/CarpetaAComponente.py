# -*- coding: utf-8 -*-
"""Modelio 6.2 / Jython: seleccionar un paquete y ejecutar esta macro.
Carpeta raiz -> componente; subcarpetas -> paquetes; archivos -> artefactos.
No lee el contenido de archivos ni elimina elementos del modelo.
"""
import os
from org.modelio.api.modelio import Modelio
from org.modelio.metamodel.uml.statik import Package, Component
from org.eclipse.draw2d.geometry import Rectangle
from org.eclipse.swt.widgets import Display, DirectoryDialog

KEY = 'folderDiagram.relativePath'
MARK = 'folderDiagram.version'
DIAGRAM_KEY = 'folderDiagram.component'
IGNORED = set(['.git', 'node_modules', '__pycache__', '.DS_Store', 'Thumbs.db'])


def scan(folder):
    def visit(path, relative):
        node = dict(name=os.path.basename(path), path=relative, children=[], kind='Package')
        for name in sorted(os.listdir(path), key=lambda s: s.lower()):
            full = os.path.join(path, name)
            if name in IGNORED or os.path.islink(full):
                continue
            rel = relative + '/' + name if relative else name
            if os.path.isdir(full):
                node['children'].append(visit(full, rel))
            elif os.path.isfile(full):
                node['children'].append(dict(name=name, path=rel, children=[], kind='Artifact'))
        return node
    result = visit(os.path.abspath(folder), '')
    result['kind'] = 'Component'
    return result


def measure(node):
    if node['kind'] == 'Artifact':
        node['width'] = max(240, len(node['name']) * 8 + 30)
        node['height'] = 65
        return
    # Three files per row; nested folders occupy their own rows.
    x, y, row_height, width = 24, 70, 0, 320
    col = 0
    for child in node['children']:
        measure(child)
        if child['kind'] != 'Artifact' or col == 3:
            y += row_height + (24 if row_height else 0)
            x, row_height, col = 24, 0, 0
        child['x'], child['y'] = x, y
        width = max(width, x + child['width'] + 24)
        if child['kind'] == 'Artifact':
            x += child['width'] + 24
            row_height = max(row_height, child['height'])
            col += 1
        else:
            y += child['height'] + 24
    node['width'], node['height'] = width, max(140, y + row_height + 24)


def generate(folder, target, dry_run=False, open_editor=True):
    tree = scan(folder)  # Finish filesystem reads before modifying the model.
    measure(tree)
    app = Modelio.getInstance()
    session = app.getModelingSession()
    factory = session.getModel()
    if not isinstance(target, (Package, Component)):
        raise ValueError('Selecciona un paquete destino o un componente creado por esta macro.')
    if isinstance(target, Component):
        root = target
        if root.getLocalProperty(MARK) != '1':
            raise ValueError('Este componente es manual. Selecciona otro paquete destino para generar uno nuevo.')
    else:
        matches = [e for e in target.getOwnedElement()
                   if e.getName() == tree['name'] and isinstance(e, Component)]
        if len(matches) > 1:
            raise ValueError('Hay varios componentes con ese nombre; selecciona el componente exacto.')
        root = matches[0] if matches else None
        if root is not None and root.getLocalProperty(MARK) != '1':
            raise ValueError('Ya existe un componente manual con ese nombre. No se modifico.')
    transaction = session.createTransaction('Generar componente desde carpeta')
    handle = None
    created = [0]
    seen = set()
    try:
        if root is None:
            root = factory.createComponent(tree['name'], target)
            root.setLocalProperty(MARK, '1')
        tree['element'] = root
        existing = {}

        def index(owner):
            for element in owner.getOwnedElement():
                rel = element.getLocalProperty(KEY)
                if rel:
                    if rel in existing:
                        raise ValueError('Subruta duplicada en el modelo: ' + rel)
                    existing[rel] = element
                if isinstance(element, (Package, Component)):
                    index(element)
        index(root)

        def populate(parent):
            for child in parent['children']:
                rel = child['path']
                seen.add(rel)
                element = existing.get(rel)
                if element is not None:
                    if element.getMClass().getName() != child['kind']:
                        raise ValueError('Cambio de archivo/carpeta en: ' + rel)
                    if element.getOwner() != parent['element']:
                        raise ValueError('El elemento fue movido manualmente: ' + rel)
                else:
                    maker = factory.createPackage if child['kind'] == 'Package' else factory.createArtifact
                    element = maker(child['name'], parent['element'])
                    element.setLocalProperty(KEY, rel)
                    created[0] += 1
                child['element'] = element
                populate(child)
        populate(tree)
        diagrams = [dg for dg in root.getProduct()
                    if dg.getLocalProperty(DIAGRAM_KEY) == root.getUuid()]
        if len(diagrams) > 1:
            raise ValueError('Hay varios diagramas generados para este componente.')
        diagram = diagrams[0] if diagrams else factory.createClassDiagram(
            tree['name'] + ' - archivos', root, None)
        diagram.setLocalProperty(DIAGRAM_KEY, root.getUuid())
        handle = app.getDiagramService().getDiagramHandle(diagram)

        def draw(node, x, y, parent_graphic=None):
            graphics = list(handle.getDiagramGraphics(node['element']))
            if not graphics:
                graphics = list(handle.unmask(node['element'], x, y))
            if not graphics:
                raise ValueError('No se pudo representar: ' + node['name'])
            graphic = graphics[0]
            prefix = node['kind'].upper()
            if node['kind'] != 'Artifact':
                graphic.setProperty(prefix + '_INNERVIEWMODE', 'DIAGRAM')
            if parent_graphic is not None:
                # Refuse a silently flattened diagram.
                parent = graphic.getParent()
                while parent is not None and parent != parent_graphic:
                    parent = parent.getParent() if hasattr(parent, 'getParent') else None
                if parent is None:
                    raise ValueError('Modelio no anido el elemento: ' + node['path'])
            # Nested graphical bounds are relative to their container.
            bx = node.get('x', x) if parent_graphic else x
            by = node.get('y', y) if parent_graphic else y
            graphic.setBounds(Rectangle(bx, by, node['width'], node['height']))
            for child in node['children']:
                draw(child, x + child['x'], y + child['y'], graphic)
        draw(tree, 30, 30)
        handle.save()
        handle.close()
        handle = None
        missing = sorted(set(existing) - seen)
        if dry_run:
            transaction.rollback()
        else:
            transaction.commit()
            if open_editor:
                app.getEditionService().openEditor(diagram)
        print('Archivos/carpetas: %s; nuevos: %s' % (len(seen), created[0]))
        if missing:
            print('Conservados aunque ya no estan en disco: ' + ', '.join(missing))
        if not dry_run:
            print('Diagrama generado. Guarda el proyecto con el boton superior izquierdo.')
        return len(seen), created[0]
    except:
        if handle is not None:
            handle.close()
        transaction.rollback()
        raise


def main():
    selection = globals().get('selectedElements', globals().get('elements', []))
    selected = list(selection)
    if len(selected) != 1:
        raise ValueError('Selecciona un unico paquete o componente en el arbol.')
    dialog = DirectoryDialog(Display.getDefault().getActiveShell())
    dialog.setText('Carpeta raiz del componente')
    dialog.setMessage('Se incluyen archivos y subcarpetas; se omiten .git y node_modules.')
    folder = dialog.open()
    if folder:
        generate(folder, selected[0])


if not globals().get('FOLDER_DIAGRAM_LIBRARY_ONLY', False):
    main()
