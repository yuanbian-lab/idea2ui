<script setup lang="ts">
import { computed } from 'vue'
import { CheckCircleOutlined, RightCircleOutlined } from '@ant-design/icons-vue'
import { pages, currentPage, phase } from '../stores/app'

const emit = defineEmits<{
  select: [name: string]
}>()

const pageList = computed(() => pages.value)

function handleClick(name: string) {
  if (phase.value !== 'page_generation') return
  currentPage.value = name
  emit('select', name)
}
</script>

<template>
  <div class="page-nav" v-if="pageList.length > 0 && phase.value === 'page_generation'">
    <span class="nav-label">页面导航</span>
    <div class="nav-tabs">
      <div
        v-for="page in pageList"
        :key="page.name"
        class="nav-tab"
        :class="{ active: currentPage === page.name, generated: page.generated }"
        @click="handleClick(page.name)"
      >
        <CheckCircleOutlined v-if="page.generated" class="icon-done" />
        <RightCircleOutlined v-else class="icon-pending" />
        <span>{{ page.name }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-nav {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-top: 1px solid #f0f0f0;
  background: #fff;
}

.nav-label {
  font-size: 12px;
  font-weight: 600;
  color: #999;
  white-space: nowrap;
}

.nav-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  color: #666;
  background: #f5f5f5;
  white-space: nowrap;
  transition: all 0.2s;
  user-select: none;
}

.nav-tab:hover {
  background: #e8e8e8;
}

.nav-tab.active {
  background: #1677ff;
  color: #fff;
}

.icon-done {
  color: #52c41a;
  font-size: 12px;
}

.nav-tab.active .icon-done {
  color: #fff;
}

.icon-pending {
  color: #bbb;
  font-size: 12px;
}
</style>
