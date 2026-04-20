# FRONTEND — Vue 3, Estado Reactivo y Render Dinámico de Dashboards

## 1) Visión General

El frontend implementa una SPA en:

- **Vue 3** (Composition API + `<script setup>`)
- **TypeScript**
- **TailwindCSS 4**
- **ECharts 6 + vue-echarts**
- **Vue Router 4**

Objetivos:
- Visualizar datasets y dashboards IA.
- Permitir iteración por chat para modificar dashboards.
- Mantener consistencia visual y UX fluida en dark theme.

---

## 2) Estructura del Proyecto

```text
ui/src/
├── views/
│   ├── LoginView.vue          # Ingreso por nombre
│   ├── ProjectsView.vue       # Lista de proyectos
│   ├── ProjectNewView.vue     # Crear proyecto (upload Excel)
│   └── DashboardView.vue      # Vista principal del proyecto
│
├── components/
│   ├── analysis/
│   │   ├── AnalisisTab.vue       # Tab Análisis + chat overlay
│   │   ├── DashboardRenderer.vue # Render de widgets + resumen banner
│   │   ├── ChartWidget.vue       # Gráficos ECharts
│   │   └── InsightWidget.vue     # Insights con severidad
│   ├── base/
│   │   ├── AppButton.vue
│   │   ├── AppCard.vue
│   │   ├── AppInput.vue
│   │   └── AppFileUpload.vue
│   ├── layout/
│   │   ├── AppHeader.vue
│   │   └── AppLayout.vue
│   └── project/
│       ├── ProjectTable.vue      # Tabla expandible
│       └── TableDataModal.vue    # Modal de datos de tabla
│
├── composables/
│   ├── useDashboard.ts        # Estado + lógica del dashboard
│   ├── useToast.ts            # Notificaciones toast
│   ├── useTableCollapse.ts    # Estado de tablas expandibles
│   ├── useUser.ts             # Usuario actual + localStorage
│   └── useSkeleton.ts         # Shimmer loading state
│
├── services/
│   ├── api.ts                 # Wrapper HTTP con error handling
│   └── endpoints.ts           # Endpoints tipados
│
├── router/
│   └── index.ts               # Rutas + guards
│
└── types/
    └── index.ts               # Tipos de widgets y contratos
```

---

## 3) Routing y Guards

### Rutas

| Ruta | Vista | Descripción |
|------|-------|-------------|
| `/` | `LoginView` | Ingreso por nombre |
| `/u/:userId/p` | `ProjectsView` | Lista de proyectos |
| `/u/:userId/p/new` | `ProjectNewView` | Crear proyecto |
| `/u/:userId/p/:projectId` | `DashboardView` | Proyecto con tabs |

### Guard principal (`router/index.ts`)

- Si no hay `user_id` en `localStorage`, redirige a `/`.
- Si hay mismatch entre `user_id` guardado y URL, corrige automáticamente.

---

## 4) Gestión del Estado

### 4.1 `DashboardView.vue` — Vista principal

Separada en dos tabs:

- **Datos**: Upload incremental de Excel + tablas del proyecto con expand/colapsar.
- **Análisis**: Render del dashboard IA + chat iterativo.

Delega toda la lógica a composables — la vista es un componente orquestador delgado.

### 4.2 `useDashboard.ts` — Fuente de verdad del dashboard

Estado reactivo:

```ts
state: Ref<'empty' | 'loading' | 'generated' | 'error'>
widgets: Ref<DashboardWidget[]>
errorMessage: Ref<string>
resumenEjecutivo: Ref<string | null>
```

Operaciones:

| Función | Endpoint | Qué hace |
|---------|----------|----------|
| `generate()` | `/generate-dashboard` | Genera dashboard inicial |
| `iterate(prompt)` | `/chat` | Itera dashboard por chat |

### 4.3 Patrón de resiliencia en iteración

Cuando el usuario envía un mensaje por chat:

1. **Optimistic UI** — el mensaje del usuario aparece instantáneamente en la burbuja.
2. **Snapshot** — se guarda `previousWidgets` antes de llamar a la API.
3. **Request** — se envía `prompt` + `current_dashboard` al endpoint `/chat`.
4. **Éxito** — se reemplazan los widgets con la respuesta, se muestra `action_message` (o `resumen_ejecutivo` como fallback).
5. **Error** — se restaura `previousWidgets` (rollback), se muestra toast con `useToast`.

### 4.4 `resumenEjecutivo`

Se extrae de la respuesta del backend y se muestra como banner en `DashboardRenderer.vue`. Es momentáneo — se muestra al generar/iterar pero no persiste visualmente entre navegaciones.

---

## 5) Componentes Clave

### 5.1 `AnalisisTab.vue` — Tab Análisis + Chat

Máquina de estados: `empty → loading → generated | error`

