<template>
  <div class="hidden lg:flex lg:w-[45%] relative flex-col justify-between p-14 text-white overflow-hidden"
    style="clip-path: url(#hal-hero-curve);">
    <div class="absolute inset-0 field-texture"
      style="background: linear-gradient(160deg, var(--color-slate-950) 0%, var(--color-green-900) 55%, var(--color-slate-900) 100%);"></div>
    <div class="absolute -right-24 top-1/3 w-80 h-80 rounded-full bg-gold-600/10 blur-3xl pointer-events-none"></div>

    <div class="relative z-10 flex items-center gap-2 animate-fade-in-up">
      <Wheat :size="24" class="text-gold-400" />
      <span class="text-2xl font-display font-semibold tracking-tight">Hal</span>
    </div>

    <div class="relative z-10">
      <Transition name="fade" mode="out-in">
        <p :key="messageIndex" class="text-xl leading-relaxed text-slate-100 max-w-sm font-display mb-9 animate-fade-in-up" style="animation-delay: 0.1s">
          {{ rotatingMessages[messageIndex] }}
        </p>
      </Transition>

      <p class="text-xs uppercase tracking-wide text-slate-500 mb-3 animate-fade-in-up" style="animation-delay: 0.2s">
        {{ $t('auth.howHalWorks') }}
      </p>
      <div class="space-y-0 animate-fade-in-up" style="animation-delay: 0.25s">
        <div v-for="(stage, i) in trustStages" :key="stage.label" class="flex gap-3">
          <div class="flex flex-col items-center">
            <div :class="['w-8 h-8 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors backdrop-blur-sm',
              stage.state === 'complete' ? 'bg-gold-400 border-gold-400 text-slate-950' :
              stage.state === 'active' ? 'bg-slate-950/25 border-gold-400 text-gold-300 animate-pulse-glow' :
              'bg-slate-950/25 border-slate-700 text-slate-500']">
              <component :is="stage.icon" :size="15" />
            </div>
            <div v-if="i < trustStages.length - 1" class="w-px flex-1 my-1"
              :class="stage.state === 'complete' ? 'bg-gold-400/50' : 'bg-slate-700'" style="min-height: 20px" />
          </div>
          <div class="pb-4">
            <p :class="['text-sm font-medium', stage.state === 'active' ? 'text-gold-200' : 'text-slate-300']">{{ stage.label }}</p>
            <p class="text-xs text-slate-500">{{ stage.caption }}</p>
          </div>
        </div>
      </div>
    </div>

    <p class="relative z-10 text-xs text-slate-500 tracking-wide animate-fade-in-up" style="animation-delay: 0.3s">
      {{ $t('auth.locationTag') }}
    </p>
  </div>
  
  <svg width="0" height="0" class="absolute">
    <defs>
      <clipPath id="hal-hero-curve" clipPathUnits="objectBoundingBox">
        <path d="M0,0 L0.92,0 C1.05,0.33 0.82,0.42 0.92,0.7 C0.98,0.85 0.86,0.9 0.9,1 L0,1 Z" />
      </clipPath>
    </defs>
  </svg>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Wheat, ShieldCheck, Landmark, CheckCircle2 } from 'lucide-vue-next'

const { t } = useI18n()

const rotatingMessages = computed(() => [t('auth.tagline'), t('auth.taglineMessage2'), t('auth.taglineMessage3')])
const messageIndex = ref(0)
let messageTimer = null
onMounted(() => {
  messageTimer = setInterval(() => {
    messageIndex.value = (messageIndex.value + 1) % rotatingMessages.value.length
  }, 5000)
})
onUnmounted(() => clearInterval(messageTimer))

const trustStages = computed(() => [
  { label: t('auth.stageVerified'), caption: t('auth.stageVerifiedCaption'), icon: ShieldCheck, state: 'complete' },
  { label: t('auth.stageFinanced'), caption: t('auth.stageFinancedCaption'), icon: Landmark, state: 'active' },
  { label: t('auth.stageSettled'), caption: t('auth.stageSettledCaption'), icon: CheckCircle2, state: 'upcoming' },
])
</script>