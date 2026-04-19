# Skill Registry — IA-Dashboard-desde-Excel

Generated: 2026-04-18

## User Skills

| Skill | Trigger | Source |
|-------|---------|--------|
| fastapi-templates | Building new FastAPI applications, setting up backend APIs | .agents/skills/ (project-level) |
| interface-design | Dashboards, admin panels, apps, tools, interactive UI products | .agents/skills/ (project-level) |
| vue-best-practices | Any Vue.js tasks, .vue files, Vue Router, Pinia, Vite with Vue | .agents/skills/ (project-level) |
| docker-expert | Dockerfiles, Docker Compose, containerization, multi-stage builds | .agents/skills/ (project-level) |

## Project Conventions

| File | Status | Notes |
|------|--------|-------|
| AGENTS.md | ❌ Not found | — |
| CLAUDE.md | ❌ Not found | — |
| .cursorrules | ❌ Not found | — |

## Compact Rules

### fastapi-templates
- **When**: Building FastAPI endpoints, services, or database setup
- **Patterns**:
  - Use dependency injection (`Depends`) for DB sessions and shared logic
  - Separate routes → services → repositories layers
  - Use `async/await` throughout for FastAPI
  - Pydantic schemas for request/response validation
  - Single commit at end of transaction; use `flush()` for IDs
  - Error handling with HTTPException in routes; ValueError in services
- **Testing**: pytest + httpx AsyncClient with SQLite in-memory for test DB

### interface-design
- **When**: Building dashboard UI, widgets, or any frontend components
- **Rules**:
  - Intent first: who is the human, what must they accomplish, how should it feel
  - Product domain exploration before any visual work
  - Token-based theming (CSS variables from primitives)
  - Subtle layering: surface elevation, border progression, text hierarchy (4 levels)
  - Pick ONE depth strategy (borders-only / subtle shadows / layered / color shifts)
  - Build spacing scale from base unit
  - Signature element unique to this product
  - Avoid: harsh borders, dramatic shadows, inconsistent spacing, mixed depth strategies

### docker-expert
- **When**: Creating Dockerfiles, Docker Compose, containerization, multi-stage builds
- **Patterns**:
  - Multi-stage builds: separate deps/install/build/runtime stages
  - Copy package files before source for layer caching
  - Non-root user in production images
  - .dockerignore to exclude unnecessary files
  - Health checks for service readiness
  - Named volumes for data persistence
  - Custom networks for service isolation
- **Compose**: depends_on with health check conditions, resource limits, restart policies

### vue-best-practices
- **When**: Any Vue.js work — components, composables, routing, state management
- **Stack**: Vue 3 + Composition API + `<script setup lang="ts">`
- **Must-read references before coding**: reactivity.md, sfc.md, component-data-flow.md, composables.md
- **Rules**:
  - One source of truth for state; derive everything else with computed
  - Props down, events up; v-model only for true two-way contracts
  - Split components when: multiple responsibilities, 3+ UI sections, repeated template blocks
  - Keep entry/root/route views thin — composition surfaces only
  - Extract reusable/stateful/side-effect logic into composables (useXxx)
  - SFC order: `<script>` → `<template>` → `<style>`
  - Performance optimization ONLY after behavior is correct
  - Feature folder layout: components/<feature>/..., composables/use<Feature>.ts

## Auto-Resolved Triggers

| Code Context | Task Context | Skills Injected |
|-------------|-------------|-----------------|
| `*.py` (routes/) | Writing endpoints | fastapi-templates |
| `*.py` (services/) | Business logic | fastapi-templates |
| `*.py` (models.py, database.py) | Database setup | fastapi-templates |
| `*.vue`, `*.ts` (ui/) | Building UI components | interface-design, vue-best-practices |
| `*.vue`, `*.ts` (ui/) | Dashboard layout | interface-design, vue-best-practices |
| `*.vue`, `*.ts` (ui/) | Vue composables, routing, state | vue-best-practices |
| `Dockerfile`, `docker-compose*.yml` | Containerization, Docker setup | docker-expert |
| `*.py` (database.py) | DB connection config for Docker | fastapi-templates, docker-expert |
