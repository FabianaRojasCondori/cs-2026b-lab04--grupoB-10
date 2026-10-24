# E1: olores y decisiones propuestas para EcoRecicla AQP

Base revisada: main 4d198cfd25a02e4b7c8ee25a1220deb5da853b3e (24/10/2026).
El Lab 05 trae un esqueleto sin comportamiento completo. E1 implementa primero
una línea base ejecutable conforme a historia.md, secuencia-solicitar-recojo.puml
y estados-solicitud.mmd. La equivalencia se mide entre E1 y E2/E3; no se afirma
que el esqueleto original ya validaba datos o lanzaba estas excepciones.

| Olor real en E1 | Patrón propuesto | SOLID | Decisión de esta implementación |
|---|---|---|---|
| if/elif por material en ServicioPuntos | Strategy y Factory de registro | OCP, DIP | Aplicar en E2; nueva regla por registro, sin editar el servicio |
| ServicioSolicitudes conoce programar y queue de dos SDK | Adapter | DIP, ISP | Aplicar en E2; convertir argumentos y respuestas, sin reglas de puntos |
| Cada transición pregunta por el nombre del estado | State | SRP, OCP | Aplicar en E3 conforme a los cinco estados del Lab 05 |
| Reintentos mezclados con el registro | Decorator | SRP, OCP | Pendiente de E4 (Fabiana); conservar la política de tres intentos |
| Notificación enlazada directamente al flujo | Observer | SRP, OCP | Pendiente de E4 (Fabiana), con al menos dos suscriptores |
| Idea candidata: una fábrica Singleton para compartir reglas | Singleton | DIP y aislamiento de pruebas | Rechazada: estado global, fuga entre pruebas y dependencia oculta; se inyecta una fábrica por composición |

La propuesta y rechazo de Singleton son parte de la revisión asistida de este
paquete. La aprobación humana y su registro definitivo corresponden al equipo.
No se inventan interacciones ni revisiones de los integrantes.

## Decisiones explícitas de la línea base

- Entrada: volumen estimado en litros; pesaje posterior en kg. No se convierten
  litros a kg. Son magnitudes distintas, como en el diseño del Lab 05.
- Tarifas SOLO para la demostración: PLASTICO=2, VIDRIO=1, PAPEL=1 punto/litro.
  Se suman con Decimal, se trunca una vez al final y se exigen puntos > 0.
  El repositorio no define tarifas oficiales; estas requieren revisión del equipo.
- Crear la solicitud no calcula ni acredita puntos: devuelve Pendiente, guarda
  primero y después encola la confirmación. La entrega de WhatsApp queda fuera.
- Se reintenta exclusivamente TimeoutError, como máximo tres intentos.
  Si falla el encolado, el registro ya persistido permanece; no se promete una
  transacción distribuida ni idempotencia de producción. E4 debe conservarlo
  o documentar un cambio deliberado y sus pruebas.
- Los identificadores son simbólicos y todos los servicios se simulan.

## Métrica inicial

Ver radon-E1.txt y radon-antes.txt, generados con radon 6.0.1.
La complejidad no se incrementó con ramas sin propósito: proviene de validar,
seleccionar SDK, normalizar resultados y controlar reintentos.
