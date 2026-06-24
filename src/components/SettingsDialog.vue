<script setup lang="ts">
import { computed, ref } from 'vue'
import { message } from 'ant-design-vue'
import { modelConfig } from '../stores/app'
import { saveConfig } from '../services/api'

const visible = defineModel<boolean>('visible')
const saving = ref(false)

const providers = [
  { label: 'OpenAI', value: 'openai', models: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo'], baseUrl: 'https://api.openai.com/v1' },
  { label: 'Anthropic', value: 'anthropic', models: ['claude-3-5-sonnet-20240620', 'claude-3-opus-20240229'], baseUrl: 'https://api.anthropic.com' },
  { label: 'DeepSeek', value: 'deepseek', models: ['deepseek-chat', 'deepseek-reasoner'], baseUrl: 'https://api.deepseek.com' },
  { label: 'Moonshot', value: 'moonshot', models: ['moonshot-v1-8k', 'moonshot-v1-32k'], baseUrl: 'https://api.moonshot.cn/v1' },
  { label: '自定义', value: 'custom', models: [], baseUrl: '' },
]

const currentProvider = computed(() => providers.find(p => p.value === modelConfig.provider))

function handleProviderChange(value: string) {
  const provider = providers.find(p => p.value === value)
  if (provider) {
    modelConfig.baseUrl = provider.baseUrl
    if (provider.models.length > 0) {
      modelConfig.model = provider.models[0]
    }
  }
}

async function handleSave() {
  saving.value = true
  try {
    await saveConfig()
    message.success('配置已保存')
  } catch {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <a-modal v-model:visible="visible" title="模型配置" width="520" @ok="handleSave" @cancel="() => visible = false">
    <a-form layout="vertical">
      <a-form-item label="服务商">
        <a-select
          :value="modelConfig.provider"
          :options="providers"
          @change="handleProviderChange"
        />
      </a-form-item>

      <a-form-item label="模型">
        <a-select
          v-if="currentProvider && currentProvider.models.length > 0"
          :value="modelConfig.model"
          :options="currentProvider.models.map(m => ({ label: m, value: m }))"
          @change="(val: string) => modelConfig.model = val"
        />
        <a-input v-else v-model:value="modelConfig.model" placeholder="输入模型名称" />
      </a-form-item>

      <a-form-item label="API Key">
        <a-input-password v-model:value="modelConfig.apiKey" placeholder="sk-..." />
      </a-form-item>

      <a-form-item label="API Base URL">
        <a-input v-model:value="modelConfig.baseUrl" placeholder="https://api.openai.com/v1" />
      </a-form-item>
    </a-form>
    <template #footer>
      <a-button @click="visible = false">取消</a-button>
      <a-button type="primary" :loading="saving" @click="handleSave">保存</a-button>
    </template>
  </a-modal>
</template>
