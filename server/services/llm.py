import httpx
import json
import re

SYSTEM_PROMPT = """You are a UI generator. Your task is to generate a complete web page based on the user's description.

You must output your response in the following JSON format (no markdown, no code fences, pure JSON only):
{
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
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


async def chat_completion(
    messages: list[dict],
    model: str,
    api_key: str,
    base_url: str,
    modified_code: str = "",
) -> dict:
    system_msg = {"role": "system", "content": SYSTEM_PROMPT}
    full_messages = [system_msg] + messages

    if modified_code:
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
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

    return _parse_response(content)
