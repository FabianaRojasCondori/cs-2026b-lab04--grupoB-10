# Bitácora de Registro de Uso de Inteligencia Artificial

## Histórico de Interacciones

| # | Fecha | Herramienta | Prompt Enviado | Propuesta de la IA | Verificación / Decisión |
|---|---|---|---|---|---|
| 1 | 2026-10-15 | ChatGPT | "Genera el diagrama C4 de nivel 1 en Mermaid para EcoRecicla AQP con Vecino, Reciclador y Municipalidad." | Creó el diagrama con los 3 usuarios y el sistema central. | **Aprobado con ajustes:** Se incluyeron los sistemas externos (Servicio de mapas y WhatsApp). |
| 2 | 2026-10-15 | Claude | "Verifica si los nombres de los contenedores cumplen la guía C4 en el diagrama Nivel 2." | Recomendó reemplazar nombres genéricos por `App Vecino (React Native)` y `Base de Datos (PostgreSQL)`. | **Aprobado:** Aplicado en la vista de contenedores. |
| 3 | 2026-10-16 | ChatGPT | "Evalúa integrar la notificación a vecinos directamente por SMS tradicional." | Sugirió usar SMS como canal principal. | **Rechazado:** Se decidió usar la integración con WhatsApp por mayor uso en Arequipa y menor costo. |
| 4 | 2026-10-16 | Claude | "Analiza si la Tarea de optimización de rutas debe estar dentro del API." | Recomendó unificar la optimización de rutas dentro del proceso de la API backend. | **Rechazado (Falso Positivo):** Refutado en `revision-c4.md` para no bloquear el backend principal. |
| 5 | 2026-10-17 | ChatGPT | "Escribe la explicación no técnica del diagrama de contexto para el Gerente Municipal en menos de 120 palabras." | Generó un texto enfocado en el impacto ambiental y uso por vecinos y recicladores. | **Aprobado con ajustes:** Se refinó la redacción para el archivo `explicacion.md`. |

---

## Registros de la Entrega Actual: ADD / ATAM-lite - Lab 08

| # | Fecha | Herramienta | Prompt Enviado | Propuesta de la IA | Verificación / Decisión y Refutación |
|---|---|---|---|---|---|
| 6 | 2026-11-06 | ChatGPT | "Sugerir patrón para mitigar p95 > 1000ms en consultas de catálogos." | Propuso implementar una capa de caché Redis con TTL. | **Aprobado:** Documentado en ADR-006. |
| 7 | 2026-11-06 | Claude | "Proponer mecanismo de tolerancia a fallos cuando WhatsApp API no responde." | Sugirió utilizar Circuit Breaker + Transactional Outbox Pattern. | **Aprobado:** Integrado en ADR-007. |
| 8 | 2026-11-07 | ChatGPT | "Recomienda cómo aislar municipios en un modelo SaaS." | Propuso multitenancia con filtro por `tenant_id` en ORM. | **Aprobado:** Registrado en ADR-008. |
| 9 | 2026-11-07 | ChatGPT | "Para garantizar disponibilidad [QA-02], reemplaza la base de datos PostgreSQL por MongoDB para evitar bloqueos de tabla en lecturas/escrituras." | Propuso migrar toda la base de datos relacional a una base NoSQL (MongoDB) argumentando mayor rendimiento en escrituras masivas. | **RECHAZADO (Falso Positivo Refutado):** Las pruebas con `fitness/disponibilidad.py` demostraron que los bloqueos se debían al procesamiento síncrono de notificaciones, no a PostgreSQL. Migrar a NoSQL rompía la integridad referencial de los pagos/puntos sin resolver la causa raíz, la cual se solucionó con Celery/Outbox (ADR-007). |
| 10 | 2026-11-08 | Claude | "Sugerir tags para representar escenarios de calidad en Structurizr DSL." | Sugirió etiquetar cada contenedor con tags del tipo `[QA-xx]`. | **Aprobado:** Incorporado en `docs/architecture/c4/workspace.dsl`. |