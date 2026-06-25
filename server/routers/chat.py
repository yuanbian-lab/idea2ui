from fastapi import APIRouter, HTTPException
from server.models.schemas import ChatRequest, ChatResponse
from server.services.llm import chat_completion
from server.services.project_manager import add_message, get_project, save_pages

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.api_key:
        raise HTTPException(status_code=400, detail="API Key 未设置")

    # Save user message
    if req.project_id:
        add_message(req.project_id, role="user", content=req.messages[-1].content if req.messages else "")

    try:
        messages = [{"role": m.role, "content": m.content} for m in req.messages]
        result = await chat_completion(
            messages=messages,
            model=req.model,
            api_key=req.api_key,
            base_url=req.base_url,
            modified_code=req.modified_code,
            mode=req.mode,
        )
        reply = ChatResponse(**result)

        # Save assistant message
        if req.project_id:
            add_message(req.project_id, role="assistant", content=reply.reply)

        # If we got pages back (PRD), update the project
        if result.get("pages") and req.project_id:
            project = get_project(req.project_id)
            if project:
                existing = {p.name for p in project.pages}
                for name in result["pages"]:
                    if name not in existing:
                        from server.models.schemas import PageInfo
                        project.pages.append(PageInfo(name=name))
                if result.get("prd"):
                    project.prd = result["prd"]
                from server.services.project_manager import save_project
                save_project(project)

        # If we got generated code, save it
        if result.get("html") and result.get("type") == "page" and req.project_id:
            project = get_project(req.project_id)
            if project and project.current_page:
                save_pages(req.project_id, project.current_page, result["html"], result["css"], result["js"])

        return reply
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
