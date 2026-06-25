import httpx
import json
import re

PRD_PROMPT = """You are a product manager and UI designer. Your task is to help the user design a PRD (Product Requirements Document) for their web project.

Follow these steps:
1. Understand the user's product idea
2. Design the complete page structure (e.g., Home page, Course page, Course Detail page)
3. For each page, briefly describe its purpose and key UI elements

You must output your response in the following JSON format (no markdown, no code fences, pure JSON only):
{
  "type": "prd",
  "reply": "对用户需求的回应，或对PRD的说明",
  "prd": "完整的 PRD 文档内容（Markdown 格式），必须包含各个页面的结构定义",
  "pages": ["页面名称1", "页面名称2", "页面名称3"]
}

Rules:
- If the user is still discussing the product idea, respond naturally with type="prd" and keep prd/pages empty
- When the user has given enough information, generate a complete PRD in Markdown
- The PRD must list all pages that need to be built
- Pages list should contain the names of all pages defined in the PRD"""

PAGE_PROMPT = """You are a UI generator. Your task is to generate a single web page based on the PRD and the user's specific requirements.

You must output your response in the following JSON format (no markdown, no code fences, pure JSON only):
{
  "type": "page",
  "reply": "简短说明你生成了什么",
  "html": "<html body content only, no <html> or <body> tags>",
  "css": "完整的 CSS 样式",
  "js": "完整的 JavaScript 代码"
}

Rules:
- HTML: only the content inside <body>, DO NOT include <html>, <head>, or <body> tags
- CSS: complete styles, including layout, colors, responsive design
- JS: all interactive logic
- The page should be visually polished, modern, and well-designed
- Use semantic HTML elements
- Make sure the design is responsive"""


def _parse_response(text: str) -> dict:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("AI 返回了空内容")

    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        idx = cleaned.find("{")
        end = cleaned.rfind("}")
        if idx != -1 and end > idx:
            try:
                return json.loads(cleaned[idx : end + 1])
            except json.JSONDecodeError:
                pass
        raise ValueError(f"AI 返回无法解析的内容: {cleaned[:500]}")


async def chat_completion(
    messages: list[dict],
    model: str,
    api_key: str,
    base_url: str,
    modified_code: str = "",
    mode: str = "page",
) -> dict:
    system_prompt = PRD_PROMPT if mode == "prd" else PAGE_PROMPT
    system_msg = {"role": "system", "content": system_prompt}
    full_messages = [system_msg] + messages

    if modified_code and mode == "page":
        full_messages.append({
            "role": "system",
            "content": f"当前用户已手动调整的版本如下，请基于此版本继续优化：\n{modified_code}",
        })

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": full_messages,
        "temperature": 0.7,
        "max_tokens": 8192,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        url = f"{base_url.rstrip('/')}/chat/completions"
        resp = await client.post(url, headers=headers, json=payload)

        raw_text = resp.text
        if not resp.is_success:
            raise ValueError(f"API 请求失败 ({resp.status_code}): {raw_text[:500]}")

        try:
            data = resp.json()
        except Exception:
            raise ValueError(f"API 返回非 JSON: {raw_text[:500]}")

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise ValueError(f"API 响应结构异常: {json.dumps(data, ensure_ascii=False)[:500]}")

    result = _parse_response(content)
    result.setdefault("type", mode)
    result.setdefault("reply", "")
    result.setdefault("html", "")
    result.setdefault("css", "")
    result.setdefault("js", "")
    result.setdefault("prd", "")
    result.setdefault("pages", [])
    return result
