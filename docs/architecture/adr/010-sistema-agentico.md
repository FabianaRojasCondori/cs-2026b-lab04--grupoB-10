# ADR-010: Arquitectura del Sistema Agéntico para Mantenimiento de EcoRecicla AQP

* **Estado:** Aprobado
* **Fecha:** 2026-11-21
* **Autores:** Grupo B-10 (Integrante 3: Flor de Liz Velazque Quispe)

## Contexto
Para resolver incidencias de negocio en EcoRecicla AQP (duplicidad de puntos, filtrado de rutas canceladas y aislamiento multitenant) se requiere un sistema capaz de explorar el repositorio, proponer parches y validarlos automáticamente sin comprometer la integridad de las pruebas ni ejecutar comandos inseguros.

## Decisión Arquitectónica
Se adopta un **Sistema Multiagente acotado por Máquina de Estados Finitos** con las siguientes características:
1. **Arquetipo:** Combinación de **Planificador-Ejecutor** con bucle **ReAct** (*Pensamiento → Acción → Observación*) controlado por contrato JSON estricto.
2. **Coordinación:** Patrón **Actor-Crítico** con un máximo de `2 rondas` (Planificador sin herramientas → Ejecutor con edición controlada → Revisor de solo lectura).
3. **Herramientas y Memoria:** Herramientas mínimas encapsuladas en sandbox (`leer_archivo`, `buscar`, `editar_archivo`, `ejecutar_pruebas`, `mapa_repo`) y memoria híbrida de corto plazo (historial) más memoria de notas persistente (`notas.md`).
4. **Límites y Guardrails:** Lista blanca de comandos (`pytest`, `radon`, `lint-imports`), bloqueo de escritura en `tests/` y presupuesto máximo de pasos (`max_pasos = 12`).
5. **Rol Humano:** Nivel **Revisor** (*Human-in-the-Loop*), exigiendo aprobación explícita en consola (`s/n`) antes de aplicar ediciones y validación humana final del Pull Request.

## Alternativas Descartadas
* **Flujo de trabajo fijo (Pipeline rígido):** Descartado porque localizar errores de lógica requiere exploración dinámica del código según los resultados de `pytest`.
* **Coordinación en Enjambre o Democrática (3 revisores votando):** Descartada por el **principio de parsimonia**; multiplicaba el consumo de tokens y latencia sin aportar mejoras significativas sobre un único crítico especializado.
* **Autonomía total (Rol Gobernador sin confirmación):** Descartada por alto riesgo de exceso de agencia (OWASP LLM06) en etapas iniciales de adopción.

## Consecuencias
* **Positivas:** Trazabilidad completa en formato `.jsonl`, cero modificaciones indebidas en suites de pruebas y reducción de errores sintácticos gracias a la validación de contrato.
* **Negativas:** Mayor latencia y consumo de tokens en incidencias que requieren segunda ronda de revisión.