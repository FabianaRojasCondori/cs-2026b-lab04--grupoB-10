# ADR-007: Resiliencia con Circuit Breaker y Patrón Transactional Outbox

* **Estado:** Aprobado
* **Fecha:** 2026-11-04
* **Autores:** Flor de Liz Velazque Quispe
* **Atributo de Calidad Asociado:** [QA-02] Disponibilidad y Resiliencia (Uptime > 99.5%)

## Contexto
Las caídas intermitentes o latencia alta del servicio externo de WhatsApp API bloqueaban los hilos de ejecución de la API principal durante el registro de solicitudes.

## Decisión
Adoptar el patrón **Transactional Outbox** para guardar notificaciones pendiente en BD PostgreSQL de forma transaccional, junto a un **Circuit Breaker** en el cliente de integración procesado asíncronamente por Celery/Redis.

## Consecuencias
* **Positivas:** Desacoplamiento total de dependencias externas y cero pérdidas de notificaciones ante caídas de WhatsApp.
* **Negativas:** Complejidad operacional añadida al monitorear colas de mensajes reintentados.