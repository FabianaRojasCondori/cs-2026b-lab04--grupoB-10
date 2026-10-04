# ADR-002: Base de Datos Relacional PostgreSQL con Esquemas Lógicos por Módulo
Estado: Aceptado
Fecha: 2026-10-03
Decisores: Equipo de Desarrollo Grupo B-10

## Contexto
El sistema requiere consistencia estricta e integridad referencial para el registro de pesaje de residuos y abono de puntos canjeables (RF-03, QA-03). Además, para preservar los límites del Monolito Modular (ADR-001) y facilitar una futura migración a microservicios si el proyecto escala, se debe evitar que un módulo acceda directamente a las tablas de otro.

## Alternativas consideradas
1. **Bases de datos independientes (una instancia por módulo):** Aislamiento físico completo, pero eleva el consumo de memoria RAM y costo en el VPS económico (R-03).
2. **Base de datos documental NoSQL (MongoDB):** Flexible para cambios de esquema, pero compleja para auditorías de puntos transaccionales y reportes relacionales (RF-04).
3. **PostgreSQL con esquemas lógicos separados (Elegida):** Una única instancia de base de datos relacional compartida físicamente en el VPS, pero con esquemas lógicos independientes (`solicitudes`, `rutas`, `puntos`, `reportes`).

## Decisión
Usaremos **PostgreSQL configurando un esquema lógico por módulo**. Cada módulo tendrá sus propias migraciones y modelos, accediendo exclusivamente a su esquema correspondiente.

## Consecuencias
- **Positivas:** Bajo costo y mínimo consumo de recursos en el VPS (R-03); integridad transaccional ACID garantizada para el balance de puntos; preserva la independencia modular.
- **Negativas / Riesgos:** No se permiten joins SQL directos entre tablas de esquemas distintos; cualquier consulta cruzada debe realizarse a nivel de capa de servicio.