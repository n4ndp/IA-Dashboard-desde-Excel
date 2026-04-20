# Fase 2: AI Dashboard Generation — Spec de Planificación

> Documento de referencia para la implementación de la generación de dashboards con IA.
> Define gráficos, KPIs, insights, tools, agente loop y ejemplos de salida.

---

## 1. Gráficos Soportados

### 1.1 Bar Chart

**Cuándo usarlo**: Existe una columna categórica (string) y una métrica numérica.

**Casos de uso**:
- Ventas por producto
- Ingresos por región
- Cantidad por categoría

**Parámetros base**:
```json
{
  "type": "chart",
  "chartType": "bar",
  "title": "Ventas por producto",
  "x": "producto",
  "y": "ventas",
  "data": [{ "name": "Casaca", "value": 5000 }, { "name": "Zapatos", "value": 3200 }]
}
```

**Variantes**:

| Variante | Descripción | Parámetro extra | Ejemplo |
|----------|-------------|-----------------|---------|
| **Grouped** (default) | Barras lado a lado por categoría | Ninguno (default) | "Trabaja/No trabaja" por sexo |
| **Stacked** | Barras apiladas mostrando composición | `"stack": true, "series": [...]` | "Trabaja/No trabaja desglosado por sexo, una barra apilada" |
| **Horizontal** | Barras horizontales (cuando categorías son largas) | `"orientation": "horizontal"` | "Descripción de productos (texto largo)" |

**Ejemplo stacked**:
```json
{
  "type": "chart",
  "chartType": "bar",
  "variant": "stacked",
  "title": "Empleados por departamento y sexo",
  "x": "departamento",
  "series": [
    { "name": "Hombre", "data": [{ "name": "Ventas", "value": 30 }, { "name": "IT", "value": 25 }] },
    { "name": "Mujer", "data": [{ "name": "Ventas", "value": 21 }, { "name": "IT", "value": 18 }] }
  ]
}
```

**Ejemplo horizontal**:
```json
{
  "type": "chart",
  "chartType": "bar",
  "variant": "horizontal",
  "title": "Ventas por categoría de producto",
  "x": "categoria",
  "y": "ventas",
  "data": [{ "name": "Electrónica y gadgets varios", "value": 15000 }, { "name": "Ropa y accesorios", "value": 12000 }]
}
```

---

### 1.2 Line Chart

**Cuándo usarlo**: Existe una columna de tipo fecha (date) y una métrica numérica.

**Casos de uso**:
- Ventas por fecha
- Evolución de ingresos en el tiempo
- Crecimiento mensual

**Parámetros base**:
```json
{
  "type": "chart",
  "chartType": "line",
  "title": "Ventas por fecha",
  "x": "fecha",
  "y": "ventas",
  "data": [{ "name": "2024-01", "value": 12000 }, { "name": "2024-02", "value": 15000 }]
}
```

**Variantes**:

| Variante | Descripción | Parámetro extra | Ejemplo |
|----------|-------------|-----------------|---------|
| **Multi-line** | Varias líneas (una por categoría) | `"series": [...]` | "Ventas de cada producto en el tiempo" |
| **Area** | Área bajo la línea (volumen acumulado) | `"areaStyle": {}` | "Revenue acumulado mensual" |

**Ejemplo multi-line**:
```json
{
  "type": "chart",
  "chartType": "line",
  "variant": "multi",
  "title": "Ventas por producto en el tiempo",
  "x": "fecha",
  "series": [
    { "name": "Casaca", "data": [{ "name": "Ene", "value": 5000 }, { "name": "Feb", "value": 6000 }] },
    { "name": "Zapatos", "data": [{ "name": "Ene", "value": 3200 }, { "name": "Feb", "value": 4100 }] }
  ]
}
```

**Ejemplo area**:
```json
{
  "type": "chart",
  "chartType": "line",
  "variant": "area",
  "title": "Revenue acumulado mensual",
  "x": "fecha",
  "y": "revenue",
  "areaStyle": {},
  "data": [{ "name": "Ene", "value": 10000 }, { "name": "Feb", "value": 25000 }, { "name": "Mar", "value": 42000 }]
}
```

---

### 1.3 Pie Chart

**Cuándo usarlo**: Pocas categorías (máximo 5-6), se quiere mostrar distribución porcentual.

**Casos de uso**:
- Distribución de ventas por categoría
- Participación de mercado
- Proporción de tipos de cliente

**Parámetros base**:
```json
{
  "type": "chart",
  "chartType": "pie",
  "title": "Distribución por categoría",
  "data": [
    { "name": "Ropa", "value": 45 },
    { "name": "Electrónica", "value": 30 },
    { "name": "Hogar", "value": 25 }
  ]
}
```

