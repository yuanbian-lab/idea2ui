<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import {
  ReloadOutlined,
  ExportOutlined,
  FullscreenOutlined,
  EditOutlined,
  CloseOutlined,
  SaveOutlined,
  HistoryOutlined,
} from '@ant-design/icons-vue'
import {
  generatedCode,
  phase,
  prdContent,
  thinking,
  deviceMode,
  getDevicePresets,
  setDevice,
  editMode,
  selectedElement,
  elementModifications,
  currentProjectId,
  currentPage,
  pages,
  addMessage,
} from '../stores/app'
import type { PageVersion } from '../stores/app'
import { marked } from 'marked'
import { exportFiles, updateProject } from '../services/api'
import { getEditorScript } from '../utils/editorInjector'

const iframeRef = ref<HTMLIFrameElement>()
const exporting = ref(false)
const customWidth = ref(deviceMode.width)
const customHeight = ref(deviceMode.height)
const showCustom = ref(false)
const saving = ref(false)
const dirtyCount = ref(0)

// Save dialog
const showSaveDialog = ref(false)
const saveVersionLabel = ref('')

// Version selector
const currentVersions = computed(() => {
  const page = pages.value.find(p => p.name === currentPage.value)
  return (page?.versions || []) as PageVersion[]
})
const currentVersionLabel = computed(() => {
  const page = pages.value.find(p => p.name === currentPage.value)
  return page?.current_version || ''
})

function getNextVersionLabel(): string {
  const count = currentVersions.value.length
  return `v${count + 1}`
}

const presets = computed(() => getDevicePresets())

