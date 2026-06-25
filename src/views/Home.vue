<script setup lang="ts">
import { onMounted } from 'vue'
import ChatPanel from '../components/ChatPanel.vue'
import PreviewPanel from '../components/PreviewPanel.vue'
import PageNav from '../components/PageNav.vue'
import ProjectPanel from '../components/ProjectPanel.vue'
import { loadConfig } from '../services/api'
import { generatedCode, pages, currentPage, addMessage, phase, currentProjectId } from '../stores/app'
import { listProjects, getProject } from '../services/api'
import { loadProjectState, projects, resetCurrentProject } from '../stores/app'

onMounted(async () => {
  await loadConfig()
  // Load project list and restore last project
  try {
    const list = await listProjects()
    projects.value = list
    if (list.length > 0) {
      // Auto-load most recent project
      const projectId = list[0].id
      currentProjectId.value = projectId
      const project = await getProject(projectId)
      if (project) {
        loadProjectState(project)
      }
    }
  } catch {}
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

function handleProjectSelect() {
  // Re-fetch the current project state after switching
}
</script>

<template>
  <div class="home">
    <ChatPanel class="chat-panel">
      <template #header-left>
        <ProjectPanel @select="handleProjectSelect" />
      </template>
    </ChatPanel>
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
