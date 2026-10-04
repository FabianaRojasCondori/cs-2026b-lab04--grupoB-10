# ADR-003: Adopción de Progressive Web App (PWA) para la Aplicación del Reciclador
Estado: Aceptado
Fecha: 2026-10-03
Decisores: Equipo de Desarrollo Grupo B-10

## Contexto
Los recicladores formalizados operan en campo utilizando smartphones de gama baja con cobertura de datos 3G intermitente (QA-02). Se requiere una solución que no obligue al usuario a descargar aplicaciones pesadas desde tiendas de apps y que permita registrar recolecciones fuera de línea, dentro del plazo de 1 mes (R-01).

## Alternativas consideradas
1. **Aplicación móvil nativa (Flutter / Kotlin):** Excelente rendimiento local, pero requiere desarrollo y empaquetado adicional, superando la capacidad del equipo en 1 mes (R-01, R-02).
2. **Aplicación Web Tradicional (Responsive Web):** Muy rápida de construir, pero no funciona en modo desconectado ante caídas de señal móvil en la calle.
3. **Progressive Web App (PWA) con Service Workers e IndexedDB (Elegida):** Web instalable y liviana que almacena en caché la interfaz y sincroniza los datos localmente.

## Decisión
Desarrollaremos el cliente móvil como una **Progressive Web App (PWA)** utilizando Service Workers para soporte offline y almacenamiento en IndexedDB para registrar transacciones de recojo que se sincronizarán automáticamente al detectar conexión.

## Consecuencias
- **Positivas:** Una sola base de código frontend; peso de descarga inferior a 2 MB (ideal para 3G y gama baja según QA-02); entrega viable dentro del plazo (R-01).
- **Negativas / Riesgos:** La gestión de resolución de conflictos durante la sincronización diferida debe ser rigurosamente programada en el cliente.