**Regla**: NO usar pie chart si hay más de 6-7 categorías. En ese caso, usar bar chart.

**Variantes**:

| Variante | Descripción | Parámetro extra | Ejemplo |
|----------|-------------|-----------------|---------|
| **Doughnut** | Pie con hueco central (más limpio visualmente) | `"variant": "doughnut"` | "Distribución de gastos por área" |

**Ejemplo doughnut**:
```json
{
  "type": "chart",
  "chartType": "pie",
  "variant": "doughnut",
  "title": "Distribución de gastos por área",
  "data": [
    { "name": "Marketing", "value": 35 },
    { "name": "Operaciones", "value": 40 },
    { "name": "RRHH", "value": 15 },
    { "name": "IT", "value": 10 }
  ]
}
```

---

## 2. KPIs

**Siempre incluir al menos 1-2 KPIs por dashboard.**

### Tipos de KPI

| Tipo | Operación | Caso de uso | Formato |
|------|-----------|-------------|---------|
| **Total (SUM)** | Suma total | "Total ventas: $150,000" | `currency` |
| **Promedio (AVG)** | Promedio | "Ticket promedio: $450" | `currency` |
| **Conteo (COUNT)** | Cantidad de registros | "Total registros: 1,230" | `number` |
| **Máximo (MAX)** | Valor máximo | "Venta más alta: $25,000" | `currency` |
| **Mínimo (MIN)** | Valor mínimo | "Venta más baja: $50" | `currency` |
| **Porcentaje** | Ratio sobre total | "% clientes recurrentes: 65%" | `percent` |
| **Tendencia** | Comparación temporal | "↑ +12% vs mes anterior" | `trend` |

### Estructura JSON

```json
{
  "id": "kpi1",
  "type": "kpi",
  "label": "Total Ventas",
  "value": 150000,
  "format": "currency",
  "prefix": "$",
  "trend": "up",
  "trendValue": "+12%"
}
```

### Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | string | ✅ | Identificador único |
| `type` | "kpi" | ✅ | Siempre "kpi" |
| `label` | string | ✅ | Título del KPI |
| `value` | number | ✅ | Valor numérico |
| `format` | string | ✅ | "currency" \| "number" \| "percent" |
| `prefix` | string | ❌ | Ej: "$", "€" |
| `suffix` | string | ❌ | Ej: "unidades", "clientes" |
| `trend` | string | ❌ | "up" \| "down" \| "neutral" |
| `trendValue` | string | ❌ | Ej: "+12%", "-5%" |

### Ejemplos

```json
{ "id": "kpi1", "type": "kpi", "label": "Total Ventas", "value": 150000, "format": "currency", "prefix": "$", "trend": "up", "trendValue": "+12%" }
{ "id": "kpi2", "type": "kpi", "label": "Ticket Promedio", "value": 450.5, "format": "currency", "prefix": "$" }
{ "id": "kpi3", "type": "kpi", "label": "Total Registros", "value": 1230, "format": "number", "suffix": "registros" }
{ "id": "kpi4", "type": "kpi", "label": "% Clientes Recurrentes", "value": 65, "format": "percent", "trend": "up", "trendValue": "+3%" }
{ "id": "kpi5", "type": "kpi", "label": "Venta Máxima", "value": 25000, "format": "currency", "prefix": "$" }
```

---

## 3. Insights

Los insights son observaciones textuales generadas por la IA sobre los datos.

### Estructura JSON

```json
{
  "id": "i1",
  "type": "insight",
  "emoji": "🔥",
  "content": "El producto más vendido es Casaca con 5,000 unidades",
  "severity": "positive"
}
```

### Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | string | ✅ | Identificador único |
| `type` | "insight" | ✅ | Siempre "insight" |
| `emoji` | string | ✅ | Emoji que representa el insight |
| `content` | string | ✅ | Texto descriptivo del insight |
| `severity` | string | ✅ | Tono/severidad del insight |

### Severities

| Severity | Cuándo | Color frontend | Ejemplo |
|----------|--------|----------------|---------|
| `positive` | Algo bueno | 🟢 Verde | "Las ventas subieron un 20% este mes" |
| `negative` | Algo malo | 🔴 Rojo | "Se perdió un 15% de clientes activos" |
| `warning` | Atención | 🟡 Amarillo | "El stock del producto X está por debajo del mínimo" |
| `info` | Informativo, neutro | 🔵 Azul | "El producto más vendido es Casaca con 5,000 unidades" |

### Reglas
- Siempre incluir 2-4 insights por dashboard
- Evitar insights obvios ("La tabla tiene datos")
- Priorizar insights accionables
- Mezclar severities (no todos info)

### Ejemplos

