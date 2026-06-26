<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/idea2ui-AI%20%E2%86%92%20UI-1677ff?style=for-the-badge&labelColor=1a1a2e">
  <img alt="idea2ui" src="https://img.shields.io/badge/idea2ui-AI%20%E2%86%92%20UI-1677ff?style=for-the-badge&labelColor=f0f5ff">
</picture>

<p align="center">
  <strong>用自然语言描述想法，AI 自动生成可交互的 UI 原型</strong>
  <br />
  <em>Talk to AI, get a prototype. Iterate with drag & drop.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Vue_3-4FC08D?logo=vue.js" alt="Vue 3" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?logo=typescript" alt="TypeScript" />
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python" alt="Python" />
  <img src="https://img.shields.io/github/license/anomalyco/idea2ui" alt="MIT License" />
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-Powered PRD Design** | Chat with AI to design product requirements documents interactively |
| 🎨 **Page Generation** | Generate individual pages from natural language descriptions |
| 📱 **Multi-Platform** | Web, Mobile Web, App, Mini Program — with device simulation presets |
| ✏️ **Drag & Drop Edit** | Select elements, drag to reposition, modify styles (background, border-radius, text, color, font-size) |
| 📋 **Version Control** | Each save creates a named version; switch between versions anytime |
| 📦 **One-Click Export** | Download all pages as a zip archive with PRD included |
| 💾 **Project Persistence** | All data saved to disk — survives server restart |
| ⚙️ **Multi-Provider** | Supports OpenAI, DeepSeek, OpenRouter, and any OpenAI-compatible API |

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** ≥ 20
- **Python** ≥ 3.11
- An LLM API key (DeepSeek, OpenAI, etc.)

### 1. Clone & Install

```bash
git clone https://github.com/anomalyco/idea2ui.git
cd idea2ui

# Frontend
npm install

# Backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r server/requirements.txt
```

### 2. Configure

```bash
# Optional: set output directory and port
echo "IDEA2UI_OUTPUT_DIR=output" >> .env
echo "PORT=8010" >> .env
```

### 3. Start

```bash
npm run dev
```

This starts both:
- **Frontend** → http://localhost:5173
- **Backend** → http://localhost:8010

### 4. Use

1. Open http://localhost:5173
2. Click ⚙️ **Settings** to configure your API key and model
3. Click **开始设计** and describe your product idea in natural language
4. AI generates a PRD → confirm → generate pages one by one
5. Click ✏️ **编辑** to enter drag-and-drop mode, adjust elements
6. Save versions via **保存为新版本**, switch versions from the toolbar dropdown
7. Click **下载项目** to export all pages as a zip

---

## 🏗 Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│  Vue 3 SPA  │────▶│  FastAPI     │────▶│  LLM API       │
│  (Vite)     │◀────│  (uvicorn)   │     │  (OpenAI/D.S.) │
└─────────────┘     └──────┬───────┘     └────────────────┘
                           │
                    ┌──────▼───────┐
                    │  File System │
                    │  (output/)   │
                    └──────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + TypeScript + Vite + ant-design-vue |
| Backend | Python FastAPI + httpx |
| Storage | JSON files on disk (no database needed) |
| AI Output | Pure HTML + CSS + JS (no framework dependency) |

### Project Structure

```
idea2ui/
├── src/                    # Frontend (Vue 3)
│   ├── components/         # UI components
│   │   ├── ChatPanel.vue   # Message input & display
│   │   ├── PreviewPanel.vue# Preview iframe + editor
│   │   ├── PageNav.vue     # Page navigation tabs
│   │   ├── ProjectPanel.vue# Project switcher
│   │   └── SettingsDialog.vue
│   ├── stores/             # Reactive state (app.ts)
│   ├── services/           # API client
│   ├── utils/              # Editor injector
│   ├── views/              # Page views
│   └── types/              # TypeScript types
├── server/                 # Backend (Python FastAPI)
│   ├── main.py             # App entry
│   ├── config.py           # Configuration
│   ├── routers/            # API routes
│   │   ├── chat.py         # Chat & code generation
│   │   ├── projects.py     # Project CRUD
│   │   ├── config.py       # Model config
│   │   ├── files.py        # File export
│   │   └── download.py     # Zip download
│   ├── services/           # Business logic
│   │   ├── llm.py          # LLM interaction + prompt templates
│   │   └── project_manager.py
│   └── models/
│       └── schemas.py      # Pydantic models
├── output/                 # Persisted projects (gitignored)
├── PRD.md                  # Product requirements document
├── LICENSE
└── README.md
```

---

## 🧠 AI Prompts

The system uses two distinct prompt modes:

- **PRD Mode** — Conversational PRD design. AI asks questions, fills in the product vision, outputs a structured PRD + page list.
- **Page Mode** — Generates a single page based on the PRD. Outputs HTML + CSS + JS as JSON with a robust fallback parser for malformed responses.

Default model: `deepseek-chat` (best Chinese + JSON adherence). Change in Settings → Model.

---

## 🖱 Drag & Drop Editor

When in **edit mode** (click ✏️), the preview iframe gets an injected editor script that enables:

- **Click to select** — highlights element with a blue outline
- **Drag to reposition** — uses CSS `transform: translate()` (non-destructive to layout)
- **Property panel** — floating panel on the right to modify background, border-radius, text color, font-size, and text content
- **Save as version** — creates a named version entry, persists to disk

---

## 🔧 Configuration

### Settings Dialog

| Field | Description |
|-------|-------------|
| Provider | OpenAI, DeepSeek, OpenRouter, or Custom |
| Model | Model name (e.g., `deepseek-chat`, `gpt-4o`) |
| API Key | Your API key |
| Base URL | API endpoint (auto-filled per provider) |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `IDEA2UI_OUTPUT_DIR` | `output` | Project data storage path |
| `HOST` | `0.0.0.0` | Backend listen address |
| `PORT` | `8010` | Backend listen port |

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

[MIT](LICENSE)
