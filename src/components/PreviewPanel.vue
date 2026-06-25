<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  ReloadOutlined,
  ExportOutlined,
  FullscreenOutlined,
} from '@ant-design/icons-vue'
import { generatedCode, phase, prdContent } from '../stores/app'
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

const showPrd = computed(() => phase.value === 'prd_confirm' && prdContent.value)
</script>

<template>
  <div class="preview-panel">
    <div class="preview-toolbar">
      <span class="preview-title">
        {{ showPrd ? 'PRD 文档预览' : '预览' }}
      </span>
      <div class="toolbar-actions" v-if="!showPrd">
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
      <div v-if="showPrd" class="prd-viewer">
        <div class="prd-render" v-html="prdContent"></div>
      </div>
      <iframe
        v-else-if="previewSrcDoc"
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

.prd-viewer {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  background: #fff;
  padding: 32px 40px;
}

.prd-render {
  font-size: 14px;
  line-height: 1.8;
  color: #333;
}

.prd-render h1 { font-size: 24px; margin-bottom: 16px; }
.prd-render h2 { font-size: 20px; margin: 24px 0 12px; }
.prd-render h3 { font-size: 16px; margin: 16px 0 8px; }
.prd-render p { margin: 8px 0; }
.prd-render ul, .prd-render ol { padding-left: 20px; margin: 8px 0; }
.prd-render li { margin: 4px 0; }
.prd-render code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
.prd-render pre { background: #f5f5f5; padding: 16px; border-radius: 8px; overflow-x: auto; }
</style>
