# ADR-001: Adoptar Monolito Modular para EcoRecicla AQP
Estado: Aceptado
Fecha: 2026-10-03
Decisores: Equipo de Desarrollo Grupo B-10

## Contexto
El proyecto EcoRecicla AQP debe entregar un MVP en producción en el plazo estricto de 1 mes (R-01) con un equipo de 3 desarrolladores (R-02) y un presupuesto limitado a un único VPS económico (R-03). El atributo de calidad crítico es la Modificabilidad (QA-01), que exige agregar distritos o variar la lógica de puntos ecológicos en ≤ 2 días-persona sin alterar el resto del sistema.

## Alternativas consideradas
1. **Monolito tradicional en capas (Puntaje: 3.95):** Simple de construir inicialmente, pero sufre de alto acoplamiento horizontal con el tiempo, poniendo en riesgo QA-01.
2. **Microservicios (Puntaje: 2.90):** Excelente aislamiento y escalabilidad, pero descartado por requerir múltiples tuberías CI/CD, monitoreo distribuido y mayor costo de nube, inviable para R-01 y R-03.
3. **Monolito modular (Puntaje: 4.10) (Elegido):** Despliegue único que organiza el código internamente en módulos desacoplados con interfaces públicas explícitas.

## Decisión
Usaremos una arquitectura de **Monolito Modular**. El sistema se estructurará en 4 módulos de dominio (Solicitudes, Rutas, Puntos y Reportes) dentro de una única base de código en Django, comunicados mediante servicios de aplicación y adaptadores.

## Consecuencias
- **Positivas:** Despliegue y mantenimiento simplificados en un único VPS; aislamiento de código que facilita cumplir QA-01; no introduce sobrecarga de red entre módulos.
- **Negativas / Riesgos:** Un error de memoria o bloqueo no gestionado en un módulo puede comprometer la disponibilidad de toda la instancia; el equipo debe mantener disciplina y linters para no romper las fronteras entre módulos.

## Precisión de implementación para el Lab 06

Esta precisión se incorpora para revisión del equipo en el PR
del modelo C4.

Se conserva el monolito modular de Django. La API utiliza Django
REST Framework, como ya se representa en el README del Lab 04.

La PWA utiliza Service Workers e IndexedDB según el ADR-003.
La persistencia utiliza PostgreSQL con esquemas separados,
según el ADR-002. Redis mantiene la cola y la caché, como se
representa en despliegue.py.

Para concretar la notificación asíncrona del flujo
"Solicitar recojo de reciclables" del Lab 05, se propone
un proceso worker de Celery que consume tareas desde Redis
y utiliza WhatsApp Business API.

El worker reutiliza la base de código del proyecto y no
constituye un microservicio de dominio independiente.
Se distingue de Redis en C4 porque ejecutar tareas y almacenar
la cola son responsabilidades de unidades de ejecución distintas.

La notificación se solicita después de confirmar el guardado.
La entrega se realiza en segundo plano, con reintentos ante fallos.
Esta separación no elimina por sí sola el riesgo de fallo entre
guardar y encolar; su tratamiento debe resolverse al implementar.