Incluye el **chat overlay** flotante con:
- Input de texto para prompts.
- Burbujas de chat (usuario + AI).
- Spinner durante carga.
- Botón minimizar/expandir.

El chat implementa **optimistic UI**: el mensaje del usuario aparece inmediatamente antes de recibir la respuesta del backend.

### 5.2 `DashboardRenderer.vue` — Render de widgets

Filtra widgets por tipo y los renderiza en grids separados:

- **KPIs** → grid superior
- **Gráficos** → grid principal (2 columnas)
- **Insights** → grid inferior

Incluye el **banner de resumen ejecutivo** con ícono `FileText` cuando `resumen` está disponible.

### 5.3 `ChartWidget.vue` — Gráficos ECharts

Traduce JSON de widgets a opciones de ECharts:

| Tipo | Variantes |
|------|-----------|
| `bar` | normal, stacked, horizontal |
| `line` | normal, area |
| `pie` | normal, doughnut |
| `scatter` | normal |

Características:
- Fallback de paletas cuando falta `colorPalette`.
- Labels de ejes (`x_label`, `y_label`).
- Responsive via `autoresize`.

### 5.4 `InsightWidget.vue` — Insights con severidad

Renderiza insights con 4 niveles de severidad:
- `positive` (verde)
- `negative` (rojo)
- `warning` (amarillo)
- `info` (azul)

Cada insight muestra emoji + contenido con acento visual según severidad.

---

## 6) Servicios y Tipado

### 6.1 `services/api.ts` — Wrapper HTTP

- Parseo uniforme de errores.
- `ApiError(status, detail)` custom error class.
- Soporte JSON y `FormData` (para uploads).
- Fallback de red controlado.

### 6.2 `services/endpoints.ts` — Endpoints tipados

Single source of truth para todos los endpoints:

```ts
// Ejemplos
createProject(userId, formData)
generateDashboard(userId, projectId)
chatDashboard(userId, projectId, prompt, currentDashboard)
```

### 6.3 `types/index.ts` — Contratos de widgets

```ts
interface KpiWidgetData { id, type, label, value, format, trend, trendValue }
interface ChartWidgetData { id, type, chartType, variant, title, data, series, colorPalette }
interface InsightWidgetData { id, type, emoji, content, severity }

// Discriminated union para render seguro
type DashboardWidget = KpiWidgetData | ChartWidgetData | InsightWidgetData

// Config del dashboard con action_message para iteración
interface DashboardConfig {
  widgets: DashboardWidget[]
  resumen_ejecutivo?: string
  action_message?: string
}
```

---

## 7) Estilos y Design System

### TailwindCSS Dark Theme

El sistema visual usa clases utilitarias para dark theme consistente:

- `bg-surface-*` para fondos escalonados
- `text-*` para jerarquía de texto
- `border-*` para bordes sutiles

### Utilidades custom

- `.input` — estilo base para inputs
- `.spinner-sm` — spinner pequeño inline
- `.animate-fade-in` — entrada suave
- `.animate-slide-up` — slide desde abajo

### Convención `App*`

Componentes base reutilizables con prefijo `App`:
- Consistencia de UX.
- Reducción de duplicación.
- Control centralizado de variantes visuales.

---

## 8) Chat Iterativo — Flujo Detallado

```text
Usuario escribe prompt en overlay
       │
       ▼
AnalisisTab.handleChatSubmit()
  ├── chatInput → bubble de usuario (optimistic)
  ├── chatLoading = true → spinner en bubble AI
  │
  ▼
useDashboard.iterate(prompt)
  ├── snapshot previousWidgets
  ├── POST /chat { prompt, current_dashboard: { widgets } }
  │
  ├── Éxito:
  │   ├── widgets = response.widgets
  │   ├── resumenEjecutivo = response.resumen_ejecutivo
  │   ├── action_message → se muestra en bubble AI
  │   └── resumen banner actualizado
  │
  └── Error:
      ├── widgets = previousWidgets (rollback)
      ├── errorMessage → toast via useToast
      └── Dashboard visual sin cambios
```

### ¿Por qué "híbrido"?

Combina:
- **Estado local UX** (input, spinner, expand/minimize del overlay).
- **Estado de dominio en composable** (`widgets`, `errorMessage`, `resumenEjecutivo`).
- **Backend iterativo** que usa JSON actual para modificar incrementalmente.

Esto evita re-procesar todo el dataset para cambios meramente visuales.

---

## 9) Puntos de Evolución

1. Migrar `generate()` de `fetch` raw a `request()` para homogeneidad total con `iterate()`.
2. Agregar tests de componentes para `AnalisisTab` y `useDashboard`.
3. Historial de iteraciones en chat (persistencia de conversación).
4. Markdown rendering en `resumen_ejecutivo` y `action_message`.
5. Soporte para más tipos de gráfico (radar, treemap, gauge).
