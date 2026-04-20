"""AI dashboard generation service — 3-step deterministic pipeline.

Step 1 (Planificador): IA call → execution plan with Structured Outputs.
Step 2 (Middleware):  Pure Python dispatch to 10 analytical functions.
Step 3 (Diseñador):   IA call → final dashboard JSON with Structured Outputs.

Both AI calls use gpt-4o-mini with ``response_format: {type: "json_schema"}``.
No iteration loop — bounded to exactly 2 API calls, zero recursion risk.
"""

import inspect
import json
import os
from datetime import datetime, timezone
from typing import Any

from openai import OpenAI
from sqlalchemy.orm import Session

from services.analytics_service import AnalyticsEngine

# ── OpenAI client (lazy init) ─────────────────────────────────────────

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Lazy-initialize the OpenAI client."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(api_key=api_key)
    return _client


# ── JSON Schemas for Structured Outputs ────────────────────────────────

PLAN_SCHEMA = {
    "name": "execution_plan",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "ejecutar": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "function_name": {"type": "string"},
                        "parametros": {
                            "type": "object",
                            "properties": {},
                            "required": [],
                            "additionalProperties": {"type": "string"},
                        },
                        "justificacion": {"type": "string"},
                    },
                    "required": ["function_name", "parametros", "justificacion"],
                    "additionalProperties": False,
                },
            },
            "message": {"type": "string"},
        },
        "required": ["ejecutar", "message"],
        "additionalProperties": False,
    },
}

DESIGNER_SCHEMA = {
    "name": "dashboard_design",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "resumen_ejecutivo": {"type": "string"},
            "kpis": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "label": {"type": "string"},
                        "value": {"type": "number"},
                        "format": {"type": "string"},
                        "trend": {"type": ["string", "null"]},
                        "trendValue": {"type": ["string", "null"]},
                    },
                    "required": ["id", "label", "value", "format", "trend", "trendValue"],
                    "additionalProperties": False,
                },
            },
            "graficos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "chartType": {"type": "string"},
                        "variant": {"type": ["string", "null"]},
                        "title": {"type": "string"},
                        "data": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "value": {"type": "number"},
                                    "x": {"type": ["number", "null"]},
                                    "y": {"type": ["number", "null"]},
                                },
                                "required": ["name", "value", "x", "y"],
                                "additionalProperties": False,
                            },
                        },
                        "series": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "data": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "value": {"type": "number"},
                                                "x": {"type": ["number", "null"]},
                                                "y": {"type": ["number", "null"]},
                                            },
                                            "required": ["name", "value", "x", "y"],
                                            "additionalProperties": False,
                                        },
                                    },
                                },
                                "required": ["name", "data"],
                                "additionalProperties": False,
                            },
                        },
                        "colorPalette": {
                            "type": ["array", "null"],
                            "items": {"type": "string"},
                        },
                        "x_label": {"type": ["string", "null"]},
                        "y_label": {"type": ["string", "null"]},
                    },
                    "required": [
                        "id", "chartType", "variant", "title",
                        "data", "series", "colorPalette", "x_label", "y_label",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["resumen_ejecutivo", "kpis", "graficos"],
        "additionalProperties": False,
    },
}


# ── Prompt builders ────────────────────────────────────────────────────


