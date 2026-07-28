<template>
  <div class="mt-3 border-t pt-3">
    <button @click="expanded = !expanded" class="text-xs text-green-700 hover:underline flex items-center gap-1">
      <MessageCircle :size="14" /> {{ expanded ? 'Hide' : 'Ask Hal about this' }}
    </button>
    <div class="collapse-grid mt-2" :class="{ 'is-open': expanded }">
      <div>
        <div v-if="messages.length" class="space-y-2 mb-2 max-h-48 overflow-y-auto">
          <div v-for="(msg, i) in messages" :key="i"
            :class="['text-xs rounded-lg px-3 py-2', msg.role === 'user' ? 'bg-green-50 text-green-800' : 'bg-gray-50 text-gray-700']">
            {{ msg.text }}
          </div>
        </div>
        <div class="flex gap-2">
          <input v-model="inputValue" type="text" placeholder="Ask a question..."
            class="flex-1 border border-gray-300 rounded-lg px-2 py-1.5 text-xs" @keyup.enter="handleAsk" />
          <button @click="handleAsk" :disabled="isAsking || !inputValue.trim()" class="btn-primary text-xs px-3 py-1.5">
            {{ isAsking ? '...' : 'Ask' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { MessageCircle } from 'lucide-vue-next'
import { askAssistant } from '@/api/assistant.js'

const props = defineProps({
  loanId: { type: String, default: null },
  batchId: { type: String, default: null },
})

const expanded = ref(false)
const messages = ref([])
const inputValue = ref('')
const isAsking = ref(false)

async function handleAsk() {
  const question = inputValue.value.trim()
  if (!question || isAsking.value) return
  messages.value.push({ role: 'user', text: question })
  inputValue.value = ''
  isAsking.value = true
  try {
    const extra = {}
    if (props.loanId) extra.loan_id = props.loanId
    if (props.batchId) extra.batch_id = props.batchId
    const res = await askAssistant(question, extra)
    messages.value.push({ role: 'assistant', text: res.data.answer })
  } finally {
    isAsking.value = false
  }
}
</script>