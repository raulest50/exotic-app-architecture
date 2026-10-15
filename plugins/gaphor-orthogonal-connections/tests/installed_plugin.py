from pathlib import Path
INSTALLED = True
exec(compile(Path(__file__).with_name("integration.py").read_text(encoding="utf-8"), str(Path(__file__).with_name("integration.py")), "exec"))
