import { defineStore } from 'pinia'
import * as inboxApi from '@/api/inbox.js'

export const useInboxStore = defineStore('inbox', {
  state: () => ({ items: [], unreadCount: 0, itemsNextUrl: null, isLoading: false }),
  actions: {
    async fetchMine() {
      this.isLoading = true
      try {
        const res = await inboxApi.listMyNotifications()
        this.items = res.data.results ?? res.data
        this.itemsNextUrl = res.data.next ?? null
      } finally {
        this.isLoading = false
      }
    },

    async fetchMoreItems() {
      if (!this.itemsNextUrl) return
      const res = await fetchNextPage(this.itemsNextUrl)
      this.items = [...this.items, ...(res.data.results ?? [])]
      this.itemsNextUrl = res.data.next ?? null
    },

    async fetchUnreadCount() {
      const res = await inboxApi.getUnreadCount()
      this.unreadCount = res.data.unread_count
    },

    async markRead(id) {
      await inboxApi.markRead(id)
      const item = this.items.find((n) => n.id === id)
      if (item) item.is_read = true
      this.unreadCount = Math.max(0, this.unreadCount - 1)
    },
    async markAllRead() {
      await inboxApi.markAllRead()
      this.items.forEach((n) => { n.is_read = true })
      this.unreadCount = 0
    },
  },
})