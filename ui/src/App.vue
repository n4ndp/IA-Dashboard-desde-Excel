<script setup lang="ts">
// ── App.vue ──
// Root: conditional AppHeader (hidden on login) + RouterView.

import { useRoute } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'

const route = useRoute()
</script>

<template>
  <div class="min-h-screen bg-surface-base">
    <AppHeader v-if="route.path !== '/'" />
    <RouterView />
  </div>
</template>
