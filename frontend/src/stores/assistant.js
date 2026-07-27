import { defineStore } from 'pinia'
import * as assistantApi from '@/api/assistant.js'

export const useAssistantStore = defineStore('assistant', {
  state: () => ({ messages: [], isAsking: false, hasLoadedHistory: false }),
  actions: {
    async fetchHistory() {
      const res = await assistantApi.getMyQueries()
      const results = (res.data.results ?? res.data).slice().reverse() 
      this.messages = results.flatMap((q) => ([
        { role: 'user', text: q.question },
        { role: 'assistant', text: q.answer, status: q.status },
      ]))
      this.hasLoadedHistory = true
    },
    async ask(question) {
      this.messages.push({ role: 'user', text: question })
      this.isAsking = true
      try {
        const res = await assistantApi.askAssistant(question)
        this.messages.push({ role: 'assistant', text: res.data.answer, status: res.data.status })
      } finally {
        this.isAsking = false
      }
    },
  },
})