// ── main.ts ──
// App entry: createApp + router mount, import design system, ECharts tree-shaking.

import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

// ── ECharts tree-shaking setup ──
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

createApp(App).use(router).mount('#app')