```json
{ "id": "i1", "type": "insight", "emoji": "🔥", "content": "El producto más vendido es Casaca con 5,000 unidades", "severity": "positive" }
{ "id": "i2", "type": "insight", "emoji": "📉", "content": "Las ventas cayeron un 15% en marzo respecto a febrero", "severity": "negative" }
{ "id": "i3", "type": "insight", "emoji": "⚠️", "content": "El 80% de los ingresos viene de solo 3 productos", "severity": "warning" }
{ "id": "i4", "type": "insight", "emoji": "📊", "content": "El ticket promedio aumentó de $450 a $520 en el último trimestre", "severity": "info" }
```

---

## 4. Tools para IA — SQL Seguro

La IA NO escribe SQL directamente. La IA llama a tools con parámetros, y el service genera SQL parametrizado contra las tablas del proyecto.

### Principio de seguridad

```
IA pide: aggregate(table_id=5, column="precio", operation="SUM")
                        ↓
Service VALIDA: tabla_id=5 → ¿pertenece al proyecto del usuario? → SÍ → ejecuta
                        ↓
SQL generado: SELECT SUM((data->>'precio')::numeric) FROM fila WHERE tabla_id = 5
```

**Jamás** la IA escribe SQL crudo. Todos los queries son parametrizados y validados contra las tablas del proyecto.

### 4.1 get_columns

Lista las columnas de una tabla con sus tipos inferidos.

```json
{
  "name": "get_columns",
  "description": "Obtiene las columnas de una tabla con sus nombres y tipos (string, number, date)",
  "parameters": {
    "table_id": "int — ID de la tabla"
  },
  "returns": [
    { "name": "producto", "type": "string" },
    { "name": "precio", "type": "number" },
    { "name": "fecha", "type": "date" }
  ]
}
```

**SQL interno**:
```sql
SELECT nombre, tipo FROM columna WHERE tabla_id = :table_id
```

---

### 4.2 get_sample

Obtiene una muestra de N filas de una tabla.

```json
{
  "name": "get_sample",
  "description": "Obtiene una muestra de filas de una tabla para entender los datos",
  "parameters": {
    "table_id": "int — ID de la tabla",
    "limit": "int — cantidad de filas (default: 50, max: 200)"
  },
  "returns": [
    { "producto": "Casaca", "precio": 150, "fecha": "2024-01-15" },
    { "producto": "Zapatos", "precio": 200, "fecha": "2024-02-20" }
  ]
}
```

**SQL interno**:
```sql
SELECT data FROM fila WHERE tabla_id = :table_id ORDER BY orden LIMIT :limit
```

---

### 4.3 count_rows

Cuenta la cantidad total de filas de una tabla.

```json
{
  "name": "count_rows",
  "description": "Cuenta el total de filas en una tabla",
  "parameters": {
    "table_id": "int — ID de la tabla"
  },
  "returns": { "count": 1230 }
}
```

**SQL interno**:
```sql
SELECT COUNT(*) FROM fila WHERE tabla_id = :table_id
```

---

### 4.4 aggregate

Aplica una función de agregación sobre una columna numérica.

```json
{
  "name": "aggregate",
  "description": "Calcula una agregación (SUM, AVG, MAX, MIN, COUNT) sobre una columna numérica",
  "parameters": {
    "table_id": "int — ID de la tabla (o virtual_table_id)",
    "column": "string — nombre de la columna",
    "operation": "string — SUM | AVG | MAX | MIN | COUNT"
  },
  "returns": { "operation": "SUM", "column": "precio", "value": 150000.50 }
}
```

**SQL interno**:
```sql
SELECT SUM((data->>'precio')::numeric) FROM fila WHERE tabla_id = :table_id
```

---

### 4.5 group_by

Agrupa por una columna categórica y aplica una agregación sobre otra columna.

```json
{
  "name": "group_by",
  "description": "Agrupa filas por una columna categórica y calcula una agregación sobre una columna numérica",
  "parameters": {
    "table_id": "int — ID de la tabla (o virtual_table_id)",
    "group_column": "string — columna para agrupar (categórica)",
    "agg_column": "string — columna para agregar (numérica)",
    "operation": "string — SUM | AVG | MAX | MIN | COUNT"
  },
  "returns": [
    { "group": "Casaca", "value": 5000 },
    { "group": "Zapatos", "value": 3200 }
  ]
}
```

**SQL interno**:
```sql
SELECT data->>'producto' AS group_val, SUM((data->>'precio')::numeric) AS agg_val
FROM fila
WHERE tabla_id = :table_id
GROUP BY data->>'producto'
ORDER BY agg_val DESC
```

---

### 4.6 filter

Filtra filas por una condición sobre una columna.

