# E4 — Iteración 2 de ADD: Disponibilidad y Resiliencia

**Autora:** Fabiana Paola Rojas Condori
**Escenario:** EcoRecicla AQP — Lab08/QA-02
**Estado:** Propuesta con evidencia de simulación Monte Carlo ejecutada

## 1. Revisar entradas

- **Caso:** Crecimiento de 3 a 12 distritos de Arequipa (Caso 10).
- **Línea base:** Monolito modular en Python/Django sobre PostgreSQL (ADR-001), con patrones Strategy y State (ADR-005) y Adapter para SDKs de mensajería heredado del Lab 07.
- **Iteración previa:** `iteracion-1.md` (QA-01, rendimiento) difirió la disponibilidad a esta iteración.
- **Restricción:** Equipo de 3 desarrolladores, un único VPS económico, plazo de 1 mes y sin DevOps dedicado.

## 2. Establecer el objetivo de calidad

**Lab08/QA-02 (H,H) — Disponibilidad y resiliencia:** Ante una indisponibilidad total de 20 minutos de la pasarela externa de mensajería (WhatsApp/SMS), el sistema debe registrar el **100 % de las solicitudes entrantes** (0 solicitudes perdidas), encolándolas de manera persistente.

## 3. Elegir elementos que se refinan

- `eco.api.solicitudes` (endpoint de registro de recojos).
- Adaptador de mensajería (`eco.api.adaptadores`).
- Tabla Outbox en persistencia (`eco.db` — PostgreSQL).
- Worker de despacho asíncrono (`eco.worker`).

## 4. Elegir conceptos de diseño

Se evaluaron tres alternativas tácticas:

1. **Sin tácticas de resiliencia:**
   - *Descarte:* En la simulación se pierden 214 de 1800 solicitudes ante la caída de 20 min.

2. **Reintentos síncronos simples (hasta 3 intentos):**
   - *Descarte:* Durante la caída total genera una "tormenta de reintentos" contra el proveedor (183 llamadas en caída) y aún pierde 62 solicitudes.

3. **Circuit Breaker + Transactional Outbox (PostgreSQL):**
   - *Decisión (Aceptada):* Fallo rápido con un Decorator (`ConCircuitBreaker`) sobre el adaptador de mensajería y persistencia transaccional ACID en una tabla outbox.

## 5. Instanciar elementos y asignar responsabilidades

- `ConCircuitBreaker`: Decorator que conmuta entre estados `CERRADO`, `ABIERTO` y `SEMIABIERTO` (umbral: 3 fallas; enfriamiento: 2 minutos).
- `OutboxEvent` (PostgreSQL): Almacena las notificaciones en estado `PENDIENTE` dentro de la misma transacción del registro de solicitud. Campos: `id`, `tipo_evento`, `payload`, `estado`, `intentos`, `creado_en`, `procesado_en`.
- `WorkerNotificaciones` (Celery): Proceso desacoplado que drena los eventos pendientes con reintentos exponenciales una vez que el circuito vuelve a cerrarse.

## 6. Evidencia cuantitativa (Simulación Monte Carlo)

Archivo: `fitness/disponibilidad.py` ejecutado con semilla determinista 7 (1800 solicitudes, 600 min de jornada, caída de 20 min entre min 180 y 200, 8 % fallas transitorias):

| Estrategia | Solicitudes perdidas | Llamadas en caída | ¿Cumple QA-02? |
|---|:---:|:---:|:---:|
| Sin tácticas | 214 | 61 | No |
| Reintentos (3) | 62 | 183 | No |
| **Circuit Breaker + Outbox** | **0** | **11** | **Sí (0 pérdidas)** |

Cumple estrictamente con **Lab08/QA-02** en el modelo simulado.

### Supuestos y limitaciones

- **Determinismo:** Semilla fija (`semilla=7`) para reproducibilidad exacta.
- **Limitación formal:** La simulación representa la Outbox mediante un contador en memoria. No ejecuta sentencias SQL transaccionales en PostgreSQL ni modela la saturación del disco o caídas de la propia base de datos.
- **Drenado:** No se simula la latencia posterior que toma Celery para despachar la cola acumulada al reactivarse el servicio; valida exclusivamente la **protección del canal y la no-pérdida de solicitudes durante la contingencia**.

## 7. Trade-offs y decisión arquitectónica (ADR-007)

- **Trade-off aceptado:** Consistencia eventual en la entrega de notificaciones a cambio de 100 % de disponibilidad en el registro de solicitudes de recojo.
- **Contrato para E5 (`tests/test_fitness.py`):**
  - `test_ff04`: Valida que `simular("breaker")["perdidos"] == 0`.
  - `test_ff05`: Valida que las llamadas en caída con breaker sean al menos 5 veces menores que con reintentos ciegos.