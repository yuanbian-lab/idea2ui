import io
import zipfile
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["download"])


class DownloadPageItem(BaseModel):
    name: str
    version_label: str = ""
    html: str = ""
    css: str = ""
    js: str = ""


class DownloadRequest(BaseModel):
    pages: list[DownloadPageItem] = []
    prd: str = ""


@router.post("/download")
async def download(req: DownloadRequest):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Landing page
        landing_lines = [
            "<!DOCTYPE html>",
            '<html lang="zh-CN">',
            "<head><meta charset='UTF-8'><title>项目导出</title>",
            "<style>body{font-family:sans-serif;max-width:800px;margin:40px auto;padding:0 20px;line-height:1.8}"
            "h1{border-bottom:1px solid #eee;padding-bottom:8px}"
            "ul{padding-left:20px}"
            "a{color:#1677ff;text-decoration:none}"
            "a:hover{text-decoration:underline}</style></head><body>",
            "<h1>📦 项目导出</h1>",
        ]

        # Add PRD
        if req.prd:
            zf.writestr("PRD.md", req.prd.encode("utf-8"))
            landing_lines.append('<p><a href="PRD.md" target="_blank">📄 PRD 文档</a></p>')

        landing_lines.append("<h2>页面列表</h2><ul>")

        for item in req.pages:
            dir_name = f"{item.name}"
            if item.version_label:
                dir_name = f"{item.name}_{item.version_label}"
            page_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>{item.css}</style>
  <title>{item.name} - {item.version_label}</title>
</head>
<body>
{item.html}
  <script>{item.js}</script>
</body>
</html>"""
            zf.writestr(f"{dir_name}/index.html", page_html.encode("utf-8"))
            landing_lines.append(
                f'<li><a href="{dir_name}/index.html" target="_blank">{item.name}'
                f'{" (" + item.version_label + ")" if item.version_label else ""}</a></li>'
            )

        landing_lines.append("</ul></body></html>")
        zf.writestr("index.html", "\n".join(landing_lines).encode("utf-8"))

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=project-export.zip"},
    )
