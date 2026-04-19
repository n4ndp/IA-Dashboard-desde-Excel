<script setup lang="ts">
// ── AppCard ──
// Container card: default, bordered, or interactive (hover border change).

interface Props {
  variant?: 'default' | 'bordered' | 'interactive'
}

withDefaults(defineProps<Props>(), {
  variant: 'default',
})
</script>

<template>
  <div
    :class="[
      'rounded-lg',
      {
        'bg-surface-raised border border-border': variant === 'default',
        'bg-surface-raised border border-border-strong': variant === 'bordered',
        'bg-surface-raised border border-border transition-colors hover:border-border-strong cursor-pointer': variant === 'interactive',
      },
    ]"
  >
    <slot />
  </div>
</template>
