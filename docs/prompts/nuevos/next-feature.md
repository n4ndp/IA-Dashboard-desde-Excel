# Implementación de Chat Iterativo para Dashboard (Fase 1 a 3)

Actualmente tenemos un Dashboard generado por IA utilizando un pipeline de 3 pasos (Planificador -> Middleware -> Diseñador) en `services/ai_service.py`.
Queremos agregar una funcionalidad para que el usuario pueda iterar y modificar el dashboard mediante un mini-chat flotante.

Por favor, implementa esto paso a paso siguiendo estrictamente estas fases. **NO pases a la siguiente fase hasta terminar y confirmar la actual.**

---

## FASE 1: Frontend Mockup (UI/UX)
**Objetivo:** Crear la interfaz del chat flotante en la vista de análisis sin lógica de backend aún.

**Archivos afectados:** `ui/src/components/analysis/AnalisisTab.vue` (de igual forma revisa para confirmar)

**Requerimientos:**
1. **Posición:** Crea un componente de chat flotante posicionado en el centro inferior de la pantalla, superpuesto sobre el dashboard.
2. **Estado Minimalista:** Solo debe existir un input para escribir. No hay historial largo.
3. **Flujo visual:** - Cuando el usuario envía un mensaje, el input se desactiva y muestra un estado de "Cargando..." o un pequeño spinner.
   - Usa un `setTimeout` de 2 segundos para simular la respuesta. Al terminar, el chat debe mostrar un pequeño "bocadillo" (bubble) justo arriba del input con el texto del usuario y una respuesta de la IA hardcodeada (ej: "He actualizado el gráfico.").
   - Si el usuario vuelve a escribir, el bocadillo se reemplaza (solo conservamos el último intercambio).
4. **Diseño:** Usa TailwindCSS respetando el proyecto.

*Detente aquí y confirma cuando la Fase 1 esté lista para que la pruebe, inicialmente es un mockup sin conexión al backend.*

---

## FASE 2: Lógica Backend (Pipeline Iterativo y Schemas)
**Objetivo:** Crear el endpoint de chat reutilizando el pipeline de 3 pasos y guardar el resultado en la base de datos.

**Archivos afectados:** `schemas.py`, `services/ai_service.py`, `routes/generate.py` (de igual forma revisa para confirmar)

**Requerimientos:**
1. **En `schemas.py`:** Crea un nuevo schema llamado `IterateDashboardRequest` que reciba:
   - `prompt` (str): El mensaje del usuario.
   - `current_dashboard` (dict): El JSON actual del dashboard.
2. **En `services/ai_service.py`:** - Crea una nueva función `iterate_dashboard(db, project_id, engine, tables_context, current_dashboard, user_prompt)`.
   - Modifica `_build_plan_prompt`: Añade soporte opcional para el prompt del usuario. Si hay `user_prompt`, inyecta el `current_dashboard` y añade la regla: *"El usuario pide: '{user_prompt}'. Si el cambio es SOLO visual/cosmético (ej. cambiar colores o tipo de gráfico), devuelve 'ejecutar': []. Si pide analizar nuevos datos, solicita las funciones necesarias."*
   - Modifica `_build_designer_prompt`: Añade soporte opcional. Si hay `user_prompt`, inyecta el `current_dashboard` y la regla: *"El usuario pide: '{user_prompt}'. MODIFICA el JSON actual para cumplir su petición. Mantén intactos los gráficos que no cambian. Integra nuevos datos de las funciones si los hay. Mantén el número de gráficos PAR."*
3. **En `routes/generate.py`:**
   - Crea el endpoint `POST /users/{user_id}/projects/{project_id}/chat` que reciba el `IterateDashboardRequest`.
   - Llama a `iterate_dashboard()`.
   - Actualiza `proyecto.dashboard_config` en la base de datos con el nuevo JSON y haz `db.commit()`.
   - Retorna la misma estructura que `GenerateDashboardResponse`.

*Detente aquí y confirma cuando la Fase 2 esté lista.*

---

## FASE 3: Integración y Reactividad
**Objetivo:** Conectar el frontend con el nuevo endpoint de chat para que los gráficos muten en tiempo real.

**Archivos afectados:** `ui/src/services/endpoints.ts` (o `api.ts`), `ui/src/components/analysis/AnalisisTab.vue`.

**Requerimientos:**
1. En `endpoints.ts`, agrega el método `chatDashboard(userId, projectId, prompt, currentDashboard)` apuntando al nuevo endpoint.
2. En `AnalisisTab.vue`, elimina el `setTimeout` hardcodeado.
3. En la función de envío del chat, llama a la API pasando el input del usuario y el estado de los widgets actuales.
4. Al recibir la respuesta, actualiza el estado local de tu dashboard. Los gráficos de ECharts deben re-renderizarse con los nuevos datos recibidos.
5. Muestra el `resumen_ejecutivo` o mensaje en el bocadillo del chat flotante. Maneja errores con el `useToast`.

*Confirma cuando todo el flujo esté integrado.*
