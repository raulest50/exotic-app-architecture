import time

from gi.repository import GLib


def entries(menu):
    for index in range(menu.get_n_items()):
        label = menu.get_item_attribute_value(index, "label", None)
        action = menu.get_item_attribute_value(index, "action", None)
        target = menu.get_item_attribute_value(index, "target", None)
        if label:
            yield label.get_string(), action.get_string() if action else None, target
        for link in ("section", "submenu"):
            if child := menu.get_item_link(index, link):
                yield from entries(child)


def action_target(menu, label):
    return next(target.get_string() for text, _action, target in entries(menu) if text == label)


def clipboard_text(window):
    values = []
    errors = []

    def ready(clipboard, result):
        try:
            values.append(clipboard.read_text_finish(result))
        except Exception as error:
            errors.append(error)

    window.get_clipboard().read_text_async(None, ready)
    deadline = time.monotonic() + 5
    context = GLib.MainContext.default()
    while not values and not errors and time.monotonic() < deadline:
        while context.pending():
            context.iteration(False)
        time.sleep(0.005)
    if errors:
        raise errors[0]
    assert values, "Clipboard read timed out"
    return values[0]
