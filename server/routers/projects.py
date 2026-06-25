from fastapi import APIRouter, HTTPException
from server.models.schemas import ProjectCreateRequest, ProjectData
from server.services.project_manager import (
    list_projects,
    create_project,
    get_project,
    delete_project,
    save_project,
)

router = APIRouter(prefix="/api", tags=["projects"])


@router.get("/projects")
async def list_all():
    return list_projects()


@router.post("/projects")
async def create(req: ProjectCreateRequest):
    return create_project(name=req.name, platform=req.platform)


@router.get("/projects/{project_id}")
async def get(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project.model_dump()


@router.put("/projects/{project_id}")
async def update(project_id: str, data: dict):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    for key in ("name", "platform", "prd", "current_page", "messages", "pages"):
        if key in data:
            setattr(project, key, data[key])
    save_project(project)
    return project.model_dump()


@router.delete("/projects/{project_id}")
async def delete(project_id: str):
    if not delete_project(project_id):
        raise HTTPException(status_code=404, detail="项目不存在")
    return {"ok": True}
