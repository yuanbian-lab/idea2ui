# PRD: idea2ui — v2.0

## 1. 产品概述

**idea2ui** 帮助用户将一个想法迅速变为一个可用的 UI 交付。用户通过自然语言描述需求，AI 自动生成原生 Web 原型（HTML + CSS + JS），并支持实时预览、拖拽调整和迭代优化。

## 2. 核心流程

1. **需求描述** — 用户用语言描述自己的产品/界面需求
2. **AI 生成** — AI 根据描述快速生成 HTML + CSS + JS 原生的 Web 原型稿件
3. **实时预览 + 拖拽编辑** — 项目界面提供实时预览，用户可以预览生成结果，并支持拖拽调整元素位置与大小
4. **结果导出** — 将调整后的结果写入产出文件夹
5. **持续迭代** — 后续用户可以继续与 AI 对话调整，系统会将已调整过的版本作为上下文一并发送给 AI

## 3. 功能需求

| 模块 | 功能 | 说明 |
|------|------|------|
| 对话输入 | 自然语言描述 | 用户输入界面或产品需求描述 |
| AI 生成 | 生成 Web 原型 | 输出 HTML + CSS + JS 原生代码 |
| 实时预览 | 渲染结果 | 在界面中实时展示生成的页面效果 |
| 拖拽编辑 | 调整位置与大小 | 用户可直接在预览区域拖拽调整元素 |
| 导出 | 写入产出文件夹 | 将调整后的最终结果保存到文件系统 |
| 上下文管理 | 记录调整版本 | 后续对话携带已调整版本作为上下文 |
| 模型配置 | API Key 管理与模型选择 | 用户可设置 API Key，并自由选择任意大模型（如 GPT-4o、Claude、DeepSeek 等） |

## 4. 技术方向

### AI 生成产出
- 产出格式：原生 HTML + CSS + JS（不依赖任何框架）
- AI 集成：通过 LLM API 生成代码
- 预览引擎：iframe / 沙箱渲染
- 拖拽方案：原生拖拽 API 或轻量库（如 interact.js）

### 项目本身技术栈
- 形态：纯 Web 应用
- 前端框架：Vue
- 构建工具：Vite
- 语言：TypeScript
- UI 组件库：antd
- 项目自身样式方案：CSS Modules 或 Tailwind CSS

## 5. 后端架构

### 技术栈
- 语言：Python
- Web 框架：FastAPI
- HTTP 客户端：httpx（用于调用 LLM API）
- 运行方式：Uvicorn ASGI 服务器

### 接口设计

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/chat | 发送对话消息，返回 AI 生成的 HTML/CSS/JS |
| POST | /api/export | 导出生成的 UI 文件到输出目录 |
| GET | /api/projects | 列出所有已导出的项目 |
| GET | /api/projects/{name} | 读取指定项目的文件内容 |
| GET | /api/health | 健康检查 |

### AI 集成流程

1. 前端收集用户消息 + 对话历史 + 模型配置（API Key、模型名、Base URL）
2. 前端通过 `/api/chat` 发送给后端
3. 后端构造 system prompt + 对话历史，调用 LLM API
4. LLM 返回结构化 JSON（reply + html + css + js）
5. 后端解析后返回给前端
6. 前端更新对话列表和预览面板

### 上下文管理
- 每次对话携带完整消息历史
- 若用户已有手动调整的版本，作为 `modified_code` 字段发送给 LLM

### 文件导出
- 导出路径通过 `IDEA2UI_OUTPUT_DIR` 环境变量配置（默认 `output/`）
- 每个项目导出为独立文件夹，包含 index.html / style.css / script.js

### 目录结构

```
server/
├── main.py               # 应用入口，CORS 配置
├── config.py             # 环境变量配置
├── requirements.txt      # Python 依赖
├── models/
│   └── schemas.py        # Pydantic 请求/响应模型
├── routers/
│   ├── chat.py           # AI 对话接口
│   └── files.py          # 文件导出与读取接口
└── services/
    ├── llm.py            # LLM API 调用
    └── file_manager.py   # 文件管理
```

## 6. 交付物

- 可运行的 idea2ui 应用（前端 + 后端）
- 产出文件夹用于保存生成的 UI 文件
