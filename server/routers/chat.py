from fastapi import APIRouter, HTTPException
from server.models.schemas import ChatRequest, ChatResponse
from server.services.llm import chat_completion

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.api_key:
        raise HTTPException(status_code=400, detail="API Key 未设置")

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
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
