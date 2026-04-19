// ── main.ts ──
// App entry: createApp + router mount, import design system.

import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

createApp(App).use(router).mount('#app')
