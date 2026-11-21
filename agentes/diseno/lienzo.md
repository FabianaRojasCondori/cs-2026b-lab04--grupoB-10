# Lienzo de diseño del sistema agéntico — EcoRecicla AQP (Lab 10, E1)

Sistema agéntico que trabaja sobre los 3 issues sembrados en el monolito modular
de EcoRecicla AQP (`src/puntos`, `src/solicitudes`, `src/rutas`). Sigue el
Paso 2 de la guía (Tabla 9) y las secciones 1.3 (arquetipos) y 1.7 (coordinación).

| Issue | Síntoma | Prueba en rojo |
|---|---|---|
| ISSUE-01 | Puntos acreditados dos veces al reintentar el evento del outbox | `tests/test_issue_01.py` |
| ISSUE-02 | La ruta del reciclador incluye solicitudes canceladas | `tests/test_issue_02.py` |
| ISSUE-03 | La regla de puntos de un distrito afecta a otro | `tests/test_issue_03.py` |

## Las 7 decisiones

| # | Decisión de diseño | Elección para EcoRecicla | Justificación |
|---|---|---|---|
| 1 | **¿Agente o flujo de trabajo?** | **Agente** para los 3 issues; **flujo fijo** para lo que ya es determinista (correr `pytest`, `radon`, `lint-imports`, generar el diagrama de la traza). | Los issues exigen explorar el repositorio para encontrar la causa (¿la duplicación está en `CuentaPuntos`, en el outbox o en `ServicioPuntos`?). Los pasos no se conocen de antemano, así que el LLM debe decidir el flujo (Anthropic, 2024; Albada cap. 1). En cambio, ejecutar las pruebas o renderizar el diagrama siempre son los mismos pasos: ahí un flujo fijo es más barato y predecible. |
| 2 | **Arquetipo** | **ReAct** para el agente único (issue 1) y **planificador-ejecutor + ReAct** para el orquestador (issues 2 y 3). Añadimos **reflexión** mediante el revisor. | Sección 1.3, Tabla 3: ReAct conviene para *explorar un repositorio para localizar un error* (es exactamente lo que hace el agente con `buscar` y `leer_archivo`). El planificador-ejecutor da un plan corto y legible que facilita depurar y abarata la ejecución. La reflexión (revisor que lee el diff antes de aprobar) se justifica porque un cambio en el cálculo de puntos afecta dinero canjeable de los vecinos: alto riesgo. |
| 3 | **Herramientas** | `listar_archivos`, `leer_archivo`, `buscar`, `ejecutar_pruebas`, `editar_archivo`, `ver_cambios`, `ejecutar_comando` (solo `pytest`, `radon cc`, `lint-imports`, `git status/diff`). En E4 (Persona 2) se agregan `mapa_repo()`, `anotar()` y `leer_notas()`. | Tabla 5: pocas herramientas con alcance mínimo. `editar_archivo` exige que el fragmento aparezca exactamente una vez; todas las rutas se validan contra el sandbox (`agentes/trabajo/`). Los errores se devuelven como observaciones para que el agente se corrija. `lint-imports` es útil aquí porque el repo ya tiene contratos de import-linter (FF-01, FF-02) que el agente no debe romper. |
| 4 | **Memoria** | **Corto plazo** (historial de la tarea) para el issue 1. **Notas / pizarra** (`notas.md` con `anotar()` y `leer_notas()`) a partir del issue 3 (E4). **Semántica** mínima: el mapa del repo (`mapa_repo()`) en lugar de leer todo el código. | Tabla 6. Las tareas son cortas (< 12 pasos) y no requieren recordar ejecuciones previas (episódica). Pero el monolito ya tiene 3 módulos y muchos archivos (`prompts/`, `docs/`, `fitness/`), así que el mapa del repo evita gastar contexto listando y leyendo archivos irrelevantes (ingeniería de contexto, G&A caps. 4 y 10). La comparación de pasos y contexto con/sin notas es el experimento de E4. |
| 5 | **Coordinación** | **Agente único** para el issue 1 (línea base). **Por gestor + actor-crítico** (planificador → ejecutor ↔ revisor de solo lectura, máx. 2 rondas) para el issue 2, comparado con el agente único en E5. | Sección 1.7: empezar con un solo agente y añadir más solo si el problema lo pide (parsimonia, Albada cap. 8). El actor-crítico separa quién cambia el código de quién lo revisa y permite dar al revisor solo permisos de lectura (`ver_cambios`, `leer_archivo`, `buscar`, `ejecutar_pruebas`). Descartamos la coordinación democrática (tres revisores votando): es más robusta pero triplica el costo para issues de una sola función. |
| 6 | **Rol humano** | **Revisor** (Albada cap. 13): la persona aprueba cada edición desde la consola (`aprobar_edicion`, E6) y es quien copia el cambio del sandbox al repositorio y fusiona el Pull Request. El agente nunca fusiona su propio cambio. | Es el primer uso del sistema sobre nuestro código: la confianza es baja y las ediciones tocan puntos canjeables (impacto económico) y la ruta del reciclador (impacto operativo). Tabla 8: patrón *aprobar o rechazar* + *validar la entrada humana* (solo "s"/"n"). La hoja de ruta ejecutor → gobernador queda en `delegacion.md` (E6). |
| 7 | **Control** | Contrato estructurado (`contrato.py`), política por rol (`politica.py`), **máx. 12 pasos** por agente, **máx. 2 rondas** actor-crítico, rutas protegidas `tests/` e `issues/`, lista blanca de comandos, sandbox en `agentes/trabajo/`. | Koenigstein caps. 1, 5 y 6: el agente como máquina de estados con guardias y condición de terminación (ver `diseno/estados.puml`). Proteger `tests/` evita que el agente "arregle" la prueba en lugar del código; proteger `issues/` evita que reescriba la tarea. El límite de pasos es la guardia que impide bucles infinitos y costos sin tope. La lista blanca de comandos es la defensa contra inyección indirecta (Greshake et al., 2023) y exceso de agencia (OWASP LLM06). |

## Lo que NO resolvemos con un agente

- Ejecutar la batería de pruebas y las fitness functions del Lab 08: flujo fijo (`python -m pytest -q`, CI).
- Renderizar diagramas a partir de las trazas: flujo fijo (`python agente/traza.py` + `python diagramas_png.py`).
- Clasificar los issues por módulo afectado: bastaría un agente reflexivo (una llamada, sin bucle), pero con 3 issues lo hicimos a mano.

## Checklist E1

- [x] 7 decisiones con justificación ligada a las secciones 1.3 y 1.7.
- [x] 3 issues en `issues/ISSUE-0N.md` con observado, esperado y prueba que lo reproduce.
- [x] 3 pruebas en `tests/test_issue_0N.py` que **fallan** antes de la corrección.
