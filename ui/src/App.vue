<script setup lang="ts">
import { useRoute } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'

const route = useRoute()
</script>

<template>
  <div class="min-h-screen bg-midnight-950">
    <AppHeader v-if="route.path !== '/'" />
    <RouterView />
  </div>
</template>
