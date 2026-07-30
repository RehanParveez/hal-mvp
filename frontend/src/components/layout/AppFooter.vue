<template>
  <footer class="bg-slate-950 text-slate-300 mt-auto">
    <div class="content-container py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div class="md:col-span-2">
          <div class="flex items-center gap-2 mb-2">
            <Wheat :size="20" class="text-gold-400" />
            <span class="text-xl font-display font-semibold text-white">Hal</span>
          </div>
          <p class="text-sm text-slate-400 max-w-xs">{{ $t('footer.tagline') }}</p>
        </div>

        <div>
          <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">{{ $t('footer.support') }}</p>
          <ul class="space-y-2 text-sm">
            <li><a href="tel:+924800000000" class="hover:text-white transition-colors">+92 48 0000000</a></li>
            <li><a href="mailto:support@hal.pk" class="hover:text-white transition-colors">support@hal.pk</a></li>
          </ul>
        </div>
      </div>
      <div class="border-t border-slate-800 mt-8 pt-6 text-xs text-slate-500 flex justify-between flex-wrap gap-2">
        <span>© {{ new Date().getFullYear() }} Hal · Punjab, Pakistan</span>
        <span>{{ $t('footer.builtFor') }}</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { Wheat } from 'lucide-vue-next'
</script>