<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { SettingOutlined, SendOutlined, LoadingOutlined } from '@ant-design/icons-vue'
import { messages, addMessage, modelConfig } from '../stores/app'
import { generatedCode } from '../stores/app'
import { chat } from '../services/api'
import SettingsDialog from './SettingsDialog.vue'

const input = ref('')
const listRef = ref<HTMLDivElement>()
const showSettings = ref(false)
const sending = ref(false)

function scrollToBottom() {
  nextTick(() => {
    if (listRef.value) {
      listRef.value.scrollTop = listRef.value.scrollHeight
    }
  })
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

  try {
    const result = await chat(
      [...messages],
      { ...modelConfig },
      [generatedCode.html, generatedCode.css, generatedCode.js].some(Boolean)
        ? `html:${generatedCode.html}\ncss:${generatedCode.css}\njs:${generatedCode.js}`
        : '',
    )
    generatedCode.html = result.html
    generatedCode.css = result.css
    generatedCode.js = result.js
    addMessage('assistant', result.reply)
  } catch (e: any) {
    addMessage('assistant', `请求失败: ${e.message}`)
  } finally {
    sending.value = false
    scrollToBottom()
  }
}
</script>

<template>
  <div class="chat-panel">
    <div class="chat-header">
      <span class="logo">idea2ui</span>
      <a-button type="text" @click="showSettings = true">
        <template #icon><SettingOutlined /></template>
      </a-button>
    </div>

    <div class="message-list" ref="listRef">
      <div v-for="msg in messages" :key="msg.id" class="message-wrapper" :class="msg.role">
        <div class="avatar">{{ msg.role === 'user' ? 'U' : 'AI' }}</div>
        <div class="bubble">{{ msg.content }}</div>
      </div>
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">💡</div>
        <p class="empty-title">描述你的想法</p>
        <p class="empty-desc">用自然语言描述你想要的界面，AI 将为你生成原型</p>
      </div>
    </div>

    <div class="chat-input">
      <a-textarea
        v-model:value="input"
        placeholder="描述你想要的界面..."
        :rows="3"
        :disabled="sending"
        @pressEnter="handleSend"
      />
      <a-button type="primary" :disabled="!input.trim() || sending" :loading="sending" @click="handleSend">
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
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.logo {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
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
}

.chat-input {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 8px;
  align-items: flex-end;
}
</style>