```json
{
  "name": "filter",
  "description": "Filtra filas de una tabla por una condición sobre una columna",
  "parameters": {
    "table_id": "int — ID de la tabla (o virtual_table_id)",
    "column": "string — columna a filtrar",
    "operator": "string — eq | neq | gt | gte | lt | lte | contains | starts_with",
    "value": "any — valor a comparar"
  },
  "returns": { "filtered_count": 450, "sample": [...] }
}
```

**SQL interno**:
```sql
-- Para operator 'eq':
SELECT data FROM fila WHERE tabla_id = :table_id AND data->>'columna' = :value

-- Para operator 'gte':
SELECT data FROM fila WHERE tabla_id = :table_id AND (data->>'columna')::numeric >= :value

-- Para operator 'contains':
SELECT data FROM fila WHERE tabla_id = :table_id AND data->>'columna' ILIKE '%' || :value || '%'
```

---

### 4.7 distinct_values

Obtiene los valores únicos de una columna (para entender cardinalidad).

```json
{
  "name": "distinct_values",
  "description": "Obtiene valores únicos de una columna y su frecuencia",
  "parameters": {
    "table_id": "int — ID de la tabla (o virtual_table_id)",
    "column": "string — nombre de la columna",
    "limit": "int — máx valores a retornar (default: 20)"
  },
  "returns": [
    { "value": "Casaca", "count": 150 },
    { "value": "Zapatos", "count": 120 },
    { "value": "Pantalón", "count": 95 }
  ]
}
```

**SQL interno**:
```sql
SELECT data->>'columna' AS val, COUNT(*) AS cnt
FROM fila
WHERE tabla_id = :table_id
GROUP BY data->>'columna'
ORDER BY cnt DESC
LIMIT :limit
```

---

### 4.8 date_range

Obtiene el rango de fechas de una columna tipo date.

```json
{
  "name": "date_range",
  "description": "Obtiene la fecha mínima y máxima de una columna tipo date",
  "parameters": {
    "table_id": "int — ID de la tabla (o virtual_table_id)",
    "column": "string — nombre de la columna date"
  },
  "returns": { "min": "2024-01-01", "max": "2024-12-31", "span_days": 365 }
}
```

**SQL interno**:
```sql
SELECT MIN(data->>'fecha') AS min_date, MAX(data->>'fecha') AS max_date
FROM fila
WHERE tabla_id = :table_id
```

---

### 4.9 join_tables

Junta dos tablas por una columna en común. Genera una tabla virtual temporal que puede ser usada por las demás tools.

```json
{
  "name": "join_tables",
  "description": "Junta dos tablas por una columna en común, generando una tabla virtual temporal. Las tools posteriores pueden usar el virtual_table_id retornado.",
  "parameters": {
    "left_table_id": "int — ID de la tabla izquierda",
    "right_table_id": "int — ID de la tabla derecha",
    "left_column": "string — columna de la tabla izquierda para el join",
    "right_column": "string — columna de la tabla derecha para el join",
    "join_type": "string — inner | left | right (default: inner)"
  },
  "returns": {
    "virtual_table_id": "v_1",
    "columns": ["producto", "precio", "departamento", "sucursal"],
    "row_count": 450
  }
}
```

**Lógica interna**:
1. Obtener todas las filas de ambas tablas
2. Realizar join en memoria usando pandas (ya instalado)
3. Almacenar resultado en un dict en memoria `{session_id: {virtual_tables: {v_1: DataFrame}}}`
4. Retornar virtual_table_id para uso en tools posteriores

### Flujo de join + tools posteriores

```
IA llama: join_tables(left=3, right=5, left_col="depto_id", right_col="id")
                ↓
Service: genera DataFrame virtual → virtual_table_id = "v_1"
                ↓
IA llama: group_by(table_id="v_1", group="departamento", agg="salario", op="AVG")
                ↓
Service: reconoce "v_1" → busca en virtual tables → ejecuta group_by sobre el DataFrame
                ↓
IA genera widget con los resultados
```

---

## 5. Agent Loop — Cómo funciona la IA

### Diagrama del flujo completo

