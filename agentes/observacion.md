# Observación comparativa E4 y E5

## E4 — Issue 3 con mapa_repo y notas

| Variante | Acciones | Bloqueadas | Contexto final |
|---|---:|---:|---:|
| E2 / Issue 1 (agente único) | 9 | 1 | 8,951 caracteres |
| E4 / Issue 3 (herramientas nuevas) | 6 | 0 | 8,140 caracteres |

El Issue 3 usó `mapa_repo` para condensar la estructura de `src/puntos` y
`anotar` para conservar la hipótesis y el archivo revisado. Frente a la
trayectoria de E2, el agente necesitó menos pasos y menos contexto final.

## E5 — Issue 2: agente único frente a actor-crítico

| Variante | Rondas | Acciones | Bloqueadas | Contexto final |
|---|---:|---:|---:|---:|
| Agente único | 1 ejecución | 4 | 1 | 4,874 caracteres |
| Planificador-ejecutor-revisor | 1 | 1 planificador + 4 ejecutor + 2 revisor | 0 | 696 + 3,854 + 1,053 = 5,603 caracteres |

El revisor no encontró un problema adicional que el agente único hubiera
pasado por alto en la trayectoria grabada; ambas variantes terminaron con
la corrección funcional y las pruebas del Issue 2 en verde.

Para este repositorio el costo adicional no compensa de forma automática:
el actor-crítico añadió coordinación, una segunda identidad y más contexto,
sin ampliar el hallazgo en esta ejecución acotada. Puede justificar el costo
cuando el diff afecte varios módulos o cuando el revisor encuentre un defecto;
con una corrección local y reproducible, el agente único sigue siendo más
parsimonioso.
