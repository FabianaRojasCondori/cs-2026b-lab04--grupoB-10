# ADR-008: Estrategia de Multitenancia por Distrito

* **Estado:** Aprobado
* **Fecha:** 2026-11-05
* **Autores:** Flor de Liz Velazque Quispe
* **Atributo de Calidad Asociado:** [QA-03] Modificabilidad y Seguridad (Aislamiento de Tenants)

## Contexto
Múltiples municipios de Arequipa (Cayma, Yanahuara, Cercado) comparten la plataforma EcoRecicla AQP, requiriendo aislamiento estricto de configuraciones de reciclaje y datos de vecinos.

## Decisión
Implementar un esquema de **Multitenancia Híbrida Lógica** utilizando `tenant_id` en la capa de datos con filtros automáticos a nivel de ORM (Django) y aislamiento de esquemas según la carga del municipio.

## Consecuencias
* **Positivas:** Permite incorporar un nuevo municipio en menos de 1 día-persona sin desplegar nueva infraestructura.
* **Negativas:** Se requiere rigurosidad en las consultas SQL personalizadas para no omitir el filtro por `tenant_id`.