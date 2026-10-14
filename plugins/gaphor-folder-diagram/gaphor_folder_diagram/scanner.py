"""Read directory names only; no Gaphor or GTK objects enter the worker thread."""

from dataclasses import dataclass
import os
from pathlib import Path
import re
import stat
from threading import Event

DEFAULT_EXCLUSIONS = (".git", "node_modules", "dist", "build", ".venv", "__pycache__")


class ScanError(ValueError):
    pass


class ScanCancelled(Exception):
    pass


@dataclass(frozen=True)
class Entry:
    name: str
    is_directory: bool
    children: tuple["Entry", ...] = ()


@dataclass(frozen=True)
class Snapshot:
    root: Entry
    files: int
    directories: int
    excluded: int
    links: int
    special: int


def parse_exclusions(text: str) -> frozenset[str]:
    names = frozenset(n.strip() for n in re.split(r"[;,\n]", text) if n.strip())
    if any(n in (".", "..") or any(c in n for c in "/\\*?[]") for n in names):
        raise ScanError("Escribe nombres de carpetas separados por comas, sin rutas ni comodines.")
    return names


def _check_cancel(cancel):
    if cancel.is_set():
        raise ScanCancelled()


def _link(info):
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def scan_folder(folder, exclusions=DEFAULT_EXCLUSIONS, cancel=None) -> Snapshot:
    cancel = cancel or Event()
    root = Path(folder).expanduser().absolute()
    excluded_names = {os.path.normcase(n) for n in exclusions}
    files = directories = excluded = links = special = 0
    records = {}
    pending = [root]
    try:
        _check_cancel(cancel)
        info = root.lstat()
        if _link(info) or not stat.S_ISDIR(info.st_mode):
            raise ScanError("Selecciona una carpeta real, no un archivo, enlace o unión de directorios.")
        while pending:
            _check_cancel(cancel)
            path = pending.pop()
            # Recheck before traversing: a previously listed directory may have changed.
            info = path.lstat()
            if _link(info) or not stat.S_ISDIR(info.st_mode):
                raise ScanError(f"La carpeta cambió durante el análisis: {path}. Vuelve a analizar.")
            children = []
            with os.scandir(path) as listing:
                for entry in listing:
                    _check_cancel(cancel)
                    info = entry.stat(follow_symlinks=False)
                    if _link(info):
                        links += 1
                    elif stat.S_ISDIR(info.st_mode):
                        if os.path.normcase(entry.name) in excluded_names:
                            excluded += 1
                        else:
                            child = path / entry.name
                            children.append((entry.name, True, child))
                            pending.append(child)
                    elif stat.S_ISREG(info.st_mode):
                        children.append((entry.name, False, None))
                        files += 1
                    else:
                        special += 1
            records[path] = sorted(children, key=lambda c: (c[1], c[0].casefold(), c[0]))
            directories += 1
        nodes = {}
        # Children were inserted later than their parents; assemble without recursion.
        for path, children in reversed(list(records.items())):
            _check_cancel(cancel)
            nodes[path] = Entry(
                path.name or path.anchor.rstrip("/\\"), True,
                tuple(nodes[child] if is_dir else Entry(name, False) for name, is_dir, child in children),
            )
        return Snapshot(nodes[root], files, directories, excluded, links, special)
    except OSError as error:
        raise ScanError(f"No se pudo leer {error.filename or root}: {error.strerror or error}. No se generó ninguna captura.") from error
