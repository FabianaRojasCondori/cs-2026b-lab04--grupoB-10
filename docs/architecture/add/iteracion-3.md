# E4 — Iteración 3 de ADD: Modificabilidad y Multitenencia por Distrito

**Autora:** Fabiana Paola Rojas Condori
**Escenarios:** EcoRecicla AQP — Lab08/QA-04 y Lab08/QA-05
**Estado:** Propuesta de diseño arquitectónico pendiente de validación con pruebas de integración.

## 1. Revisar entradas

- **Caso:** EcoRecicla AQP crece de 3 a 12 distritos municipales (Cayma, Yanahuara, Paucarpata, Cerro Colorado, etc.), cada uno con calendarios de recojo y reglas de puntos propios (Caso 10).
- **Línea base:** Monolito modular Django/DRF sobre PostgreSQL (ADR-001).
- **Decisiones previas reutilizadas:** ADR-001 (monolito modular), ADR-005 (Strategy y State), ADR-006 (índices + caché distrital), ADR-007 (Circuit Breaker + Outbox, iteración 2).
- **Restricción:** Un único sistema desplegado, un VPS económico, sin DevOps dedicado, plazo de 1 mes.

## 2. Establecer los objetivos de calidad

**Lab08/QA-04 (H,M) — Aislamiento multitenencia.**
Durante operaciones concurrentes de consulta o generación de reportes, ningún usuario, reciclador o supervisor del Distrito A puede acceder ni visualizar datos de recojo o ciudadanos del Distrito B. Criterio: **0 accesos cruzados**.

**Lab08/QA-05 (H,M) — Modificabilidad.**
El administrador debe poder registrar un nuevo distrito municipal o actualizar sus factores de puntos por tipo de residuo en ≤ 1 día, mediante configuración persistente y sin recompilar ni redesplegar la aplicación.

> *Nota de coherencia:* el `arbol.dot` mergeado en `main` marca QA-05 como (H,M). Se respeta esa calificación para no contradecir el árbol compartido. Si el equipo decide (M,M), debe actualizarse el árbol en E6.

## 3. Elegir elementos que se refinan

- Módulo de gestión de distritos.
- Módulo de solicitudes y recojos (`eco.api.solicitudes`).
- Capa de acceso a datos sobre PostgreSQL (`eco.db`).
- Configuración de reglas de puntos y horarios por distrito.
- Mecanismo de autorización y aislamiento (middleware + RLS).

## 4. Elegir conceptos de diseño

Se evaluaron tres alternativas para el aislamiento.

### Alternativa 1 — Una base de datos por distrito (12 BDs)

**Ventajas:** aislamiento físico fuerte.
**Desventajas:** 12 migraciones, 12 backups, 12 conexiones; inmanejable para 3 personas en un VPS.
**Decisión:** rechazada.

### Alternativa 2 — Un esquema (`schema`) por distrito

**Ventajas:** separación lógica clara.
**Desventajas:** migraciones duplicadas; `search_path` mal gestionado puede filtrar datos; el ORM de Django no lo soporta nativamente.
**Decisión:** rechazada por complejidad operativa.

### Alternativa 3 — Multitenencia lógica: `distrito_id` + Row-Level Security (seleccionada)

Una sola base, una columna `distrito_id` en cada tabla con datos distritales. PostgreSQL aplica políticas RLS usando una variable de sesión (`app.current_distrito_id`) que la API setea desde el claim del JWT del usuario autenticado, dentro de la transacción del request.

**Ventajas:**
- Centraliza administración, backups y migraciones.
- El aislamiento lo aplica el motor, no cada `QuerySet` en Django (defensa en profundidad).
- Escala a 12 distritos sin sobrecoste de infraestructura.

**Desventajas:**
- Requiere disciplina al setear el contexto de sesión.
- Las conexiones del pool deben resetear el contexto (`SET LOCAL`, no `SET`).
- Hay que escribir políticas RLS para cada tabla sensible.

**Decisión:** seleccionada, **complementada** con autorización en Django (primera capa) y RLS (segunda capa).

## 5. Instanciar elementos y asignar responsabilidades

