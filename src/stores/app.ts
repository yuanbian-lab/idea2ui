import { reactive } from 'vue'
import type { Message, ModelConfig } from '../types'

export type Phase = 'idle' | 'platform_select' | 'prd_design' | 'prd_confirm' | 'page_generation'

export interface PageVersion {
  label: string
  timestamp: number
  html: string
  css: string
  js: string
}

export interface PageInfo {
  name: string
  generated: boolean
  html: string
  css: string
  js: string
  current_version: string
  versions: PageVersion[]
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

export const editMode = reactive<{ value: boolean }>({ value: false })

export const selectedElement = reactive<{ value: any }>({ value: null })

export const elementModifications = reactive<Record<string, Record<string, string>>>({})

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
    const firstVersion: PageVersion = { label: 'v1', timestamp: Date.now(), html, css, js }
    if (!page.versions) page.versions = []
    if (!page.versions.find(v => v.label === 'v1')) {
      page.versions.unshift(firstVersion)
    }
    page.current_version = 'v1'
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
    pages.value = project.pages.map((p: any) => {
      const versions = p.versions || []
      let cv = p.current_version || ''
      if (!cv && p.generated && versions.length === 0) {
        versions.push({ label: 'v1', timestamp: p.updated_at || Date.now(), html: p.html, css: p.css, js: p.js })
        cv = 'v1'
      }
      return { ...p, versions, current_version: cv }
    })
    if (project.current_page) {
      currentPage.value = project.current_page
      const page = pages.value.find(p => p.name === project.current_page)
      if (page && page.generated) {
        const targetVersion = page.current_version
        const ver: PageVersion | undefined = targetVersion
          ? (page.versions || []).find((v: PageVersion) => v.label === targetVersion)
          : undefined
        if (ver) {
          generatedCode.html = ver.html
          generatedCode.css = ver.css
          generatedCode.js = ver.js
        } else {
          generatedCode.html = page.html
          generatedCode.css = page.css
          generatedCode.js = page.js
        }
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
