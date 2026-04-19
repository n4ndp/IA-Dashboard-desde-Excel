"""AI dashboard generation service.

Implements the OpenAI agent loop that:
  1. Builds a system prompt with dynamic table metadata
  2. Registers 9 analytics tools as OpenAI function calling tools
  3. Runs an agent loop (max 15 iterations, 10 tool calls, 60s timeout)
  4. Validates the output JSON against widget schemas
  5. Returns a DashboardConfig dict
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Any

from openai import OpenAI
from sqlalchemy.orm import Session

from schemas import KpiWidgetSchema, ChartWidgetSchema, InsightWidgetSchema
from services.analytics_service import AnalyticsEngine

# ── Constants ─────────────────────────────────────────────────────────

MAX_ITERATIONS = 15
MAX_TOOL_CALLS = 10
TIMEOUT_SECONDS = 60

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


# ── Tool definitions (OpenAI function calling format) ─────────────────

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_columns",
            "description": "Obtiene las columnas de una tabla con sus nombres y tipos (string, number, date)",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": ["integer", "string"],
                        "description": "ID de la tabla. Puede ser un entero (tabla real) o un string como 'v_1' (tabla virtual de un join)",
                    },
                },
                "required": ["table_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_sample",
            "description": "Obtiene una muestra de filas de una tabla para entender los datos",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": ["integer", "string"],
                        "description": "ID de la tabla (real o virtual)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Cantidad de filas a retornar (default: 50, max: 200)",
                        "default": 50,
                    },
                },
                "required": ["table_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_rows",
            "description": "Cuenta el total de filas en una tabla",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": ["integer", "string"],
                        "description": "ID de la tabla (real o virtual)",
                    },
                },
                "required": ["table_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aggregate",
            "description": "Calcula una agregación (SUM, AVG, MAX, MIN, COUNT) sobre una columna numérica",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": ["integer", "string"],
                        "description": "ID de la tabla (real o virtual)",
                    },
                    "column": {
                        "type": "string",
                        "description": "Nombre de la columna numérica",
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["SUM", "AVG", "MAX", "MIN", "COUNT"],
                        "description": "Operación de agregación",
                    },
                },
                "required": ["table_id", "column", "operation"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "group_by",
            "description": "Agrupa filas por una columna categórica y calcula una agregación sobre una columna numérica. Retorna los grupos ordenados por valor descendente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": ["integer", "string"],
                        "description": "ID de la tabla (real o virtual)",
                    },
                    "group_column": {
                        "type": "string",
                        "description": "Columna categórica para agrupar",
                    },
                    "agg_column": {
                        "type": "string",
                        "description": "Columna numérica para agregar",
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["SUM", "AVG", "MAX", "MIN", "COUNT"],
                        "description": "Operación de agregación",
                    },
                },
                "required": ["table_id", "group_column", "agg_column", "operation"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter",
            "description": "Filtra filas de una tabla por una condición sobre una columna",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": ["integer", "string"],
                        "description": "ID de la tabla (real o virtual)",
                    },
                    "column": {
                        "type": "string",
                        "description": "Columna a filtrar",
                    },
                    "operator": {
                        "type": "string",
                        "enum": ["eq", "neq", "gt", "gte", "lt", "lte", "contains", "starts_with"],
                        "description": "Operador de comparación",
                    },
                    "value": {
                        "description": "Valor a comparar",
                    },
                },
                "required": ["table_id", "column", "operator", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "distinct_values",
            "description": "Obtiene valores únicos de una columna y su frecuencia, ordenados por frecuencia descendente",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": ["integer", "string"],
                        "description": "ID de la tabla (real o virtual)",
                    },
                    "column": {
                        "type": "string",
                        "description": "Nombre de la columna",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Máximo de valores a retornar (default: 20)",
                        "default": 20,
                    },
                },
                "required": ["table_id", "column"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "date_range",
            "description": "Obtiene la fecha mínima, máxima y el rango en días de una columna tipo date",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": ["integer", "string"],
                        "description": "ID de la tabla (real o virtual)",
                    },
                    "column": {
                        "type": "string",
                        "description": "Nombre de la columna tipo date",
                    },
                },
                "required": ["table_id", "column"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "join_tables",
            "description": "Junta dos tablas por una columna en común, generando una tabla virtual temporal. Las tools posteriores pueden usar el virtual_table_id retornado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "left_table_id": {
                        "type": ["integer", "string"],
                        "description": "ID de la tabla izquierda",
                    },
                    "right_table_id": {
                        "type": ["integer", "string"],
                        "description": "ID de la tabla derecha",
                    },
                    "left_column": {
                        "type": "string",
                        "description": "Columna de la tabla izquierda para el join",
                    },
                    "right_column": {
                        "type": "string",
                        "description": "Columna de la tabla derecha para el join",
                    },
                    "join_type": {
                        "type": "string",
                        "enum": ["inner", "left", "right"],
                        "description": "Tipo de join (default: inner)",
                        "default": "inner",
                    },
                },
                "required": ["left_table_id", "right_table_id", "left_column", "right_column"],
            },
        },
    },
]


# ── System prompt builder ─────────────────────────────────────────────

def _build_system_prompt(tables_context: list[dict]) -> str:
    """Build the system prompt with dynamic table metadata.

    Args:
        tables_context: List of table summary dicts with id, sheet_name, columns, rows, row_count.
    """
    # Build table summaries for injection
    table_descriptions = []
    for t in tables_context:
        cols = ", ".join(f"{c['name']}({c['type']})" for c in t.get("columns", []))
        sample_lines = []
        for row in t.get("rows", [])[:5]:
            sample_lines.append("    " + json.dumps(row, ensure_ascii=False, default=str))
        sample_str = "\n".join(sample_lines) if sample_lines else "    (no data)"

        table_descriptions.append(
            f"- Tabla '{t['sheet_name']}' (id={t['id']}): {t.get('row_count', '?')} filas\n"
            f"  Columnas: {cols}\n"
            f"  Muestra:\n{sample_str}"
        )

    tables_block = "\n".join(table_descriptions)

    return f"""Eres un analista de datos experto. Tu trabajo es analizar las tablas del proyecto y generar un dashboard con widgets (gráficos, KPIs e insights).

