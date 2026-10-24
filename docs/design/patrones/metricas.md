
# E6: Métricas y Trade-offs de Patrones de Diseño (EcoRecicla AQP)

**Fecha:** 24/10/2026  
**Responsable:** Fabiana Paola Rojas Condori   
**Herramientas:** `radon 6.0.1`, `pytest 9.1.1`

---

## 1. Tabla Comparativa de Complejidad Ciclomática (Radon CC)

Se comparó la versión monolítica inicial (`src/solicitudes/antes/servicio.py`) con la versión refactorizada, distribuida en los módulos de `src/solicitudes/` y `src/puntos/`.

### 1.1. Complejidad por método

| Componente / Método Crítico | Antes (Monolito) | Después (Patrones GoF) | Interpretación |
| :--- | :---: | :---: | :--- |
| `ServicioSolicitudes.solicitar_recojo` | **14 (C)** | **1 (A)** | El método principal delega las responsabilidades en componentes especializados. |
| `ServicioSolicitudes.validar_datos` | Integrado en el monolito | **6 (B)** | La validación se separa del flujo principal. |
| `ServicioSolicitudes._encolar_confirmacion` | Integrado en el monolito | **4 (A)** | El encolado se aísla mediante adaptadores. |
| `ServicioPuntos.calcular_y_acreditar` | **6 (B)** | **2 (A)** | El cálculo de puntos se delega a estrategias polimórficas. |
| `ConCacheLLM.clasificar_residuo` | No existía | **2 (A)** | La caché evita llamadas repetidas al proveedor de IA. |
| `SinResiduosPeligrosos._aplicar` | No existía | **3 (A)** | Se incorpora una validación determinista de materiales peligrosos. |

### 1.2. Promedio global de complejidad

| Métrica | Antes (`antes/`) | Después (Módulos Refactorizados) | Total Analizado (Salida Radon) |
| :--- | :---: | :---: | :---: |
| Bloques analizados | 14 | 100 | 114 |
| Complejidad ciclomática promedio | **4,14 (A)** | **1,76 (A)** | **2,05 (A)** |
| Mayor complejidad de un método | 14 (C) | 6 (B) | 14 (C) *(en `antes/`)* |

El promedio de complejidad de los bloques analizados disminuyó de 4,14 a 1,76, una reducción aproximada del 57,5 % entre los conjuntos medidos. La ejecución conjunta de Radon analizó 114 bloques y obtuvo un promedio de 2,05 (A), incluyendo los 14 bloques de la versión anterior. Por ello, se presentan por separado los resultados de cada versión para facilitar una comparación más clara.


El cambio más significativo se observa en `solicitar_recojo`, cuya complejidad pasó de 14 (C) a 1 (A), equivalente a una reducción del **92,9 %** en ese método orquestador. Ningún método en la versión refactorizada supera una complejidad ciclomática de 6.

---

## 2. Comparativa de Tamaño y Mantenibilidad (Radon RAW y MI)

### 2.1. Tamaño del código

| Métrica | Antes (`antes/servicio.py`) | Después (módulos refactorizados) | Variación |
| :--- | :---: | :---: | :---: |
| Líneas totales (LOC) | 122 | 420 | +244,3 % |
| Líneas lógicas (LLOC) | 107 | 313 | +192,5 % |
| Líneas de código reales (SLOC) | 101 | 287 | +184,2 % |
| Archivos Python incluidos en la medición | 1 archivo monolítico | 9 archivos de producción |  +8 archivos medidos |

Las cifras posteriores corresponden a los nueve archivos de producción incluidos en los comandos de medición de Radon. Se excluyen el directorio `antes/`, los archivos `__init__.py`, las pruebas y otros módulos que no se incluyeron en dicha medición. Por tanto, la comparación se refiere únicamente a los archivos analizados y no al número total de archivos del proyecto.

El aumento de SLOC refleja la separación de responsabilidades en módulos especializados, la introducción de interfaces y la implementación de los patrones de diseño.

### 2.2. Índice de mantenibilidad

