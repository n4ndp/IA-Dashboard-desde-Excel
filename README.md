# IA Dashboard desde Excel

<div align="center">

![Vue.js](https://img.shields.io/badge/Vue.js-3.5-42b883?logo=vuedotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991?logo=openai&logoColor=white)

**Transformá archivos Excel en dashboards analíticos interactivos usando GenAI + un pipeline multi-agente determinístico.**

</div>

---

## 🚀 Demo en Producción

- **Frontend (AWS):** http://3.129.10.23:5173
- **API Docs (Swagger):** http://3.129.10.23:8000/docs

> Verificado: ambos endpoints responden actualmente.

---

## 🎯 ¿Qué problema resuelve?

Construir dashboards útiles desde Excel suele requerir:
- limpieza manual de datos,
- modelado,
- queries,
- y diseño visual.

Este proyecto automatiza ese flujo de punta a punta:

1. Subís un `.xlsx`.
2. El backend infiere tipos y estructura.
3. Un pipeline IA + Python decide y ejecuta análisis matemáticos reales.
4. Se genera un dashboard con KPIs, gráficos e insights.
5. Podés iterar por chat para modificar el dashboard sin empezar de cero.

---

## ✨ Features Principales

### 1) Ingesta dinámica de Excel
- Lectura de múltiples sheets con `pandas`.
- Inferencia de tipo por columna (`string | number | date`).
- Persistencia en modelo híbrido relacional + columna JSON para filas dinámicas.

### 2) Pipeline agéntico de 3 pasos (Planificador → Middleware → Diseñador)
- **Planificador (IA):** decide qué funciones analíticas ejecutar.
- **Middleware (Python/pandas):** ejecuta cálculos reales (sin alucinaciones numéricas).
- **Diseñador (IA):** transforma resultados en JSON de widgets para frontend.

### 3) Chat iterativo sobre dashboard existente
- Endpoint dedicado `/chat` para modificar dashboards por prompt.
- Envía `current_dashboard` para evitar reconstrucciones ciegas.
- Cambios cosméticos pueden devolver `ejecutar: []`.

### 4) Arquitectura de datos sólida
- Jerarquía: `Usuario → Proyecto → Tabla → Columna/Fila`.
- `Proyecto.dashboard_config` persiste dashboard generado.
- `Fila.data` guarda datos tabulares flexibles en JSON.

---

## 🧠 Flujo IA (alto nivel)

```text
Excel Upload
   ↓
Ingesta + Tipado (excel_service.py)
   ↓
Planificador IA (generate_execution_plan)
   ↓
Middleware Python (execute_plan + AnalyticsEngine)
   ↓
Diseñador IA (generate_final_dashboard)
   ↓
Post-proceso (_enforce_even_charts + _map_to_widgets)
   ↓
Frontend Vue + ECharts (DashboardRenderer)
```

---

## 🏗️ Arquitectura a Alto Nivel

| Capa | Responsabilidad | Tecnología |
|---|---|---|
| **Frontend** | UI, estado reactivo, render de widgets y chat iterativo | Vue 3, TypeScript, TailwindCSS, ECharts |
| **Backend API** | Ingesta, orquestación IA, endpoints REST | FastAPI, SQLAlchemy, pandas, OpenAI |
| **Base de Datos** | Persistencia de usuarios/proyectos/tablas + dashboard config | PostgreSQL |
| **Infra** | Orquestación de servicios | Docker Compose |

Servicios en `docker-compose.yml`:
- `postgres`
- `backend`
- `frontend`
- `adminer`

---

## 🧩 Decisiones de Ingeniería y Aprendizajes

Este proyecto evolucionó con decisiones arquitectónicas concretas:

1. **Se reemplazó un loop agéntico único por pipeline determinístico de 3 pasos.**
   - Beneficio: menos riesgo de timeouts y mejor control del flujo.

2. **Structured Outputs con JSON Schema en ambos pasos IA.**
   - Beneficio: menos parsing frágil y contratos más estables.

3. **Capa middleware con funciones analíticas explícitas.**
   - Beneficio: la IA planifica, pero Python ejecuta los números reales.

4. **Iteración de dashboard con contexto del JSON actual.**
   - Beneficio: modificaciones incrementales en lugar de regeneración ciega.

5. **Token safety para iteraciones.**
   - `_compact_dashboard()` acota payload para prompts grandes.

---

## ✅ Requisitos Previos

| Requisito | Versión sugerida | Obligatorio |
|---|---|---|
| Docker | 20+ | Sí |
| Docker Compose | v2+ | Sí |
| Python | 3.12 | Solo desarrollo local |
| Node.js | 18+ | Solo desarrollo local frontend |
| OpenAI API Key | vigente | Sí |

---

## ⚡ Quickstart (Docker)

```bash
# 1) Clonar repositorio
git clone <tu-repo>
cd IA-Dashboard-desde-Excel

# 2) Configurar variables (ver tabla más abajo)
#    Crear .env en raíz con al menos DATABASE_URL + OPENAI_API_KEY

# 3) Levantar stack completo
docker-compose up --build
```

Accesos:
- Frontend: `http://localhost:5173`
- Backend docs: `http://localhost:8000/docs`
- Adminer: `http://localhost:8080`

---

## 🛠️ Desarrollo Local (sin Docker)

### Backend

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configurar .env (DATABASE_URL, OPENAI_API_KEY, etc.)

uvicorn app:app --reload --port 8000
```

### Frontend

```bash
cd ui
npm install
npm run dev
```

---

## 🔐 Variables de Entorno

> Fuente verificada desde código (`app.py`, `database.py`, `routes/projects.py`, `services/ai_service.py`, `docker-compose.yml`, `ui/vite.config.ts`, `ui/nginx.conf.template`).

| Variable | Uso | Default / Ejemplo |
|---|---|---|
| `DATABASE_URL` | Conexión SQLAlchemy | `postgresql://postgres:postgres@postgres:5432/postgres` |
| `OPENAI_API_KEY` | Cliente OpenAI | *(requerida)* |
| `OPENAI_MODEL` | Modelo IA | `gpt-4o-mini` |
| `API_TITLE` | Título FastAPI | `IA Dashboard desde Excel` |
| `API_VERSION` | Versión API | `0.1.0` |
| `CORS_ORIGINS` | Orígenes CORS (csv) | `*` |
| `MAX_FILE_SIZE` | Límite upload backend | `10485760` (10MB) |
| `POSTGRES_USER` | Usuario Postgres | `postgres` |
| `POSTGRES_PASSWORD` | Password Postgres | `postgres` |
| `POSTGRES_DB` | DB Postgres | `postgres` |
| `POSTGRES_PORT` | Puerto Postgres host | `5432` |
| `BACKEND_PORT` | Puerto interno backend | `8000` |
| `BACKEND_EXPOSED_PORT` | Puerto host backend | `8000` |
| `FRONTEND_PORT` | Puerto host frontend | `5173` |
| `ADMINER_PORT` | Puerto host adminer | `8080` |
| `BACKEND_URL` | Proxy Nginx frontend → backend | `http://backend:8000` |
| `MAX_UPLOAD_SIZE` | `client_max_body_size` de nginx | `50M` |
| `VITE_API_URL` | Proxy de Vite en dev | `http://localhost:8000` |

---

## 📡 Endpoints Clave

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/users` | Crear (o reutilizar) usuario por nombre |
| `GET` | `/api/users/{user_id}/projects` | Listar proyectos |
| `POST` | `/api/users/{user_id}/projects` | Crear proyecto subiendo Excel |
| `POST` | `/api/users/{user_id}/projects/{project_id}/upload` | Agregar sheets al proyecto |
| `GET` | `/api/users/{user_id}/projects/{project_id}` | Obtener detalle del proyecto |
| `POST` | `/api/users/{user_id}/projects/{project_id}/generate-dashboard` | Generar dashboard inicial |
| `POST` | `/api/users/{user_id}/projects/{project_id}/chat` | Iterar dashboard por chat |
| `GET` | `/api/users/{user_id}/projects/{project_id}/tables/{table_id}` | Ver datos de una tabla |

---

## 📚 Documentación Técnica

- [`docs/BACKEND.md`](docs/BACKEND.md) — arquitectura backend y flujo agéntico.
- [`docs/FRONTEND.md`](docs/FRONTEND.md) — estructura frontend y flujo de interacción.