## TABLAS DEL PROYECTO

{tables_block}

## REGLAS

1. Máximo 5 gráficos (charts)
2. Siempre incluir al menos 1-2 KPIs
3. Incluir 2-4 insights con emoji y severity
4. Si hay una columna de fecha → incluir al menos un line chart
5. Si hay categoría + número → incluir bar chart
6. NO usar pie chart si hay más de 6 categorías distintas
7. Barras apiladas (stacked) cuando hay 2+ series por categoría
8. Barras horizontales (horizontal) cuando las etiquetas de categoría son largas (>20 caracteres)
9. Los insights deben ser accionables, no obvios ("La tabla tiene datos" = malo)
10. Mezclar severities en los insights (no todos "info")
11. Usar variantes de gráfico cuando sea apropiado (stacked, horizontal, multi, area, doughnut)

## FORMATO DE SALIDA

Responde ÚNICAMENTE con un JSON válido con esta estructura exacta:

{{
  "widgets": [
    {{
      "id": "kpi1",
      "type": "kpi",
      "label": "Total Ventas",
      "value": 150000,
      "format": "currency",
      "prefix": "$",
      "trend": "up",
      "trendValue": "+12%"
    }},
    {{
      "id": "w1",
      "type": "chart",
      "chartType": "bar",
      "variant": "stacked",
      "title": "Ventas por Categoría",
      "x": "categoría",
      "series": [
        {{"name": "Hombre", "data": [{{"name": "Ropa", "value": 5000}}, {{"name": "Calzado", "value": 3200}}]}},
        {{"name": "Mujer", "data": [{{"name": "Ropa", "value": 4500}}, {{"name": "Calzado", "value": 2800}}]}}
      ]
    }},
    {{
      "id": "w2",
      "type": "chart",
      "chartType": "line",
      "variant": "area",
      "title": "Tendencia de Ventas",
      "x": "fecha",
      "data": [{{"name": "Ene", "value": 12000}}, {{"name": "Feb", "value": 15000}}]
    }},
    {{
      "id": "w3",
      "type": "chart",
      "chartType": "pie",
      "variant": "doughnut",
      "title": "Distribución por Categoría",
      "data": [{{"name": "Ropa", "value": 45}}, {{"name": "Calzado", "value": 30}}]
    }},
    {{
      "id": "i1",
      "type": "insight",
      "emoji": "🔥",
      "content": "El producto más vendido es X con Y unidades",
      "severity": "positive"
    }},
    {{
      "id": "i2",
      "type": "insight",
      "emoji": "⚠️",
      "content": "Marzo tuvo una caída del 12% respecto a febrero",
      "severity": "warning"
    }}
  ]
}}

### Campos por tipo de widget:

**KPI**: id, type="kpi", label, value (number), format ("currency"|"number"|"percent"), prefix? (ej: "$"), suffix? (ej: "unidades"), trend? ("up"|"down"|"neutral"), trendValue? (ej: "+12%")

**Chart**: id, type="chart", chartType ("bar"|"line"|"pie"), variant? ("stacked"|"grouped"|"horizontal"|"multi"|"area"|"doughnut"), title, x?, y?, data? ([{{name, value}}]), series? ([{{name, data: [{{name, value}}]}}]), orientation? ("horizontal"), areaStyle? ({{}})

**Insight**: id, type="insight", emoji (1 emoji), content (texto descriptivo accionable), severity ("positive"|"negative"|"warning"|"info")

