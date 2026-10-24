# Contrato para continuar E4-E8

## Discrepancias resueltas

1. La guía docente E2 pide Strategy + Adapter + Factory. Se incluyen dos
   adaptadores de SDK de mensajería simulados; guia7.pdf omitía Adapter.
2. La estructura docente ubica la versión refactorizada directamente en el
   módulo: se importa src.solicitudes.servicio. No se crea despues/; ese nombre
   es solo la etiqueta del fixture y el del ejemplo AgroConecta.
3. El Lab 05 establece que Solicitudes NO calcula puntos. Las reglas canónicas
   están en src/puntos/reglas.py y el cálculo en src/puntos/servicio.py.
   src/solicitudes/puntos.py reexporta nombres para la ruta de la división;
   el servicio de Solicitudes no depende de ese puente ni del módulo Puntos.
   La fábrica es por registro (como la guía), no una Abstract Factory ni una
   afirmación de que se implementó el Factory Method GoF canónico por herencia.
4. Volumen estimado = litros; peso real posterior = kg. No son intercambiables.

## APIs y comportamiento que deben conservarse

- ServicioSolicitudes(repositorio, notificador).solicitar_recojo(vecino, direccion, items)
  guarda y devuelve una Solicitud Pendiente; luego se simula el encolado.
- Vecino(id, nombre, celular), ItemMaterial(tipo_material, volumen_estimado_litros).
- asignar_reciclador(reciclador_id), registrar_recojo(), registrar_pesaje(peso_kg),
  registrar_acreditacion(puntos); strings de estado iguales al Lab 05.
- ServicioPuntos(fabrica).calcular_y_acreditar(solicitud) recibe una solicitud
  pesada, calcula y registra puntos una vez. Las reglas solo calculan.
- ReglaPuntos.calcular(volumen_litros) devuelve un valor numérico Decimal-compatible.
  Una bonificación debe envolver esta interfaz para que la fábrica la pueda crear.
- Factory.registrar(material, creador) admite lambdas para configurar decoradores.
- WhatsAppSDK.programar(telefono, cuerpo) devuelve dict; MensajeriaCliente.queue(text, number)
  devuelve tupla. Los adaptadores normalizan a notificar_solicitud(celular, solicitud_id).
- Tres intentos como máximo ante TimeoutError. Una negativa explícita no se reintenta.
- Todas las pruebas son locales. No hay PostgreSQL, Django, Celery ni WhatsApp reales.

## Fabiana (E4-E6)

- Partir de esta rama integrada en main. Evitar reescribir la línea base antes/.
- Observer con dos suscriptores (WhatsApp y estadísticas), y su prueba de extensión.
- Decorator de campaña sobre ReglaPuntos en src/puntos/reglas.py (reexportarlo en
  el puente si es útil); extraer reintentos si se elige ese segundo decorador.
- Añadir ia.py con proveedor intercambiable, adaptador de ClienteLLMFalso,
  caché y al menos dos validaciones encadenadas adecuadas a residuos.
- Mantener las pruebas de caracterización; agregar pruebas explícitas para
  funcionalidades nuevas de E4/E5 y explicar cambios deliberados de contrato.
- Medir todos los archivos de producción nuevos; no comparar un monolito entero
  con un único método corto ni mezclar la copia antes/ dentro del promedio después.

## Flor (E7-E8)

- Diagramas de Strategy, Adapter, Factory, State, Observer, Decorator y Chain,
  según lo que finalmente se implemente; clases.puml debe reflejar rutas reales.
- Actualizar el round-trip: el archivo clases.py será un puente de importación,
  no el modelo canónico. Revisar modelos.py, estados.py, adaptadores.py y src/puntos.
- No atribuir tarifas ni validaciones a una norma: son decisiones didácticas.
- No copiar métricas, fallos de IA ni 27 passed / 1 xfailed de AgroConecta.
- La bitácora final requiere cinco interacciones reales y una corrección
  detectada por pruebas; este paquete no inventa cinco conversaciones.
- ADR-005, README y etiqueta v0.7-patrones después de integrar los tres PR.
  El README actual usa UTF-16 y termina dentro de un bloque Mermaid sin cerrar:
  convertirlo cuidadosamente a UTF-8 y cerrar el bloque al actualizarlo.

La implementación es un prototipo ejecutable para Lab 07. No despliega el MVP.
