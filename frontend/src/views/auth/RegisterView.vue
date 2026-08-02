<template>
  <div class="min-h-screen flex relative bg-gray-50">
    <LanguageSwitcher class="absolute top-4 right-4 z-20" />

    <AuthHeroPanel />

    <div class="flex-1 flex items-center justify-center px-4 py-10">
      <div class="w-full max-w-md">
        <div class="lg:hidden flex items-center gap-2 mb-6 justify-center">
          <Wheat :size="22" class="text-green-700" />
          <span class="text-xl font-display font-semibold text-green-900">Hal</span>
        </div>

        <div :class="['bg-white p-8 sm:p-9 rounded-3xl shadow-sm border border-gray-200 animate-fade-in-up', shakeClass]">
          <div class="w-11 h-11 rounded-full bg-green-900/5 border border-green-900/10 flex items-center justify-center mx-auto mb-4">
            <Wheat :size="20" class="text-green-700" />
          </div>

          <div class="text-center mb-2">
            <h1 class="text-2xl font-display font-semibold text-gray-900">{{ $t('auth.createAccount') }}</h1>
            <p class="text-sm text-gray-500 mt-1">{{ $t('auth.joinPlatform') }}</p>
          </div>

          <StepWizard
            v-if="wizardSteps && currentStep > 0"
            :steps="wizardSteps"
            :current-step="currentStep"
            :completed-steps="completedSteps"
            class="mb-5"
          />

          <p v-if="errorMessage" class="text-red-600 text-sm font-medium bg-red-50 p-3 rounded-xl border border-red-200 mb-4">
            {{ errorMessage }}
          </p>

          <Transition name="step-fade" mode="out-in">
            <form v-if="currentStep === 0" :key="0" @submit.prevent="handleStep0Continue" class="space-y-4">

              <div class="relative">
                <User :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input v-model="form.full_name" type="text" id="reg-name" required placeholder=" "
                  class="peer w-full border border-gray-300 rounded-lg pl-10 pr-3 pt-5 pb-2 text-sm
                    focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition" />
                <label for="reg-name" class="absolute left-10 text-gray-500 pointer-events-none transition-all duration-150
                  top-1 text-xs peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-sm peer-placeholder-shown:text-gray-400
                  peer-focus:top-1 peer-focus:text-xs peer-focus:text-green-700">
                  {{ $t('common.fullName') }}
                </label>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="relative">
                  <Phone :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input v-model="form.phone" type="text" id="reg-phone" required placeholder=" "
                    class="peer w-full border border-gray-300 rounded-lg pl-10 pr-3 pt-5 pb-2 text-sm
                      focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition" />
                  <label for="reg-phone" class="absolute left-10 text-gray-500 pointer-events-none transition-all duration-150
                    top-1 text-xs peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-sm peer-placeholder-shown:text-gray-400
                    peer-focus:top-1 peer-focus:text-xs peer-focus:text-green-700">
                    {{ $t('common.phone') }}
                  </label>
                </div>
                <div class="relative">
                  <IdCard :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input v-model="form.cnic" type="text" id="reg-cnic" required placeholder=" "
                    class="peer w-full border border-gray-300 rounded-lg pl-10 pr-3 pt-5 pb-2 text-sm
                      focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition" />
                  <label for="reg-cnic" class="absolute left-10 text-gray-500 pointer-events-none transition-all duration-150
                    top-1 text-xs peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-sm peer-placeholder-shown:text-gray-400
                    peer-focus:top-1 peer-focus:text-xs peer-focus:text-green-700">
                    {{ $t('common.cnic') }}
                  </label>
                </div>
              </div>

              <div class="relative">
                <Lock :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input v-model="form.password" :type="showPassword ? 'text' : 'password'" id="reg-password" required placeholder=" "
                  class="peer w-full border border-gray-300 rounded-lg pl-10 pr-10 pt-5 pb-2 text-sm
                    focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition" />
                <label for="reg-password" class="absolute left-10 text-gray-500 pointer-events-none transition-all duration-150
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

              <div class="relative">
                <Briefcase :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 z-10" />
                <select v-model="form.role" required
                  class="w-full border border-gray-300 rounded-lg pl-10 pr-9 py-2.5 text-sm bg-white
                    focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition appearance-none">
                  <option value="">{{ $t('auth.selectRolePlaceholder') }}</option>
                  <option value="smallholder">{{ $t('auth.smallholder') }}</option>
                  <option value="tenant">{{ $t('auth.tenant') }}</option>
                  <option value="landowner">{{ $t('auth.landowner') }}</option>
                  <option value="shopkeeper">{{ $t('auth.shopkeeper') }}</option>
                </select>
                <ChevronDown :size="16" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
              </div>

              <DistrictSelect v-model="form.district" />

              <button type="submit" :disabled="isSubmitting" class="btn-primary w-full flex items-center justify-center gap-2 group mt-2">
                <span>{{ isSubmitting ? $t('common.pleaseWait') : (isLandownerRole || !form.role ? $t('auth.register') : $t('common.continue')) }}</span>
                <ArrowRight v-if="!isSubmitting" :size="16" class="transition-transform group-hover:translate-x-0.5" />
              </button>

              <router-link to="/login" class="block text-center text-sm text-gray-600 hover:text-green-700 transition mt-2">
                {{ $t('auth.alreadyHaveAccount') }}
              </router-link>
            </form>

            <div v-else-if="currentStep === 1 && isFarmerRole" :key="'farmer-1'">
              <div class="flex items-center gap-2 mb-2">
                <Users :size="18" class="text-green-700" />
                <h3 class="font-display font-semibold text-gray-800">{{ $t('auth.findNumberdar') }}</h3>
              </div>
              <p class="text-sm text-gray-500 mb-3">{{ $t('auth.communityLinkExplain') }}</p>

              <div v-if="community.numberdars.length > 0" class="space-y-2 mb-4 max-h-64 overflow-y-auto">
                <label v-for="nd in community.numberdars" :key="nd.id"
                  :class="['flex items-center justify-between p-3 border rounded-xl cursor-pointer transition-colors',
                    selectedNumberdarId === nd.id ? 'border-green-600 bg-green-50' : 'border-gray-200 hover:border-gray-300']">
                  <div>
                    <p class="text-sm font-medium text-gray-800">{{ nd.full_name }}</p>
                    <p class="text-xs text-gray-500">{{ nd.jurisdiction_district }} — {{ nd.total_farmers_verified }} farmers verified</p>
                  </div>
                  <input type="radio" :value="nd.id" v-model="selectedNumberdarId" class="ml-2 accent-green-700" />
                </label>
              </div>
              <p v-else class="text-sm text-gray-400 mb-4">{{ $t('auth.noNumberdarsFound', { district: form.district }) }}</p>

              <button @click="handleSubmitVerificationRequest" :disabled="!selectedNumberdarId"
                class="btn-primary w-full mb-3">
                {{ $t('auth.submitRequest') }}
              </button>

              <p class="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-xl p-3 mb-2">
                ⚠ {{ $t('auth.skipWarning') }}
              </p>
              <button @click="handleSkipVerification" type="button" class="w-full text-sm text-gray-500 hover:text-gray-700 py-1">
                {{ $t('auth.skipForNow') }}
              </button>
            </div>

            <div v-else-if="currentStep === 1 && isCorporateRole" :key="'corp-1'" class="space-y-4">
              <h3 class="font-display font-semibold text-gray-800 mb-1">{{ $t('auth.businessDetails') }}</h3>

              <div class="relative">
                <Store :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input v-model="form.shop_name" type="text" id="reg-shop" placeholder=" "
                  class="peer w-full border border-gray-300 rounded-lg pl-10 pr-3 pt-5 pb-2 text-sm
                    focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition" />
                <label for="reg-shop" class="absolute left-10 text-gray-500 pointer-events-none transition-all duration-150
                  top-1 text-xs peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-sm peer-placeholder-shown:text-gray-400
                  peer-focus:top-1 peer-focus:text-xs peer-focus:text-green-700">
                  {{ $t('auth.shopName') }}
                </label>
              </div>

              <div class="relative">
                <Hash :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input v-model="form.secp_registration_number" type="text" id="reg-secp" placeholder=" "
                  class="peer w-full border border-gray-300 rounded-lg pl-10 pr-3 pt-5 pb-2 text-sm
                    focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition" />
                <label for="reg-secp" class="absolute left-10 text-gray-500 pointer-events-none transition-all duration-150
                  top-1 text-xs peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-sm peer-placeholder-shown:text-gray-400
                  peer-focus:top-1 peer-focus:text-xs peer-focus:text-green-700">
                  {{ $t('auth.secpNumber') }}
                </label>
              </div>

              <div class="relative">
                <Hash :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input v-model="form.ntn_number" type="text" id="reg-ntn" placeholder=" "
                  class="peer w-full border border-gray-300 rounded-lg pl-10 pr-3 pt-5 pb-2 text-sm
                    focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition" />
                <label for="reg-ntn" class="absolute left-10 text-gray-500 pointer-events-none transition-all duration-150
                  top-1 text-xs peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-sm peer-placeholder-shown:text-gray-400
                  peer-focus:top-1 peer-focus:text-xs peer-focus:text-green-700">
                  {{ $t('auth.ntnNumber') }}
                </label>
              </div>

              <button @click="handleBusinessDetailsContinue" :disabled="isSubmitting" class="btn-primary w-full flex items-center justify-center gap-2 group">
                <span>{{ isSubmitting ? $t('common.pleaseWait') : $t('common.continue') }}</span>
                <ArrowRight v-if="!isSubmitting" :size="16" class="transition-transform group-hover:translate-x-0.5" />
              </button>
            </div>

            <div v-else-if="currentStep === 2 && isFarmerRole" :key="'farmer-2'">
              <div class="flex items-center gap-2 mb-2">
                <ShieldCheck :size="18" class="text-green-700" />
                <h3 class="font-display font-semibold text-gray-800">{{ $t('auth.beforeYouContinue') }}</h3>
              </div>
              <p class="text-sm text-gray-500 mb-3">{{ $t('auth.consentExplain') }}</p>

              <label class="flex items-start gap-2 text-sm mb-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                <input type="checkbox" v-model="consent1" class="mt-1 accent-green-700" />
                <span>{{ $t('auth.consentUnderstand') }}</span>
              </label>
              <label class="flex items-start gap-2 text-sm mb-4 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                <input type="checkbox" v-model="consent2" class="mt-1 accent-green-700" />
                <span>{{ $t('auth.consentTerms') }}</span>
              </label>

              <button @click="handleCompleteFarmerRegistration" :disabled="!allConsented" class="btn-primary w-full">
                {{ $t('auth.completeRegistration') }}
              </button>
            </div>

            <div v-else-if="currentStep === 2 && isCorporateRole" :key="'corp-2'" class="space-y-4">
              <h3 class="font-display font-semibold text-gray-800 mb-1">{{ $t('auth.verificationDocuments') }}</h3>
              <p class="text-sm text-gray-500 mb-2">{{ $t('auth.uploadDocumentsExplain') }}</p>

              <DocumentUpload v-model="secpDocument" :label="$t('auth.uploadSecpCert')" />
              <DocumentUpload v-model="incorporationDocument" :label="$t('auth.uploadIncorporation')" />

              <button @click="handleFinishCorporateRegistration" :disabled="!documentsReady" class="btn-primary w-full">
                {{ $t('auth.submitForVerification') }}
              </button>
              <p class="text-xs text-gray-500 text-center">{{ $t('auth.pendingVerificationNote') }}</p>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useCommunityStore } from '@/stores/community.js'
