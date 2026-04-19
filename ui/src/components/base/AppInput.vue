<script setup lang="ts">
// ── AppInput ──
// Text input with v-model support, error display, and validation.

interface Props {
  modelValue?: string
  placeholder?: string
  type?: string
  disabled?: boolean
  error?: string
}

withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '',
  type: 'text',
  disabled: false,
  error: '',
})

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div>
    <input
      :value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="['input', { 'input-error': error }]"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <p v-if="error" class="mt-1 text-xs text-danger">
      {{ error }}
    </p>
  </div>
</template>
