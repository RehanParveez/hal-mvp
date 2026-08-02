<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('common.province') }}</label>
    <div class="flex items-center gap-2 mb-3 px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-600">
      <MapPin :size="14" class="text-gray-400" />
      {{ reference.province }}
      <span class="text-xs text-gray-400 ml-auto">{{ $t('common.pilotProvinceNote') }}</span>
    </div>
 
    <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('common.district') }}</label>
    <select :value="modelValue" @change="$emit('update:modelValue', $event.target.value)" required
      :disabled="reference.loadError"
      class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm bg-white
        focus:outline-none focus:ring-2 focus:ring-green-700/20 focus:border-green-700 transition
        disabled:bg-gray-50 disabled:text-gray-400">
      <option value="">{{ $t('common.selectDistrict') }}</option>
      <optgroup v-for="div in reference.districtDivisions" :key="div.division" :label="`${div.division} Division`">
        <option v-for="d in div.districts" :key="d" :value="d">{{ d }}</option>
      </optgroup>
    </select>
 
    <p v-if="reference.loadError" class="text-xs text-red-600 mt-1.5 flex items-center gap-1">
      <AlertCircle :size="12" class="flex-shrink-0" />
      {{ $t('common.districtLoadError') }}
      <button type="button" @click="reference.fetchIfNeeded()" class="underline hover:text-red-700">
        {{ $t('common.retry') }}
      </button>
    </p>
  </div>
</template>
 
<script setup>
import { onMounted } from 'vue'
import { MapPin, AlertCircle } from 'lucide-vue-next'
import { useReferenceStore } from '@/stores/reference.js'
 
defineProps({ modelValue: { type: String, default: '' } })
defineEmits(['update:modelValue'])
const reference = useReferenceStore()
onMounted(() => reference.fetchIfNeeded())
</script>