- **`Distrito`:** identificador, nombre, activo. Tabla raíz de la que dependen todas las entidades distritales.
- **`ConfiguracionPuntos`:** `(distrito_id, tipo_residuo, factor)`. Leída dinámicamente por `ReglaPuntos` (patrón Strategy del ADR-005).
- **`ConfiguracionHorario`:** `(distrito_id, dia, ventana_inicio, ventana_fin)`.
- **Middleware de Django:** tras autenticar, ejecuta `SET LOCAL app.current_distrito_id = <id>` **dentro de la misma transacción del request**.
- **PostgreSQL RLS:** políticas `USING (distrito_id = current_setting('app.current_distrito_id')::int)` en `solicitud`, `recojo`, `outbox_event`, `configuracion_puntos`, `configuracion_horario`.
- **Administrador:** crea distritos y actualiza configuraciones vía API; los cambios se persisten como filas, no como constantes en el código.
- **Caché Redis (coherencia con ADR-006):** la clave incluye `distrito_id` + permisos + filtros + versión. Nunca solo `distrito_id`.

## 6. Esbozar vistas y registrar decisiones

### Flujo de aislamiento distrital

1. Usuario inicia sesión → Django emite JWT con claim `distrito_id`.
2. En cada request, el middleware abre transacción y ejecuta `SET LOCAL app.current_distrito_id = <id>`.
3. Toda consulta del request queda filtrada por RLS automáticamente en PostgreSQL.
4. Al COMMIT/ROLLBACK, la conexión del pool queda limpia (nuevo `SET LOCAL` en el siguiente request).

### Flujo de modificación de reglas

1. Administrador edita `ConfiguracionPuntos` del distrito vía panel administrativo.
2. Se valida el cambio y se persiste en PostgreSQL.
3. La siguiente operación de recolección lee el nuevo factor vía `ReglaPuntos` (Strategy).
4. **No hay recompilación ni redeploy.**

## 7. Evidencia y criterios de validación

| Escenario | Prueba propuesta | Criterio de aceptación |
|---|---|---|
| QA-04 | Consultar recojos del Distrito B con identidad del Distrito A | 0 filas del Distrito B visibles |
| QA-04 | Ejecutar reportes concurrentes con identidades de A y B | 0 accesos cruzados |
| QA-04 | Intentar `UPDATE` sobre recurso del Distrito B | Operación denegada por RLS |
| QA-04 | Consultar a través de caché sin `distrito_id` en clave | Miss forzado, nunca devolver dato de otro distrito |
| QA-05 | Crear nuevo distrito vía admin | Fila persistida, sin redeploy |
| QA-05 | Actualizar factor de puntos y consultar | Cambio aplicado en siguiente request, sin redeploy |

**Estado:** estas pruebas **están propuestas pero no ejecutadas**. La implementación real de RLS y middleware corresponde al despliegue (E6/E8), no a esta iteración de diseño.

## 8. Trade-offs y riesgos

**Trade-off aceptado:** mayor complejidad en configuración PostgreSQL y middleware Django, a cambio de aislamiento aplicado por el motor y una sola instancia para 12 distritos.

| Riesgo | Mitigación |
|---|---|
| Contexto de distrito no seteado → RLS no filtra | Test negativo obligatorio: request sin contexto debe fallar o devolver 0 filas |
| Conexión del pool reutilizada con contexto viejo | Usar `SET LOCAL` (no `SET`) dentro de transacción |
| Consulta a caché sin `distrito_id` en clave | Heredar ADR-006: claves incluyen distrito + permisos + filtros |
| Política RLS mal escrita (`USING true`) | Code review + test con `EXPLAIN` y `pg_policies` |
| Cambio de factor de puntos retroactivo | Snapshot del factor aplicado en cada `recojo` (columna `factor_aplicado`) |
| Migración de datos existentes a RLS | Script de migración que verifique `distrito_id NOT NULL` antes de activar RLS |

## 9. Conclusión

La combinación de `distrito_id` + Row-Level Security + configuración persistente permite atender QA-04 y QA-05 sin abandonar el monolito modular ni introducir una base de datos por distrito. La estrategia debe validarse con pruebas de integración y seguridad (negativas de acceso) antes de declararse cumplida.

Trazabilidad hacia ATAM-lite (E3/E7):

Esta decisión introduce el Riesgo R2 (error de configuración en políticas RLS expone datos entre distritos). Se clasifica en la matriz con Impacto 5 (Crítico) y Probabilidad 2 (Baja). Su mitigación mandatoria en CI será una fitness function de aislamiento (test_ff06_aislamiento_multitenencia_distrital) que verifique que una consulta con claim de Distrito A reciba exactamente 0 filas del Distrito B.