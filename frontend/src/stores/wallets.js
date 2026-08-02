import { defineStore } from 'pinia'
import * as walletsApi from '@/api/wallets.js'

export const useWalletsStore = defineStore('wallets', {
  state: () => ({
    wallet: null,
    transactions: [],
    transactionsNextUrl: null,
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchMyBalance() {
      this.isLoading = true
      this.error = null
      try {
        const res = await walletsApi.getMyBalance()
        this.wallet = { ...res.data, balance: Number(res.data.balance) }
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load wallet balance.'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async fetchTransactions(params) {
      this.isLoading = true
      this.error = null
      try {
        const res = await walletsApi.listTransactions(params)
        const raw = res.data.results ?? res.data
        this.transactions = raw.map(t => ({
          ...t,
          amount: Number(t.amount)
        }))
        this.transactionsNextUrl = res.data.next ?? null
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load transactions.'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async fetchMoreTransactions() {
      if (!this.transactionsNextUrl) return
      try {
        const res = await fetchNextPage(this.transactionsNextUrl)
        const raw = res.data.results ?? []
        const mapped = raw.map(t => ({
          ...t,
          amount: Number(t.amount)
        }))
        this.transactions = [...this.transactions, ...mapped]
        this.transactionsNextUrl = res.data.next ?? null
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load more transactions.'
        throw err
      }
    },
  },
})