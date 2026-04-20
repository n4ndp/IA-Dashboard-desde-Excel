# Refactorización Completa de Arquitectura AI para Generación de Dashboards (FastAPI + OpenAI)

Actualmente tenemos un servicio en `services/ai_service.py` que utiliza un solo agente de OpenAI con herramientas (Function Calling) en un bucle (while/for loop) para explorar datos y generar un dashboard. Este enfoque está causando "Context Overflow", consume muchos tokens y da errores de Timeout.

Vamos a refactorizarlo hacia una arquitectura **"Planificador -> Ejecutor Middleware -> Diseñador"** utilizando `gpt-4o-mini` y validación estricta de JSON (Structured Outputs).

## 1. Visión General de la Nueva Arquitectura

El flujo constará de 3 pasos estrictos y secuenciales, sin bucles infinitos:

1. **Agente Planificador (IA 1):** Recibe el esquema de la base de datos (nombres de tablas, columnas, tipos de datos y un head(5) de muestra). Su trabajo es razonar qué datos necesita para armar un buen dashboard y devolver un JSON con una lista de "funciones a ejecutar" y un mensaje explicativo. No ejecuta nada, solo planifica.
2. **Middleware Ejecutor (Python):** Lee el JSON del Planificador, mapea las funciones solicitadas a métodos reales en Python (Pandas/SQLAlchemy), ejecuta las consultas, y empaqueta los resultados en un diccionario/string estructurado.
3. **Agente Diseñador (IA 2):** Recibe los resultados calculados por el Middleware y el "mensaje explicativo" del Planificador. Con esta información precisa, genera el JSON final del dashboard que consumirá el Frontend.

---

## 2. Definición de Funciones Analíticas (Soporte para el Middleware)

Debes crear estas funciones en `services/analytics_service.py`. Ya no serán "tools" de OpenAI, serán métodos puros de Python que el Middleware ejecutará.

1. `get_basic_stats(table, column)`: Retorna min, max, cantidad de nulos y top 3 valores frecuentes.
2. `aggregate_column(table, column, operation)`: Operaciones: sum, avg, count.
3. `group_by_and_aggregate(table, group_col, agg_col, operation, limit=10)`: Agrupa por categoría y aplica una operación a una métrica. Ordena de mayor a menor y corta en `limit`.
4. `time_series_trend(table, date_col, agg_col, operation, interval='month')`: Agrupa por periodo de tiempo y retorna la tendencia.
5. `join_and_aggregate(table1, table2, join_col1, join_col2, group_col, agg_col, operation, limit=10)`: Hace un INNER/LEFT JOIN de dos tablas y automáticamente aplica un group_by + aggregate para retornar estadística útil, no datos crudos.

---

## 3. Agente Planificador (IA 1)

Debes crear la función `generate_execution_plan(...)` que llame a OpenAI con el siguiente comportamiento:

**Input (Prompt del Sistema + Usuario):**
"Eres un Arquitecto de Datos experto. Recibes el esquema de las siguientes tablas: {schemas_y_muestras}.
Tu objetivo es diseñar qué consultas a la base de datos se necesitan para construir un dashboard completo.
Puedes solicitar que el sistema ejecute las siguientes funciones predefinidas: [listar las 5 funciones de arriba con sus parámetros].
Regla: Debes solicitar un mínimo de 4 y un máximo de 8 ejecuciones. Siempre incluye al menos una tendencia temporal si hay fechas."

**Output Requerido (Fuerza este JSON Schema usando la API de OpenAI):**
```json
{
  "ejecutar": [
    {
      "function_name": "group_by_and_aggregate",
      "parametros": {"table": "ventas", "group_col": "categoria", "agg_col": "monto", "operation": "sum"},
      "justificacion": "Necesito saber las ventas totales por categoría para sugerir un gráfico de barras o pie."
    }
  ],
  "message": "Mensaje para el Diseñador UI: He solicitado las ventas por categoría y la tendencia mensual. Te sugiero usar las categorías para un gráfico de barras, la tendencia para un gráfico de líneas, y calcular el ticket promedio como KPI..."
}
```

