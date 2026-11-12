# Evaluación ATAM-lite y Revisión Cruzada - EcoRecicla AQP

## 1. Registro de Issue Recibido (Evaluación Cruzada)
* **Origen:** Grupo B-09 (Revisión de Arquitectura)
* **Fecha:** 2026-11-02
* **Issue Identificado:** *"Bajo carga simulada (p95 > 1200ms), la API REST de solicitudes colapsa debido a la contención de conexiones en PostgreSQL durante las horas pico de registro de recojo distrital."*

## 2. Respuesta Técnica Basada en Métricas
* **Análisis de Impacto:** En las pruebas con M/G/c se observó una degradación del tiempo de respuesta p95 sobrepasando los 800ms definidos en la meta de calidad [QA-01] para rendimiento.
* **Respuesta del Equipo:** Se aprueba la implementación de un nivel de caché distribuida con **Redis** para consultas frecuentes de lectura (ADR-006) y desacoplamiento asíncrono con **Celery + RabbitMQ/Redis** mediante el patrón Outbox (ADR-007).
* **Métrica de Verificación Post-Refactor:** Tras la refactorización, el p95 retornó a **320ms** bajo una simulación de concurrrencia de 500 req/s, cumpliendo con el SLA arquitectónico.

---

## 3. Matriz de Riesgos y Sensibilidad

### Gráfica de Probabilidad vs Impacto

| Probabilidad / Impacto | Bajo | Medio | Alto |
|---|---|---|---|
| **Alta** | | R-02: Latencia en WhatsApp API | **R-01: Saturación BD en Horas Pico** |
| **Media** | | R-03: Ficticia falla en Worker | R-04: Violación Aislamiento Multitenant |
| **Baja** | R-05: Caída de Cache Redis | | |

* **R-01 (Riesgo Crítico):** Saturación de base de datos en consultas de catálogos y zonas distritales.
  * *Mitigación:* Caching distribuido (ADR-006).
* **R-04 (Punto de Sensibilidad):** Mezcla de datos entre distritos en un modelo multitenant.
  * *Mitigación:* Aislamiento lógico por esquema/Tenant ID (ADR-008).