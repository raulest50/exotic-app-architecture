from pathlib import Path

path = Path(__file__).with_name("integration.py")
exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"),
     {"__file__": str(path), "INSTALLED": True})
