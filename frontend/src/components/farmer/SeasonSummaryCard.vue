<template>
  <div class="mt-4">
    <button v-if="!summary && !isLoading" @click="handleGenerate" class="btn-primary w-full">
      <Sparkles :size="16" class="inline mr-1" /> {{ $t('seasonSummary.generateBtn') }}
    </button>
    <div v-if="isLoading" class="skeleton h-20 rounded-2xl"></div>
    <div v-if="summary" class="card bg-gradient-to-br from-green-50 to-gold-100 border-green-100 animate-fade-in-up">
      <p class="text-xs font-semibold text-green-700 uppercase tracking-wide mb-2 flex items-center gap-1">
        <Sparkles :size="14" /> {{ $t('seasonSummary.title') }}
      </p>
      <p class="text-sm text-gray-700 leading-relaxed">{{ summary.narrative }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Sparkles } from 'lucide-vue-next'
import { getSeasonSummary } from '@/api/assistant.js'
import { useNotificationsStore } from '@/stores/notifications.js'

const props = defineProps({ invoiceId: { type: String, required: true } })
const summary = ref(null)
const isLoading = ref(false)

async function handleGenerate() {
  isLoading.value = true
  try {
    const res = await getSeasonSummary(props.invoiceId)
    summary.value = res.data
  } catch (err) {
    useNotificationsStore().showError({ message: 'Failed to generate your season summary. Please try again.' })
  } finally {
    isLoading.value = false
  }
}
</script>