---

## 4. Middleware Ejecutor (Lógica Python)

Debes crear una función `execute_plan(plan_json, analytics_engine)` que itere sobre la lista `ejecutar` devuelta por la IA 1.
1. Utiliza un `match/case` o un diccionario de funciones para llamar al método correspondiente en `analytics_engine`.
2. Captura los resultados.
3. Concatena los resultados en un diccionario de Python de la siguiente manera:
   `{"resultados_funciones": [...], "estrategia_sugerida": plan_json["message"]}`

---

## 5. Agente Diseñador (IA 2)

Debes crear la función `generate_final_dashboard(ejecucion_results)` que llame a OpenAI.

**Input (Prompt del Sistema):**
"Eres un Experto en Visualización de Datos y UI. Recibes un conjunto de datos pre-calculados y una estrategia de un Arquitecto de datos. Tu tarea es generar la configuración JSON para un Dashboard interactivo.
DATOS Y ESTRATEGIA: {ejecucion_results}

Reglas estrictas:
1. El número total de 'graficos' DEBE ser par (2, 4, 6) para que la grilla del frontend encaje perfectamente de dos en dos.
2. Utiliza la estrategia sugerida para orientar tu diseño.
3. El 'resumen_ejecutivo' debe ser un texto conciso que incluya una sección de 'Insights' o viñetas accionables (ej: '🔥 Categoría X es líder').
4. Solo usa gráficos de tipo 'bar', 'line' o 'pie'. Selecciona variantes apropiadas (stacked, horizontal) si la data lo requiere."

**Output Requerido (Fuerza este JSON Schema):**
```json
{
  "resumen_ejecutivo": "Texto en formato Markdown con el resumen y viñetas de insights destacando hallazgos críticos de los datos.",
  "kpis": [
    {
      "id": "k1",
      "label": "Total Ventas",
      "value": 150000,
      "format": "currency",
      "trend": "up"
    }
  ],
  "graficos": [
    {
      "id": "g1",
      "chartType": "bar",
      "title": "Ventas por Categoría",
      "data": [{"name": "Ropa", "value": 5000}]
    }
  ]
}
```

