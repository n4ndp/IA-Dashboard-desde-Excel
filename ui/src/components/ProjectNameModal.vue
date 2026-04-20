<script setup lang="ts">
// ── ProjectNameModal ──
// Teleported modal for entering a project name during upload.

import { ref } from 'vue'
import AppButton from './base/AppButton.vue'
import AppInput from './base/AppInput.vue'

const props = withDefaults(defineProps<{
  defaultName: string
  loading?: boolean
}>(), {
  loading: false,
})

const emit = defineEmits<{
  confirm: [name: string]
  cancel: []
}>()

const projectName = ref(props.defaultName)

function handleConfirm() {
  if (!projectName.value.trim()) return
  emit('confirm', projectName.value.trim())
}
</script>

<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('cancel')">
      <div class="modal-container animate-fade-in w-full max-w-sm">
        <div class="modal-header">
          <h2 class="text-lg font-bold text-text-primary">Nombre del proyecto</h2>
          <p class="mt-1 text-sm text-text-muted">
            Elige un nombre para tu proyecto
          </p>
        </div>

        <div class="modal-body">
          <AppInput
            v-model="projectName"
            placeholder="Nombre del proyecto..."
            @keydown.enter="handleConfirm"
            @keydown.escape="$emit('cancel')"
          />
        </div>

        <div class="modal-footer">
          <AppButton variant="secondary" size="md" @click="$emit('cancel')">
            Cancelar
          </AppButton>
          <AppButton
            variant="primary"
            size="md"
            :loading="loading"
            :disabled="!projectName.trim() || loading"
            @click="handleConfirm"
          >
            Crear
          </AppButton>
        </div>
      </div>
    </div>
  </Teleport>
</template>
