import json
import time
import uuid
from pathlib import Path
from server.config import OUTPUT_DIR
from server.models.schemas import ProjectData, Message, PageInfo


def _project_path(project_id: str) -> Path:
    return OUTPUT_DIR / project_id


def _data_path(project_id: str) -> Path:
    return _project_path(project_id) / "project.json"


def _pages_dir(project_id: str) -> Path:
    return _project_path(project_id) / "pages"


def list_projects() -> list[dict]:
    if not OUTPUT_DIR.exists():
        return []
    projects = []
    for p in OUTPUT_DIR.iterdir():
        data_file = p / "project.json"
        if data_file.exists():
            data = json.loads(data_file.read_text(encoding="utf-8"))
            projects.append({
                "id": data["id"],
                "name": data.get("name", ""),
                "platform": data.get("platform", "web"),
                "created_at": data.get("created_at", 0),
                "updated_at": data.get("updated_at", 0),
            })
    projects.sort(key=lambda x: x["updated_at"], reverse=True)
    return projects


def create_project(name: str, platform: str) -> dict:
    project_id = uuid.uuid4().hex[:12]
    now = time.time()
    project = ProjectData(
        id=project_id,
        name=name,
        platform=platform,
        created_at=now,
        updated_at=now,
    )
    save_project(project)
    return project.model_dump()


def get_project(project_id: str) -> ProjectData | None:
    path = _data_path(project_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return ProjectData(**data)


def save_project(project: ProjectData):
    path = _data_path(project.id)
    path.parent.mkdir(parents=True, exist_ok=True)
    project.updated_at = time.time()
    path.write_text(
        json.dumps(project.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # Save each page's code as individual files
    pages_dir = _pages_dir(project.id)
    for page in project.pages:
        if page.generated:
            page_dir = pages_dir / page.name
            page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "index.html").write_text(
                f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>{page.css}</style>
  <title>{page.name}</title>
</head>
<body>
{page.html}
  <script src="script.js"></script>
</body>
</html>""",
                encoding="utf-8",
            )
            (page_dir / "style.css").write_text(page.css, encoding="utf-8")
            (page_dir / "script.js").write_text(page.js, encoding="utf-8")


def delete_project(project_id: str) -> bool:
    path = _project_path(project_id)
    if not path.exists():
        return False
    import shutil
    shutil.rmtree(path)
    return True


def add_message(project_id: str, role: str, content: str):
    project = get_project(project_id)
    if not project:
        return
    project.messages.append(Message(role=role, content=content))
    save_project(project)


def save_pages(project_id: str, page_name: str, html: str, css: str, js: str):
    project = get_project(project_id)
    if not project:
        return
    for p in project.pages:
        if p.name == page_name:
            p.generated = True
            p.html = html
            p.css = css
            p.js = js
            break
    save_project(project)
