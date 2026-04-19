<script setup lang="ts">
// ── App.vue ──
// Root: conditional AppHeader (hidden on login) + ToastContainer + RouterView.

import { useRoute } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import ToastContainer from './components/ToastContainer.vue'

const route = useRoute()
</script>

<template>
  <div class="min-h-screen bg-surface-base">
    <AppHeader v-if="route.path !== '/'" />
    <ToastContainer />
    <RouterView />
  </div>
</template>
