# Delegación progresiva del sistema agéntico

## Ejecutor humano

El agente conserva permisos de lectura, búsqueda, ejecución acotada de pruebas y
propuesta de edición. Solo puede editar código fuera de `tests/` e `issues/`.
Pasa a revisor cuando reproduce el fallo, identifica una causa acotada y entrega
una primera prueba en verde en el sandbox.

Evidencia mínima: trazas con acciones permitidas, una edición exacta, resultado
de `ejecutar_pruebas` y ausencia de rechazos por ruta protegida.

## Revisor humano

El agente recibe permisos de solo lectura sobre cambios y pruebas:
`ver_cambios`, `leer_archivo`, `buscar` y `ejecutar_pruebas`. No puede editar ni
ejecutar comandos arbitrarios. Pasa a colaborador cuando el revisor confirma el
diff y la prueba objetivo, o cuando quedan observaciones de un actor-crítico.

Evidencia mínima: una decisión `APROBADO`, diff limitado al issue, pruebas objetivo
en verde y ninguna modificación fuera del alcance.

## Colaborador humano

El agente puede coordinar plan, edición y revisión en rondas acotadas, pero cada
edición requiere aprobación humana desde la consola. El valor admitido es
exactamente `s` o `n`; otra entrada vuelve a solicitarla y `EOF` se interpreta
como rechazo seguro. Pasa a gobernador solo tras pasar el revisor y demostrar
reproducibilidad.

Evidencia mínima: trazas del planificador, ejecutor y revisor; máximo dos rondas;
una aprobación o rechazo humano asociado a cada edición; diff final revisado.

## Gobernador humano

El agente conserva un presupuesto máximo de pasos y políticas por rol, pero el
humano conserva autoridad sobre fusión, despliegue y liberación. El agente puede
proponer cambios y explicar impacto, no fusionarlos automáticamente.

Evidencia mínima: contexto final y métricas de pasos/bloqueos registradas,
pruebas verdes, revisión humana registrada y cumplimiento de las restricciones
del issue. Solo se pasa a mayor autonomía si no aparecen errores nuevos ni
decisiones fuera de contrato en varias ejecuciones reproducibles.