def _build_plan_prompt(tables_context: list[dict]) -> str:
    import json

    table_descriptions = []
    for t in tables_context:
        cols = ", ".join(f"{c['name']}({c['type']})" for c in t.get("columns", []))
        sample_lines = []
        for row in t.get("rows", [])[:5]:
            sample_lines.append("    " + json.dumps(row, ensure_ascii=False, default=str))
        sample_str = "\n".join(sample_lines) if sample_lines else "    (sin datos)"
        table_descriptions.append(
            f"- Tabla '{t['sheet_name']}' (id={t['id']}): {t.get('row_count', '?')} filas\n"
            f"  Columnas: {cols}\n"
            f"  Muestra:\n{sample_str}"
        )

    tables_block = "\n".join(table_descriptions)

    return f"""Eres un Arquitecto de Datos experto en análisis de negocio. Tu misión es diseñar el plan de análisis óptimo para construir un dashboard de alto impacto.

## TABLAS DEL PROYECTO

{tables_block}

## FUNCIONES DISPONIBLES

1. get_column_summary(table, column)
   → Retorna: min, max, nulos, cantidad_unicos, top3_frecuentes
   → Úsala para: explorar columnas antes de graficar, detectar cardinalidad

2. calculate_kpi(table, agg_col, operation, filter_col, filter_val)
   → Retorna: valor único (número)
   → Úsala para: KPI cards — totales, promedios, máximos

3. period_over_period_growth(table, date_col, agg_col, operation, interval)
   → Retorna: valor_actual, valor_anterior, pct_cambio
   → Úsala para: KPIs con trend (↑ +12% vs mes anterior)
   → interval: "month" | "quarter" | "year"

4. group_by_category(table, group_col, agg_col, operation, limit)
   → Retorna: [{{name, value}}] ordenado desc
   → Úsala para: bar charts, pie/donut charts

5. time_series_trend(table, date_col, agg_col, operation, interval)
   → Retorna: [{{period, value}}] cronológico
   → Úsala para: line charts, area charts
   → interval: "day" | "week" | "month" | "quarter"

6. cross_tabulation(table, group_col_1, group_col_2, agg_col, operation, limit)
   → Retorna: {{categories: [...], series: [{{name, data: [...]}}]}}
   → Úsala para: stacked bar charts (2 dimensiones)

7. distribution_bins(table, numeric_col, bins)
   → Retorna: [{{range, count}}]
   → Úsala para: histogramas — entender distribución de precios, edades, etc.

8. find_top_bottom_records(table, entity_col, agg_col, operation, n)
   → Retorna: {{top: [{{name, value}}], bottom: [{{name, value}}]}}
   → Úsala para: ranking charts + insights accionables

9. correlation_check(table, num_col_1, num_col_2)
   → Retorna: {{pearson_r, interpretation, scatter_points: [{{x, y}}]}}
   → Úsala para: scatter charts + insights de correlación

10. join_and_aggregate(table1, table2, join_col1, join_col2, group_col, agg_col, operation, limit)
    → Retorna: [{{name, value}}] del join
    → Úsala para: análisis cruzados entre tablas relacionadas

## REGLAS DE ESCALAMIENTO ADAPTATIVO

Primero, calcula la complejidad del dataset:
- Cuenta el total de tablas (T)
- Cuenta el total de columnas analíticas (C) — excluyendo IDs puros como `id_venta`
- Suma las filas aproximadas (F) de todas las tablas

Luego aplica esta tabla:

| Complejidad | Criterio | Funciones a solicitar | KPIs esperados | Gráficos esperados |
|---|---|---|---|---|
| Mínima | T≤2 y C≤6 y F≤50 | 4-5 | 2 | 2 |
| Pequeña | T≤3 y C≤12 y F≤200 | 5-7 | 2-3 | 3-4 |
| Media | T≤5 y C≤25 y F≤1000 | 7-10 | 3-5 | 5-8 |
| Grande | T≤8 y C≤50 y F≤5000 | 10-15 | 5-8 | 8-12 |
| Muy Grande | T>8 o C>50 o F>5000 | 15-22 | 6-10 | 12-18 |

REGLAS:
- Aplica la tabla de arriba. El número de funciones DEBE corresponder a la complejidad detectada
- Si hay columna de fecha → SIEMPRE incluye time_series_trend + period_over_period_growth
- Si hay columna numérica → SIEMPRE incluye calculate_kpi
- Si hay 2 columnas categóricas → incluye cross_tabulation
- Si hay 2 columnas numéricas → incluye correlation_check
- EXPLORA todas las tablas — no te concentres solo en una. Cada tabla con datos útiles merece al menos 1 función
- Si hay muchas tablas relacionadas → usa join_and_aggregate para cruzar información rica
- El campo `message` es tu briefing para el Diseñador: explica qué gráficos sugieres, cuántos KPIs y gráficos esperas, y por qué
- Todos los valores de parámetros deben ser strings

## REGLA CRÍTICA DE IDs Y JOINS

- Las columnas llamadas `id_*` o `*_id` son claves foráneas (ej: id_producto, id_cliente, id_region)
- NUNCA uses una columna ID como group_col en group_by_category — los valores "P01", "C12", "R03" NO son legibles ni útiles para un dashboard
- Si detectas que una tabla tiene una FK y existe otra tabla con el nombre legible → USA join_and_aggregate
- Ejemplo: si 'ventas' tiene 'id_producto' y existe la tabla 'productos' con 'nombre_producto' y 'categoria':
  - ❌ MAL: group_by_category(table="ventas", group_col="id_producto", ...) → muestra "P01", "P02"
  - ✅ BIEN: join_and_aggregate(table1="ventas", table2="productos", join_col1="id_producto", join_col2="id_producto", group_col="nombre_producto", ...) → muestra "Producto 1", "Producto 2"
  - ✅ TAMBIÉN: join_and_aggregate(table1="ventas", table2="productos", join_col1="id_producto", join_col2="id_producto", group_col="categoria", ...) → muestra "Ropa", "Deportes"
- SIEMPRE prefiere agrupar por nombres legibles (nombre_producto, nombre_cliente, region) sobre IDs
- Si haces joins, asegúrate de usar el group_col de la tabla que tiene el nombre legible (table2)

## EJEMPLOS FEW-SHOT

### Ejemplo 1 — Dataset de Ventas (fecha + categoría + monto)
Input: Tabla 'ventas' con columnas: fecha(date), categoria(string), region(string), monto(number), cantidad(number)

Output correcto:
{{
  "ejecutar": [
    {{
      "function_name": "calculate_kpi",
      "parametros": {{"table": "ventas", "agg_col": "monto", "operation": "SUM", "filter_col": "", "filter_val": ""}},
      "justificacion": "KPI principal: total de ventas en el período"
    }},
    {{
      "function_name": "period_over_period_growth",
      "parametros": {{"table": "ventas", "date_col": "fecha", "agg_col": "monto", "operation": "SUM", "interval": "month"}},
      "justificacion": "KPI de tendencia: crecimiento vs mes anterior para mostrar momentum"
    }},
    {{
      "function_name": "time_series_trend",
      "parametros": {{"table": "ventas", "date_col": "fecha", "agg_col": "monto", "operation": "SUM", "interval": "month"}},
      "justificacion": "Serie temporal mensual para el área/line chart de tendencia"
    }},
    {{
      "function_name": "group_by_category",
      "parametros": {{"table": "ventas", "group_col": "categoria", "agg_col": "monto", "operation": "SUM", "limit": "6"}},
      "justificacion": "Ventas por categoría para bar chart o donut chart"
    }},
    {{
      "function_name": "group_by_category",
      "parametros": {{"table": "ventas", "group_col": "region", "agg_col": "monto", "operation": "SUM", "limit": "8"}},
      "justificacion": "Ventas por región para bar chart horizontal (etiquetas largas)"
    }},
    {{
      "function_name": "find_top_bottom_records",
      "parametros": {{"table": "ventas", "entity_col": "categoria", "agg_col": "monto", "operation": "SUM", "n": "3"}},
      "justificacion": "Top 3 y bottom 3 categorías para insights accionables"
    }}
  ],
  "message": "COMPLEJIDAD: Pequeña (1 tabla, 5 columnas analíticas). OBJETIVO: 2-3 KPIs, 4 gráficos. Diseñador: tengo datos para 4 gráficos y 2-3 KPIs. Sugiero: (1) KPI Total Ventas con trend de crecimiento, (2) KPI Ticket Promedio, (3) Area chart de tendencia mensual, (4) Bar chart de ventas por categoría, (5) Bar horizontal de ventas por región, (6) Donut de distribución. Los insights deben mencionar la categoría líder y la región con menor desempeño."
}}

### Ejemplo 2 — Dataset Relacional (ventas + productos + clientes) — CON JOINS
Input: Tabla 'ventas' (id_venta, fecha, id_cliente, id_producto, id_region, cantidad, precio_unitario, total_venta), Tabla 'productos' (id_producto, nombre_producto, categoria, costo_unitario), Tabla 'clientes' (id_cliente, nombre_cliente, genero, edad, tipo_cliente), Tabla 'regiones' (id_region, region, pais)

Complejidad: Media (4 tablas, ~18 columnas analíticas, ~170 filas) → solicitar 7-10 funciones

Output correcto:
{{
  "ejecutar": [
    {{
      "function_name": "calculate_kpi",
      "parametros": {{"table": "ventas", "agg_col": "total_venta", "operation": "SUM", "filter_col": "", "filter_val": ""}},
      "justificacion": "KPI principal: total de ventas"
    }},
    {{
      "function_name": "calculate_kpi",
      "parametros": {{"table": "ventas", "agg_col": "total_venta", "operation": "AVG", "filter_col": "", "filter_val": ""}},
      "justificacion": "KPI: ticket promedio por venta"
    }},
    {{
      "function_name": "period_over_period_growth",
      "parametros": {{"table": "ventas", "date_col": "fecha", "agg_col": "total_venta", "operation": "SUM", "interval": "month"}},
      "justificacion": "Crecimiento mensual para KPI con trend"
    }},
    {{
      "function_name": "time_series_trend",
      "parametros": {{"table": "ventas", "date_col": "fecha", "agg_col": "total_venta", "operation": "SUM", "interval": "month"}},
      "justificacion": "Tendencia mensual para line/area chart"
    }},
    {{
      "function_name": "join_and_aggregate",
      "parametros": {{"table1": "ventas", "table2": "productos", "join_col1": "id_producto", "join_col2": "id_producto", "group_col": "categoria", "agg_col": "total_venta", "operation": "SUM", "limit": "10"}},
      "justificacion": "Ventas por categoría (Ropa, Deportes...) — JOIN necesario porque 'ventas' solo tiene id_producto"
    }},
    {{
      "function_name": "join_and_aggregate",
      "parametros": {{"table1": "ventas", "table2": "regiones", "join_col1": "id_region", "join_col2": "id_region", "group_col": "region", "agg_col": "total_venta", "operation": "SUM", "limit": "10"}},
      "justificacion": "Ventas por región (Lima, Cusco...) — JOIN necesario porque 'ventas' solo tiene id_region"
    }},
    {{
      "function_name": "join_and_aggregate",
      "parametros": {{"table1": "ventas", "table2": "clientes", "join_col1": "id_cliente", "join_col2": "id_cliente", "group_col": "tipo_cliente", "agg_col": "total_venta", "operation": "SUM", "limit": "10"}},
      "justificacion": "Ventas por tipo de cliente (Nuevo vs Recurrente) — JOIN para obtener tipo_cliente"
    }},
    {{
      "function_name": "join_and_aggregate",
      "parametros": {{"table1": "ventas", "table2": "productos", "join_col1": "id_producto", "join_col2": "id_producto", "group_col": "nombre_producto", "agg_col": "total_venta", "operation": "SUM", "limit": "5"}},
      "justificacion": "Top 5 productos por ventas — JOIN para obtener nombre_producto en vez de P01, P02..."
    }},
    {{
      "function_name": "join_and_aggregate",
      "parametros": {{"table1": "ventas", "table2": "pagos", "join_col1": "id_venta", "join_col2": "id_venta", "group_col": "metodo_pago", "agg_col": "total_venta", "operation": "SUM", "limit": "10"}},
      "justificacion": "Ventas por método de pago — JOIN con tabla pagos para ver Tarjeta/Efectivo/Transferencia"
    }},
    {{
      "function_name": "find_top_bottom_records",
      "parametros": {{"table": "ventas", "entity_col": "id_producto", "agg_col": "total_venta", "operation": "SUM", "n": "3"}},
      "justificacion": "Top/bottom 3 productos por ventas — para insights de rendimiento"
    }}
  ],
  "message": "COMPLEJIDAD: Media (4 tablas + pagos, ~18 columnas, ~170 filas). OBJETIVO: 4-5 KPIs, 6-8 gráficos. Diseñador: dataset relacional con 5 tablas. Usé joins para obtener nombres legibles. Sugiero: (1) KPI Total Ventas con trend mensual, (2) KPI Ticket Promedio, (3) Area chart tendencia mensual, (4) Bar chart ventas por categoría, (5) Bar horizontal por región, (6) Donut por tipo de cliente, (7) Bar horizontal top 5 productos, (8) Donut por método de pago. Insights: destacar la categoría líder, la región más fuerte, si los recurrentes gastan más, y qué método de pago domina."
}}

### Ejemplo 3 — Dataset de RRHH (sin fechas, sin IDs)
Input: Tabla 'empleados' con columnas: nombre(string), departamento(string), salario(number), nivel(string), antiguedad(number)

Output correcto:
{{
  "ejecutar": [
    {{
      "function_name": "calculate_kpi",
      "parametros": {{"table": "empleados", "agg_col": "salario", "operation": "AVG", "filter_col": "", "filter_val": ""}},
      "justificacion": "KPI: salario promedio de la empresa"
    }},
    {{
      "function_name": "group_by_category",
      "parametros": {{"table": "empleados", "group_col": "departamento", "agg_col": "salario", "operation": "AVG", "limit": "8"}},
      "justificacion": "Salario promedio por departamento para bar chart"
    }},
    {{
      "function_name": "cross_tabulation",
      "parametros": {{"table": "empleados", "group_col_1": "departamento", "group_col_2": "nivel", "agg_col": "salario", "operation": "COUNT", "limit": "6"}},
      "justificacion": "Headcount por departamento y nivel para stacked bar chart"
    }},
    {{
      "function_name": "distribution_bins",
      "parametros": {{"table": "empleados", "numeric_col": "salario", "bins": "5"}},
      "justificacion": "Distribución salarial para histograma — detectar concentración de rangos"
    }},
    {{
      "function_name": "correlation_check",
      "parametros": {{"table": "empleados", "num_col_1": "antiguedad", "num_col_2": "salario"}},
      "justificacion": "Correlación antigüedad-salario para scatter chart e insight"
    }},
    {{
      "function_name": "find_top_bottom_records",
      "parametros": {{"table": "empleados", "entity_col": "departamento", "agg_col": "salario", "operation": "AVG", "n": "3"}},
      "justificacion": "Top/bottom departamentos por salario para insights de equidad"
    }}
  ],
  "message": "COMPLEJIDAD: Pequeña (1 tabla, 5 columnas, sin fechas). OBJETIVO: 2-3 KPIs, 4 gráficos. Diseñador: sin fechas, enfocarse en estructura organizacional. Sugiero: (1) KPI Headcount total, (2) KPI Salario promedio, (3) Bar horizontal salario por dept, (4) Stacked bar headcount por dept+nivel, (5) Histograma distribución salarial, (6) Scatter correlación antigüedad-salario. Insight clave: mencionar el dept con mayor/menor salario y si la correlación antigüedad-salario es significativa."
}}

### Ejemplo 4 — Dataset Grande (10 tablas, cientos de filas, múltiples relaciones)
Input: 10 tablas: ventas(~500 filas), productos(~30), clientes(~80), regiones(~10), pagos(~500), inventario(~30), categorias(~6), proveedores(~15), envios(~500), reseñas(~200). Tabla principal 'ventas' con FKs a productos, clientes, regiones. Tabla 'inventario' ligada a productos y proveedores. Tabla 'envios' con estados y fechas. Tabla 'reseñas' con puntuaciones.

Complejidad: Grande (10 tablas, ~50+ columnas analíticas, ~1400+ filas) → solicitar 10-15 funciones

Output correcto:
{{
  "ejecutar": [
    {{
      "function_name": "calculate_kpi",
      "parametros": {{"table": "ventas", "agg_col": "total_venta", "operation": "SUM", "filter_col": "", "filter_val": ""}},
      "justificacion": "KPI principal: facturación total"
    }},
    {{
      "function_name": "calculate_kpi",
      "parametros": {{"table": "ventas", "agg_col": "total_venta", "operation": "AVG", "filter_col": "", "filter_val": ""}},
      "justificacion": "KPI: ticket promedio"
    }},
    {{
      "function_name": "calculate_kpi",
      "parametros": {{"table": "reseñas", "agg_col": "puntuacion", "operation": "AVG", "filter_col": "", "filter_val": ""}},
      "justificacion": "KPI: satisfacción promedio del cliente"
    }},
    {{
      "function_name": "period_over_period_growth",
      "parametros": {{"table": "ventas", "date_col": "fecha", "agg_col": "total_venta", "operation": "SUM", "interval": "month"}},
      "justificacion": "Trend mensual para KPI de facturación"
    }},
    {{
      "function_name": "time_series_trend",
      "parametros": {{"table": "ventas", "date_col": "fecha", "agg_col": "total_venta", "operation": "SUM", "interval": "month"}},
      "justificacion": "Tendencia mensual para area chart"
    }},
    {{
      "function_name": "join_and_aggregate",
      "parametros": {{"table1": "ventas", "table2": "productos", "join_col1": "id_producto", "join_col2": "id_producto", "group_col": "categoria", "agg_col": "total_venta", "operation": "SUM", "limit": "10"}},
      "justificacion": "Ventas por categoría — JOIN para obtener nombres"
    }},
    {{
      "function_name": "join_and_aggregate",
      "parametros": {{"table1": "ventas", "table2": "regiones", "join_col1": "id_region", "join_col2": "id_region", "group_col": "region", "agg_col": "total_venta", "operation": "SUM", "limit": "10"}},
      "justificacion": "Ventas por región — JOIN para nombres legibles"
    }},
    {{
      "function_name": "join_and_aggregate",
      "parametros": {{"table1": "ventas", "table2": "clientes", "join_col1": "id_cliente", "join_col2": "id_cliente", "group_col": "tipo_cliente", "agg_col": "total_venta", "operation": "SUM", "limit": "10"}},
      "justificacion": "Ventas por tipo de cliente — Nuevo vs Recurrente"
    }},
    {{
      "function_name": "join_and_aggregate",
      "parametros": {{"table1": "ventas", "table2": "productos", "join_col1": "id_producto", "join_col2": "id_producto", "group_col": "nombre_producto", "agg_col": "total_venta", "operation": "SUM", "limit": "8"}},
      "justificacion": "Top 8 productos — JOIN para nombres legibles"
    }},
    {{
      "function_name": "join_and_aggregate",
      "parametros": {{"table1": "ventas", "table2": "pagos", "join_col1": "id_venta", "join_col2": "id_venta", "group_col": "metodo_pago", "agg_col": "total_venta", "operation": "SUM", "limit": "10"}},
      "justificacion": "Ventas por método de pago"
    }},
    {{
      "function_name": "join_and_aggregate",
      "parametros": {{"table1": "envios", "table2": "regiones", "join_col1": "id_region", "join_col2": "id_region", "group_col": "region", "agg_col": "costo_envio", "operation": "AVG", "limit": "10"}},
      "justificacion": "Costo envío promedio por región — desde tabla envios"
    }},
    {{
      "function_name": "group_by_category",
      "parametros": {{"table": "envios", "group_col": "estado_envio", "agg_col": "costo_envio", "operation": "COUNT", "limit": "10"}},
      "justificacion": "Distribución de estados de envío para donut chart"
    }},
    {{
      "function_name": "join_and_aggregate",
      "parametros": {{"table1": "inventario", "table2": "proveedores", "join_col1": "id_proveedor", "join_col2": "id_proveedor", "group_col": "nombre_proveedor", "agg_col": "stock", "operation": "SUM", "limit": "8"}},
      "justificacion": "Stock total por proveedor — explorando tabla inventario"
    }},
    {{
      "function_name": "find_top_bottom_records",
      "parametros": {{"table": "reseñas", "entity_col": "id_producto", "agg_col": "puntuacion", "operation": "AVG", "n": "5"}},
      "justificacion": "Top/bottom 5 productos por reseña — para insights de calidad"
    }}
  ],
  "message": "COMPLEJIDAD: Grande (10 tablas, ~50 columnas, ~1400 filas). OBJETIVO: 6-8 KPIs, 10-12 gráficos. Diseñador: dataset complejo con 10 tablas interconectadas. Exploré ventas, pagos, envíos, inventario y reseñas. Sugiero: (1) KPI Facturación total con trend, (2) KPI Ticket promedio, (3) KPI Satisfacción promedio, (4) Area chart tendencia mensual, (5) Bar chart ventas por categoría, (6) Bar horizontal ventas por región, (7) Donut tipo de cliente, (8) Bar horizontal top 8 productos, (9) Donut método de pago, (10) Bar horizontal costo envío por región, (11) Donut estados de envío, (12) Bar horizontal stock por proveedor. Insights: categoría líder, región con mayor costo de envío, satisfacción vs ventas, método de pago dominante."
}}"""


