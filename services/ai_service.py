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
    """Build the Planificador system prompt with table metadata."""
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

    return f"""Eres un planificador de análisis de datos experto. Analiza las tablas y determina qué funciones ejecutar para generar insights de máximo valor.

## TABLAS DEL PROYECTO

{tables_block}

## FUNCIONES DISPONIBLES

1. get_column_summary(table, column) — resumen de columna (min, max, nulos, únicos, top3)
2. calculate_kpi(table, agg_col, operation, filter_col, filter_val) — KPI agregado [SUM|AVG|MAX|MIN|COUNT], filtro opcional
3. period_over_period_growth(table, date_col, agg_col, operation, interval) — crecimiento vs periodo anterior [month|quarter|year]
4. group_by_category(table, group_col, agg_col, operation, limit) — agrupar por categoría [{{name, value}}]
5. time_series_trend(table, date_col, agg_col, operation, interval) — serie temporal [{{period, value}}]
6. cross_tabulation(table, group_col_1, group_col_2, agg_col, operation, limit) — tabla cruzada {{categories, series}}
7. distribution_bins(table, numeric_col, bins) — distribución en rangos [{{range, count}}]
8. find_top_bottom_records(table, entity_col, agg_col, operation, n) — top/bottom N {{top, bottom}}
9. correlation_check(table, num_col_1, num_col_2) — correlación Pearson + puntos scatter
10. join_and_aggregate(table1, table2, join_col1, join_col2, group_col, agg_col, operation, limit) — join + agregación

## REGLAS

1. Selecciona 4-8 funciones que maximicen los insights del dataset
2. Si hay columna de fecha → incluye time_series_trend y period_over_period_growth
3. Si hay columna numérica → incluye calculate_kpi y distribution_bins
4. Si hay categoría + número → incluye group_by_category
5. Si hay 2+ columnas numéricas → incluye correlation_check
6. El parámetro `table` usa el sheet_name de las tablas listadas arriba
7. Todos los valores de parámetros deben ser strings
8. El campo `message` describe tu estrategia para el diseñador del dashboard"""


def _build_designer_prompt(execution_results: dict) -> str:
    """Build the Diseñador system prompt with analytical results."""
    results_str = json.dumps(execution_results, ensure_ascii=False, default=str, indent=2)
    strategy = execution_results.get("estrategia_sugerida", "")

    return f"""Eres un diseñador de dashboards experto. Recibirás los resultados de análisis estadísticos y debes diseñar un dashboard profesional con KPIs y gráficos.

## RESULTADOS DE ANÁLISIS

{results_str}

## ESTRATEGIA DEL PLANIFICADOR

{strategy}

## REGLAS

1. Genera 2-4 KPIs relevantes con valores concretos extraídos de los resultados
2. Genera un número PAR de gráficos (2, 4, 6 o 8)
3. Tipos de chartType: bar, line, pie, scatter
4. Variantes: stacked, horizontal, area, doughnut, histogram
5. Cada gráfico DEBE incluir colorPalette: array de 4-6 hex codes (#RRGGBB)
6. Pie chart SOLO si ≤5 categorías en los datos, si no usar bar
7. scatter chart para datos de correlación — usa campos x/y en los data items
8. histogram variant para datos de distribución — rangos como labels (name)
9. El resumen_ejecutivo debe ser en Markdown con 3-5 bullets de insights clave
10. Formatos KPI: "currency", "number", "percent"
11. trend: "up", "down" o "neutral"
12. x_label e y_label describen los ejes del gráfico"""


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
    """Drop lowest-value chart if count is odd (AD-3)."""
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
