# Prompt: Excel AI Dashboard — Backend Fase 1

## Contexto del proyecto
Este proyecto es una prueba técnica para un puesto de **Trainee de Agentic AI**.
El objetivo es construir una aplicación web full-stack que demuestre habilidades en
arquitectura de datos, integración de APIs de IA y despliegue continuo.

El caso elegido es el **A: IA Dashboard desde Excel** — una aplicación que recibe
un archivo Excel, procesa la información en el backend, y genera un dashboard
interactivo con gráficos y un resumen ejecutivo generado por IA.

El deadline de entrega es el **lunes 20/04 a las 9:00am**.

---

## Stack tecnológico (inicial, ya que puede evolucionar en fases posteriores)
- **Backend**: FastAPI (Python 3.12)
- **ORM**: SQLAlchemy 2.0
- **Base de datos**: PostgreSQL vía Supabase (Session Pooler)
- **Procesamiento de archivos**: Pandas + OpenPyXL
- **Variables de entorno**: python-dotenv
- **Frontend**: Vue 3 + TypeScript + Vite

---

## Estado actual del proyecto
La estructura de carpetas ya está creada. Los archivos base del backend
(`app.py`, `database.py`, `models.py`) ya existen y están vacías.
Las carpetas `routes/` y `services/` también están vacías.

---

## Modelo de datos (entidad-relación)

El sistema maneja inicialmente 5 entidades relacionadas entre sí:

**Usuario** — representa a la persona que usa la app.
Tiene un identificador único y un nombre. Un usuario puede tener múltiples proyectos.

**Proyecto** — se crea cada vez que un usuario sube un archivo Excel.
Pertenece a un usuario. Guarda el nombre del archivo y la fecha de creación.
Un proyecto puede tener múltiples tablas.

**Tabla** — representa cada hoja del archivo Excel.
Pertenece a un proyecto. Guarda el nombre de la hoja.
Una tabla tiene múltiples columnas y múltiples filas.

**Columna** — representa cada columna detectada en una hoja del Excel.
Pertenece a una tabla. Guarda el nombre de la columna y su tipo de dato inferido.
Los únicos tipos posibles son: `string`, `number` o `date`.

**Fila** — representa cada fila de datos de una hoja del Excel.
Pertenece a una tabla. Guarda los datos como un objeto JSON flexible,
donde cada clave es el nombre de una columna y el valor es el dato de esa celda.
Ejemplo: `{"fecha": "2026-04-01", "producto": "Polo", "ventas": 100}`

Este diseño es completamente genérico — no asume nada sobre el contenido del Excel.
Funciona igual para un dataset de ventas, recursos humanos, finanzas o cualquier otro.

---

## Objetivo de esta fase

Completar los archivos faltantes del backend para que el flujo completo funcione:
el usuario sube un Excel, el sistema lo procesa y guarda toda la información en
la base de datos de Supabase.

---

## Buenas prácticas a seguir
- Las rutas no deben contener lógica de negocio — solo delegan a los servicios
- Un único `db.commit()` al final para mantener la integridad de la transacción
- Usar `db.flush()` para obtener IDs generados antes del commit final
- Manejar errores con mensajes claros
- El código debe ser limpio, modular y fácil de leer
- Documentar funciones con docstrings
