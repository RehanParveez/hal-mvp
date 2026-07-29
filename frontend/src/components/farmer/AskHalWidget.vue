<template>
  <div class="card overflow-hidden p-0"> 
    <div class="bg-slate-900 text-white px-5 py-3 flex items-center gap-2">
      <MessageCircle :size="18" class="text-gold-400" />
      <p class="font-display font-semibold">{{ $t('assistant.title') }}</p>
    </div>
    <p class="text-xs text-gray-500 bg-gray-50 px-5 py-2 border-b border-gray-100">
      {{ $t('assistant.disclaimer') }}
    </p>

    <div ref="messageArea" class="max-h-80 overflow-y-auto px-5 py-4 space-y-3">
      <div v-if="assistant.messages.length === 0" class="text-sm text-gray-400 text-center py-4">
        {{ $t('assistant.emptyState') }}
      </div>
      <div v-for="(msg, i) in assistant.messages" :key="i" :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
        <div :class="['rounded-2xl px-4 py-2 text-sm max-w-[80%]', msg.role === 'user' ? 'bg-green-700 text-white' : 'bg-gray-100 text-gray-800']">
          {{ msg.text }}
        </div>
      </div>
      <div v-if="assistant.isAsking" class="flex justify-start">
        <div class="bg-gray-100 rounded-2xl px-4 py-2 text-sm text-gray-400 animate-pulse">{{ $t('assistant.thinking') }}</div>
      </div>
    </div>

    <div v-if="suggestedQuestions.length" class="px-5 pb-2 flex flex-wrap gap-2">
      <button v-for="q in suggestedQuestions" :key="q" @click="handleAsk(q)"
        class="text-xs bg-green-50 text-green-800 px-3 py-1.5 rounded-full hover:bg-green-100 transition-colors">
        {{ q }}
      </button>
    </div>

    <form @submit.prevent="handleAsk(inputValue)" class="border-t border-gray-100 p-3 flex gap-2">
      <input v-model="inputValue" type="text" :placeholder="$t('assistant.inputPlaceholder')" class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm" />
      <button type="submit" :disabled="assistant.isAsking || !inputValue.trim()" class="btn-primary px-4">{{ $t('assistant.send') }}</button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { MessageCircle } from 'lucide-vue-next'
import { useAssistantStore } from '@/stores/assistant.js'
import { useAuthStore } from '@/stores/auth.js'
import { useLoansStore } from '@/stores/loans.js'

const { t } = useI18n()
const assistant = useAssistantStore()
const auth = useAuthStore()
const loans = useLoansStore()
const inputValue = ref('')
const messageArea = ref(null)

const suggestedQuestions = computed(() => {
  const qs = []
  if (!auth.user?.numberdar_verified) qs.push(t('assistant.suggestVerification'))
  if (loans.hasCreditPending) qs.push(t('assistant.suggestCreditCheck'))
  if (loans.activeLoan) qs.push(t('assistant.suggestEscrow'))
  qs.push(t('assistant.suggestGeneral'))
  return qs.slice(0, 3)
})

async function handleAsk(question) {
  if (!question?.trim() || assistant.isAsking) return
  inputValue.value = ''
  await assistant.ask(question.trim())
  await nextTick()
  if (messageArea.value) messageArea.value.scrollTop = messageArea.value.scrollHeight
}

onMounted(() => { if (!assistant.hasLoadedHistory) assistant.fetchHistory() })
</script>