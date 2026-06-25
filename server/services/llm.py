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
- Pages list should contain the names of all pages defined in the PRD
- IMPORTANT: All string values in JSON must be properly escaped. Escape double quotes inside strings as \\", newlines as \\n, tabs as \\t.
"""

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
- Make sure the design is responsive
- IMPORTANT: All string values in JSON must be properly escaped. Escape double quotes inside strings as \\", newlines as \\n, tabs as \\t."""


def _extract_string(text: str, pos: int) -> tuple[str, int]:
    """Extract a JSON string value starting at pos (which should point to the opening quote).
    Returns (value, end_position) where end_position is past the closing quote."""
    if text[pos] != '"':
        return "", pos
    pos += 1
    chars = []
    while pos < len(text):
        c = text[pos]
        if c == '\\':
            pos += 1
            if pos < len(text):
                chars.append(text[pos])
                pos += 1
        elif c == '"':
            return "".join(chars), pos + 1
        else:
            chars.append(c)
            pos += 1
    return "".join(chars), pos


def _extract_array(text: str, pos: int) -> tuple[list, int]:
    """Extract a JSON array starting at pos (should point to '[')."""
    items = []
    if text[pos] != '[':
        return items, pos
    pos += 1
    while pos < len(text) and text[pos] != ']':
        c = text[pos]
        if c == '"':
            val, pos = _extract_string(text, pos)
            items.append(val)
        elif c == ',':
            pos += 1
        else:
            pos += 1
    return items, pos + 1 if pos < len(text) else pos


def _lenient_parse(text: str) -> dict:
    """Parse known JSON structure field by field using a state machine.
    Handles HTML/CSS/JS content with unescaped characters."""
    result = {}
    i = text.find("{")
    if i == -1:
        return result
    i += 1

    known_keys = ["type", "reply", "html", "css", "js", "prd", "pages"]

    while i < len(text):
        # Skip whitespace and punctuation
        while i < len(text) and text[i] in " \t\n\r,}":
            i += 1
        if i >= len(text) or text[i] == '}':
            break

        # Extract key
        if text[i] == '"':
            key, i = _extract_string(text, i)
        else:
            i += 1
            continue

        # Skip colon
        while i < len(text) and text[i] in " \t\n\r:":
            i += 1

        # Extract value based on type
        if key in ("pages",):
            val, i = _extract_array(text, i)
            result[key] = val
        elif i < len(text) and text[i] == '"':
            val, i = _extract_string(text, i)
            result[key] = val
        else:
            i += 1

    return result


def _parse_response(text: str) -> dict:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("AI 返回了空内容")

    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()

    # Try strict JSON parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fallback: extract {...} block and try strict
    idx = cleaned.find("{")
    end = cleaned.rfind("}")
    if idx != -1 and end > idx:
        block = cleaned[idx : end + 1]
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            pass

    # Final fallback: lenient state machine
    result = _lenient_parse(cleaned)
    if result.get("type") or result.get("reply") or result.get("html"):
        return result

    # If nothing worked, treat the entire response as a plain text reply
    return {"type": "page", "reply": cleaned[:2000], "html": "", "css": "", "js": ""}


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