import { ROLE_HOME } from '@/constants/roles.js'
import StepWizard from '@/components/shared/StepWizard.vue'
import DocumentUpload from '@/components/shared/DocumentUpload.vue'
import LanguageSwitcher from '@/components/shared/LanguageSwitcher.vue'
import AuthHeroPanel from '@/components/auth/AuthHeroPanel.vue'
import { Wheat, User, Phone, IdCard, Lock, Eye, EyeOff, Briefcase, ChevronDown, MapPin, Users, ShieldCheck, Store, Hash, ArrowRight } from 'lucide-vue-next'
import { uploadVerificationDocument } from '@/api/auth.js'
import { useReferenceStore } from '@/stores/reference.js'   
import DistrictSelect from '@/components/shared/DistrictSelect.vue' 

const reference = useReferenceStore() 
onMounted(() => {
  reference.fetchIfNeeded().then(() => { form.province = reference.province })
})

const router = useRouter()
const auth = useAuthStore()
const community = useCommunityStore()
const isSubmitting = ref(false)
const errorMessage = ref('')
const currentStep = ref(0)
const completedSteps = ref([])
const showPassword = ref(false) 

const form = reactive({ full_name: '', phone: '', cnic: '', password: '', role: '', district: '', province: 'Punjab', shop_name: '', secp_registration_number: '', ntn_number: '' })

