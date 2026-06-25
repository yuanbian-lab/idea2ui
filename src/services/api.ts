import type { Message, ModelConfig } from '../types'
import { modelConfig } from '../stores/app'

export async function chat(
  messages: Message[],
  config: ModelConfig,
  modifiedCode: string = '',
  mode: string = 'page',
): Promise<{
  type: string
  reply: string
  html: string
  css: string
  js: string
  prd: string
  pages: string[]
}> {
  const resp = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: messages.map(m => ({ role: m.role, content: m.content })),
      model: config.model,
      api_key: config.apiKey,
      base_url: config.baseUrl,
      modified_code: modifiedCode,
      mode,
    }),
  })
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }))
    throw new Error(err.detail || '请求失败')
  }
  return resp.json()
}

export async function exportFiles(
  html: string,
  css: string,
  js: string,
  name: string = 'index',
): Promise<{ path: string; files: string[] }> {
  const resp = await fetch('/api/export', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ html, css, js, name }),
  })
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }))
    throw new Error(err.detail || '导出失败')
  }
  return resp.json()
}

export async function fetchProjects(): Promise<{ projects: string[]; current: string | null }> {
  const resp = await fetch('/api/projects')
  if (!resp.ok) throw new Error('获取项目列表失败')
  return resp.json()
}

export async function fetchProject(name: string): Promise<{ html: string; css: string; js: string }> {
  const resp = await fetch(`/api/projects/${name}`)
  if (!resp.ok) throw new Error('获取项目失败')
  return resp.json()
}

export async function loadConfig(): Promise<void> {
  const resp = await fetch('/api/config')
  if (!resp.ok) return
  const data = await resp.json()
  Object.assign(modelConfig, data)
}

export async function saveConfig(): Promise<void> {
  await fetch('/api/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...modelConfig }),
  })
}
