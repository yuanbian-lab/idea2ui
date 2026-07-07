<script setup lang="ts">
import { ref } from 'vue'
import { PlusOutlined, SwapOutlined } from '@ant-design/icons-vue'
import { projects, currentProjectId, resetCurrentProject } from '../stores/app'
import { listProjects, createProject, getProject } from '../services/api'
import { loadProjectState } from '../stores/app'

const emit = defineEmits<{
  select: []
}>()

const showCreate = ref(false)
const createName = ref('')
const createPlatform = ref('web')

const visible = ref(false)

const platforms = [
  { label: 'Web 端', value: 'web' },
  { label: '移动网页端', value: 'mobile_web' },
  { label: 'App 端', value: 'app' },
  { label: '小程序端', value: 'mini_program' },
]

async function refreshProjects() {
  const list = await listProjects()
  projects.value = list
}

async function handleCreate() {
  if (!createName.value.trim()) return
  const proj = await createProject(createName.value.trim(), createPlatform.value)
  await switchProject(proj.id)
  showCreate.value = false
  createName.value = ''
  visible.value = false
}

async function handleSelect(projectId: string) {
  if (projectId === 'new') {
    openCreate()
    return
  }
  await switchProject(projectId)
  visible.value = false
}

async function switchProject(projectId: string) {
  try {
    const project = await getProject(projectId)
    if (!project) return
    resetCurrentProject()
    currentProjectId.value = project.id
    loadProjectState(project)
  } catch (e: any) {
    console.error('切换项目失败:', e.message)
    return
  }
  await refreshProjects()
  emit('select')
}

function openCreate() {
  showCreate.value = true
  createName.value = ''
  createPlatform.value = 'web'
}

function closeCreate() {
  showCreate.value = false
}
</script>

<template>
  <a-dropdown v-if="currentProjectId.value || projects.value.length > 0" placement="bottomLeft" trigger="click">
    <a-button type="text" class="project-selector">
      <span class="project-name">
        {{ projects.value.find(p => p.id === currentProjectId.value)?.name || '选择项目' }}
      </span>
      <SwapOutlined />
    </a-button>
    <template #overlay>
      <a-menu @click="(e: any) => handleSelect(e.key)">
        <a-menu-item v-for="p in projects.value" :key="p.id" :class="{ active: p.id === currentProjectId.value }">
          {{ p.name }}
          <span class="platform-tag">{{ { web: 'Web', mobile_web: '移动', app: 'App', mini_program: '小程序' }[p.platform] || p.platform }}</span>
        </a-menu-item>
        <a-menu-divider />
        <a-menu-item key="new" @click="openCreate">
          <PlusOutlined /> 新建项目
        </a-menu-item>
      </a-menu>
    </template>
  </a-dropdown>

  <a-modal v-model:visible="showCreate" title="新建项目" width="420" :footer="null" @cancel="closeCreate">
    <a-form layout="vertical">
      <a-form-item label="项目名称">
        <a-input v-model:value="createName" placeholder="输入项目名称" />
      </a-form-item>
      <a-form-item label="目标平台">
        <a-radio-group v-model:value="createPlatform" :options="platforms.map(p => ({ label: p.label, value: p.value }))" />
      </a-form-item>
      <a-button type="primary" :disabled="!createName.trim()" @click="handleCreate">创建并进入</a-button>
    </a-form>
  </a-modal>
</template>

<style scoped>
.project-selector {
  display: flex;
  align-items: center;
  gap: 6px;
  max-width: 180px;
  overflow: hidden;
}

.project-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.platform-tag {
  margin-left: 8px;
  font-size: 11px;
  color: #999;
  background: #f5f5f5;
  padding: 0 6px;
  border-radius: 3px;
}
</style>