const previewSrcDoc = computed(() => {
  if (!generatedCode.html && !generatedCode.css && !generatedCode.js) return ''
  const editorScript = editMode.value ? getEditorScript() : ''
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
  ${editorScript}
</body>
</html>`
})

const prdHtml = computed(() => {
  if (!prdContent.value) return ''
  return marked(prdContent.value)
})

const showEditorPanel = computed(() =>
  editMode.value && phase.value === 'page_generation' && selectedElement.value
)

const sel = computed(() => selectedElement.value)

// Edit mode property bindings
const editBackground = ref('')
const editBorderRadius = ref('')
const editColor = ref('')
const editFontSize = ref('')
const editTextContent = ref('')

function syncPropsFromSelection() {
  const s = sel.value
  if (!s) return
  editBackground.value = s.styles?.backgroundColor || s.styles?.background || ''
  editBorderRadius.value = s.styles?.borderRadius || ''
  editColor.value = s.styles?.color || ''
  editFontSize.value = s.styles?.fontSize || ''
  editTextContent.value = s.text || ''
}

// Message handling from iframe editor
function handleMessage(e: MessageEvent) {
  const msg = e.data
  if (!msg.type || !msg.type.startsWith('editor:')) return
  const d = msg.data || msg

  switch (msg.type) {
    case 'editor:ready':
      if (Object.keys(elementModifications).length > 0) {
        try {
          iframeRef.value?.contentWindow?.postMessage({
            type: 'editor:applyAll',
            modifications: { ...elementModifications },
          }, '*')
        } catch {}
      }
      break
    case 'editor:select':
      selectedElement.value = d
      nextTick(syncPropsFromSelection)
      break
    case 'editor:drag':
      if (sel.value?.eid === d.eid) {
        const cur = { ...sel.value, x: d.x, y: d.y }
        selectedElement.value = cur
      }
      if (d.eid) {
        if (!elementModifications[d.eid]) elementModifications[d.eid] = {}
        elementModifications[d.eid].transform = d.transform
      }
      break
    case 'editor:html':
      handleSaveHtml(d.html)
      break
  }
}

function applyAllProperties() {
  const s = sel.value
  if (!s?.eid) return
  const eid = s.eid
  const props: Record<string, string> = {}

  if (editBackground.value !== (s.styles?.backgroundColor || s.styles?.background || '')) {
    props.backgroundColor = editBackground.value
  }
  if (editBorderRadius.value !== (s.styles?.borderRadius || '')) {
    props.borderRadius = editBorderRadius.value
  }
  if (editColor.value !== (s.styles?.color || '')) {
    props.color = editColor.value
  }
  if (editFontSize.value !== (s.styles?.fontSize || '')) {
    props.fontSize = editFontSize.value
  }
  if (editTextContent.value !== (s.text || '')) {
    props.textContent = editTextContent.value
  }

  if (Object.keys(props).length === 0) return
  try {
    iframeRef.value?.contentWindow?.postMessage({ type: 'editor:apply', eid, properties: props }, '*')
  } catch {}
  if (!elementModifications[eid]) elementModifications[eid] = {}
  Object.assign(elementModifications[eid], props)
  dirtyCount.value++
}

function handlePropertyBlur() {
  applyAllProperties()
}

let saveTimeout: ReturnType<typeof setTimeout> | null = null

function handleSave() {
  if (saving.value || !iframeRef.value?.contentWindow) return
  showSaveDialog.value = true
  saveVersionLabel.value = getNextVersionLabel()
}

function handleSaveDialogOk() {
  if (!saveVersionLabel.value.trim()) return
  showSaveDialog.value = false
  saving.value = true
  iframeRef.value?.contentWindow?.postMessage({ type: 'editor:getHtml' }, '*')
  saveTimeout = setTimeout(() => {
    if (saving.value) {
      saving.value = false
      if (editMode.value) {
        addMessage('assistant', '保存超时，请确认页面已加载编辑模式后重试。')
      }
    }
  }, 5000)
}

async function handleSaveHtml(bodyHtml: string) {
  if (saveTimeout) { clearTimeout(saveTimeout); saveTimeout = null }
  try {
    const label = saveVersionLabel.value.trim() || getNextVersionLabel()
    const cleanHtml = bodyHtml.replace(/<script[\s\S]*?<\/script>/gi, '').trim()
    const page = pages.value.find(p => p.name === currentPage.value)
    if (!page || !currentProjectId.value) {
      addMessage('assistant', '保存失败: 未找到当前页面或项目。')
      return
    }
    generatedCode.html = cleanHtml
    generatedCode.css = page.css
    generatedCode.js = page.js
    const now = Date.now()
    if (!page.versions) page.versions = []
    page.versions.push({ label, timestamp: now, html: cleanHtml, css: page.css, js: page.js })
    page.current_version = label
    page.html = cleanHtml
    page.css = page.css
    page.js = page.js
    page.generated = true
    await updateProject(currentProjectId.value, { pages: pages.value.map(p => ({ ...p })) })
    Object.keys(elementModifications).forEach(k => delete elementModifications[k])
    dirtyCount.value = 0
    editMode.value = false
    selectedElement.value = null
    saveVersionLabel.value = ''
    addMessage('assistant', `✅ 已保存版本「${label}」`)
  } catch (e: any) {
    console.error('保存失败:', e.message)
    addMessage('assistant', `保存失败: ${e.message}`)
  } finally {
    saving.value = false
  }
}

function handleVersionSelect(label: string) {
  const page = pages.value.find(p => p.name === currentPage.value)
  if (!page) return
  const ver = (page.versions || []).find((v: PageVersion) => v.label === label)
  if (!ver) return
  generatedCode.html = ver.html
  generatedCode.css = ver.css
  generatedCode.js = ver.js
  page.current_version = label
  if (currentProjectId.value) {
    updateProject(currentProjectId.value, { pages: pages.value.map(p => ({ ...p })) }).catch(() => {})
  }
  addMessage('assistant', `已切换到版本「${label}」`)
}

function handleCancelEdit() {
  editMode.value = false
  selectedElement.value = null
  Object.keys(elementModifications).forEach(k => delete elementModifications[k])
  dirtyCount.value = 0
}

function toggleEditMode() {
  editMode.value = !editMode.value
  if (!editMode.value) {
    selectedElement.value = null
  }
}

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

onMounted(() => window.addEventListener('message', handleMessage))
onUnmounted(() => window.removeEventListener('message', handleMessage))
</script>

<template>
  <div class="preview-panel">
    <div class="preview-toolbar">
      <span class="preview-title">
        {{ showPrd ? 'PRD 文档预览' : editMode.value ? '✏️ 编辑模式' : '预览' }}
      </span>
      <div class="toolbar-actions" v-if="!showPrd">
        <!-- Device toolbar -->
        <div class="device-bar" v-if="phase.value === 'page_generation' && !editMode.value">
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

        <!-- Edit mode toggle -->
        <!-- Version selector -->
        <template v-if="phase.value === 'page_generation' && !editMode.value && currentVersions.length > 0">
          <span class="version-badge">
            <HistoryOutlined /> {{ currentVersionLabel }}
          </span>
          <a-select
            v-model:value="currentVersionLabel"
            size="small"
            style="width: 130px"
            :options="currentVersions.map(v => ({ label: v.label, value: v.label }))"
            @change="handleVersionSelect"
          />
        </template>

        <template v-if="phase.value === 'page_generation'">
          <a-button
            v-if="!editMode.value"
            size="small"
            :type="editMode.value ? 'primary' : 'default'"
            @click="toggleEditMode"
          >
            <template #icon><EditOutlined /></template>
            编辑
          </a-button>
          <template v-else>
            <a-button size="small" @click="handleCancelEdit">
              <template #icon><CloseOutlined /></template>
              取消
            </a-button>
            <a-button size="small" type="primary" :loading="saving" @click="handleSave">
              <template #icon><SaveOutlined /></template>
              保存为新版本
            </a-button>
          </template>
        </template>

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
      <div v-else-if="previewSrcDoc" class="preview-and-props">
        <div
          class="device-frame"
          :style="{ width: deviceMode.width + 'px', height: deviceMode.height + 'px' }"
          :class="{ 'device-frame-editing': editMode.value }"
        >
          <div class="device-notch" v-if="deviceMode.width < 500">
            <span class="notch-status-bar">{{ deviceMode.label }}</span>
          </div>
          <iframe
            ref="iframeRef"
            :srcdoc="previewSrcDoc"
            class="preview-iframe"
            sandbox="allow-scripts allow-same-origin"
          />
        </div>

        <!-- Properties Panel (floating right) -->
        <div v-if="showEditorPanel" class="props-panel">
          <div class="props-header">
            <span>✏️ 元素属性</span>
            <a-button type="text" size="small" @click="selectedElement.value = null">
              <template #icon><CloseOutlined /></template>
            </a-button>
          </div>
          <div class="props-body">
            <div class="prop-info">
              <span class="prop-tag">{{ sel?.tag || '' }}</span>
              <span class="prop-text" :title="sel?.text">{{ sel?.text || '' }}</span>
            </div>

            <div class="prop-row">
              <label>背景色</label>
              <div class="prop-input-row">
                <span class="color-swatch" :style="{ background: editBackground || 'transparent' }"></span>
                <a-input
                  v-model:value="editBackground"
                  size="small"
                  placeholder="透明"
                  @blur="handlePropertyBlur"
                  @pressEnter="handlePropertyBlur"
                />
              </div>
            </div>

            <div class="prop-row">
              <label>圆角</label>
              <a-input
                v-model:value="editBorderRadius"
                size="small"
                placeholder="0px"
                @blur="handlePropertyBlur"
                @pressEnter="handlePropertyBlur"
              >
                <template #suffix>px</template>
              </a-input>
            </div>

            <div class="prop-row">
              <label>文字色</label>
              <div class="prop-input-row">
                <span class="color-swatch" :style="{ background: editColor || 'inherit' }"></span>
                <a-input
                  v-model:value="editColor"
                  size="small"
                  placeholder="继承"
                  @blur="handlePropertyBlur"
                  @pressEnter="handlePropertyBlur"
                />
              </div>
            </div>

            <div class="prop-row">
              <label>字号</label>
              <a-input
                v-model:value="editFontSize"
                size="small"
                placeholder="继承"
                @blur="handlePropertyBlur"
                @pressEnter="handlePropertyBlur"
              >
                <template #suffix>px</template>
              </a-input>
            </div>

            <div class="prop-row">
              <label>文字</label>
              <a-input
                v-model:value="editTextContent"
                size="small"
                placeholder="元素文本"
                @blur="handlePropertyBlur"
                @pressEnter="handlePropertyBlur"
              />
            </div>

            <div class="prop-pos" v-if="sel?.x !== undefined || sel?.transform">
              <span>拖拽偏移</span>
              <span class="pos-value">X: {{ Math.round(sel?.x || 0) }}px, Y: {{ Math.round(sel?.y || 0) }}px</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="!thinking.value" class="preview-empty">
        <div class="empty-icon">🎨</div>
        <p>在左侧描述你的需求，AI 生成的界面将显示在这里</p>
      </div>
    </div>

    <!-- Save version dialog -->
    <a-modal
      v-model:open="showSaveDialog"
      title="保存为新版本"
      @ok="handleSaveDialogOk"
      :ok-button-props="{ disabled: !saveVersionLabel.trim() }"
    >
      <a-input
        v-model:value="saveVersionLabel"
        placeholder="输入版本名称，如 v2、优化后"
        @pressEnter="handleSaveDialogOk"
      />
      <div class="save-dialog-hint">保存后将退出编辑模式，可在版本选择器中切换查看历史版本。</div>
    </a-modal>
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

.preview-and-props {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  justify-content: center;
  width: 100%;
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

.device-frame-editing {
  box-shadow: 0 4px 24px rgba(22,119,255,0.2);
  outline: 2px solid #1677ff;
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

/* Properties panel */
.props-panel {
  width: 240px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.12);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  font-size: 13px;
}

.props-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0;
  font-weight: 600;
  font-size: 13px;
}

.props-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.prop-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 4px;
}

.prop-tag {
  background: #1677ff;
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.prop-text {
  color: #666;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.prop-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.prop-row label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.prop-input-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.color-swatch {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #d9d9d9;
  flex-shrink: 0;
}

.prop-pos {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
  color: #999;
}

.pos-value {
  font-family: monospace;
  font-size: 12px;
  color: #666;
}

.version-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
  padding: 0 4px;
}

.save-dialog-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}
</style>
