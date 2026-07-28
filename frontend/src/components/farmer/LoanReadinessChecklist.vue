<template>
  <div class="card mb-4">
    <p class="text-sm font-semibold text-gray-700 mb-3">{{ $t('readiness.title') }}</p>
    <div class="space-y-1">
      <div v-for="item in loans.readinessChecklist" :key="item.key"
        class="flex items-start gap-3 py-2 border-b border-gray-50 last:border-0">
        <component :is="statusIcon(item.status)" :size="18" :class="statusColor(item.status)" class="flex-shrink-0 mt-0.5" />
        <div class="flex-1">
          <p class="text-sm font-medium text-gray-800">{{ item.label }}</p>
          <p class="text-xs text-gray-500">{{ item.reason }}</p>
        </div>
        <button v-if="item.status !== 'complete'" @click="explainItem(item)"
          class="text-xs text-green-700 hover:underline whitespace-nowrap">
          {{ $t('readiness.askHal') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { CheckCircle2, Circle, XCircle } from 'lucide-vue-next'
import { useLoansStore } from '@/stores/loans.js'
import { useAssistantStore } from '@/stores/assistant.js'
import { useScrollTo } from '@/composables/useScrollTo.js'

const loans = useLoansStore()
const assistant = useAssistantStore()
const scrollToSection = useScrollTo()

function statusIcon(status) {
  return status === 'complete' ? CheckCircle2 : status === 'blocked' ? XCircle : Circle
}
function statusColor(status) {
  return status === 'complete' ? 'text-green-700' : status === 'blocked' ? 'text-red-600' : 'text-gray-300'
}

async function explainItem(item) {
  scrollToSection('assistant-section')
  await assistant.ask(`Explain why "${item.label}" isn't complete yet and what I should do next.`)
}

onMounted(() => loans.fetchReadiness())
</script>