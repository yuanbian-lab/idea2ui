from pydantic import BaseModel


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


class FileListResponse(BaseModel):
    projects: list[str]
    current: str | None = None