```
Usuario presiona "Generar dashboard con IA"
        ↓
POST /api/users/{user_id}/projects/{project_id}/generate-dashboard
        ↓
Backend: obtiene tablas del proyecto
        ↓
Backend: construye contexto inicial (tablas, columnas, tipos, samples)
        ↓
Backend: envía a IA con system prompt + tools definidas
        ↓
┌─ AGENT LOOP (max 15 iteraciones, max 10 tool calls, 60s timeout) ──┐
│                                                                      │
│  IA piensa → ¿Necesito más datos?                                   │
│     ↓ SÍ                              ↓ NO                          │
│  Llama tool (function calling)    Genera JSON final                 │
│  Backend ejecuta tool                 ↓                              │
│  Retorna resultado a IA           ┌───FIN───┐                       │
│  IA analiza resultado             │  Salida  │                       │
│  Vuelve a pensar                  └──────────┘                       │
│                                                                      │
│  Si alcanza max iteraciones: forzar generación con lo que tiene      │
│  Si timeout (60s): forzar generación o retornar error               │
└──────────────────────────────────────────────────────────────────────┘
        ↓
Validar JSON contra schema de widgets
        ↓
Guardar en proyecto.dashboard_config (JSONB)
        ↓
Retornar JSON al frontend
        ↓
Frontend renderiza widgets
```

### Parámetros de configuración

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `MAX_ITERATIONS` | 15 | Máximo de vueltas del loop de razonamiento |
| `MAX_TOOL_CALLS` | 10 | Máximo de consultas a la base de datos |
| `TIMEOUT_SECONDS` | 60 | Timeout total para la generación |
| `SAMPLE_LIMIT` | 200 | Máximo de filas en get_sample |
| `MAX_CHARTS` | 5 | Máximo de gráficos en el dashboard generado |
| `MIN_KPIS` | 1 | Mínimo de KPIs obligatorios |
| `MAX_INSIGHTS` | 4 | Máximo de insights generados |

### System Prompt (resumen)

```
Eres un analista de datos experto. Tu trabajo es analizar las tablas del proyecto
y generar un dashboard con widgets (gráficos, KPIs e insights).

REGLAS:
- Máximo 5 gráficos
- Siempre incluir al menos 1-2 KPIs
- Incluir 2-4 insights con emoji y severity
- Si hay fecha → incluir al menos un line chart
- Si hay categoría + número → incluir bar chart
- No usar pie chart si hay más de 6 categorías
- Priorizar claridad sobre complejidad
- Los insights deben ser accionables, no obvios

TOOLS disponibles: get_columns, get_sample, count_rows, aggregate,
                   group_by, filter, distinct_values, date_range, join_tables

OUTPUT: JSON con estructura de widgets válida.
```

### Cuándo termina el loop

| Condición | Qué pasa |
|-----------|----------|
| IA devuelve JSON final | ✅ Éxito — validar y guardar |
| Max iteraciones alcanzadas | ⚠️ Forzar generación con datos disponibles |
| Max tool calls alcanzados | ⚠️ Forzar generación con datos disponibles |
| Timeout (60s) | ❌ Error — retornar lo generado hasta el momento |
| Error en tool | ⚠️ Reintentar o saltar esa tool |
| Error de validación JSON | ⚠️ Pedir a la IA que corrija el formato |

---

## 6. JSON de Salida — Estructura completa

### Schema principal

```json
{
  "widgets": [
    // KPIs (1-2 obligatorios)
    { "id": "kpi1", "type": "kpi", ... },
    { "id": "kpi2", "type": "kpi", ... },

    // Charts (1-5, máximo 5)
    { "id": "w1", "type": "chart", "chartType": "bar", ... },
    { "id": "w2", "type": "chart", "chartType": "line", ... },
    { "id": "w3", "type": "chart", "chartType": "pie", ... },

    // Insights (2-4)
    { "id": "i1", "type": "insight", ... },
    { "id": "i2", "type": "insight", ... }
  ]
}
```

### Orden de renderizado

1. **KPIs** — fila superior (grid-cols-2 o grid-cols-3)
2. **Charts** — grid principal (1-2 columnas)
3. **Insights** — al final, en cards

---

## 7. Ejemplos Completos

### Ejemplo 1: Ventas de productos

**Datos**: Tabla "ventas" con columnas: producto (string), precio (number), cantidad (number), fecha (date), categoría (string)

