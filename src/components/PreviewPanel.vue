<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  ReloadOutlined,
  ExportOutlined,
  FullscreenOutlined,
} from '@ant-design/icons-vue'
import {
  generatedCode,
  phase,
  prdContent,
  thinking,
  deviceMode,
  getDevicePresets,
  setDevice,
} from '../stores/app'
import { marked } from 'marked'
import { exportFiles } from '../services/api'

const iframeRef = ref<HTMLIFrameElement>()
const exporting = ref(false)
const customWidth = ref(deviceMode.width)
const customHeight = ref(deviceMode.height)
const showCustom = ref(false)

const presets = computed(() => getDevicePresets())

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

const prdHtml = computed(() => {
  if (!prdContent.value) return ''
  return marked(prdContent.value)
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

function handlePresetClick(w: number, h: number, label: string) {
  setDevice(w, h, label)
  customWidth.value = w
  customHeight.value = h
}

function handleCustomSize() {
  setDevice(customWidth.value, customHeight.value, `${customWidth.value}×${customHeight.value}`)
  showCustom.value = false
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
        <!-- Device toolbar -->
        <div class="device-bar" v-if="phase === 'page_generation'">
          <a-button
            v-for="p in presets"
            :key="p.width"
            :type="deviceMode.width === p.width && deviceMode.height === p.height ? 'primary' : 'default'"
            size="small"
            @click="handlePresetClick(p.width, p.height, `${p.width}×${p.height}`)"
          >
            {{ p.width }}×{{ p.height }}
          </a-button>
          <a-button size="small" @click="showCustom = !showCustom">
            {{ deviceMode.label }}
          </a-button>
        </div>
        <div v-if="showCustom" class="custom-size">
          <a-input-number v-model:value="customWidth" :min="320" :max="2560" size="small" style="width:80px" />
          <span>×</span>
          <a-input-number v-model:value="customHeight" :min="240" :max="1600" size="small" style="width:80px" />
          <a-button size="small" type="primary" @click="handleCustomSize">应用</a-button>
        </div>
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
      <div v-if="thinking.value" class="loading-overlay">
        <a-spin size="large" />
        <p>AI 正在生成中...</p>
      </div>
      <div v-if="showPrd" class="prd-viewer">
        <div class="prd-render" v-html="prdHtml"></div>
      </div>
      <div v-else-if="previewSrcDoc" class="device-frame" :style="{ width: deviceMode.width + 'px', height: deviceMode.height + 'px' }">
        <div class="device-notch" v-if="deviceMode.width < 500">
          <span class="notch-status-bar">{{ deviceMode.label }}</span>
        </div>
        <iframe
          ref="iframeRef"
          :srcdoc="previewSrcDoc"
          class="preview-iframe"
          sandbox="allow-scripts"
        />
      </div>
      <div v-else-if="!thinking.value" class="preview-empty">
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
  flex-wrap: wrap;
  gap: 8px;
}

.preview-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.device-bar {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 0 8px;
  border-right: 1px solid #f0f0f0;
  margin-right: 8px;
}

.custom-size {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
}

.preview-content {
  flex: 1;
  position: relative;
  overflow: auto;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 24px;
  background: #f0f0f0;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #fff;
}

.device-frame {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.12);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: width 0.3s, height 0.3s;
  flex-shrink: 0;
}

.device-notch {
  padding: 6px 16px;
  background: #333;
  color: #fff;
  font-size: 11px;
  text-align: center;
}

.notch-status-bar {
  opacity: 0.7;
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

.prd-render h1 { font-size: 24px; margin-bottom: 16px; border-bottom: 1px solid #eee; padding-bottom: 8px; }
.prd-render h2 { font-size: 20px; margin: 24px 0 12px; }
.prd-render h3 { font-size: 16px; margin: 16px 0 8px; }
.prd-render p { margin: 8px 0; }
.prd-render ul, .prd-render ol { padding-left: 20px; margin: 8px 0; }
.prd-render li { margin: 4px 0; }
.prd-render code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; font-size: 13px; color: #d63384; }
.prd-render pre { background: #f5f5f5; padding: 16px; border-radius: 8px; overflow-x: auto; }
.prd-render pre code { background: none; padding: 0; color: inherit; }
.prd-render table { border-collapse: collapse; width: 100%; margin: 12px 0; }
.prd-render th, .prd-render td { border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left; }
.prd-render th { background: #fafafa; font-weight: 600; }

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.85);
  z-index: 10;
  gap: 16px;
  color: #666;
  font-size: 14px;
}
</style>