Por favor, reescribe el archivo `services/ai_service.py` eliminando el loop de iteraciones anterior y aplicando estos tres pasos en una función principal `generate_dashboard(...)` que orqueste todo el flujo de forma síncrona.
```




MAS CONTEXTO:
¡Excelente iniciativa! Escalar las funciones del **Middleware Ejecutor** es exactamente lo que le dará "superpoderes" a tu dashboard sin arriesgar el límite de tokens.

Si el agente Planificador (IA 1) tiene un abanico más rico de funciones, podrá pedir análisis mucho más sofisticados y, por lo tanto, el agente Diseñador (IA 2) tendrá datos increíbles para graficar.

Aquí tienes el **Top 10 de Funciones Analíticas** ideales para este tipo de arquitectura, con su justificación, y luego el **Prompt Maestro Actualizado** incluyendo la instrucción estricta de usar colores en los gráficos.

### El Top 10 de Funciones Analíticas y su Justificación

1. **`get_column_summary(table, column)`**: Retorna estadísticas básicas (min, max, nulos, cantidad de únicos, top 3 frecuentes).
   * *Justificación:* Es la "vista de pájaro". Sirve para que la IA decida si una columna vale la pena graficarla (ej. si hay 500 valores únicos, un Pie Chart es mala idea).
2. **`calculate_kpi(table, agg_col, operation, filter_col=None, filter_val=None)`**: Calcula un número único (ej. Suma de Ventas totales, o Suma de Ventas donde Estado='Pagado').
   * *Justificación:* Alimenta directamente los "Tarjetones" (KPIs) de la parte superior del dashboard.
3. **`period_over_period_growth(table, date_col, agg_col, operation, interval='month')`**: Compara el último mes/año con el anterior y devuelve el % de crecimiento/caída.
   * *Justificación:* Indispensable para los KPIs interactivos (ej. "$15,000 *↑ +12% vs mes anterior*").
4. **`group_by_category(table, group_col, agg_col, operation, limit=10)`**: Agrupa por una categoría y suma/promedia una métrica, ordenado de mayor a menor.
   * *Justificación:* Es el motor principal de los gráficos de Barras, Donas y Pie Charts.
5. **`time_series_trend(table, date_col, agg_col, operation, interval='month')`**: Agrupa los datos temporalmente de forma cronológica.
   * *Justificación:* Única forma correcta de alimentar gráficos de Líneas o Áreas.
6. **`cross_tabulation(table, group_col_1, group_col_2, agg_col, operation)`**: Crea una tabla dinámica (Pivot Table) agrupando por dos categorías (ej. Ventas por Categoría y por Género).
   * *Justificación:* Fundamental para generar gráficos de **Barras Apiladas (Stacked Bars)** o múltiples líneas.
7. **`distribution_bins(table, numeric_col, bins=5)`**: Divide un valor numérico en rangos (ej. 0-100, 100-200) y cuenta cuántos registros caen en cada uno.
   * *Justificación:* Excelente para Histogramas o insights del tipo "El 80% de los clientes compra en el rango de $0 a $50".
8. **`find_top_bottom_records(table, entity_col, agg_col, operation, n=3)`**: Devuelve los 3 mejores y los 3 peores elementos según una métrica.
   * *Justificación:* Oro puro para la sección de "Insights" accionables (ej. "Tus productos estrella son X e Y, pero debes revisar las ventas de Z").
9. **`correlation_check(table, num_col_1, num_col_2)`**: Verifica si existe correlación matemática (0 a 1) entre dos métricas (ej. Descuento vs Volumen de Venta).
   * *Justificación:* Permite generar insights ultra-inteligentes o alimentar gráficos de dispersión (Scatter plots).
10. **`join_and_aggregate(table1, table2, join_col1, join_col2, group_col, agg_col, operation, limit=10)`**: Junta dos tablas y luego agrupa/agrega.
    * *Justificación:* Permite resolver preguntas complejas de bases de datos relacionales sin saturar a la IA con millones de filas cruzadas.

---

### PROMPT MAESTRO ACTUALIZADO (Copia y pega en tu Opencode/Cursor)

```markdown
# Refactorización Completa de Arquitectura AI para Generación de Dashboards (FastAPI + OpenAI)

Actualmente tenemos un servicio en `services/ai_service.py` que utiliza un solo agente en un bucle causando "Context Overflow". Vamos a refactorizarlo hacia una arquitectura **"Planificador -> Ejecutor Middleware -> Diseñador"** utilizando `gpt-4o-mini` y validación estricta de JSON (Structured Outputs).

## 1. Visión General del Flujo Secuencial
1. **Agente Planificador (IA 1):** Recibe el esquema y solicita la ejecución de funciones estadísticas.
2. **Middleware Ejecutor (Python):** Ejecuta esas funciones localmente usando Pandas/SQLAlchemy y empaqueta el resultado.
3. **Agente Diseñador (IA 2):** Lee los resultados y diseña el dashboard (KPIs, Insights y Gráficos), inyectando una estética colorida y atractiva.

---

## 2. Definición de Funciones Analíticas (Soporte para el Middleware)
Debes crear estas 10 funciones en `services/analytics_service.py`. Estas funciones serán llamadas por el Middleware basándose en el JSON de la IA 1. Retornarán diccionarios de Python limitados en tamaño.

