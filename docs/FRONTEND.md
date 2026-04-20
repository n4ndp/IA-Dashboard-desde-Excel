# FRONTEND — Vue 3, Estado Reactivo y Render Dinámico de Dashboards

## 1) Visión General

El frontend implementa una SPA en:

- **Vue 3** (Composition API + `<script setup>`)
- **TypeScript**
- **TailwindCSS 4**
- **ECharts 6 + vue-echarts**
- **Vue Router 4**

Objetivo principal:
- visualizar datasets y dashboards IA,
- permitir iteración por chat,
- mantener consistencia visual y UX fluida.

---

## 2) Estructura del Proyecto

```text
ui/src/
├── views/
│   ├── LoginView.vue
│   ├── ProjectsView.vue
│   ├── ProjectNewView.vue
│   └── DashboardView.vue
│
├── components/
│   ├── analysis/
│   │   ├── AnalisisTab.vue
│   │   ├── DashboardRenderer.vue
│   │   ├── ChartWidget.vue
│   │   └── InsightWidget.vue
│   ├── base/
│   │   ├── AppButton.vue
│   │   ├── AppCard.vue
│   │   ├── AppInput.vue
│   │   └── AppFileUpload.vue
│   ├── layout/
│   │   ├── AppHeader.vue
│   │   └── AppLayout.vue
│   └── ...
│
├── composables/
│   ├── useDashboard.ts
│   ├── useToast.ts
│   ├── useTableCollapse.ts
│   ├── useUser.ts
│   └── useSkeleton.ts
│
├── services/
│   ├── api.ts
│   └── endpoints.ts
│
├── router/
│   └── index.ts
│
└── types/
    └── index.ts
```

---

## 3) Gestión del Estado y Componentes Clave

### 3.1 `DashboardView.vue` + `AnalisisTab.vue`

`DashboardView.vue` es la vista principal del proyecto y separa dos tabs:

- **Datos**: upload incremental + tablas del proyecto
- **Análisis**: render del dashboard IA

`AnalisisTab.vue` encapsula una máquina de estados:

```text
empty -> loading -> generated | error
```

y delega lógica a `useDashboard(...)`.

### 3.2 `useDashboard.ts` como fuente de verdad

Responsabilidades:

- mantiene `state`, `widgets`, `errorMessage`.
- `generate()`: llama `/generate-dashboard`.
- `iterate(prompt)`: llama `/chat` con `current_dashboard`.
- en errores de iteración: restaura widgets previos (rollback).

Patrón de resiliencia aplicado en iteración:

1. snapshot `previousWidgets`
2. request API
3. validar respuesta (`data.widgets` array)
4. si falla: rollback + `errorMessage`

### 3.3 Render dinámico de widgets

`DashboardRenderer.vue` filtra por tipo:

- `kpi`
- `chart`
- `insight`

y los renderiza en grids separados.

### 3.4 `ChartWidget.vue` e `InsightWidget.vue`

`ChartWidget.vue` traduce JSON de widgets a opciones de ECharts y soporta:

- tipos: `bar`, `line`, `pie`, `scatter`
- variantes: `stacked`, `horizontal`, `area`, `doughnut`, `histogram`
- fallback de paletas cuando falta `colorPalette`

`InsightWidget.vue` renderiza insights con severidad (`positive`, `negative`, `warning`, `info`) y acentos visuales.

---

## 4) Flujo de Interacción — Chat Híbrido

El frontend implementa edición iterativa de dashboards ya generados.

### Flujo completo

1. Usuario escribe prompt en overlay flotante (`AnalisisTab.vue`).
2. `handleChatSubmit()` valida input y activa `chatLoading`.
3. Llama `iterate(prompt)` en `useDashboard.ts`.
4. `iterate()` invoca `chatDashboard(...)` en `services/endpoints.ts`.
5. Request enviado:

```json
{
  "prompt": "cambiar colores del gráfico",
  "current_dashboard": {
    "widgets": [ ...estado actual... ]
  }
}
```

6. En éxito:
   - reemplaza `widgets` reactivos,
   - actualiza bubble con `resumen_ejecutivo`.

7. En error:
   - mantiene dashboard anterior,
   - muestra toast con `useToast`.

### ¿Por qué “híbrido”?

Porque combina:

- **estado local UX** (input, spinner, expand/minimize),
- **estado de dominio en composable** (`widgets`, `errorMessage`),
- **backend iterativo** que usa JSON actual para modificar incrementalmente.

Esto evita re-procesar todo el dataset para cambios meramente visuales.

---

## 5) Estilos y Componentes Base

### Tailwind + Design Tokens

El sistema visual usa clases utilitarias (`bg-surface-*`, `text-*`, `border-*`) para dark theme consistente.

Se reutilizan utilidades como:
- `.input`
- `.spinner-sm`
- `.animate-fade-in`
- `.animate-slide-up`

### Convención `App*`

Componentes base reutilizables con prefijo:

- `AppButton`
- `AppCard`
- `AppInput`
- `AppFileUpload`
- `AppHeader`

Beneficios:
- consistencia de UX,
- reducción de duplicación,
- control centralizado de variantes visuales.

---

## 6) Servicios y Tipado

### `services/api.ts`

Wrapper HTTP con:

- parseo uniforme de errores,
- `ApiError(status, detail)`,
- soporte JSON y `FormData`,
- fallback de red controlado.

### `services/endpoints.ts`

Single source of truth para endpoints tipados.

Incluye `chatDashboard(...)`:

```ts
chatDashboard(userId, projectId, prompt, currentDashboard)
```

### `types/index.ts`

Modela contrato de widgets:

- `KpiWidgetData`
- `ChartWidgetData`
- `InsightWidgetData`
- `DashboardWidgetMap`

Esto permite render seguro y mantenible sin castings frágiles en componentes.

---

## 7) Routing y Guards

`router/index.ts` define rutas:

- `/` login
- `/u/:userId/p`
- `/u/:userId/p/new`
- `/u/:userId/p/:projectId`

Guard principal:

- si no hay `user_id` en `localStorage`, redirige a `/`.
- si hay mismatch entre `user_id` guardado y URL, corrige automáticamente.

---

## 8) Puntos de Evolución Recomendados

1. Migrar `generate()` de `fetch` raw a `request()` para homogeneidad total.
2. Agregar tests de componentes para `AnalisisTab` y `useDashboard`.
3. Añadir soporte a historial de iteraciones en chat (si negocio lo requiere).
4. Exponer `resumen_ejecutivo` también como panel persistente en UI.