def _build_designer_prompt(execution_results: dict) -> str:
    import json

    results_str = json.dumps(execution_results, ensure_ascii=False, indent=2)
    strategy = execution_results.get("estrategia_sugerida", "")

    return f"""Eres un Experto en Visualización de Datos y Diseño de Dashboards. Recibes datos pre-calculados por un sistema analítico y debes generar la configuración JSON de un dashboard profesional y visualmente impactante.

## DATOS Y ESTRATEGIA ANALÍTICA

{results_str}

## ESTRATEGIA SUGERIDA POR EL ARQUITECTO

{strategy}

## PALETAS DE COLORES (elige UNA por gráfico)

Paleta Vibrante:   ["#FF6B6B", "#4ECDC4", "#45B7D1", "#F9A826", "#A855F7", "#10B981"]
Paleta Oceánica:   ["#0EA5E9", "#06B6D4", "#3B82F6", "#6366F1", "#8B5CF6", "#EC4899"]
Paleta Cálida:     ["#F97316", "#EF4444", "#F59E0B", "#84CC16", "#22C55E", "#14B8A6"]
Paleta Neón:       ["#22D3EE", "#A3E635", "#FB923C", "#F472B6", "#818CF8", "#34D399"]

## CATÁLOGO DE GRÁFICOS — MAPEO EXACTO

### Datos de group_by_category → Tipo de gráfico:
- Si ≤5 categorías → chartType: "pie", variant: "doughnut" (más moderno)
- Si 6-8 categorías → chartType: "bar", variant: null (barras verticales)
- Si etiquetas >15 chars → chartType: "bar", variant: "horizontal"

### Datos de time_series_trend → Tipo de gráfico:
- Si >8 puntos → chartType: "line", variant: "area" (relleno bajo la línea)
- Si ≤8 puntos → chartType: "line", variant: null

### Datos de cross_tabulation → Tipo de gráfico:
- SIEMPRE → chartType: "bar", variant: "stacked"
- Usa el campo `series` (no `data`)

### Datos de distribution_bins → Tipo de gráfico:
- SIEMPRE → chartType: "bar", variant: "histogram"
- x_label: nombre del rango, y_label: "Cantidad"

### Datos de correlation_check → Tipo de gráfico:
- SIEMPRE → chartType: "scatter", variant: null
- Usa campos x/y en los data items

### Datos de find_top_bottom_records → Tipo de gráfico:
- Usar solo el array `top` → chartType: "bar", variant: "horizontal"
- Título: "Top N [entidad] por [métrica]"

## REGLAS DE KPIs

- El Arquitecto te indicó la complejidad y el objetivo de KPIs/gráficos en su mensaje — SIGUE esas directivas
- Cada KPI usa una métrica diferente
- Si tienes period_over_period_growth → usa ese valor para trend y trendValue
- format: "currency" si parece dinero, "number" para conteos, "percent" para porcentajes
- NO incluir prefix "$" en currency (el frontend lo agrega)
- trend: "up" | "down" | "neutral" — SOLO si tienes datos reales de crecimiento
- trendValue: "+12.3%" o "-5.1%" — SOLO si tienes el % calculado

## REGLAS DE INSIGHTS (resumen_ejecutivo)

El resumen_ejecutivo debe ser Markdown con bullets accionables.
- Si el dataset es pequeño (≤4 gráficos): 4-6 bullets
- Si el dataset es mediano (5-8 gráficos): 6-8 bullets
- Si el dataset es grande (8+ gráficos): 8-12 bullets

MALO ❌: "Las ventas son altas en Lima"
BUENO ✅: "🔥 Lima lidera con $45,200 representando el 42% del total — concentrar esfuerzos de marketing aquí"

MALO ❌: "Hay correlación entre cantidad y precio"
BUENO ✅: "📊 Correlación cantidad-ventas de 0.72 (alta) — a mayor volumen de unidades, mayor ingreso de forma consistente"

MALO ❌: "El mes de enero fue bueno"
BUENO ✅: "📈 Enero fue el pico con $72,000 (+23% vs diciembre) — investigar qué impulsó ese crecimiento"

Estructura recomendada del resumen:
- 1-2 bullets de hallazgos positivos (🔥 🏆 📈)
- 1-2 bullets de oportunidades o advertencias (⚠️ 📉 💡)
- 1 bullet de correlación o patrón interesante (📊)

## REGLAS DE DISEÑO

- El número total de `graficos` DEBE ser par — obligatorio para el layout (2, 4, 6, 8, 10, 12...)
- La cantidad de gráficos y KPIs DEBE coincidir con el objetivo que el Arquitecto indicó en su mensaje
- Si recibiste 10+ funciones con datos útiles → genera 8-12 gráficos (no te quedes en 4!)
- Si recibiste 7-9 funciones → genera 6-8 gráficos
- Si recibiste 4-6 funciones → genera 2-4 gráficos
- NUNCA inventar valores — usar SOLO los numbers de los resultados analíticos
- Todo gráfico de tipo bar, pie o scatter DEBE tener colorPalette con 4-6 hex codes
- Los gráficos de línea/área NO necesitan colorPalette (el frontend usa el color del tema)
- x_label e y_label son obligatorios cuando el tipo de eje no es obvio
- Títulos de gráficos: concisos, informativos, sin "Gráfico de" al inicio

## EJEMPLOS FEW-SHOT

### Ejemplo — KPI con trend real
Datos recibidos: period_over_period_growth retornó valor_actual=85000, valor_anterior=70000, pct_cambio=21.4

KPI correcto:
{{
  "id": "k1",
  "label": "Ventas del Período",
  "value": 85000,
  "format": "currency",
  "trend": "up",
  "trendValue": "+21.4%"
}}

KPI incorrecto ❌:
{{
  "id": "k1",
  "label": "Ventas",
  "value": 85000,
  "format": "currency",
  "trend": "up",
  "trendValue": "+12%"   ← valor inventado, diferente al calculado
}}

### Ejemplo — Donut chart correcto
Datos recibidos: group_by_category retornó [Lima:9200, Cusco:4800, Arequipa:3100] (3 categorías → usar donut)

Gráfico correcto:
{{
  "id": "g1",
  "chartType": "pie",
  "variant": "doughnut",
  "title": "Ventas por Región",
  "x_label": null,
  "y_label": null,
  "data": [
    {{"name": "Lima", "value": 9200, "x": null, "y": null}},
    {{"name": "Cusco", "value": 4800, "x": null, "y": null}},
    {{"name": "Arequipa", "value": 3100, "x": null, "y": null}}
  ],
  "series": null,
  "colorPalette": ["#FF6B6B", "#4ECDC4", "#45B7D1"]
}}

### Ejemplo — Stacked bar correcto
Datos recibidos: cross_tabulation retornó categorías:[Tech,Ventas,RRHH], series:[{{Senior:[40,25,10]}}, {{Junior:[15,30,20]}}]

Gráfico correcto:
{{
  "id": "g2",
  "chartType": "bar",
  "variant": "stacked",
  "title": "Empleados por Departamento y Nivel",
  "x_label": "Departamento",
  "y_label": "Cantidad",
  "data": null,
  "series": [
    {{"name": "Senior", "data": [{{"name":"Tech","value":40,"x":null,"y":null}},{{"name":"Ventas","value":25,"x":null,"y":null}},{{"name":"RRHH","value":10,"x":null,"y":null}}]}},
    {{"name": "Junior", "data": [{{"name":"Tech","value":15,"x":null,"y":null}},{{"name":"Ventas","value":30,"x":null,"y":null}},{{"name":"RRHH","value":20,"x":null,"y":null}}]}}
  ],
  "colorPalette": ["#4ECDC4", "#FF6B6B"]
}}

### Ejemplo — Scatter chart correcto
Datos recibidos: correlation_check retornó pearson_r=0.72, scatter_points=[{{x:1,y:100}},...]

Gráfico correcto:
{{
  "id": "g3",
  "chartType": "scatter",
  "variant": null,
  "title": "Correlación Cantidad vs Ventas (r=0.72)",
  "x_label": "Cantidad",
  "y_label": "Total Venta",
  "data": [
    {{"name": "p1", "value": 0, "x": 1, "y": 100}},
    {{"name": "p2", "value": 0, "x": 3, "y": 280}}
  ],
  "series": null,
  "colorPalette": ["#4ECDC4"]
}}"""


