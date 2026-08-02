<template>
  <div class="min-h-screen flex relative bg-gray-50">
    <LanguageSwitcher class="absolute top-4 right-4 z-20" />
    <AuthHeroPanel />
    <div class="flex-1 flex items-center justify-center px-4">
      <div class="w-full max-w-sm">
        <div class="bg-white p-8 rounded-3xl shadow-sm border border-gray-200 space-y-5 animate-fade-in-up">
          <h1 class="text-2xl font-display font-semibold text-center">{{ $t('auth.resetPasswordTitle') }}</h1>

          <form v-if="step === 'phone'" @submit.prevent="handleRequestReset" class="space-y-4">
            <div class="relative">
              <Phone :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input v-model="phone" type="text" required placeholder=" " id="fp-phone"
                class="peer w-full border border-gray-300 rounded-lg pl-10 pr-3 pt-5 pb-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition" />
              <label for="fp-phone" class="absolute left-10 text-gray-500 pointer-events-none transition-all duration-150 top-1 text-xs
                peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-sm peer-placeholder-shown:text-gray-400 peer-focus:top-1 peer-focus:text-xs peer-focus:text-green-700">
                {{ $t('common.phone') }}
              </label>
            </div>
            <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
            <button type="submit" :disabled="isSubmitting" class="btn-primary w-full">
              {{ isSubmitting ? $t('common.loading') : $t('auth.sendResetCode') }}
            </button>
          </form>

          <div v-else-if="step === 'otp'">
            <p class="text-sm text-gray-500 mb-3">{{ $t('auth.enterResetCode') }}</p>
            <OTPInputField v-model="otpValue" :has-error="otpError" @complete="handleVerifyOTP" @resend="handleRequestReset" />
          </div>

          <form v-else-if="step === 'newPassword'" @submit.prevent="handleCompleteReset" class="space-y-4">
            <div class="relative">
              <Lock :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input v-model="newPassword" type="password" required placeholder=" " id="fp-password" minlength="8"
                class="peer w-full border border-gray-300 rounded-lg pl-10 pr-3 pt-5 pb-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition" />
              <label for="fp-password" class="absolute left-10 text-gray-500 pointer-events-none transition-all duration-150 top-1 text-xs
                peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-sm peer-placeholder-shown:text-gray-400 peer-focus:top-1 peer-focus:text-xs peer-focus:text-green-700">
                {{ $t('auth.newPassword') }}
              </label>
            </div>
            <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
            <button type="submit" :disabled="isSubmitting" class="btn-primary w-full">
              {{ isSubmitting ? $t('common.loading') : $t('auth.setNewPassword') }}
            </button>
          </form>

          <div v-else-if="step === 'success'" class="text-center">
            <CheckCircle2 :size="40" class="text-green-700 mx-auto mb-3" />
            <p class="text-gray-700 mb-4">{{ $t('auth.resetSuccess') }}</p>
            <router-link to="/login" class="btn-primary w-full block text-center">{{ $t('common.login') }}</router-link>
          </div>

          <router-link v-if="step === 'phone'" to="/login" class="block text-center text-sm text-gray-600 hover:text-green-700 transition">
            {{ $t('auth.backToLogin') }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Phone, Lock, CheckCircle2 } from 'lucide-vue-next'
import { requestPasswordReset, verifyPasswordResetOTP, completePasswordReset } from '@/api/auth.js'
import OTPInputField from '@/components/shared/OTPInputField.vue'
import LanguageSwitcher from '@/components/shared/LanguageSwitcher.vue'
import AuthHeroPanel from '@/components/auth/AuthHeroPanel.vue'

const step = ref('phone')
const phone = ref('')
const otpValue = ref('')
const otpError = ref(false)
const newPassword = ref('')
const resetReference = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)

async function handleRequestReset() {
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    const res = await requestPasswordReset(phone.value)
    if (!res.data.reset_reference) {
      errorMessage.value = 'if this phone number is registered, a reset code has been sent.'
      return
    }
    resetReference.value = res.data.reset_reference
    step.value = 'otp'
  } finally {
    isSubmitting.value = false
  }
}

async function handleVerifyOTP(code) {
  otpError.value = false
  try {
    await verifyPasswordResetOTP(resetReference.value, code)
    step.value = 'newPassword'
  } catch {
    otpError.value = true
  }
}

async function handleCompleteReset() {
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    await completePasswordReset(resetReference.value, newPassword.value)
    step.value = 'success'
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Something went wrong. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>