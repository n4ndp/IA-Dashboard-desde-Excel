# BACKEND — Arquitectura, Ingesta y Pipeline Multi-Agente

## 1) Visión General

El backend está construido con:

- **FastAPI** (API REST + validación)
- **SQLAlchemy 2.0** (ORM y sesiones)
- **PostgreSQL** (persistencia)
- **pandas / numpy / openpyxl** (ingesta y analítica)
- **OpenAI API** (Planificador y Diseñador con Structured Outputs)

Archivo de entrada:
- `app.py`: define app, CORS y monta routers con prefijo `/api`.

Routers activos:
- `routes/users.py`
- `routes/projects.py`
- `routes/tables.py`
- `routes/generate.py`

---

## 2) Arquitectura de Datos (Modelo Híbrido)

La base sigue una jerarquía relacional clara:

```text
Usuario
  └── Proyecto
        └── Tabla
              ├── Columna
              └── Fila
```

Definición en `models.py`:

- `Usuario(id, nombre)`
- `Proyecto(id, usuario_id, nombre_archivo, fecha_creacion, dashboard_config)`
- `Tabla(id, proyecto_id, nombre_hoja)`
- `Columna(id, tabla_id, nombre, tipo)`
- `Fila(id, tabla_id, orden, data)`

### ¿Qué hace híbrido al modelo?

1. **Relacional para estructura y ownership**
   - permite validar pertenencia `usuario → proyecto → tabla`.

2. **JSON en `Fila.data` para contenido dinámico**
   - cada fila se guarda como objeto clave/valor por nombre de columna.
   - evita migraciones DDL por cada Excel distinto.

3. **`dashboard_config` en `Proyecto`**
   - persiste el JSON final de widgets generado por IA.

Resultado: estabilidad de dominio + flexibilidad para datasets heterogéneos.

---

## 3) Motor de Ingesta (`services/excel_service.py`)

Pipeline de ingesta:

1. `pd.read_excel(..., sheet_name=None, engine="openpyxl")` para leer todas las sheets.
2. Por cada sheet:
   - crea `Tabla`
   - infiere tipos con `infer_column_type(...)`
   - crea registros `Columna`
   - serializa cada fila con `sanitize_value(...)`
   - crea registros `Fila(data=...)`
3. Commit transaccional único por operación de alto nivel.

### Helpers importantes

- `_parse_excel_sheets(...)`: núcleo reutilizado por:
  - `create_project(...)`
  - `add_sheets_to_project(...)`

- `infer_column_type(...)`:
  - detecta `date` / `number` / `string` con reglas de precedence.

- `sanitize_value(...)`:
  - normaliza `NaN`, `NaT`, `Timestamp`, tipos numpy para serializar seguro.

---

## 4) Flujo Agéntico Plan-and-Execute (núcleo del sistema)

Implementado en `services/ai_service.py` con 3 pasos determinísticos:

```text
Step 1 — Planificador (IA)
  generate_execution_plan(...)
  -> output: { ejecutar: [...], message: "..." }

Step 2 — Middleware (Python)
  execute_plan(plan_json, engine)
  -> ejecuta funciones analíticas reales (pandas)
  -> output: { resultados_funciones: [...], estrategia_sugerida: "..." }

Step 3 — Diseñador (IA)
  generate_final_dashboard(execution_results)
  -> output: { resumen_ejecutivo, kpis, graficos }

Post-proceso
  _enforce_even_charts(...)
  _map_to_widgets(...)
```

### 4.1 IA Planificadora

- Usa `PLAN_SCHEMA` con Structured Outputs.
- Analiza contexto de tablas (columnas + muestra de filas).
- Propone operaciones analíticas concretas en `ejecutar`.

### 4.2 Middleware Python (failsafe)

`execute_plan(...)` despacha a `AnalyticsEngine` (`services/analytics_service.py`).

Funciones analíticas principales:

- `get_column_summary`
- `calculate_kpi`
- `period_over_period_growth`
- `group_by_category`
- `time_series_trend`
- `cross_tabulation`
- `distribution_bins`
- `find_top_bottom_records`
- `correlation_check`
- `join_and_aggregate`

Característica clave:
- cada función se ejecuta con manejo de errores por entrada (`status: ok/error`), evitando abortar todo el pipeline por una falla puntual.

### 4.3 IA Diseñadora

- Usa `DESIGNER_SCHEMA` con Structured Outputs.
- Traduce resultados analíticos en configuración visual:
  - KPIs
  - gráficos
  - resumen ejecutivo

### 4.4 Modo Iterativo (Chat)

Además de `generate_dashboard(...)`, existe `iterate_dashboard(...)`:

- reutiliza el mismo pipeline de 3 pasos,
- agrega contexto opcional `user_prompt + current_dashboard`,
- compacta dashboard (`_compact_dashboard`) para evitar prompt overflow,
- permite cambios cosméticos con `"ejecutar": []`.

---

## 5) API Endpoints Principales

### Usuarios
- `POST /api/users`
- `GET /api/users/{user_id}`

### Proyectos
- `GET /api/users/{user_id}/projects`
- `POST /api/users/{user_id}/projects`
- `GET /api/users/{user_id}/projects/{project_id}`
- `PATCH /api/users/{user_id}/projects/{project_id}`
- `DELETE /api/users/{user_id}/projects/{project_id}`
- `POST /api/users/{user_id}/projects/{project_id}/upload`

### Tablas
- `GET /api/users/{user_id}/projects/{project_id}/tables`
- `GET /api/users/{user_id}/projects/{project_id}/tables/{table_id}`
- `DELETE /api/users/{user_id}/projects/{project_id}/tables/{table_id}`

### Dashboards
- `POST /api/users/{user_id}/projects/{project_id}/generate-dashboard`
- `POST /api/users/{user_id}/projects/{project_id}/chat`

Schema de iteración (`schemas.py`):

```python
class IterateDashboardRequest(BaseModel):
    prompt: str = Field(..., min_length=1, strip_whitespace=True)
    current_dashboard: dict[str, Any]
```

---

## 6) Manejo de Sesión y Transacciones

`database.py` expone `get_db()` como dependencia FastAPI:

- abre sesión
- `yield db`
- commit automático al terminar sin error
- rollback ante excepción
- cierre garantizado

Este patrón permite que rutas usen `db.flush()` localmente y deleguen commit final al lifecycle de dependencia.

---

## 7) Buenas Prácticas Aplicadas

- Structured outputs con JSON Schema en llamadas IA.
- Separación por capas (`routes -> services -> models`).
- Validaciones de ownership en rutas.
- Error mapping HTTP consistente (`400/404/408/500/422`).
- Protección de token context en iteración (`_compact_dashboard`).
- Persistencia de dashboard generado para continuidad de usuario.
