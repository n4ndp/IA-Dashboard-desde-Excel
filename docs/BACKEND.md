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
- `routes/users.py` — gestión de usuarios
- `routes/projects.py` — CRUD de proyectos + upload de Excel
- `routes/tables.py` — consulta y eliminación de tablas
- `routes/generate.py` — generación e iteración de dashboards

---

## 2) Arquitectura de Datos (Modelo Híbrido)

La base sigue una jerarquía relacional clara:

```text
Usuario
  └── Proyecto
        └── Tabla
              ├── Columna (tipo inferido)
              └── Fila (data JSONB)
```

Definición en `models.py`:

- `Usuario(id, nombre)`
- `Proyecto(id, usuario_id, nombre_archivo, fecha_creacion, dashboard_config)`
- `Tabla(id, proyecto_id, nombre_hoja)`
- `Columna(id, tabla_id, nombre, tipo)`
- `Fila(id, tabla_id, orden, data)`

### ¿Qué hace híbrido al modelo?

1. **Relacional para estructura y ownership**
   - Permite validar pertenencia `usuario → proyecto → tabla`.
   - Queries eficientes por ownership y joins.

2. **JSONB en `Fila.data` para contenido dinámico**
   - Cada fila se guarda como objeto clave/valor por nombre de columna.
   - Evita migraciones DDL por cada Excel distinto.
   - Permite consultas flexibles sobre campos JSON.

3. **`dashboard_config` en `Proyecto`**
   - Persiste el JSON final de widgets generado por IA.
   - Incluye `generated_at` para control de versión.

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
  - `create_project(...)` — primer upload
  - `add_sheets_to_project(...)` — uploads adicionales al mismo proyecto

- `infer_column_type(...)`:
  - Detecta `date` / `number` / `string` con reglas de precedencia.

- `sanitize_value(...)`:
  - Normaliza `NaN`, `NaT`, `Timestamp`, tipos numpy para serializar seguro.

---

## 4) Flujo Agéntico Plan-and-Execute (núcleo del sistema)

Implementado en `services/ai_service.py` con 3 pasos determinísticos:

```text
Step 1 — Planificador (IA)
  generate_execution_plan(...)
  → Analiza columnas + muestra de filas
  → Output: { ejecutar: [...funciones], message: "..." }

Step 2 — Middleware (Python/pandas)
  execute_plan(plan_json, engine)
  → Ejecuta funciones analíticas reales
  → Output: { resultados_funciones: [...], estrategia_sugerida: "..." }

Step 3 — Diseñador (IA)
  generate_final_dashboard(execution_results)
  → Transforma resultados en widgets de dashboard
  → Output: { resumen_ejecutivo, kpis, graficos, accion_realizada }

Post-proceso
  _enforce_even_charts(...)  → garantiza cantidad par de gráficos
  _map_to_widgets(...)       → convierte a formato de widgets
```

### 4.1 IA Planificadora (`_build_plan_prompt`)

- Usa `PLAN_SCHEMA` con Structured Outputs (`strict: True`).
- Analiza contexto de tablas (columnas + muestra de filas).
- Propone operaciones analíticas concretas en `ejecutar`.
- En modo iteración: recibe JSON completo del dashboard actual con reglas de modificación estrictas.

### 4.2 Middleware Python (`services/analytics_service.py`)

`execute_plan(...)` despacha a `AnalyticsEngine`.

Funciones analíticas principales:

| Función | Qué hace |
|---------|----------|
| `get_column_summary` | Estadísticas descriptivas de una columna |
| `calculate_kpi` | Cálculo de KPI con agregación configurable |
| `period_over_period_growth` | Crecimiento entre períodos |
| `group_by_category` | Agrupación y agregación por categoría |
| `time_series_trend` | Tendencia temporal |
| `cross_tabulation` | Tabulación cruzada entre dos columnas |
| `distribution_bins` | Distribución en bins/histograma |
| `find_top_bottom_records` | Top N y Bottom N registros |
| `correlation_check` | Correlación entre dos variables |
| `join_and_aggregate` | Join entre tablas + agregación |

Características:
- Cada función se ejecuta con manejo de errores individual (`status: ok/error`).
- Una falla puntual no aborta todo el pipeline.
- Soporte para **tablas virtuales** (resultados intermedios almacenados como DataFrames en memoria).
- SQL parametrizado via SQLAlchemy `text()` con bind variables contra JSONB.

### 4.3 IA Diseñadora (`_build_designer_prompt`)

- Usa `DESIGNER_SCHEMA` con Structured Outputs (`strict: True`).
- Traduce resultados analíticos en configuración visual:
  - **KPIs**: valor, formato, tendencia, trendValue
  - **Gráficos**: chartType, variant, data/series, colorPalette
  - **Insights**: emoji, content, severity
  - **Resumen ejecutivo**: descripción narrativa de los datos
