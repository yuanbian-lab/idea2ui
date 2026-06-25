import { reactive } from 'vue'
import type { Message, ModelConfig } from '../types'
import type { ChatApiResponse } from '../services/api'

export type Phase = 'idle' | 'platform_select' | 'prd_design' | 'prd_confirm' | 'page_generation'

export interface PageInfo {
  name: string
  generated: boolean
  html: string
  css: string
  js: string
}

export interface ProjectInfo {
  id: string
  name: string
  platform: string
  created_at: number
  updated_at: number
}

export const messages = reactive<Message[]>([])

export const modelConfig = reactive<ModelConfig>({
  provider: 'deepseek',
  model: 'deepseek-chat',
  apiKey: '',
  baseUrl: 'https://api.deepseek.com',
})

export const generatedCode = reactive<{
  html: string
  css: string
  js: string
}>({
  html: '',
  css: '',
  js: '',
})

export const phase = reactive<{ value: Phase }>({ value: 'idle' })

export const prdContent = reactive<{ value: string }>({ value: '' })

export const pages = reactive<{ value: PageInfo[] }>({ value: [] })

export const currentPage = reactive<{ value: string | null }>({ value: null })

export const thinking = reactive<{ value: boolean }>({ value: false })

export const projects = reactive<{ value: ProjectInfo[] }>({ value: [] })

export const currentProjectId = reactive<{ value: string }>({ value: '' })

export const currentPlatform = reactive<{ value: string }>({ value: 'web' })

export const deviceMode = reactive<{
  width: number
  height: number
  label: string
}>({ width: 1440, height: 900, label: 'PC' })

const DEVICE_PRESETS: Record<string, { width: number; height: number }[]> = {
  web: [
    { width: 1440, height: 900 },
    { width: 1920, height: 1080 },
    { width: 1024, height: 768 },
  ],
  mobile_web: [
    { width: 375, height: 812 },
    { width: 390, height: 844 },
    { width: 414, height: 896 },
  ],
  app: [
    { width: 375, height: 812 },
    { width: 390, height: 844 },
    { width: 430, height: 932 },
  ],
  mini_program: [
    { width: 375, height: 812 },
    { width: 390, height: 844 },
  ],
}

export function getDevicePresets() {
  return DEVICE_PRESETS[currentPlatform.value] || DEVICE_PRESETS.web
}

export function setDevice(width: number, height: number, label: string) {
  deviceMode.width = width
  deviceMode.height = height
  deviceMode.label = label
}

export function addMessage(role: 'user' | 'assistant', content: string) {
  messages.push({
    id: Date.now().toString(),
    role,
    content,
    timestamp: Date.now(),
  })
}

export function confirmPrd() {
  phase.value = 'page_generation'
}

export function setPageGenerated(name: string, html: string, css: string, js: string) {
  const page = pages.value.find(p => p.name === name)
  if (page) {
    page.generated = true
    page.html = html
    page.css = css
    page.js = js
  }
}

export function getPage(name: string): PageInfo | undefined {
  return pages.value.find(p => p.name === name)
}

export function loadProjectState(project: any) {
  messages.splice(0)
  pages.value = []
  currentPage.value = null
  generatedCode.html = ''
  generatedCode.css = ''
  generatedCode.js = ''
  prdContent.value = ''
  currentPlatform.value = project.platform || 'web'

  for (const msg of project.messages || []) {
    messages.push({ id: Date.now().toString() + Math.random(), role: msg.role, content: msg.content, timestamp: Date.now() })
  }

  if (project.prd) {
    prdContent.value = project.prd
    phase.value = 'prd_confirm'
  }

  if (project.pages && project.pages.length > 0) {
    pages.value = project.pages.map(p => ({ ...p }))
    if (project.current_page) {
      currentPage.value = project.current_page
      const page = pages.value.find(p => p.name === project.current_page)
      if (page && page.generated) {
        generatedCode.html = page.html
        generatedCode.css = page.css
        generatedCode.js = page.js
      }
    }
    if (project.prd) {
      phase.value = 'page_generation'
    }
  }

  if (!project.prd && messages.length === 0) {
    phase.value = 'platform_select'
  } else if (messages.length > 0 && !project.prd) {
    phase.value = 'prd_design'
  }
}

export function resetCurrentProject() {
  messages.splice(0)
  generatedCode.html = ''
  generatedCode.css = ''
  generatedCode.js = ''
  prdContent.value = ''
  pages.value = []
  currentPage.value = null
  phase.value = 'idle'
  currentProjectId.value = ''
}