```json
{
  "widgets": [
    {
      "id": "kpi1",
      "type": "kpi",
      "label": "Total Ventas",
      "value": 156780,
      "format": "currency",
      "prefix": "$",
      "trend": "up",
      "trendValue": "+18%"
    },
    {
      "id": "kpi2",
      "type": "kpi",
      "label": "Ticket Promedio",
      "value": 487.50,
      "format": "currency",
      "prefix": "$",
      "trend": "up",
      "trendValue": "+5%"
    },
    {
      "id": "w1",
      "type": "chart",
      "chartType": "bar",
      "title": "Ventas por Producto",
      "x": "producto",
      "y": "precio",
      "data": [
        { "name": "Casaca", "value": 5000 },
        { "name": "Zapatos", "value": 4200 },
        { "name": "Pantalón", "value": 3800 },
        { "name": "Camisa", "value": 2900 }
      ]
    },
    {
      "id": "w2",
      "type": "chart",
      "chartType": "line",
      "title": "Evolución de Ventas",
      "x": "fecha",
      "y": "precio",
      "data": [
        { "name": "Ene", "value": 12000 },
        { "name": "Feb", "value": 15000 },
        { "name": "Mar", "value": 13200 },
        { "name": "Abr", "value": 18500 },
        { "name": "May", "value": 21000 }
      ]
    },
    {
      "id": "w3",
      "type": "chart",
      "chartType": "pie",
      "variant": "doughnut",
      "title": "Distribución por Categoría",
      "data": [
        { "name": "Ropa", "value": 45 },
        { "name": "Calzado", "value": 30 },
        { "name": "Accesorios", "value": 25 }
      ]
    },
    {
      "id": "i1",
      "type": "insight",
      "emoji": "🔥",
      "content": "Casaca es el producto estrella con $5,000 en ventas, superando al segundo por 19%",
      "severity": "positive"
    },
    {
      "id": "i2",
      "type": "insight",
      "emoji": "📈",
      "content": "Las ventas muestran una tendencia alcista del +18% en los últimos 5 meses",
      "severity": "positive"
    },
    {
      "id": "i3",
      "type": "insight",
      "emoji": "⚠️",
      "content": "Marzo tuvo una caída del 12% respecto a febrero — investigar causas",
      "severity": "warning"
    }
  ]
}
```

---

### Ejemplo 2: Recursos Humanos — Empleados

**Datos**: Tabla "empleados" con columnas: nombre (string), departamento (string), salario (number), sexo (string), fecha_ingreso (date), activo (string)

```json
{
  "widgets": [
    {
      "id": "kpi1",
      "type": "kpi",
      "label": "Total Empleados",
      "value": 243,
      "format": "number",
      "suffix": "empleados"
    },
    {
      "id": "kpi2",
      "type": "kpi",
      "label": "Salario Promedio",
      "value": 4520,
      "format": "currency",
      "prefix": "$"
    },
    {
      "id": "w1",
      "type": "chart",
      "chartType": "bar",
      "variant": "stacked",
      "title": "Empleados por Departamento y Sexo",
      "x": "departamento",
      "series": [
        { "name": "Hombre", "data": [
          { "name": "Ventas", "value": 30 },
          { "name": "IT", "value": 25 },
          { "name": "RRHH", "value": 10 },
          { "name": "Finanzas", "value": 15 }
        ]},
        { "name": "Mujer", "data": [
          { "name": "Ventas", "value": 21 },
          { "name": "IT", "value": 18 },
          { "name": "RRHH", "value": 14 },
          { "name": "Finanzas", "value": 12 }
        ]}
      ]
    },
    {
      "id": "w2",
      "type": "chart",
      "chartType": "bar",
      "variant": "horizontal",
      "title": "Salario Promedio por Departamento",
      "x": "departamento",
      "y": "salario",
      "orientation": "horizontal",
      "data": [
        { "name": "IT", "value": 5800 },
        { "name": "Finanzas", "value": 5200 },
        { "name": "Ventas", "value": 4100 },
        { "name": "RRHH", "value": 3900 }
      ]
    },
    {
      "id": "w3",
      "type": "chart",
      "chartType": "pie",
      "title": "Distribución por Departamento",
      "data": [
        { "name": "Ventas", "value": 51 },
        { "name": "IT", "value": 43 },
        { "name": "Finanzas", "value": 27 },
        { "name": "RRHH", "value": 24 }
      ]
    },
    {
      "id": "i1",
      "type": "insight",
      "emoji": "💼",
      "content": "IT tiene el salario promedio más alto ($5,800), un 49% más que RRHH ($3,900)",
      "severity": "info"
    },
    {
      "id": "i2",
      "type": "insight",
      "emoji": "⚖️",
      "content": "Ventas tiene la mayor brecha de género: 30 hombres vs 21 mujeres",
      "severity": "warning"
    }
  ]
}
```

---

### Ejemplo 3: E-commerce — Transacciones

**Datos**: Tabla "transacciones" con columnas: cliente (string), producto (string), monto (number), fecha (date), método_pago (string), estado (string)