1. `get_column_summary(table, column)`: Retorna min, max, nulos, uniques, y top 3 frecuentes.
2. `calculate_kpi(table, agg_col, operation, filter_col=None, filter_val=None)`: Retorna un valor único agregado.
3. `period_over_period_growth(table, date_col, agg_col, operation, interval='month')`: Retorna valor actual, valor anterior y % de cambio.
4. `group_by_category(table, group_col, agg_col, operation, limit=10)`: Agrupa 1D y retorna top N.
5. `time_series_trend(table, date_col, agg_col, operation, interval='month')`: Tendencia cronológica.
6. `cross_tabulation(table, group_col_1, group_col_2, agg_col, operation, limit=5)`: Agrupación 2D para barras apiladas.
7. `distribution_bins(table, numeric_col, bins=5)`: Retorna rangos y conteo (histograma).
8. `find_top_bottom_records(table, entity_col, agg_col, operation, n=3)`: Retorna el top N y el bottom N.
9. `correlation_check(table, num_col_1, num_col_2)`: Retorna el índice de correlación de Pearson.
10. `join_and_aggregate(table1, table2, join_col1, join_col2, group_col, agg_col, operation, limit=10)`: JOIN + GroupBy.

---

## 3. Agente Planificador (IA 1)
Crea la función `generate_execution_plan(...)`.

**Prompt del Sistema:**
"Eres un Arquitecto de Datos. Recibes el esquema de tablas: {schemas_y_muestras}.
Diseña qué consultas necesitas para un dashboard. Puedes usar estas funciones: [Listar las 10 funciones].
Reglas: Solicita entre 4 y 8 ejecuciones. Pide siempre tendencias de tiempo si hay fechas, y usa 'period_over_period_growth' y 'find_top_bottom_records' para obtener buenos KPIs e insights."

**Output Requerido (Fuerza JSON Schema):**
```json
{
  "ejecutar": [
    {
      "function_name": "nombre_de_la_funcion",
      "parametros": {"key": "value"},
      "justificacion": "motivo analítico"
    }
  ],
  "message": "Mensaje para el Diseñador UI con la estrategia..."
}
```

---

## 4. Middleware Ejecutor (Lógica Python)
Crea `execute_plan(plan_json, analytics_engine)`.
Mapea el JSON `ejecutar` a los métodos de `analytics_engine`. Ejecuta sin fallar (si una falla, añade un error string al resultado y continúa). Retorna:
`{"resultados_funciones": [...], "estrategia_sugerida": plan_json["message"]}`

---

## 5. Agente Diseñador (IA 2)
Crea `generate_final_dashboard(ejecucion_results)`.

**Prompt del Sistema:**
"Eres un Experto en Visualización UI. Recibes datos calculados: {ejecucion_results}. Genera la config JSON del Dashboard.
Reglas ESTRICTAS:
1. El número de 'graficos' DEBE ser par (2, 4, 6).
2. Diseño Colorido y Atractivo: DEBES incluir arreglos de colores hexadecimales vibrantes o aleatorios (pero estéticamente agradables) dentro de la configuración de cada gráfico, para que no queden en blanco y negro o colores por defecto. Específicamente en gráficos de pie/donas y barras.
3. El 'resumen_ejecutivo' debe incluir 'Insights' accionables basados en los top/bottom y crecimientos.
4. ChartTypes permitidos: 'bar', 'line', 'pie'. Variantes: 'stacked', 'doughnut', 'area'."

**Output Requerido (Fuerza JSON Schema):**
```json
{
  "resumen_ejecutivo": "Texto Markdown con insights...",
  "kpis": [
    { "id": "k1", "label": "Ventas", "value": 1500, "trend": "up", "trendValue": "+10%" }
  ],
  "graficos": [
    {
      "id": "g1",
      "chartType": "pie",
      "variant": "doughnut",
      "title": "Ventas por Categoría",
      "data": [{"name": "Ropa", "value": 50}],
      "colorPalette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
    }
  ]
}
```
*Nota para el codificador: Asegúrate de adaptar la interfaz de Vue/Echarts para que lea el campo `colorPalette` y lo aplique al gráfico.*

