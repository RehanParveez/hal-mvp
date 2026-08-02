import { defineStore } from 'pinia'
import { getRegistrationReferenceData } from '@/api/accounts.js'

export const useReferenceStore = defineStore('reference', {
  state: () => ({ province: '', districtDivisions: [], isLoaded: false, loadError: false }),
  actions: {
    async fetchIfNeeded() {
      if (this.isLoaded) return
      this.loadError = false
      try {
        const res = await getRegistrationReferenceData()
        this.province = res.data.province
        this.districtDivisions = res.data.district_divisions
        this.isLoaded = true
      } catch (err) {
        this.loadError = true
      }
    },
  },
})