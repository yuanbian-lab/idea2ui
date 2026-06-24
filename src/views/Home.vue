<script setup lang="ts">
import { onMounted } from 'vue'
import ChatPanel from '../components/ChatPanel.vue'
import PreviewPanel from '../components/PreviewPanel.vue'
import { loadConfig } from '../services/api'

onMounted(() => {
  loadConfig()
})
</script>

<template>
  <div class="home">
    <ChatPanel class="chat-panel" />
    <PreviewPanel class="preview-panel" />
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

.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}
</style>