const isFarmerRole = computed(() => ['smallholder', 'tenant'].includes(form.role))
const isCorporateRole = computed(() => form.role === 'shopkeeper')
const isLandownerRole = computed(() => form.role === 'landowner')

const wizardSteps = computed(() => {
  if (isFarmerRole.value) {
    return [
      { id: 'basic', label: 'Basic Info', icon: '📋' },
      { id: 'community', label: 'Community Link', icon: '👤' },
      { id: 'consent', label: 'Consent', icon: '✓' },
    ]
  }
  if (isCorporateRole.value) {
    return [
      { id: 'basic', label: 'Basic Info', icon: '📋' },
      { id: 'business', label: 'Business Details', icon: '🏪' },
      { id: 'documents', label: 'Documents', icon: '📄' },
    ]
  }
  return null
})

function validateBasicInfo() {
  if (!form.full_name.trim() || !form.phone.trim() || !form.cnic.trim() || !form.password || !form.role || !form.district.trim()) {
    errorMessage.value = 'All fields are required.'
    return false
  }
  return true
}

function handleError(err) {
  errorMessage.value = err.response?.data?.message || Object.values(err.response?.data || {})[0]?.[0] || 'Registration failed.'
}

async function submitRegistration() {
  const payload = {
    full_name: form.full_name, phone: form.phone, cnic: form.cnic, password: form.password,
    role: form.role, district: form.district, province: form.province,
  }
  if (isCorporateRole.value) {
    payload.shop_name = form.shop_name
    payload.secp_registration_number = form.secp_registration_number
    payload.ntn_number = form.ntn_number
  }
  return auth.register(payload)
}

