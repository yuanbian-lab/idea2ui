<script setup lang="ts">
import { onMounted } from 'vue'
import ChatPanel from '../components/ChatPanel.vue'
import PreviewPanel from '../components/PreviewPanel.vue'
import PageNav from '../components/PageNav.vue'
import { loadConfig } from '../services/api'
import { generatedCode, pages, currentPage, addMessage } from '../stores/app'

onMounted(() => {
  loadConfig()
})

async function handlePageSelect(name: string) {
  const page = pages.value.find(p => p.name === name)
  if (!page) return
  if (page.generated) {
    generatedCode.html = page.html
    generatedCode.css = page.css
    generatedCode.js = page.js
  } else {
    addMessage('assistant', `「${name}」页面尚未生成，请在输入框中描述该页面的具体需求。`)
  }
}
</script>

<template>
  <div class="home">
    <ChatPanel class="chat-panel" />
    <div class="right-area">
      <PreviewPanel class="preview-panel" />
      <PageNav @select="handlePageSelect" />
    </div>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.chat-panel {
  width: 420px;
  min-width: 360px;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
}

.right-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fafafa;
  min-height: 0;
}
</style>
