# E1 — Catálogo MCP de EcoRecicla AQP

Responsable: Andrés (Persona 1). Caso 10. Alcance: demostración local con datos
ficticios; transporte stdio y SDK oficial Python mcp 2.3.0.

## Decisiones de exposición

| Capacidad | Primitiva / identificador | ¿Escribe? | Justificación |
| --- | --- | --- | --- |
| Saldo e historial de un vecino | Tool `puntos_usuario` | No | El modelo elige el vecino de la consulta. |
| Ruta por fecha y distrito | Tool `rutas_del_dia` | No | Requiere parámetros y el planificador del dominio. |
| Solicitud de recojo demo | Tool `registrar_solicitud` | Sí, solo creación | Única acción persistente; genera un JSON nuevo con UUID. |
| Tarifas estándar de materiales | Resource `ecorecicla://puntos/tabla` | No | Contexto estable que el host decide incorporar; calculado desde la fábrica real. |
| Datos disponibles y límites | Resource `ecorecicla://demo/contexto` | No | Evita inventar vecinos, distritos o una conexión con producción. |
| Decisiones de arquitectura | Resource template `ecorecicla://adr/{numero}` | No | Contexto por URI; lectura limitada a `docs/architecture/adr/`. |
| Documentación de funciones | Prompt `documentar_funcion` | No | Lo solicita el usuario; reutiliza `prompts/docstrings/v3.txt` del Lab 09. |

Hay exactamente **3 tools, 2 recursos estáticos, 1 recurso plantilla y 1 prompt**.
El orden de declaración de herramientas es estable y se verifica en E3.

## Contratos de herramientas

### puntos_usuario(vecino_id)

Consulta saldo y movimientos ficticios sin modificar la cuenta. `vecino_id` es
texto obligatorio de 1–40 caracteres: `vecino-7`, `vecino-8` o `vecino-9`.
Devuelve `{vecino_id, saldo, movimientos:[{solicitud_id,puntos}]}`.
Ejemplo: `{"vecino_id":"vecino-7"}` devuelve saldo 25 y dos movimientos.
Un vecino desconocido produce `isError=true` con identificadores válidos.
El saldo procede de `CuentaPuntos.acreditar` sobre una cuenta temporal; no se
duplica la regla de acreditación ni se persisten cambios al consultar.

### rutas_del_dia(fecha, distrito)

Lista hasta 20 paradas activas del distrito y día, ordenadas por dirección.
`fecha`: texto de 10 caracteres, fecha real `AAAA-MM-DD`.
`distrito`: texto de 1–40 caracteres, exactamente `Cayma`, `Yanahuara` o
`Cerro Colorado`. Ambos parámetros son obligatorios.
Devuelve `{fecha,distrito,total,truncado,paradas:[{solicitud_id,direccion,estado,vecino_id}]}`.
`total` cuenta todas las coincidencias; `truncado` indica si se omitieron resultados
por el límite. Sin coincidencias devuelve una lista vacía, no un error.
Ejemplo: `{"fecha":"2026-11-25","distrito":"Cayma"}` devuelve `demo-002`,
`demo-001`. Excluye la cancelada, otra fecha y otro distrito.
Fechas imposibles o distritos desconocidos producen errores con instrucciones.
La fecha es metadato del adaptador demo porque la entidad actual no la contiene;
la selección por estado/distrito y el orden pertenecen a `planificar_ruta`.

### registrar_solicitud(vecino_id, fecha, distrito, direccion, material, volumen_litros)

Crea una solicitud local ficticia en estado `Pendiente`. Todos los parámetros
son obligatorios. Los tres primeros usan los formatos anteriores.
`direccion`: 5–160 caracteres tras recortar extremos, sin caracteres de control.
`material`: `PLASTICO`, `VIDRIO` o `PAPEL` en mayúsculas.
`volumen_litros`: número finito mayor que 0 y menor o igual que 1000; no se aceptan
cadenas ni booleanos. Los límites también figuran en el JSON Schema.
Devuelve `{solicitud_id,estado,fecha,distrito,demo:true}`.

Ejemplo:

```json
{"vecino_id":"vecino-7","fecha":"2026-11-25","distrito":"Cayma","direccion":"Calle Demo Z 900","material":"PLASTICO","volumen_litros":10}
```

Delega en `ServicioSolicitudes.solicitar_recojo`, `ItemMaterial`, `Solicitud` y
la fábrica real de materiales. El puerto de notificación es una implementación
demo sin red. El adaptador de repositorio agrega fecha/distrito y persiste.
La nueva solicitud aparece en `rutas_del_dia`, incluso al reiniciar el servidor.
No se acreditan puntos al crearla: falta el ciclo de recojo, pesaje y acreditación.

## Salida estructurada y errores

Las tres herramientas usan `TypedDict`, publican `outputSchema` y devuelven
`structuredContent`. Los errores semánticos se convierten en `ToolError`;
el SDK convierte errores de tipo/límites del esquema en resultados de tool con
`isError=true`. El texto permite corregir los argumentos.
Los errores de lectura de ADR usan `ResourceError` (error de recurso/protocolo).
No se escribe texto de depuración en stdout del servidor: se reserva para MCP.

## Por qué la escritura es acotada

- Solo crea `agentes/mcp/datos/solicitudes/<UUID>.json`; el usuario no elige rutas.
- Usa apertura exclusiva `open(..., "x")`: una colisión no sobrescribe un archivo.
- No expone borrado, edición, shell, red, notificaciones reales ni credenciales.
- Los registros son ficticios, ignorados por Git y no están conectados a producción.
- Una llamada repetida crea otro registro: se anuncia `idempotentHint=false`.
- Las consultas llevan `readOnlyHint=true`, `destructiveHint=false`,
  `idempotentHint=true` y `openWorldHint=false`.
- La creación lleva `readOnlyHint=false`, `destructiveHint=false`,
  `idempotentHint=false` y `openWorldHint=false`.

Las anotaciones son pistas, no autorización. En E4/E5 la Persona 2 debe exigir
aprobación humana en el host/política; el servidor stdio no puede probar por sí
solo que un humano aprobó. No se presenta un parámetro booleano como garantía.
El acceso al directorio local debe limitarse al usuario que ejecuta el servidor;
esto es un prototipo del curso, no una API autenticada multiusuario.

## Recursos y prompt

`ecorecicla://puntos/tabla` indica puntos/litro, no puntos/kg. Las tarifas estándar
son PLASTICO=2, VIDRIO=1 y PAPEL=1; las produce `fabrica_estandar`, no una segunda
tabla de lógica. No incluye campañas ni sobrescrituras por distrito.

La plantilla ADR acepta tres dígitos ASCII (por ejemplo `001` o `010`) y rechaza
`..`, rutas codificadas y enlaces simbólicos. No crea ADR-011 (entregable E8).

`documentar_funcion(funcion,codigo)` recibe un identificador Python de hasta
80 caracteres y código no vacío de hasta 12000 caracteres. Devuelve el prompt v3
con los marcadores sustituidos una sola vez y conserva las instrucciones para
tratar código/comentarios como datos. Obtener el prompt no ejecuta código ni llama
al LLM. Es una reutilización verificable del Lab 09, no una plantilla nueva.

## Fuentes de implementación

- Guía Lab 11, E1–E3 y tabla 14 (caso 10); recursos docentes AgroConecta.
- Código real de este repositorio en `src/puntos`, `src/rutas`, `src/solicitudes`.
- [SDK oficial](https://github.com/modelcontextprotocol/python-sdk).
- [Especificación 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28).
