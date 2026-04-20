# 🧠 1. ¿La salida de la IA debe ser JSON?

👉 **SÍ. 100% SÍ.**

Debe ser algo así:

```json
{
  "widgets": [
    {
      "id": "w1",
      "type": "chart",
      "chartType": "bar",
      "x": "producto",
      "y": "ventas",
      "data": [...],
      "title": "Ventas por producto"
    },
    {
      "id": "w2",
      "type": "insight",
      "content": "El producto más vendido es Casaca"
    }
  ]
}
```

👉 Ese JSON es tu “dashboard state”

---

# 🧠 2. ¿Guardar ese JSON en proyecto?

👉 **SÍ, excelente decisión**

Agrega algo como:

```sql
dashboard_config JSONB
```

en `proyecto`

---

💥 Ventajas:

* persistencia
* no recalculas siempre
* puedes editar / iterar

---

# 🚀 Ahora sí: PROMPT COMPLETO (3 fases)

Este prompt está diseñado para que el agente construya esto bien, sin sobrecomplicar.

---

## 🧠 PROMPT

````text
Vamos a implementar la funcionalidad de análisis con inteligencia artificial dentro del dashboard.

El sistema ya permite:
- subir archivos Excel
- procesarlos y almacenarlos en PostgreSQL
- visualizar tablas en el frontend

Ahora queremos construir la capa de análisis.

---

# 🧩 OBJETIVO GENERAL

Agregar una pestaña "Análisis" dentro de la vista del proyecto, donde el usuario pueda generar un dashboard dinámico usando IA.

Este dashboard debe incluir:
- gráficos generados automáticamente
- insights en texto
- estructura dinámica

La IA NO debe generar código.
Debe generar un JSON estructurado que el frontend renderizará.

---

# 🧱 FASE 1: UI + ESTRUCTURA BASE

## Frontend

Dentro de la vista de proyecto:

1. Implementar tabs:
   - "Datos"
   - "Análisis"

2. La pestaña "Datos" mantiene lo actual:
   - tablas
   - upload

3. La pestaña "Análisis":
   - estado vacío inicial
   - mensaje:
     "Convierte tus datos en insights con IA"
   - botón:
     "Generar dashboard con IA"

4. Estados:
   - empty
   - loading
   - generado

---

## Backend

Agregar campo en proyecto:

- dashboard_config (JSONB)

---

# 🧠 FASE 2: GENERACIÓN DE DASHBOARD CON IA

## Endpoint

POST /projects/{project_id}/generate-dashboard (esto es una idea inicial, puedes ajustarlo)

---

## Flujo

1. Obtener tablas del proyecto
2. Analizar columnas (tipo: string, number, date)
3. Usar tools:

- get_columns
- get_sample
- aggregate
- join_tables

y mas si es necesario para entender los datos

4. Construir contexto para IA

---

## IA debe devolver:

```json
{
  "widgets": [
    {
      "type": "chart",
      "chartType": "bar | line | pie",
      "x": "column",
      "y": "column",
      "data": [],
      "title": "string"
    },
    {
      "type": "insight",
      "content": "string"
    }
  ]
}
````

---

## Backend

* guardar JSON en proyecto.dashboard_config
* retornar JSON al frontend

---

## Frontend

Render dinámico:

* ChartCard → usa ECharts y vue-echarts
* InsightCard → texto

Crear función tipo:

function renderWidget(widget)

---

# 🎨 FASE 3: DASHBOARD DINÁMICO

## UI

Renderizar widgets en grid:

* lista de widgets
* cada uno en card

---

## A futuro

* usar vue-grid-layout o gridstack
* permitir:

  * mover widgets
  * redimensionar

---

## Reglas

* máximo 3–5 gráficos inicialmente
* UI limpia
* no saturar
* contenido valioso
---

# 🧠 BUENAS PRÁCTICAS

* fallback si IA falla
* no confiar en datos inválidos
* manejar loading states
* evitar lógica compleja en frontend

---

# 🚀 FUTURO (NO IMPLEMENTAR AÚN)

Agregar un chat pequeño en la pestaña de análisis que permita:

* hacer preguntas sobre los datos
* modificar el dashboard
* agregar o quitar gráficos

Ejemplo:
"muéstrame ventas por región"

El chat reutilizará las mismas tools del agente.

---

# 🎯 OBJETIVO FINAL

El usuario:

1. sube un Excel
2. entra a "Análisis"
3. hace clic en "Generar con IA"
4. obtiene:

   * gráficos relevantes
   * insights automáticos

El sistema debe sentirse:

* inteligente
* dinámico
* útil para toma de decisiones

```