Reescribe `services/ai_service.py` aplicando este flujo síncrono.
```


MAS CONTEXTO:
# Actualización del Prompt del Agente Diseñador (IA 2): Catálogo de Gráficos

Necesitamos actualizar el Prompt del Sistema del **Agente Diseñador (IA 2)** para incluir un mapeo exacto entre el tipo de dato que recibe (proveniente de las nuevas funciones de Python) y el tipo de gráfico que debe generar.

Reemplaza la sección de "Reglas ESTRICTAS" de la IA 2 con el siguiente bloque detallado:

**Prompt del Sistema (IA 2 - Diseñador UI):**
"Eres un Experto en Visualización de Datos y UI. Recibes un conjunto de datos pre-calculados por un Middleware y una estrategia de un Arquitecto de datos. Tu tarea es generar la configuración JSON para un Dashboard interactivo.
DATOS Y ESTRATEGIA: {ejecucion_results}

### REGLAS ESTRICTAS DE VISUALIZACIÓN:
1. **Grilla Par:** El número total de 'graficos' generados DEBE ser par (2, 4, 6) para mantener la simetría de la interfaz.
2. **Estética Colorida:** Todo gráfico de tipo 'pie', 'bar' o 'scatter' DEBE incluir un array `colorPalette` con códigos hexadecimales vibrantes y estéticos (ej: ["#FF6B6B", "#4ECDC4", "#45B7D1", "#F9A826"]). No uses los colores por defecto.

### CATÁLOGO DE GRÁFICOS PERMITIDOS Y JUSTIFICACIÓN:
Debes elegir el `chartType` y la `variant` basándote estrictamente en el tipo de información que recibiste:

* **Tipos de Barras (`chartType`: "bar"):**
    * `variant: "standard"`: Úsalo para rankings simples (provenientes de `group_by_category`).
    * `variant: "horizontal"`: Úsalo OBLIGATORIAMENTE si las etiquetas de las categorías son textos largos (más de 15 caracteres) para evitar superposición.
    * `variant: "stacked"` (Barras Apiladas): Úsalo EXCLUSIVAMENTE si recibes datos de 2 dimensiones (provenientes de `cross_tabulation`), para mostrar composición dentro de un grupo.
    * `variant: "histogram"`: Úsalo EXCLUSIVAMENTE si recibes rangos de frecuencias (provenientes de `distribution_bins`). Eje X: Rangos, Eje Y: Conteo.

* **Tipos de Líneas (`chartType`: "line"):**
    * `variant: "standard"`: Úsalo ÚNICAMENTE para datos cronológicos o series de tiempo (provenientes de `time_series_trend`).
    * `variant: "area"`: Úsalo para series de tiempo donde quieras enfatizar el volumen total acumulado bajo la línea.
    * `variant: "multi-line"`: Úsalo si tienes múltiples series de tiempo comparativas.

* **Tipos Circulares (`chartType`: "pie"):**
    * `variant: "standard"`: Úsalo para mostrar proporciones (100%), pero SOLO si hay 5 categorías o menos. Si hay más, usa un gráfico de barras.
    * `variant: "doughnut"`: Versión moderna del pie chart (con hueco en el centro). Úsalo por defecto en lugar del pie estándar por su estética superior.

* **Tipos de Dispersión (`chartType`: "scatter"):**
    * `variant: "standard"`: Úsalo EXCLUSIVAMENTE para mostrar si existe relación entre dos métricas numéricas (provenientes de `correlation_check`).

**Output Requerido (Fuerza este JSON Schema):**
```json
{
  "resumen_ejecutivo": "Texto Markdown con insights...",
  "kpis": [
    { "id": "k1", "label": "Ventas", "value": 1500, "trend": "up", "trendValue": "+10%" }
  ],
  "graficos": [
    {
      "id": "g1",
      "chartType": "bar",
      "variant": "histogram",
      "title": "Distribución de Precios",
      "x_label": "Rangos de Precio",
      "y_label": "Cantidad de Productos",
      "data": [{"name": "0-50", "value": 120}, {"name": "51-100", "value": 85}],
      "colorPalette": ["#4ECDC4"]
    }
  ]
}
