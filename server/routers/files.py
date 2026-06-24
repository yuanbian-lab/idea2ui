from fastapi import APIRouter, HTTPException
from server.models.schemas import ExportRequest, ExportResponse, FileListResponse
from server.services.file_manager import export_files, list_projects, read_project

router = APIRouter(prefix="/api", tags=["files"])


@router.post("/export", response_model=ExportResponse)
async def export(req: ExportRequest):
    try:
        project_dir = export_files(name=req.name, html=req.html, css=req.css, js=req.js)
        files = [f.name for f in project_dir.iterdir() if f.is_file()]
        return ExportResponse(path=str(project_dir), files=files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects", response_model=FileListResponse)
async def list_projects_api():
    projects = list_projects()
    return FileListResponse(projects=projects, current=projects[0] if projects else None)


@router.get("/projects/{name}")
async def get_project(name: str):
    data = read_project(name)
    if data is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    return data
