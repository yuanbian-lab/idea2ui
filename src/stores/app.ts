import { reactive } from 'vue'
import type { Message, ModelConfig } from '../types'

export type Phase = 'idle' | 'prd_design' | 'prd_confirm' | 'page_generation'

export interface PageInfo {
  name: string
  generated: boolean
  html: string
  css: string
  js: string
}

export const messages = reactive<Message[]>([])

export const modelConfig = reactive<ModelConfig>({
  provider: 'openai',
  model: 'gpt-4o',
  apiKey: '',
  baseUrl: 'https://api.openai.com/v1',
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

export function reset() {
  messages.splice(0)
  generatedCode.html = ''
  generatedCode.css = ''
  generatedCode.js = ''
  prdContent.value = ''
  pages.value = []
  currentPage.value = null
  phase.value = 'idle'
}

export function getPage(name: string): PageInfo | undefined {
  return pages.value.find(p => p.name === name)
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
