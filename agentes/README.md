# Sistema agéntico de EcoRecicla AQP (Lab 10)

Mini framework de agentes del curso (bucle ReAct como máquina de estados) apuntando a una
copia del repositorio (`agentes/trabajo/`, ignorada por git). **El agente propone; el contrato y la
política filtran; el humano aprueba.**

    pip install pytest radon
    python -m pytest -q pruebas_agente                     # contrato, política y sandbox (sin LLM)
    python ejecutar_issue1.py                              # E2: agente único sobre ISSUE-01 (ModeloInteractivo)
    python agente/traza.py trazas/issue1_agente_unico.jsonl   # traza JSONL -> diagrama Mermaid + métricas
    python diagramas_png.py trazas/issue1_agente_unico.mmd diseno/estados.puml   # PNG vía kroki.io
    python orquestador.py --issue 2 --interactivo          # E5: planificador -> [ejecutor <-> revisor] -> humano

| Carpeta / archivo | Contenido | Entregable |
|---|---|---|
| `diseno/lienzo.md` | lienzo de diseño (7 decisiones) | E1 |
| `diseno/estados.puml` + `.png` | máquina de estados del agente | E3 |
| `agente/` | núcleo ReAct, contrato, política, herramientas (sandbox), modelos, traza | E2–E5 |
| `pruebas_agente/` | pruebas del contrato, la política y el sandbox | E3, E4 |
| `sandbox.py` | copia parcial del repo a `trabajo/` | E2 |
| `ejecutar_issue1.py` | agente único con ModeloInteractivo | E2 |
| `orquestador.py` | coordinación por gestor + actor-crítico + humano | E5, E6 |
| `trayectorias/*.json` | decisiones grabadas del asistente | E2, E5 |
| `trazas/*.jsonl`, `*.mmd`, `*.png` | trazas y diagramas generados | E2, E5, E7 |

## Cómo pasa un cambio del sandbox al repositorio

El agente edita solo `agentes/trabajo/src/...`. Al terminar, el script imprime el diff
(`ver_cambios`). Un integrante lo revisa y, si lo aprueba, copia el archivo corregido a `src/`
(por ejemplo `cp agentes/trabajo/src/puntos/cuenta.py src/puntos/cuenta.py`), corre
`python -m pytest -q` en la raíz y hace el commit. Nunca se fusiona un cambio sin esa revisión.
