<div align="center">

# IA Dashboard desde Excel

![Vue.js](https://img.shields.io/badge/Vue.js-3.5-42b883?logo=vuedotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o-412991?logo=openai&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?logo=amazonaws&logoColor=white)

**Subí un Excel. Obtené un dashboard interactivo con KPIs, gráficos y resumen ejecutivo generado por IA.**

**Iterá por chat para modificarlo sin empezar de cero.**

[Ver App en Vivo](http://3.129.10.23:5173) · [API Docs (Swagger)](http://3.129.10.23:8000/docs) · [Presentación del Usuario](docs/PRESENTACION.md)

</div>

---

## Vista Rápida

<p align="center">
  <img src="img/bienvenido.png" width="45%" alt="Login">
  <img src="img/analisis-generado.png" width="45%" alt="Dashboard generado">
</p>
<p align="center">
  <img src="img/pedir-cambio.png" width="45%" alt="Chat iterativo">
  <img src="img/resultado-cambio.png" width="45%" alt="Resultado del cambio">
</p>

---

## Tabla de Contenidos

- [Problema y Solución](#-problema-y-solución)
- [Funcionalidades](#-funcionalidades)
- [Arquitectura](#-arquitectura)
- [Modelo de Datos](#-modelo-de-datos)
- [Pipeline IA](#-pipeline-ia-agéntico-determinístico)
- [Decisiones de Ingeniería](#-decisiones-de-ingeniería)
- [Stack Tecnológico](#-stack-tecnológico)
- [Quickstart](#-quickstart-docker)
- [API Endpoints](#-api-endpoints)
- [Variables de Entorno](#-variables-de-entorno)
- [Herramientas de Desarrollo](#-herramientas-de-desarrollo)
- [Documentación Técnica](#-documentación-técnica)

---

## Problema y Solución

**Problema:** Construir dashboards analíticos desde archivos Excel requiere limpieza manual, modelado, queries y diseño visual. Es un proceso lento, repetitivo y propenso a errores.

**Solución:** Automatización de punta a punta:

1. **Subís** un `.xlsx` (una o varias hojas).
2. **El backend** infiere tipos, estructura y persiste todo.
3. **Un pipeline IA + Python** decide y ejecuta análisis matemáticos reales.
4. **Se genera** un dashboard con KPIs, gráficos e insights.
5. **Iterás por chat** para modificar el dashboard sin empezar de cero.

---

## Funcionalidades

### Ingesta Dinámica de Excel

- Lectura de múltiples sheets con `pandas` + `openpyxl`.
- Inferencia automática de tipos por columna (`string | number | date`).
- Soporte para agregar más Excel a un proyecto existente — todas las tablas cuentan como parte del mismo proyecto.
- Persistencia en modelo híbrido: relacional para estructura + JSONB para datos dinámicos.

### Dashboard Automático con IA

- Pipeline de 3 pasos determinístico (Planificador → Middleware → Diseñador).
- KPIs con formato, tendencia y valor de tendencia.
- Gráficos ECharts: bar, line, pie, scatter, doughnut, area, horizontal, stacked.
- Insights automáticos con severidad (positive, negative, warning, info).
- Resumen ejecutivo generado por IA (se muestra como banner al generar).

### Chat Iterativo

- Modificá tu dashboard por chat en lenguaje natural.
- El AI entiende el dashboard actual y hace **modificaciones quirúrgicas** — solo cambia lo que pedís.
- Cambios cosméticos (colores, títulos) no requieren recalcular datos.
- Cambios de datos ejecutan nuevas funciones analíticas reales.
- Acción realizada confirmada por el AI para transparencia.

### Proyectos y Datos

- Jerarquía: `Usuario → Proyecto → Tabla → Columna/Fila`.
- Tablas expandibles/colapsables con vista previa.
- Eliminación individual de tablas.
- Renombrado de proyectos.

---

## Arquitectura

```text
┌──────────────────────────────────────────────────────────┐
│                    Frontend (Vue 3)                      │
│  LoginView → ProjectsView → DashboardView                │
│  ┌─────────┐  ┌─────────────┐  ┌───────────────────┐     │
│  │ Datos   │  │  Análisis   │  │  Chat Overlay     │     │
│  │ Tab     │  │  Tab        │  │  (iteración)      │     │
│  └─────────┘  └─────────────┘  └───────────────────┘     │
│         │            │                │                  │
│         └────────────┼────────────────┘                  │
│                      │ /api/*                            │
│              Nginx (proxy)                               │
└──────────────────────┼───────────────────────────────────┘
                       │
┌──────────────────────┼───────────────────────────────────┐
│              Backend (FastAPI)                           │
│                      │                                   │
│  ┌───────────┐  ┌────┴─────┐  ┌───────────────────┐      │
│  │ Routes    │→ │Services  │→ │ AI Pipeline       │      │
│  │           │  │          │  │ Planificador (IA) │      │
│  │ users     │  │ excel    │  │      ↓            │      │
│  │ projects  │  │ analytics│  │ Middleware (PY)   │      │
│  │ tables    │  │ ai       │  │      ↓            │      │
│  │ generate  │  │          │  │ Diseñador (IA)    │      │
│  └───────────┘  └──────────┘  └───────────────────┘      │
│                      │                                   │
│              ┌───────┴───────┐                           │
│              │  PostgreSQL   │                           │
│              │  (JSONB)      │                           │
│              └───────────────┘                           │
└──────────────────────────────────────────────────────────┘
```

### Servicios Docker

| Servicio | Tecnología | Puerto |
|----------|------------|--------|
| `frontend` | Node 20 → Nginx Alpine | 5173 |
| `backend` | Python 3.12 + Uvicorn | 8000 |
| `postgres` | PostgreSQL 15 Alpine | 5432 |
| `adminer` | Adminer (DB UI) | 8080 |

---

## Modelo de Datos

![Modelo de Datos](img/modeloER.png)

### Por qué este modelo híbrido

| Aspecto | Enfoque | Razón |
|---------|---------|-------|
| **Estructura** | Relacional (SQL) | Valida pertenencia `usuario → proyecto → tabla`, queries eficientes por ownership |
| **Contenido** | JSONB en `Fila.data` | Cada Excel tiene columnas diferentes — sin migraciones DDL por cada archivo |
| **Dashboard** | JSON en `Proyecto.dashboard_config` | Schema flexible que evoluciona con los widgets sin alterar la tabla |

**Resultado:** Estabilidad del dominio + flexibilidad para datasets heterogéneos.

---

## Pipeline IA: Agéntico Determinístico

La decisión arquitectónica central: **NO usar un único loop agéntico**. En su lugar, un pipeline de 3 pasos determinísticos donde la IA planifica pero Python ejecuta los números.

```text
┌─────────────────────────────────────────────────────────┐
│  Paso 1 — PLANIFICADOR (IA)                             │
│  "Dados los datos y columnas, ¿qué análisis ejecutar?"  │
│  → Output: { ejecutar: [...funciones], message }        │
│  → Usa Structured Outputs con JSON Schema               │
├─────────────────────────────────────────────────────────┤
│  Paso 2 — MIDDLEWARE (Python/pandas)                    │
│  Ejecuta funciones analíticas REALES:                   │
│  • get_column_summary    • group_by_category            │
│  • calculate_kpi         • time_series_trend            │
│  • period_over_period    • distribution_bins            │
│  • correlation_check     • find_top_bottom              │
│  • cross_tabulation      • join_and_aggregate           │
│  → Output: { resultados_funciones: [...] }              │
│  → Cada función con manejo de errores individual        │
├─────────────────────────────────────────────────────────┤
│  Paso 3 — DISEÑADOR (IA)                                │
│  "Transformá los resultados en widgets de dashboard"    │
│  → Output: { resumen_ejecutivo, kpis, graficos }        │
│  → Usa Structured Outputs con DESIGNER_SCHEMA (strict)  │
└─────────────────────────────────────────────────────────┘
         │
         ▼
  Post-proceso: _map_to_widgets (kpis + graficos + insights)
```

### Por qué determinístico y no agéntico

| Agente único | Pipeline determinístico |
|-------------|------------------------|
| Riesgo de timeouts | Control total del flujo |
| Alucinaciones numéricas | Python ejecuta los números reales |
| Difícil de debuggear | Cada paso es auditable |
| Output impredecible | Contratos estables via JSON Schema |

---

## Decisiones de Ingeniería

### 1. Pipeline determinístico de 3 pasos en lugar de agente único

**Problema:** Un agente único tendía a timeouts y alucinaciones numéricas — inventaba datos en vez de calcularlos.

**Solución:** La IA planifica qué análisis ejecutar, pero Python ejecuta las funciones analíticas reales. La IA nunca toca los números — solo decide qué calcular y cómo visualizarlo.

### 2. Structured Outputs con JSON Schema

**Problema:** Parsear texto libre de la IA es frágil — una coma fuera de lugar rompe todo.

**Solución:** `PLAN_SCHEMA` y `DESIGNER_SCHEMA` con `strict: True` garantizan que la IA devuelve JSON válido contra un schema definido. Cero parsing manual.

### 3. Modelo híbrido relacional + JSONB

**Problema:** Cada Excel tiene columnas diferentes. Con un modelo puramente relacional, cada upload nuevo requeriría `ALTER TABLE` o tablas dinámicas.

**Solución:** Estructura (usuarios, proyectos, tablas) en tablas relacionales. Contenido dinámico en `Fila.data` como JSONB. Sin migraciones por archivo.

### 4. Iteración quirúrgica con JSON completo

**Problema:** Al iterar por chat, el AI cambiaba widgets que el usuario no pidió modificar.

**Solución:** Se envía el dashboard completo (sin truncar) con reglas de preservación explícitas: copia fiel por ID, estabilidad de IDs, reglas negativas ("NO mejores widgets no mencionados"), y `accion_realizada` que confirma qué cambió y qué preservó.

### 5. Capa middleware con 10 funciones analíticas

**Problema:** La IA no puede hacer cálculos confiables — tiende a alucinar números.

**Solución:** 10 funciones pandas parametrizadas que el Planificador invoca por nombre. Cada función ejecuta con manejo de errores individual (`status: ok/error`), evitando que una falla aborte todo el pipeline.

### 6. Optimistic UI + Rollback en iteración

**Problema:** El chat necesitaba feedback inmediato pero la API tarda segundos.

**Solución:** El mensaje del usuario aparece instantáneamente en la burbuja. Si la API falla, se restaura el dashboard anterior (snapshot de widgets previo al request).

---

## Stack Tecnológico

| Capa | Tecnología | Por qué |
|------|-----------|---------|
| **Frontend** | Vue 3 + Composition API + TypeScript | Reactividad natural, tipado seguro |
| **Estilos** | TailwindCSS 4 | Dark theme consistente sin CSS custom |
| **Gráficos** | ECharts 6 + vue-echarts | 10+ tipos de gráfico, responsive, temas |
| **Backend** | FastAPI 0.115 + Uvicorn | Async nativo, OpenAPI automático, validación Pydantic |
| **ORM** | SQLAlchemy 2.0 | Sessions con lifecycle gestionado por FastAPI |
| **Base de Datos** | PostgreSQL 15 | JSONB para datos dinámicos, relacional para estructura |
| **IA** | OpenAI gpt-4o | Structured Outputs, costo eficiente |
| **Analítica** | pandas + numpy | 10 funciones analíticas parametrizadas |
| **Infra** | Docker Compose + AWS EC2 | 4 servicios, health checks, deploy en un comando |
| **Proxy** | Nginx Alpine | Template con envsubst para configuración dinámica |

---

## Quickstart (Docker)

### Prerrequisitos

- Docker 20+ y Docker Compose v2+
- OpenAI API Key vigente

### Pasos

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd IA-Dashboard-desde-Excel

# 2. Crear .env en la raíz
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres
OPENAI_API_KEY=tu-key-aqui
OPENAI_MODEL=gpt-4o
BACKEND_URL=http://backend:8000
EOF

# 3. Levantar todo
docker-compose up --build
```

### Accesos

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Adminer (DB) | http://localhost:8080 |

### Datasets de prueba

La carpeta `examples/` contiene datasets de ejemplo para probar la aplicación:

| Archivo | Tema | Columnas destacadas |
|---------|------|-------------------|
| `ecommerce_test_dataset.xlsx` | E-commerce | Ventas, categorías, regiones, tendencias |
| `restaurant_dataset.xlsx` | Restaurante | Platos, precios, pedidos, satisfacción |
| `fitness_dataset.xlsx` | Fitness | Ejercicios, calorias, duración, frecuencia |
| `education_dataset.xlsx` | Educación | Estudiantes, calificaciones, asistencia |

---

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/users` | Crear o reutilizar usuario por nombre |
| `GET` | `/api/users/{user_id}/projects` | Listar proyectos del usuario |
| `POST` | `/api/users/{user_id}/projects` | Crear proyecto subiendo Excel |
| `POST` | `/api/users/{user_id}/projects/{project_id}/upload` | Agregar más sheets al proyecto |
| `GET` | `/api/users/{user_id}/projects/{project_id}` | Detalle del proyecto con tablas |
| `PATCH` | `/api/users/{user_id}/projects/{project_id}` | Renombrar proyecto |
| `DELETE` | `/api/users/{user_id}/projects/{project_id}` | Eliminar proyecto |
| `GET` | `/api/users/{user_id}/projects/{project_id}/tables` | Listar tablas del proyecto |
| `GET` | `/api/users/{user_id}/projects/{project_id}/tables/{table_id}` | Ver datos de una tabla |
| `DELETE` | `/api/users/{user_id}/projects/{project_id}/tables/{table_id}` | Eliminar tabla |
| `POST` | `/api/users/{user_id}/projects/{project_id}/generate-dashboard` | Generar dashboard inicial |
| `POST` | `/api/users/{user_id}/projects/{project_id}/chat` | Iterar dashboard por chat |

---

## Variables de Entorno

| Variable | Uso | Default |
|----------|-----|---------|
| `DATABASE_URL` | Conexión SQLAlchemy | `postgresql://postgres:postgres@postgres:5432/postgres` |
| `OPENAI_API_KEY` | Cliente OpenAI | *(requerida)* |
| `OPENAI_MODEL` | Modelo IA | `gpt-4o` |
| `BACKEND_PORT` | Puerto interno backend | `8000` |
| `FRONTEND_PORT` | Puerto host frontend | `5173` |
| `BACKEND_URL` | Proxy Nginx → backend | `http://backend:8000` |
| `MAX_UPLOAD_SIZE` | Límite upload Nginx | `50M` |

---

## Herramientas de Desarrollo

Este proyecto fue desarrollado utilizando herramientas de aceleración con IA como lo sugiere la prueba técnica.

### [OpenCode](https://github.com/opencode-ai/opencode) + [Gentle AI](https://github.com/Gentleman-Programming/gentle-ai)

Se utilizó **Gentle AI** — el ecosistema de [Gentleman Programming](https://github.com/Gentleman-Programming) — que superpotencia el agente de código con:

- **Spec-Driven Development (SDD):** Workflow estructurado de 6 fases (explore → propose → spec → design → tasks → apply) que asegura que cada cambio tiene diseño, especificación y tareas claras antes de escribir código.
- **Engram (Memoria Persistente):** El agente recuerda decisiones, bugs y contexto entre sesiones. Cada decisión arquitectónica queda documentada con qué se hizo, por qué, dónde, y qué se aprendió.
- **Skills especializadas:** Templates para FastAPI, Vue.js, Docker y diseño de interfaces que inyectan buenas prácticas automáticamente.
- **Persona de enseñanza:** El agente explica el *por qué* detrás de cada decisión, no solo el *qué*.

### Cómo se usó

| Fase | Herramienta | Resultado |
|------|------------|-----------|
| Arquitectura | SDD explore + propose | Decisiones documentadas con tradeoffs |
| Diseño | SDD spec + design | Specs con requisitos y escenarios |
| Implementación | SDD tasks + apply | Checklist atómico con verificación |
| Memoria | Engram | 170+ observaciones persistidas entre sesiones |
| Frontend | Vue Best Practices skill | Composition API + TypeScript + patrones |
| Backend | FastAPI Templates skill | Inyección de dependencias, capas, async |
| Docker | Docker Expert skill | Multi-stage builds, health checks |

### Filosofía

> **CONCEPTOS > CÓDIGO.** La IA ejecuta, el humano dirige. Cada decisión se tomó entendiendo el problema primero, buscando la solución después.

---

## Documentación Técnica

| Documento | Contenido |
|-----------|-----------|
| [`docs/PRESENTACION.md`](docs/PRESENTACION.md) | Manual de usuario con capturas de pantalla |
| [`docs/BACKEND.md`](docs/BACKEND.md) | Arquitectura backend, pipeline IA, endpoints |
| [`docs/FRONTEND.md`](docs/FRONTEND.md) | Estructura frontend, estado, componentes |
| [`docs/PRUEBA.md`](docs/PRUEBA.md) | Enunciado original de la prueba técnica |

---

## Respuesta a los Criterios de Evaluación

### 1. Funcionalidad Full-Stack

Frontend Vue 3 + Backend FastAPI conectados via REST API con proxy Nginx. Ingesta de Excel, generación de dashboards, iteración por chat — todo funciona end-to-end. Desplegado en AWS EC2.

### 2. Arquitectura de Datos

Modelo híbrido relacional + JSONB (ver [Modelo de Datos](#modelo-de-datos)). La estructura (usuarios, proyectos, tablas) usa relaciones SQL para queries eficientes. El contenido dinámico (filas con datos variables) usa JSONB para flexibilidad sin migraciones. `dashboard_config` persiste el JSON de widgets como campo del proyecto.

### 3. Integración de IA

- **OpenAI gpt-4o** con Structured Outputs en dos pasos del pipeline (Planificador y Diseñador).
- **Planificador:** Analiza columnas y datos muestra → propone funciones analíticas concretas.
- **Diseñador:** Transforma resultados numéricos en widgets de dashboard (KPIs, gráficos, insights).
- **Chat iterativo:** El Diseñador recibe el dashboard actual y hace modificaciones quirúrgicas con reglas de preservación.
- **Middleware Python:** 10 funciones pandas que ejecutan los cálculos reales — la IA nunca toca los números.

### 4. Despliegue y DevOps

- **Docker Compose** con 4 servicios, health checks y dependencias condicionales.
- **Multi-stage builds** para backend (Python slim) y frontend (Node build → Nginx runtime).
- **Deploy en AWS EC2** con acceso público.
- **Nginx** como proxy reverso con configuración dinámica via `envsubst`.
- **GitHub** como repositorio de código fuente.

---

<div align="center">

**Hecho con Vue 3, FastAPI, PostgreSQL, OpenAI y mucho café.**

</div>
