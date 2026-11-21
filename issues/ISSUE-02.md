# Issue #02: La ruta diaria incluye solicitudes canceladas

**Reportado por:** reciclador formalizado de Cayma
**Modulo:** `src/rutas/planificador.py` (HU-03) y `src/solicitudes/estados.py`

**Observado:** la ruta del martes incluyo la parada en Calle Mercaderes 200
aunque el vecino cancelo la solicitud la noche anterior. El reciclador llego y
no habia material.

**Esperado:** `planificar_ruta()` solo incluye solicitudes del distrito que
siguen activas para recojo (`Pendiente` o `Asignada`). Una solicitud
`Cancelada` no debe aparecer en la ruta.

**Prueba que reproduce el error:**
`tests/test_issue_02.py::test_issue_02_ruta_excluye_solicitudes_canceladas`

**Restricciones para el agente:** no modificar `tests/` ni `issues/`; la
transicion `cancelar()` ya existe en el patron State y no debe eliminarse.
