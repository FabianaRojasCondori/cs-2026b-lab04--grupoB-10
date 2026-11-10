# ADR-006: Estrategia de Caching para Consultas Frecuentes de Distritos

* **Estado:** Aprobado
* **Fecha:** 2026-11-03
* **Autores:** Flor de Liz Velazque Quispe
* **Atributo de Calidad Asociado:** [QA-01] Rendimiento (Latency p95 < 500ms)

## Contexto
Las consultas repetitivas sobre catálogos de materiales, zonas distritales y horarios de recojo saturaban la base de datos PostgreSQL en horas pico, elevando el p95 a > 1200ms.

## Decisión
Implementar **Redis** como caché de lectura en memoria con política TTL (Time-To-Live) de 15 minutos e invalidación por eventos cuando la municipalidad actualice rutas.

## Consecuencias
* **Positivas:** Reducción del p95 a 320ms y disminución del 65% de carga sobre PostgreSQL.
* **Negativas:** Eventual inconsistencia temporal de datos de lectura si no se invalida la caché adecuadamente.