IMPORTANTE: Responde SOLO con el JSON, sin markdown, sin bloques de código, sin texto adicional."""


# ── Output validation ─────────────────────────────────────────────────

def _validate_widget(widget: dict) -> str | None:
    """Validate a single widget against its schema.

    Returns an error message string if invalid, or None if valid.
    """
    widget_type = widget.get("type")
    if widget_type == "kpi":
        try:
            KpiWidgetSchema(**widget)
        except Exception as exc:
            return f"KPI widget validation error: {exc}"
    elif widget_type == "chart":
        try:
            ChartWidgetSchema(**widget)
        except Exception as exc:
            return f"Chart widget validation error: {exc}"
    elif widget_type == "insight":
        try:
            InsightWidgetSchema(**widget)
        except Exception as exc:
            return f"Insight widget validation error: {exc}"
    else:
        return f"Unknown widget type: {widget_type}"
    return None


def _validate_dashboard_config(config: dict) -> str | None:
    """Validate a full dashboard config.

    Returns an error message if invalid, or None if valid.
    """
    if "widgets" not in config:
        return "Missing 'widgets' field"
    if not isinstance(config["widgets"], list):
        return "'widgets' must be an array"

    for i, widget in enumerate(config["widgets"]):
        if not isinstance(widget, dict):
            return f"Widget at index {i} is not an object"
        error = _validate_widget(widget)
        if error:
            return f"Widget {i} ({widget.get('id', 'unknown')}): {error}"

    return None


# ── JSON extraction from AI response ──────────────────────────────────

def _extract_json(content: str) -> dict | None:
    """Extract JSON from AI response content.

    Handles cases where AI wraps JSON in markdown code blocks.
    """
    text = content.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try stripping markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    return None


# ── Main generation function ──────────────────────────────────────────

def generate_dashboard(
    db: Session,
    project_id: int,
    engine: AnalyticsEngine,
    tables_context: list[dict],
) -> dict:
    """Run the AI agent loop to generate a dashboard configuration.

    Args:
        db: SQLAlchemy session.
        project_id: The project ID.
        engine: AnalyticsEngine instance for tool execution.
        tables_context: Table metadata for system prompt injection.

    Returns:
        A dict with `widgets` and `generated_at`.

    Raises:
        TimeoutError: If generation exceeds the timeout limit.
        ValueError: If the AI fails to produce valid output.
    """
    client = _get_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Build system prompt
    system_prompt = _build_system_prompt(tables_context)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
    ]

    start_time = time.monotonic()
    tool_calls_count = 0
    dashboard_config = None

    for iteration in range(MAX_ITERATIONS):
        # Check timeout
        elapsed = time.monotonic() - start_time
        if elapsed >= TIMEOUT_SECONDS:
            raise TimeoutError("Dashboard generation timed out")

        # Call OpenAI
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=0.3,
        )

        msg = response.choices[0].message

        # Append assistant message to conversation
        assistant_msg: dict[str, Any] = {"role": "assistant"}
        if msg.content:
            assistant_msg["content"] = msg.content
        if msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]
        messages.append(assistant_msg)

        # Handle tool calls
        if msg.tool_calls:
            tool_calls_count += len(msg.tool_calls)

            # Check tool call limit
            if tool_calls_count > MAX_TOOL_CALLS:
                # Force generation with available data
                messages.append({
                    "role": "user",
                    "content": "Genera el dashboard ahora con los datos que tienes. Responde SOLO con el JSON.",
                })
                continue

            # Execute each tool call
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}

                result = engine.execute_tool(tc.function.name, args)
                result_str = json.dumps(result, ensure_ascii=False, default=str)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_str,
                })

            continue  # Go to next iteration to let AI process tool results

        # No tool calls — try to parse as final JSON output
        if msg.content:
            parsed = _extract_json(msg.content)
            if parsed is not None:
                validation_error = _validate_dashboard_config(parsed)
                if validation_error is None:
                    dashboard_config = parsed
                    break
                else:
                    # Re-prompt once with error details
                    retry_msg = {
                        "role": "user",
                        "content": f"El JSON es inválido: {validation_error}. Corrige y retorna el JSON válido. Responde SOLO con el JSON corregido.",
                    }
                    messages.append(retry_msg)

                    # One retry call
                    retry_response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        tools=TOOL_DEFINITIONS,
                        tool_choice="auto",
                        temperature=0.2,
                    )
                    retry_msg_content = retry_response.choices[0].message.content
                    if retry_msg_content:
                        retry_parsed = _extract_json(retry_msg_content)
                        if retry_parsed is not None:
                            retry_error = _validate_dashboard_config(retry_parsed)
                            if retry_error is None:
                                dashboard_config = retry_parsed
                                break

                    # If retry also failed, try one more forced generation
                    break

    # If loop exhausted without valid output, try one forced generation
    if dashboard_config is None:
        messages.append({
            "role": "user",
            "content": "Genera el dashboard ahora con los datos que tienes. Responde SOLO con el JSON de widgets.",
        })
        try:
            forced_response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
            )
            forced_content = forced_response.choices[0].message.content
            if forced_content:
                forced_parsed = _extract_json(forced_content)
                if forced_parsed is not None:
                    _validate_dashboard_config(forced_parsed)  # Best effort
                    dashboard_config = forced_parsed
        except Exception:
            pass

    if dashboard_config is None:
        raise ValueError("AI failed to generate a valid dashboard configuration")

    # Add generated_at timestamp
    dashboard_config["generated_at"] = datetime.now(timezone.utc).isoformat()

    return dashboard_config