```json
{
  "widgets": [
    {
      "id": "kpi1",
      "type": "kpi",
      "label": "Revenue Total",
      "value": 892450,
      "format": "currency",
      "prefix": "$",
      "trend": "up",
      "trendValue": "+22%"
    },
    {
      "id": "kpi2",
      "type": "kpi",
      "label": "Transacciones",
      "value": 3456,
      "format": "number",
      "suffix": "transacciones"
    },
    {
      "id": "w1",
      "type": "chart",
      "chartType": "line",
      "variant": "multi",
      "title": "Revenue por Método de Pago",
      "x": "fecha",
      "series": [
        { "name": "Tarjeta", "data": [
          { "name": "Ene", "value": 45000 }, { "name": "Feb", "value": 52000 },
          { "name": "Mar", "value": 48000 }, { "name": "Abr", "value": 61000 }
        ]},
        { "name": "Efectivo", "data": [
          { "name": "Ene", "value": 22000 }, { "name": "Feb", "value": 25000 },
          { "name": "Mar", "value": 19000 }, { "name": "Abr", "value": 28000 }
        ]},
        { "name": "Transferencia", "data": [
          { "name": "Ene", "value": 15000 }, { "name": "Feb", "value": 18000 },
          { "name": "Mar", "value": 21000 }, { "name": "Abr", "value": 24000 }
        ]}
      ]
    },
    {
      "id": "w2",
      "type": "chart",
      "chartType": "pie",
      "variant": "doughnut",
      "title": "Distribución por Estado",
      "data": [
        { "name": "Completada", "value": 72 },
        { "name": "Pendiente", "value": 18 },
        { "name": "Cancelada", "value": 10 }
      ]
    },
    {
      "id": "w3",
      "type": "chart",
      "chartType": "bar",
      "title": "Top 5 Clientes por Gasto",
      "x": "cliente",
      "y": "monto",
      "data": [
        { "name": "María García", "value": 25000 },
        { "name": "Juan López", "value": 18500 },
        { "name": "Ana Torres", "value": 15200 },
        { "name": "Pedro Ruiz", "value": 12800 },
        { "name": "Laura Díaz", "value": 10500 }
      ]
    },
    {
      "id": "i1",
      "type": "insight",
      "emoji": "💳",
      "content": "Las tarjetas representan el 55% del revenue total — consolidar como canal principal",
      "severity": "positive"
    },
    {
      "id": "i2",
      "type": "insight",
      "emoji": "🚨",
      "content": "El 10% de transacciones son canceladas — revisar proceso de checkout",
      "severity": "negative"
    },
    {
      "id": "i3",
      "type": "insight",
      "emoji": "👑",
      "content": "Los top 5 clientes generan el 9% del revenue total — considerar programa de fidelización",
      "severity": "info"
    },
    {
      "id": "i4",
      "type": "insight",
      "emoji": "📉",
      "content": "Efectivo cayó un 13% en marzo — los clientes migran a métodos digitales",
      "severity": "warning"
    }
  ]
}
```

---

### Ejemplo 4: Inventario — Stock de Productos

**Datos**: Tabla "productos" con columnas: nombre (string), categoría (string), stock (number), precio_unitario (number), proveedor (string), fecha_reposicion (date)

```json
{
  "widgets": [
    {
      "id": "kpi1",
      "type": "kpi",
      "label": "Valor Total Inventario",
      "value": 284500,
      "format": "currency",
      "prefix": "$"
    },
    {
      "id": "kpi2",
      "type": "kpi",
      "label": "Productos en Stock",
      "value": 156,
      "format": "number",
      "suffix": "productos"
    },
    {
      "id": "w1",
      "type": "chart",
      "chartType": "bar",
      "variant": "horizontal",
      "title": "Stock por Categoría",
      "x": "categoría",
      "y": "stock",
      "data": [
        { "name": "Electrónica", "value": 450 },
        { "name": "Ropa", "value": 320 },
        { "name": "Hogar", "value": 280 },
        { "name": "Alimentos", "value": 190 },
        { "name": "Juguetes", "value": 85 }
      ]
    },
    {
      "id": "w2",
      "type": "chart",
      "chartType": "bar",
      "variant": "stacked",
      "title": "Stock por Categoría y Proveedor",
      "x": "categoría",
      "series": [
        { "name": "Proveedor A", "data": [
          { "name": "Electrónica", "value": 200 }, { "name": "Ropa", "value": 150 },
          { "name": "Hogar", "value": 100 }
        ]},
        { "name": "Proveedor B", "data": [
          { "name": "Electrónica", "value": 250 }, { "name": "Ropa", "value": 170 },
          { "name": "Hogar", "value": 180 }
        ]}
      ]
    },
    {
      "id": "w3",
      "type": "chart",
      "chartType": "pie",
      "title": "Distribución de Valor por Categoría",
      "data": [
        { "name": "Electrónica", "value": 42 },
        { "name": "Ropa", "value": 28 },
        { "name": "Hogar", "value": 18 },
        { "name": "Alimentos", "value": 12 }
      ]
    },
    {
      "id": "i1",
      "type": "insight",
      "emoji": "📦",
      "content": "Electrónica concentra el 42% del valor del inventario con solo el 29% del stock",
      "severity": "info"
    },
    {
      "id": "i2",
      "type": "insight",
      "emoji": "⚠️",
      "content": "Juguetes tiene solo 85 unidades — riesgo de quiebre de stock",
      "severity": "warning"
    }
  ]
}
```

