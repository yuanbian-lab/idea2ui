import json
from pathlib import Path
from server.config import OUTPUT_DIR


def export_files(name: str, html: str, css: str, js: str) -> Path:
    project_dir = OUTPUT_DIR / name
    project_dir.mkdir(parents=True, exist_ok=True)

    (project_dir / "index.html").write_text(
        f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="stylesheet" href="style.css" />
  <title>{name}</title>
</head>
<body>
{html}
  <script src="script.js"></script>
</body>
</html>""",
        encoding="utf-8",
    )

    (project_dir / "style.css").write_text(css, encoding="utf-8")
    (project_dir / "script.js").write_text(js, encoding="utf-8")
    return project_dir


def list_projects() -> list[str]:
    if not OUTPUT_DIR.exists():
        return []
    return sorted(
        [p.name for p in OUTPUT_DIR.iterdir() if p.is_dir()],
        reverse=True,
    )


def read_project(name: str) -> dict | None:
    project_dir = OUTPUT_DIR / name
    if not project_dir.exists():
        return None

    files = {}
    for f in project_dir.iterdir():
        if f.is_file() and f.suffix in (".html", ".css", ".js"):
            files[f.suffix.lstrip(".")] = f.read_text(encoding="utf-8")
    return files if files else None
