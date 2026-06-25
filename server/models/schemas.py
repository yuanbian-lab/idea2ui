from pydantic import BaseModel
from typing import Optional


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    model: str = "gpt-4o"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    modified_code: str = ""
    mode: str = "page"
    project_id: str = ""


class ChatResponse(BaseModel):
    type: str = "page"
    reply: str = ""
    html: str = ""
    css: str = ""
    js: str = ""
    prd: str = ""
    pages: list[str] = []


class ExportRequest(BaseModel):
    html: str
    css: str
    js: str
    name: str = "index"


class ExportResponse(BaseModel):
    path: str
    files: list[str]


class PageInfo(BaseModel):
    name: str
    generated: bool = False
    html: str = ""
    css: str = ""
    js: str = ""


class ProjectData(BaseModel):
    id: str
    name: str = ""
    platform: str = "web"
    created_at: float = 0
    updated_at: float = 0
    messages: list[Message] = []
    prd: str = ""
    pages: list[PageInfo] = []
    current_page: str = ""


class ProjectSummary(BaseModel):
    id: str
    name: str
    platform: str
    created_at: float
    updated_at: float


class FileListResponse(BaseModel):
    projects: list[str]
    current: str | None = None


class ProjectCreateRequest(BaseModel):
    name: str
    platform: str = "web"
