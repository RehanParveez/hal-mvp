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

        <div v-if="quickLinks.length">
          <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">{{ $t('footer.quickLinks') }}</p>
          <ul class="space-y-2 text-sm">
            <li v-for="link in quickLinks" :key="link.labelKey">
              <router-link v-if="link.isRoute" :to="link.target" class="hover:text-white transition-colors">
                {{ $t(`nav.${link.labelKey}`) }}
              </router-link>
              <a v-else :href="link.target" class="hover:text-white transition-colors">
                {{ $t(`nav.${link.labelKey}`) }}
              </a>
            </li>
          </ul>
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
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { Wheat } from 'lucide-vue-next'

const auth = useAuthStore()

const ROLE_LINKS = {
  smallholder: [
    { labelKey: 'escrow', target: '#escrow-section', isRoute: false },
    { labelKey: 'myLoans', target: '#loan-section', isRoute: false },    
    { labelKey: 'contracts', target: '#contracts-section', isRoute: false },
  ],
  tenant: [
    { labelKey: 'escrow', target: '#escrow-section', isRoute: false },
    { labelKey: 'myLoans', target: '#loan-section', isRoute: false },   
    { labelKey: 'contracts', target: '#contracts-section', isRoute: false },
  ],
  landowner: [
    { labelKey: 'landParcels', target: '#parcels-section', isRoute: false },
    { labelKey: 'agreements', target: '#agreements-section', isRoute: false },
  ],
  bank: [
    { labelKey: 'settlements', target: '#settlements-section', isRoute: false },
  ],
  factory: [
    { labelKey: 'deliveries', target: '#deliveries-section', isRoute: false },
    { labelKey: 'settlements', target: '#settlements-section', isRoute: false },
  ],
  insurance: [ 
    { labelKey: 'claims', target: '#claims-section', isRoute: false },
    { labelKey: 'policies', target: '#policies-section', isRoute: false },
  ],
  afo: [ 
    { labelKey: 'cropTypes', target: '#crop-types-section', isRoute: false },
    { labelKey: 'spendingCaps', target: '#input-caps-section', isRoute: false },
    { labelKey: 'milestones', target: '#milestones-section', isRoute: false },
  ],
  numberdar: [ 
    { labelKey: 'verificationQueue', target: '/numberdar/queue', isRoute: true },
  ],
}

const quickLinks = computed(() => ROLE_LINKS[auth.user?.role] || [])
</script>