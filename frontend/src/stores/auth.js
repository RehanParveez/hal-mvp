import { defineStore } from 'pinia'
import * as authApi from '@/api/auth.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,
    isLoading: false,
    loginError: null,
    registerError: null,
    sessionChecked: false,
  }),
  getters: {
    isLoggedIn: (state) => !!state.accessToken,
    isFarmer: (state) => ['smallholder', 'tenant'].includes(state.user?.role),
    isLandowner: (state) => state.user?.role === 'landowner',
    isBankManager: (state) => state.user?.role === 'bank',
    isFactory: (state) => state.user?.role === 'factory',
    isShopkeeper: (state) => state.user?.role === 'shopkeeper',
    isInsuranceAgent: (state) => state.user?.role === 'insurance',
    isAFOOfficer: (state) => state.user?.role === 'afo',
    isAdmin: (state) => state.user?.role === 'admin',
    isNumberdar: (state) => state.user?.role === 'numberdar',                  
    isNumberdarVerified: (state) => state.user?.numberdar_verified === true,      
    creditTier: (state) => state.user?.credit_tier ?? 'unverified',            
    isLowRisk: (state) => state.user?.credit_tier === 'low_risk',               
    isMediumRisk: (state) => state.user?.credit_tier === 'medium_risk',           
    isHighRisk: (state) => state.user?.credit_tier === 'high_risk',
    hasCreditApproval: (state) => ['low_risk', 'medium_risk'].includes(state.user?.credit_tier),
    isCorporateVerified: (state) => state.user?.secp_verified === true && state.user?.ntn_verified === true,
  },
  actions: {
    async login(phone, password) {
      this.isLoading = true
      this.loginError = null
      try {
        const tokenRes = await authApi.login(phone, password)
        this.accessToken = tokenRes.data.access
        const profileRes = await authApi.fetchProfile()
        this.user = profileRes.data
        this.sessionChecked = true

        return this.user
      } catch (err) {
        this.registerError = err.response?.data?.message || err.response?.data?.detail || 'The Login failed. Kindly check your phone and password.'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async register(payload) {
      this.isLoading = true
      this.registerError = null
      try {
        const res = await authApi.register(payload)
        this.accessToken = res.data.access
        this.refreshToken = res.data.refresh
        this.user = res.data.user
        sessionStorage.setItem('accessToken', this.accessToken)
        localStorage.setItem('refreshToken', this.refreshToken)
        return this.user
      } catch (err) {
        this.registerError = err.response?.data?.message || err.response?.data?.detail || 'Registration failed.'
        throw err

      } finally {
        this.isLoading = false
      }
    },

    async refreshAccessToken() {
    const res = await authApi.refreshToken() 
    this.accessToken = res.data.access
    return this.accessToken
  },

    async updateProfile(payload) {
     const res = await authApi.updateProfile(payload)
     this.user = res.data
     return this.user
    },

    async updateEmail(email) {
     return this.updateProfile({ email })
   },

    async restoreSession() {
    try {
      await this.refreshAccessToken()
      const profileRes = await authApi.fetchProfile()
      this.user = profileRes.data
    } catch {
      this.user = null
      this.accessToken = null
    } finally {
        this.sessionChecked = true 
      }
    },

    async logout() { 
    try { await authApi.logout() } catch {}
    this.user = null
    this.accessToken = null
    this.sessionChecked = true
  },
},
})