import { reactive } from 'vue'
import type { Message, ModelConfig } from '../types'

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

export function addMessage(role: 'user' | 'assistant', content: string) {
  messages.push({
    id: Date.now().toString(),
    role,
    content,
    timestamp: Date.now(),
  })
}
