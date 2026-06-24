<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  ReloadOutlined,
  ExportOutlined,
  FullscreenOutlined,
} from '@ant-design/icons-vue'
import { generatedCode } from '../stores/app'
import { exportFiles } from '../services/api'

const iframeRef = ref<HTMLIFrameElement>()
const exporting = ref(false)

const previewSrcDoc = computed(() => {
  if (!generatedCode.html && !generatedCode.css && !generatedCode.js) return ''
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>${generatedCode.css}</style>
</head>
<body>
  ${generatedCode.html}
  <script>${generatedCode.js}<\/script>
</body>
</html>`
})

function handleRefresh() {
  if (iframeRef.value) {
    iframeRef.value.srcdoc = previewSrcDoc.value
  }
}

async function handleExport() {
  if (exporting.value) return
  exporting.value = true
  try {
    const result = await exportFiles(
      generatedCode.html,
      generatedCode.css,
      generatedCode.js,
    )
    console.log('导出成功:', result)
  } catch (e: any) {
    console.error('导出失败:', e.message)
  } finally {
    exporting.value = false
  }
}

function handleFullscreen() {
  if (iframeRef.value) {
    iframeRef.value.requestFullscreen?.()
  }
}
</script>

<template>
  <div class="preview-panel">
    <div class="preview-toolbar">
      <span class="preview-title">预览</span>
      <div class="toolbar-actions">
        <a-tooltip title="刷新预览">
          <a-button type="text" @click="handleRefresh">
            <template #icon><ReloadOutlined /></template>
          </a-button>
        </a-tooltip>
        <a-tooltip title="导出">
          <a-button type="text" :loading="exporting" @click="handleExport">
            <template #icon><ExportOutlined /></template>
          </a-button>
        </a-tooltip>
        <a-tooltip title="全屏">
          <a-button type="text" @click="handleFullscreen">
            <template #icon><FullscreenOutlined /></template>
          </a-button>
        </a-tooltip>
      </div>
    </div>
    <div class="preview-content">
      <iframe
        v-if="previewSrcDoc"
        ref="iframeRef"
        :srcdoc="previewSrcDoc"
        class="preview-iframe"
        sandbox="allow-scripts"
      />
      <div v-else class="preview-empty">
        <div class="empty-icon">🎨</div>
        <p>在左侧描述你的需求，AI 生成的界面将显示在这里</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #fff;
}

.preview-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.toolbar-actions {
  display: flex;
  gap: 4px;
}

.preview-content {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #fff;
}

.preview-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 14px;
  text-align: center;
  padding: 40px;
}

.preview-empty .empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}
</style>
