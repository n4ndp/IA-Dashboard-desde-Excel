<script setup lang="ts">
// ── AppButton ──
// Reusable button: 4 variants × 3 sizes, loading spinner, disabled state.

interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false,
})

defineEmits<{
  click: []
}>()
</script>

<template>
  <button
    :class="[
      'btn',
      `btn-${size}`,
      `btn-${variant}`,
    ]"
    :disabled="disabled || loading"
    @click="$emit('click')"
  >
    <span v-if="loading" class="spinner-sm" />
    <slot />
  </button>
</template>