async function handleStep0Continue() {
  errorMessage.value = ''
  if (!validateBasicInfo()) return

  if (isLandownerRole.value || !form.role) {
    isSubmitting.value = true
    try {
      await submitRegistration()
      router.push(ROLE_HOME[form.role] || '/login')
    } catch (err) {
      handleError(err)
    } finally {
      isSubmitting.value = false
    }
    return
  }

  if (isFarmerRole.value) {
    isSubmitting.value = true
    try {
      await submitRegistration()
      completedSteps.value = [0]
      currentStep.value = 1
    } catch (err) {
      handleError(err)
    } finally {
      isSubmitting.value = false
    }
    return
  }

  completedSteps.value = [0]
  currentStep.value = 1
}

const selectedNumberdarId = ref('')

watch(currentStep, (step) => {
  if (isFarmerRole.value && step === 1) {
    community.fetchNumberdars(form.district)
  }
})

async function handleSubmitVerificationRequest() {
  if (!selectedNumberdarId.value) return
  try {
    await community.submitRequest(selectedNumberdarId.value)
    completedSteps.value = [0, 1]
    currentStep.value = 2
  } catch (err) {

  }
}

function handleSkipVerification() {
  completedSteps.value = [0, 1]
  currentStep.value = 2
}

const consent1 = ref(false)
const consent2 = ref(false)
const allConsented = computed(() => consent1.value && consent2.value)

function handleCompleteFarmerRegistration() {
  router.push(ROLE_HOME[form.role] || '/login')
}

async function handleBusinessDetailsContinue() {
  errorMessage.value = ''
  if (!form.shop_name.trim() || !form.secp_registration_number.trim() || !form.ntn_number.trim()) {
    errorMessage.value = 'Shop name, SECP number, and NTN number are all required.'
    return
  }
  isSubmitting.value = true
  try {
    await submitRegistration()
    completedSteps.value = [0, 1]
    currentStep.value = 2
  } catch (err) {
    handleError(err)
  } finally {
    isSubmitting.value = false
  }
}

const secpDocument = ref(null)
const incorporationDocument = ref(null)
const documentsReady = computed(() => !!secpDocument.value && !!incorporationDocument.value)

async function handleFinishCorporateRegistration() {
  isSubmitting.value = true
  errorMessage.value = ''
  try {
    if (secpDocument.value) await uploadVerificationDocument('secp_certificate', secpDocument.value)
    if (incorporationDocument.value) await uploadVerificationDocument('incorporation_certificate', incorporationDocument.value)
    router.push(ROLE_HOME[form.role] || '/login')
  } catch (err) {
    errorMessage.value = 'Failed to upload documents. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}

const shakeClass = ref('')
watch(errorMessage, (val) => {
  if (val) {
    shakeClass.value = 'animate-shake'
    setTimeout(() => { shakeClass.value = '' }, 500)
  }
})
</script>