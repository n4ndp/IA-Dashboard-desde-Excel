<script setup lang="ts">
// ── DeleteConfirmModal ──
// Teleported confirmation modal for project deletion.

import AppButton from './base/AppButton.vue'

defineProps<{
  projectName: string
  loading?: boolean
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('cancel')">
      <div class="modal-container animate-fade-in w-full max-w-sm">
        <div class="modal-body text-center">
          <h2 class="mb-1 text-lg font-bold text-text-primary">
            Eliminar proyecto
          </h2>
          <p class="text-sm text-text-muted">
            ¿Estás seguro de que quieres eliminar
            <span class="font-medium text-text-primary">"{{ projectName }}"</span>?
            Esta acción no se puede deshacer.
          </p>
        </div>

        <div class="modal-footer">
          <AppButton variant="secondary" size="md" @click="$emit('cancel')">
            Cancelar
          </AppButton>
          <AppButton variant="danger" size="md" :loading="loading" @click="$emit('confirm')">
            Eliminar
          </AppButton>
        </div>
      </div>
    </div>
  </Teleport>
</template>
