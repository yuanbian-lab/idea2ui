<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { SettingOutlined, SendOutlined } from '@ant-design/icons-vue'
import {
  messages,
  addMessage,
  modelConfig,
  generatedCode,
  phase,
  prdContent,
  pages,
  currentPage,
  confirmPrd,
  setPageGenerated,
  resetCurrentProject,
  thinking,
  currentProjectId,
  currentPlatform,
} from '../stores/app'
import { chat, createProject } from '../services/api'
import SettingsDialog from './SettingsDialog.vue'

const input = ref('')
const listRef = ref<HTMLDivElement>()
const showSettings = ref(false)
const sending = ref(false)

// Platform selection state
const platform = ref(currentPlatform.value || 'web')
const projectName = ref('')
const showNameInput = ref(false)

const platforms = [
  { label: 'Web 端', value: 'web', icon: '🖥️' },
  { label: '移动网页端', value: 'mobile_web', icon: '📱' },
  { label: 'App 端', value: 'app', icon: '📲' },
  { label: '小程序端', value: 'mini_program', icon: '💬' },
]

function scrollToBottom() {
  nextTick(() => {
    if (listRef.value) {
      listRef.value.scrollTop = listRef.value.scrollHeight
    }
  })
}

async function handlePlatformSelect(value: string) {
  platform.value = value
  showNameInput.value = true
}

async function handleStartProject() {
  if (!projectName.value.trim()) return
  const proj = await createProject(projectName.value.trim(), platform.value)
  resetCurrentProject()
  currentProjectId.value = proj.id
  // Update platform in store as well
  Object.assign(currentPlatform, { value: platform.value })
  phase.value = 'prd_design'
  addMessage('assistant', `项目「${projectName.value}」已创建！请描述你的产品想法，我来帮你设计 PRD 文档。`)
  showNameInput.value = false
  projectName.value = ''
}

async function handleSend() {
  const text = input.value.trim()
  if (!text || sending.value) return

  if (!modelConfig.apiKey) {
    showSettings.value = true
    return
  }

  addMessage('user', text)
  input.value = ''
  scrollToBottom()
  sending.value = true
  thinking.value = true

  try {
    const mode = phase.value === 'page_generation' ? 'page' : 'prd'
    const modified =
      mode === 'page' && [generatedCode.html, generatedCode.css, generatedCode.js].some(Boolean)
        ? `html:${generatedCode.html}\ncss:${generatedCode.css}\njs:${generatedCode.js}`
        : ''

    const result = await chat(
      [...messages],
      { ...modelConfig },
      modified,
      mode,
      currentProjectId.value,
      currentPage.value || '',
    )

    if (result.type === 'prd') {
      if (result.prd) {
        prdContent.value = result.prd
        if (result.pages.length > 0) {
          pages.value = result.pages.map(name => ({
            name,
            generated: false,
            html: '',
            css: '',
            js: '',
          }))
        }
        phase.value = 'prd_confirm'
        addMessage('assistant', result.reply)
      } else {
        addMessage('assistant', result.reply)
      }
    } else {
      if (result.html) {
        generatedCode.html = result.html
        generatedCode.css = result.css
        generatedCode.js = result.js
        if (currentPage.value) {
          setPageGenerated(currentPage.value, result.html, result.css, result.js)
        }
        if (phase.value === 'idle' || phase.value === 'platform_select') {
          phase.value = 'page_generation'
        }
        addMessage('assistant', result.reply)
      } else {
        addMessage('assistant', `AI 未返回代码: ${result.reply}\n请检查 Settings 中的模型配置，确保选择了支持结构化输出的模型（如 deepseek-chat、gpt-4o），或更换服务商重试。`)
      }
    }
  } catch (e: any) {
    addMessage('assistant', `请求失败: ${e.message}`)
  } finally {
    sending.value = false
    thinking.value = false
    scrollToBottom()
  }
}

function handleConfirmPrd() {
  confirmPrd()
  addMessage('assistant', 'PRD 已确认！请在页面导航中选择一个页面开始生成。')
}

function handleStart() {
  phase.value = 'platform_select'
}
</script>