- En modo iteración: recibe JSON completo con reglas de preservación quirúrgica.

### 4.4 Modo Iterativo (Chat)

`iterate_dashboard(...)` reutiliza el mismo pipeline de 3 pasos con contexto adicional:

- Se envía el **dashboard completo sin truncar** (no se usa `_compact_dashboard()`).
- El Planificador recibe reglas de "modificación quirúrgica":
  - Alcance estricto sobre lo que el usuario pidió
  - Cambios cosméticos → `ejecutar: []`
  - Cambios de datos → solo funciones necesarias
  - No expandir alcance, no reemplazar estrategia existente

- El Diseñador recibe 3 bloques de reglas:
  - **REGLAS DE PRESERVACIÓN** (5): copia fiel por ID, estabilidad de IDs, datos exactos, cambios cosméticos puntuales, datos nuevos = widgets adicionales
  - **REGLAS NEGATIVAS** (6): no mejorar, no cambiar colores, no reescribir títulos, no reordenar, no cambiar tipos, no recalcular
  - **REGLAS DE ESTRUCTURA** (3): total de gráficos par, IDs incrementales para nuevos, `accion_realizada` descriptiva

- **`accion_realizada`**: campo en `DESIGNER_SCHEMA` que confirma qué cambió y qué preservó. Se devuelve al frontend como `action_message`.

---

## 5) API Endpoints

### Usuarios

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/users` | Crear o reutilizar usuario por nombre |

### Proyectos

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/users/{user_id}/projects` | Listar proyectos |
| `POST` | `/api/users/{user_id}/projects` | Crear proyecto subiendo Excel |
| `GET` | `/api/users/{user_id}/projects/{project_id}` | Detalle del proyecto |
| `PATCH` | `/api/users/{user_id}/projects/{project_id}` | Renombrar proyecto |
| `DELETE` | `/api/users/{user_id}/projects/{project_id}` | Eliminar proyecto |
| `POST` | `/api/users/{user_id}/projects/{project_id}/upload` | Agregar sheets al proyecto |

### Tablas

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/users/{user_id}/projects/{project_id}/tables` | Listar tablas |
| `GET` | `/api/users/{user_id}/projects/{project_id}/tables/{table_id}` | Ver datos de tabla |
| `DELETE` | `/api/users/{user_id}/projects/{project_id}/tables/{table_id}` | Eliminar tabla |

### Dashboards

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/users/{user_id}/projects/{project_id}/generate-dashboard` | Generar dashboard |
| `POST` | `/api/users/{user_id}/projects/{project_id}/chat` | Iterar por chat |

Schema de iteración (`schemas.py`):

```python
class IterateDashboardRequest(BaseModel):
    prompt: str = Field(..., min_length=1, strip_whitespace=True)
    current_dashboard: dict[str, Any]
```

Schema de respuesta:

```python
class GenerateDashboardResponse(BaseModel):
    widgets: list[dict[str, Any]]
    generated_at: datetime
    resumen_ejecutivo: str | None = None
    action_message: str | None = None  # Solo en iteración
```

---

## 6) Manejo de Sesión y Transacciones

`database.py` expone `get_db()` como dependencia FastAPI:

- Abre sesión
- `yield db`
- Commit automático al terminar sin error
- Rollback ante excepción
- Cierre garantizado

Las rutas usan `db.flush()` para obtener IDs generados y delegan el commit final al lifecycle de dependencia.

---

## 7) Schemas Pydantic (`schemas.py`)

| Schema | Uso |
|--------|-----|
| `UserCreate` | Request body para crear usuario |
| `UserResponse` | Response de usuario |
| `ProjectUploadResponse` | Response post-upload con tablas resumidas |
| `SingleTableResponse` | Detalle de tabla con columnas + filas |
| `GenerateDashboardResponse` | Response de generación/iteración |
| `IterateDashboardRequest` | Request body para chat iterativo |
| `ProjectDetail` | Detalle completo con tablas y dashboard |
| `DashboardConfigSchema` | Estructura del dashboard persistido |

---

## 8) Buenas Prácticas Aplicadas

- **Structured Outputs** con JSON Schema en llamadas IA — cero parsing manual.
- **Separación por capas** (`routes → services → models`).
- **Validaciones de ownership** en rutas (usuario → proyecto → tabla).
- **Error mapping HTTP** consistente (`400/404/408/500/422`).
- **Pipeline determinístico** en lugar de agente único — control total, sin timeouts.
- **Funciones analíticas con error handling individual** — una falla no aborta todo.
- **Iteración quirúrgica** — reglas de preservación + negativas para cambios precisos.
- **Persistencia de dashboard** para continuidad del usuario entre sesiones.
