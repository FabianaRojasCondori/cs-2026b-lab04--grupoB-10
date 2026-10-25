# ADR-005: Adopción de Patrones de Diseño GoF en EcoRecicla AQP

* **Estado:** Aprobado
* **Fecha:** 2026-10-24
* **Autores:** Flor de Liz Velazque Quispe

## Contexto
El sistema EcoRecicla AQP requería eliminar code smells (bloques `if/else` anidados en la lógica de estados y lógica de cálculo de puntos acoplada al dominio) para garantizar que los cambios en reglas de negocio se puedan realizar en ≤ 2 días-persona.

## Decisión Adoptada
Se decidió implementar los siguientes patrones GoF:
1. **Strategy (`<<Strategy>>`):** Para encapsular los algoritmos de cálculo de puntos según el tipo de residuo y promociones del distrito.
2. **State (`<<State>>`):** Para modelar las transiciones del ciclo de vida de la Solicitud de Recojo (Pendiente, Asignado, Completado, Cancelado).

### Patrones Rechazados
* **Singleton para Conexiones de BD:** Rechazado debido a que rompe las pruebas unitarias aisladas y Django maneja nativamente el pool de conexiones.
* **Chain of Responsibility:** Rechazado para el flujo de validaciones simples, evitando sobreingeniería.

## Consecuencias
* **Positivas:** Reducción de la complejidad ciclomática, mejora en la mantenibilidad y desacoplamiento de reglas de negocio.
* **Negativas:** Incremento en el número de clases y archivos pequeños en la capa de dominio.