| Archivo | MI | Grado |
| :--- | :---: | :---: |
| Versión anterior: `antes/servicio.py` | 44,18 | A |
| `adaptadores.py` | 63,09 | A |
| `estados.py` | 54,46 | A |
| `eventos.py` | 63,28 | A |
| `externos.py` | 49,09 | A |
| `ia.py` | 48,77 | A |
| `modelos.py` | 54,47 | A |
| `servicio.py` | 65,31 | A |
| `reglas.py` | 55,56 | A |
| `puntos/servicio.py` | 100,00 | A |

Radon asignó grado A a todos los archivos posteriores medidos. Los valores de MI varían entre 48,77 y 100,00. Este índice debe interpretarse junto con la complejidad, el tamaño del código y la facilidad para realizar pruebas; no constituye por sí solo una garantía de calidad.

---

## 3. Análisis Honesto del Trade-off (Costo vs. Beneficio)

La refactorización redujo la complejidad ciclomática de `solicitar_recojo` de 14 a 1 y el promedio de los bloques medidos de 4,14 a 1,76. Esto permite separar responsabilidades y facilita las pruebas y el mantenimiento de cada componente. El costo fue aumentar el código de 101 a 287 SLOC y pasar de un archivo a nueve archivos medidos. También se introdujeron más niveles de indirección y conceptos que el equipo debe comprender. Este costo se justifica si EcoRecicla AQP necesita incorporar nuevos materiales, estrategias de puntos, proveedores de mensajería y guardrails de IA con frecuencia. Si el sistema fuera pequeño, estable y con reglas que rara vez cambian, la versión monolítica habría sido suficiente y más sencilla de mantener. Por ello, la decisión de refactorizar depende de la evolución prevista del sistema y no de aplicar patrones por sí mismos.

---

## 4. Patrones Rechazados y Justificación

### 4.1. Singleton para `FabricaReglasPuntos`

**Propuesta:** implementar `FabricaReglasPuntos` como un Singleton para compartir una única instancia global en todo el sistema.

**Motivo de rechazo:** el Singleton puede introducir estado global compartido y dificultar el aislamiento de las pruebas unitarias. También limita la sustitución de dependencias por implementaciones alternativas o mocks.

**Alternativa elegida:** una fábrica basada en un registro de estrategias inyectable, que permite registrar y sustituir reglas sin imponer una instancia global.

### 4.2. Abstract Factory para familias de materiales

**Propuesta:** crear una jerarquía de fábricas para construir familias de objetos relacionados con cada tipo de residuo.

**Motivo de rechazo:** el sistema necesita seleccionar una regla de puntos según el material, pero no requiere construir familias complejas de productos relacionados. Incorporar esa jerarquía aumentaría la cantidad de abstracciones sin un beneficio proporcional.

**Alternativa elegida:** un registro de estrategias junto con una fábrica sencilla, suficiente para seleccionar la regla de puntos correspondiente.

### 4.3. LLM como juez evaluador de otra respuesta de IA

**Propuesta:** realizar una segunda llamada a un modelo de lenguaje para verificar la clasificación producida por el primer modelo.

**Motivo de rechazo:** esta solución agregaría latencia, consumo de tokens y variabilidad a una validación que puede resolverse con reglas deterministas.

**Alternativa elegida:** una cadena de responsabilidad (`Chain of Responsibility`) compuesta por `SinResiduosPeligrosos` y `CategoriaPermitida`, que comprueba los materiales peligrosos y las categorías admitidas mediante reglas explícitas y auditables.

---

## 5. Conclusiones

Las mediciones de Radon muestran una disminución de la complejidad del método principal y un promedio de complejidad inferior en el conjunto de componentes refactorizados. El costo fue un incremento importante del tamaño del código y del número de archivos. Este aumento se considera razonable si los requisitos del proyecto evolucionan y se necesitan nuevas estrategias, proveedores o validaciones. La selección de patrones se basó en necesidades concretas, evitando mecanismos adicionales que no aportaran suficiente valor. Las métricas deben evaluarse junto con las pruebas automatizadas y la facilidad de evolución del sistema.
