# Issue #01: Puntos acreditados dos veces al vecino

**Reportado por:** administracion municipal (reporte mensual de canje)
**Modulo:** `src/puntos/cuenta.py` (HU-05, ADR-007 cola outbox)

**Observado:** el vecino `vecino-7` entrego una sola solicitud (`sol-001`) de
10 litros de plastico (20 puntos). Tras una caida breve de la cola de
notificaciones, el evento `puntos_acreditados` se reintento y la cuenta quedo
con **40 puntos** y dos movimientos para la misma solicitud.

**Esperado:** una solicitud acredita puntos **una sola vez**, aunque el evento
llegue repetido. El saldo debe quedar en 20 y debe existir un unico movimiento
para `sol-001`. Solicitudes distintas si deben sumar.

**Prueba que reproduce el error:**
`tests/test_issue_01.py::test_issue_01_reintento_del_evento_no_acredita_dos_veces`

**Restricciones para el agente:** no modificar `tests/` ni `issues/`; la
correccion debe mantener en verde `tests/test_patrones.py` y
`tests/test_comportamiento.py`.