---

### Ejemplo 5: Datos de Empleados con JOIN

**Datos**: Dos tablas:
- "empleados" (nombre, depto_id, salario, fecha_ingreso)
- "departamentos" (id, nombre, presupuesto)

La IA hace `join_tables` para combinar empleados con departamentos, luego analiza.

```json
{
  "widgets": [
    {
      "id": "kpi1",
      "type": "kpi",
      "label": "Total Planilla",
      "value": 245000,
      "format": "currency",
      "prefix": "$"
    },
    {
      "id": "kpi2",
      "type": "kpi",
      "label": "Empleados Activos",
      "value": 89,
      "format": "number",
      "suffix": "empleados"
    },
    {
      "id": "kpi3",
      "type": "kpi",
      "label": "% Uso de Presupuesto",
      "value": 73,
      "format": "percent",
      "trend": "neutral",
      "trendValue": "0%"
    },
    {
      "id": "w1",
      "type": "chart",
      "chartType": "bar",
      "title": "Salario Promedio por Departamento",
      "x": "departamento",
      "y": "salario",
      "data": [
        { "name": "Ingeniería", "value": 6200 },
        { "name": "Marketing", "value": 4800 },
        { "name": "Ventas", "value": 4100 },
        { "name": "Soporte", "value": 3500 },
        { "name": "Administración", "value": 3200 }
      ]
    },
    {
      "id": "w2",
      "type": "chart",
      "chartType": "bar",
      "variant": "stacked",
      "title": "Presupuesto vs Salarios Pagados por Departamento",
      "x": "departamento",
      "series": [
        { "name": "Presupuesto", "data": [
          { "name": "Ingeniería", "value": 80000 },
          { "name": "Marketing", "value": 50000 },
          { "name": "Ventas", "value": 45000 },
          { "name": "Soporte", "value": 30000 },
          { "name": "Admin", "value": 25000 }
        ]},
        { "name": "Gastado", "data": [
          { "name": "Ingeniería", "value": 62000 },
          { "name": "Marketing", "value": 38400 },
          { "name": "Ventas", "value": 32800 },
          { "name": "Soporte", "value": 24500 },
          { "name": "Admin", "value": 22400 }
        ]}
      ]
    },
    {
      "id": "w3",
      "type": "chart",
      "chartType": "line",
      "variant": "area",
      "title": "Crecimiento de Planilla Mensual",
      "x": "fecha",
      "y": "salario",
      "areaStyle": {},
      "data": [
        { "name": "Ene", "value": 38000 },
        { "name": "Feb", "value": 39500 },
        { "name": "Mar", "value": 42000 },
        { "name": "Abr", "value": 43500 },
        { "name": "May", "value": 45000 }
      ]
    },
    {
      "id": "i1",
      "type": "insight",
      "emoji": "🎯",
      "content": "Ingeniería consume el 25% del presupuesto total pero tiene el salario promedio más alto ($6,200)",
      "severity": "info"
    },
    {
      "id": "i2",
      "type": "insight",
      "emoji": "✅",
      "content": "Ningún departamento supera el 80% de su presupuesto — buena salud financiera",
      "severity": "positive"
    },
    {
      "id": "i3",
      "type": "insight",
      "emoji": "📊",
      "content": "La planilla crece un promedio de $1,500 mensuales — proyectar presupuesto anual",
      "severity": "info"
    },
    {
      "id": "i4",
      "type": "insight",
      "emoji": "⚠️",
      "content": "Administración gasta el 90% de su presupuesto con el salario promedio más bajo — revisar asignación",
      "severity": "warning"
    }
  ]
}
```

---

## 8. Resumen de Decisiones

| Tema | Decisión |
|------|----------|
| **Chart types** | bar, line, pie |
| **Chart variants** | stacked, grouped, horizontal, multi-line, area, doughnut |
| **KPIs** | SUM, AVG, COUNT, MAX, MIN, percent, trend |
| **Insights** | emoji + content + severity (positive/negative/warning/info) |
| **Tools** | get_columns, get_sample, count_rows, aggregate, group_by, filter, distinct_values, date_range, join_tables |
| **Joins** | Tablas virtuales temporales, reutilizables por tools posteriores |
| **Agent loop** | Max 15 iteraciones, 10 tool calls, 60s timeout |
| **Max charts** | 5 |
| **Min KPIs** | 1 |
| **Max insights** | 4 |
| **Seguridad** | SQL parametrizado, solo tablas del proyecto, sin SQL crudo de la IA |
