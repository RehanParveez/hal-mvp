<template>
  <div class="min-h-screen flex relative bg-gray-50">
    <LanguageSwitcher class="absolute top-4 right-4 z-20" />

    <AuthHeroPanel />

    <div class="flex-1 flex items-center justify-center px-4">
      <div class="w-full max-w-sm">
        <div class="lg:hidden flex items-center gap-2 mb-6 justify-center">
          <Wheat :size="22" class="text-green-700" />
          <span class="text-xl font-display font-semibold text-green-900">Hal</span>
        </div>

        <form @submit.prevent="handleSubmit"
          :class="['bg-white p-9 rounded-3xl shadow-sm border border-gray-200 space-y-5 animate-fade-in-up', shakeClass]">

          <div class="w-11 h-11 rounded-full bg-green-900/5 border border-green-900/10 flex items-center justify-center mx-auto">
            <Wheat :size="20" class="text-green-700" />
          </div>

          <h1 class="text-2xl font-display font-semibold text-center text-gray-900">{{ $t('auth.loginTitle') }}</h1>

          <div class="relative">
            <Phone :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input v-model="phone" type="text" id="login-phone" required placeholder=" "
              class="peer w-full border border-gray-300 rounded-lg pl-10 pr-3 pt-5 pb-2 text-sm
                focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition" />
            <label for="login-phone" class="absolute left-10 text-gray-500 pointer-events-none transition-all duration-150
              top-1 text-xs peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-sm peer-placeholder-shown:text-gray-400
              peer-focus:top-1 peer-focus:text-xs peer-focus:text-green-700">
              {{ $t('common.phone') }}
            </label>
          </div>

          <div class="relative">
            <Lock :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input v-model="password" :type="showPassword ? 'text' : 'password'" id="login-password" required placeholder=" "
              class="peer w-full border border-gray-300 rounded-lg pl-10 pr-10 pt-5 pb-2 text-sm
                focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition" />
            <label for="login-password" class="absolute left-10 text-gray-500 pointer-events-none transition-all duration-150
              top-1 text-xs peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-sm peer-placeholder-shown:text-gray-400
              peer-focus:top-1 peer-focus:text-xs peer-focus:text-green-700">
              {{ $t('common.password') }}
            </label>
            <button type="button" @click="showPassword = !showPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              :aria-label="showPassword ? $t('common.hidePassword') : $t('common.showPassword')">
              <component :is="showPassword ? EyeOff : Eye" :size="16" />
            </button>
          </div>

          <p v-if="auth.loginError" class="text-red-600 text-sm">{{ auth.loginError }}</p>

          <button type="submit" :disabled="auth.isLoading" class="btn-primary w-full flex items-center justify-center gap-2 group">
            <span>{{ auth.isLoading ? $t('common.loading') : $t('common.login') }}</span>
            <ArrowRight v-if="!auth.isLoading" :size="16" class="transition-transform group-hover:translate-x-0.5" />
          </button>

          <p class="text-center text-sm text-gray-500">
            {{ $t('auth.noAccountYet') }}
            <router-link to="/register" class="text-green-700 font-medium hover:text-green-800 hover:underline transition">
              {{ $t('auth.registerNow') }}
            </router-link>
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { ROLE_HOME } from '@/constants/roles.js'
import LanguageSwitcher from '@/components/shared/LanguageSwitcher.vue'
import AuthHeroPanel from '@/components/auth/AuthHeroPanel.vue'
import { Wheat, Lock, Phone, Eye, EyeOff, ArrowRight } from 'lucide-vue-next'

const phone = ref('')
const password = ref('')
const showPassword = ref(false)
const auth = useAuthStore()
const router = useRouter()

const shakeClass = ref('')
watch(() => auth.loginError, (val) => {
  if (val) {
    shakeClass.value = 'animate-shake'
    setTimeout(() => { shakeClass.value = '' }, 500)
  }
})

async function handleSubmit() {
  try {
    const user = await auth.login(phone.value, password.value)
    router.push(ROLE_HOME[user.role] || '/login')
  } catch (err) {
  }
}
</script>