import type { Message, ModelConfig } from '../types'
import { modelConfig } from '../stores/app'

export interface ChatApiResponse {
  type: string
  reply: string
  html: string
  css: string
  js: string
  prd: string
  pages: string[]
}

export async function chat(
  messages: Message[],
  config: ModelConfig,
  modifiedCode: string = '',
  mode: string = 'page',
  projectId: string = '',
  currentPage: string = '',
): Promise<ChatApiResponse> {
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
      project_id: projectId,
      current_page: currentPage,
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

export async function listProjects(): Promise<any[]> {
  const resp = await fetch('/api/projects')
  if (!resp.ok) throw new Error('获取项目列表失败')
  return resp.json()
}

export async function createProject(name: string, platform: string): Promise<any> {
  const resp = await fetch('/api/projects', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, platform }),
  })
  if (!resp.ok) throw new Error('创建项目失败')
  return resp.json()
}

export async function getProject(id: string): Promise<any> {
  const resp = await fetch(`/api/projects/${id}`)
  if (!resp.ok) throw new Error('获取项目失败')
  return resp.json()
}

export async function updateProject(id: string, data: any): Promise<any> {
  const resp = await fetch(`/api/projects/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!resp.ok) throw new Error('更新项目失败')
  return resp.json()
}

export async function deleteProject(id: string): Promise<void> {
  const resp = await fetch(`/api/projects/${id}`, { method: 'DELETE' })
  if (!resp.ok) throw new Error('删除项目失败')
}

export interface DownloadPageItem {
  name: string
  version_label: string
  html: string
  css: string
  js: string
}

export async function downloadProject(data: { pages: DownloadPageItem[]; prd: string }): Promise<void> {
  const resp = await fetch('/api/download', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!resp.ok) throw new Error('下载失败')
  const blob = await resp.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'project-export.zip'
  a.click()
  URL.revokeObjectURL(url)
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