# ── Step 1: Planificador ──────────────────────────────────────────────


def generate_execution_plan(
    db: Session,
    project_id: int,
    engine: AnalyticsEngine,
    tables_context: list[dict],
) -> dict:
    """Call IA 1 to produce an execution plan.

    Returns the parsed JSON: {ejecutar: [...], message: "..."}.
    """
    client = _get_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    system_prompt = _build_plan_prompt(tables_context)
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": "Genera el plan de ejecución para analizar este dataset. Responde con el JSON.",
        },
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": PLAN_SCHEMA,
        },
        temperature=0.3,
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


# ── Step 2: Middleware Ejecutor ───────────────────────────────────────


def _safe_call(func, params: dict):
    """Call *func* filtering to only its accepted parameter names."""
    sig = inspect.signature(func)
    valid = {k: v for k, v in params.items() if k in sig.parameters}
    return func(**valid)


def execute_plan(plan_json: dict, engine: AnalyticsEngine) -> dict:
    """Dispatch each plan entry to the corresponding AnalyticsEngine method.

    Per-function try/except — pipeline never aborts (REQ-1.7).
    """
    dispatch = {
        "get_column_summary": engine.get_column_summary,
        "calculate_kpi": engine.calculate_kpi,
        "period_over_period_growth": engine.period_over_period_growth,
        "group_by_category": engine.group_by_category,
        "time_series_trend": engine.time_series_trend,
        "cross_tabulation": engine.cross_tabulation,
        "distribution_bins": engine.distribution_bins,
        "find_top_bottom_records": engine.find_top_bottom_records,
        "correlation_check": engine.correlation_check,
        "join_and_aggregate": engine.join_and_aggregate,
    }

    results: list[dict] = []
    for entry in plan_json.get("ejecutar", []):
        fn_name = entry.get("function_name", "")
        params = entry.get("parametros", {})

        handler = dispatch.get(fn_name)
        if handler is None:
            results.append({
                "function": fn_name,
                "status": "error",
                "error": f"Unknown function: {fn_name}",
            })
            continue

        try:
            result = _safe_call(handler, params)
            results.append({"function": fn_name, "status": "ok", "data": result})
        except Exception as exc:
            results.append({"function": fn_name, "status": "error", "error": str(exc)})

    return {
        "resultados_funciones": results,
        "estrategia_sugerida": plan_json.get("message", ""),
    }


