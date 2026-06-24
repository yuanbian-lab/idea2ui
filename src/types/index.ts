export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

export interface ModelConfig {
  provider: string
  model: string
  apiKey: string
  baseUrl: string
}

export interface ProjectFile {
  path: string
  content: string
}