<template>
  <div class="chat-panel">
    <div class="chat-header">
      <slot name="header-left" />
      <div class="header-right">
        <a-button size="small" @click="handleStart">新建</a-button>
        <a-button type="text" @click="showSettings = true">
          <template #icon><SettingOutlined /></template>
        </a-button>
      </div>
    </div>

    <div class="message-list" ref="listRef">
      <div v-for="msg in messages" :key="msg.id" class="message-wrapper" :class="msg.role">
        <div class="avatar">{{ msg.role === 'user' ? 'U' : 'AI' }}</div>
        <div class="bubble">{{ msg.content }}</div>
      </div>

      <div v-if="thinking.value" class="message-wrapper assistant">
        <div class="avatar">AI</div>
        <div class="bubble thinking-bubble">
          <span class="thinking-dot"></span>
          <span class="thinking-dot"></span>
          <span class="thinking-dot"></span>
        </div>
      </div>

      <div v-if="phase.value === 'platform_select'" class="platform-select">
        <p class="select-title">请选择目标平台</p>
        <div class="platform-grid">
          <div
            v-for="p in platforms"
            :key="p.value"
            class="platform-card"
            @click="handlePlatformSelect(p.value)"
          >
            <span class="platform-icon">{{ p.icon }}</span>
            <span>{{ p.label }}</span>
          </div>
        </div>
      </div>

      <div v-if="showNameInput" class="name-input-area">
        <a-input v-model:value="projectName" placeholder="输入项目名称" @pressEnter="handleStartProject" />
        <a-button type="primary" :disabled="!projectName.trim()" @click="handleStartProject">确定</a-button>
      </div>

      <div v-else-if="messages.length === 0 && phase.value !== 'platform_select'" class="empty-state">
        <div class="empty-icon">💡</div>
        <p class="empty-title">描述你的想法</p>
        <p class="empty-desc">用自然语言描述你想要的产品，AI 将先为你设计 PRD，再逐页生成 UI</p>
        <a-button type="primary" @click="handleStart">开始设计</a-button>
      </div>
    </div>

    <div v-if="phase.value === 'prd_confirm' && prdContent.value" class="prd-actions">
      <a-button type="primary" @click="handleConfirmPrd">确认 PRD，开始生成页面</a-button>
      <a-button @click="() => { phase.value = 'prd_design'; addMessage('assistant', '请告诉我需要修改的地方。') }">继续修改</a-button>
    </div>

    <div class="chat-input">
      <a-textarea
        v-model:value="input"
        :placeholder="phase.value === 'page_generation' && currentPage.value
          ? `请输入「${currentPage.value}」页面的具体要求...`
          : phase.value === 'platform_select' ? '请先选择平台...'
          : '描述你的想法...'"
        :rows="3"
        :disabled="sending || phase.value === 'platform_select'"
        @pressEnter="handleSend"
      />
      <a-button type="primary" :disabled="!input.trim() || sending || phase.value === 'platform_select'" :loading="sending" @click="handleSend">
        <template #icon><SendOutlined /></template>
        发送
      </a-button>
    </div>

    <SettingsDialog v-model:visible="showSettings" />
  </div>
</template>

<style scoped>
.chat-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  gap: 8px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-wrapper {
  display: flex;
  gap: 8px;
  max-width: 100%;
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.message-wrapper.user .avatar {
  background: #1677ff;
  color: #fff;
}

.message-wrapper.assistant .avatar {
  background: #722ed1;
  color: #fff;
}

.bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-wrapper.user .bubble {
  background: #1677ff;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message-wrapper.assistant .bubble {
  background: #f5f5f5;
  color: #333;
  border-bottom-left-radius: 4px;
}

.thinking-bubble {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 12px 16px;
}

.thinking-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: pulse 1.4s ease-in-out infinite;
}

.thinking-dot:nth-child(2) { animation-delay: 0.2s; }
.thinking-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: #666;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 13px;
  color: #999;
  max-width: 280px;
  margin-bottom: 16px;
}

.platform-select {
  padding: 20px 0;
}

.select-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  text-align: center;
}

.platform-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.platform-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  color: #333;
}

.platform-card:hover {
  border-color: #1677ff;
  background: #f0f5ff;
}

.platform-icon {
  font-size: 28px;
}

.name-input-area {
  display: flex;
  gap: 8px;
  padding: 12px 0;
}

.prd-actions {
  padding: 8px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 8px;
}

.chat-input {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 8px;
  align-items: flex-end;
}
</style>