# ── Step 3: Diseñador ────────────────────────────────────────────────


def generate_final_dashboard(execution_results: dict) -> dict:
    """Call IA 2 to design the dashboard from analytical results."""
    client = _get_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    system_prompt = _build_designer_prompt(execution_results)
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": "Diseña el dashboard con KPIs y gráficos basándote en los resultados. Responde con el JSON.",
        },
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": DESIGNER_SCHEMA,
        },
        temperature=0.3,
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


# ── Post-processing helpers ───────────────────────────────────────────


def _enforce_even_charts(graficos: list[dict]) -> list[dict]:
    """Drop lowest-value chart if count is odd — layout requires even count."""
    if len(graficos) % 2 == 0 or not graficos:
        return graficos

    # Score each chart by aggregate data value
    scored = [
        (i, sum(item.get("value", 0) for item in (g.get("data") or [])))
        for i, g in enumerate(graficos)
    ]
    drop_idx = min(scored, key=lambda x: x[1])[0]
    return [g for i, g in enumerate(graficos) if i != drop_idx]


def _map_to_widgets(designer_output: dict) -> list[dict]:
    """Map IA 2 output (kpis + graficos) to frontend-compatible widgets[] (AD-6)."""
    widgets: list[dict] = []

    for kpi in designer_output.get("kpis", []):
        widgets.append({**kpi, "type": "kpi", "format": kpi.get("format", "number")})

    for graf in designer_output.get("graficos", []):
        widgets.append({**graf, "type": "chart"})

    return widgets


# ── Orchestrator ──────────────────────────────────────────────────────


def generate_dashboard(
    db: Session,
    project_id: int,
    engine: AnalyticsEngine,
    tables_context: list[dict],
) -> dict:
    """Run the 3-step pipeline and return a dashboard configuration.

    Returns a dict with ``widgets``, ``generated_at``, and ``resumen_ejecutivo``.
    """
    # Step 1 — Planificador
    plan = generate_execution_plan(db, project_id, engine, tables_context)

    # Step 2 — Middleware
    execution_results = execute_plan(plan, engine)

    # Step 3 — Diseñador
    designer_output = generate_final_dashboard(execution_results)

    # Post-process
    graficos = _enforce_even_charts(designer_output.get("graficos", []))
    designer_output["graficos"] = graficos

    # Map to widgets
    widgets = _map_to_widgets(designer_output)

    return {
        "widgets": widgets,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "resumen_ejecutivo": designer_output.get("resumen_ejecutivo", ""),
    }
