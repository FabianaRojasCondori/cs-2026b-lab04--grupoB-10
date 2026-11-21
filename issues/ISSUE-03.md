# Issue #03: La regla de puntos de un distrito afecta a otro

**Reportado por:** coordinador del piloto de Yanahuara
**Modulo:** `src/puntos/distritos.py` (ADR-008 multitenencia por distrito)

**Observado:** Cayma activo una campana que triplica los puntos del plastico.
Desde ese momento los vecinos de Yanahuara, que no tienen campana, tambien
reciben 60 puntos por 10 litros en lugar de 20.

**Esperado:** la configuracion de `ReglasDistrito("Cayma")` no debe alterar a
`ReglasDistrito("Yanahuara")`. Cada instancia mantiene sus propias tarifas y,
si no configura nada, usa la fabrica estandar.

**Prueba que reproduce el error:**
`tests/test_issue_03.py::test_issue_03_regla_de_un_distrito_no_afecta_a_otro`

**Restricciones para el agente:** no modificar `tests/` ni `issues/`; no tocar
`src/puntos/reglas.py` (las reglas estandar son correctas).
