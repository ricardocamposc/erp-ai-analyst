# ADR-0006 — Agentic dynamic query execution with deterministic guardrails

- **Estado:** Accepted for Slice 10
- **Fecha:** 2026-08-25
- **Decisión:** autoriza la implementación de Slice 10 bajo los guardrails definidos

## Contexto

El catálogo de tools especializadas y rutas de intención se está convirtiendo en un catálogo cerrado de preguntas. Una nueva dimensión o combinación de filtros suele exigir otra tool aunque los datos ya existan en el modelo canónico.

El sistema necesita responder consultas analíticas nuevas sin conceder al LLM permisos irrestrictos sobre PostgreSQL.

## Decisión propuesta

Adoptar un workflow agentic de consulta dinámica:

1. El LLM descubre metadata ERP mediante tools.
2. El agente analista genera plan y SQL candidato.
3. El agente validador revisa semántica, joins y coherencia.
4. Un parser/guardrail determinista aprueba o rechaza la consulta.
5. Un usuario read-only ejecuta sólo SQL aprobado.
6. El resultado se sintetiza y audita.

Las tools estáticas se mantienen para cálculos especializados y como ruta de migración, pero dejan de ser el límite principal de preguntas.

Los contratos de tools se abstraen mediante `ToolProvider` para permitir una implementación local y una futura implementación MCP.

## Alternativas consideradas

### Mantener sólo tools estáticas

Ventajas: seguridad, tipos y ground truth directos.

Desventajas: baja generalización, crecimiento por pregunta y sobreajuste a evaluaciones congeladas.

### Ejecutar SQL libre generado por el LLM

Ventajas: máxima flexibilidad y menor código de routing.

Desventajas: riesgo destructivo, acceso indebido, joins incorrectos, coste impredecible y baja auditabilidad sin una barrera posterior.

### Plan estructurado sin SQL generado

Ventajas: validación fuerte y portabilidad.

Desventajas: exige un compilador semántico amplio y puede ocultar capacidades del motor necesarias para análisis nuevos.

## Consecuencias

### Positivas

- Nuevas combinaciones de métricas y dimensiones sin una tool por pregunta.
- Mejor demostración de Agentic AI aplicada a ERP.
- Separación clara entre razonamiento, seguridad y ejecución.
- Compatibilidad futura con providers MCP.
- Auditoría de SQL, decisiones y costes.

### Negativas

- Mayor complejidad de validación y evaluación.
- Corrección sintáctica no garantiza corrección empresarial.
- Se requiere un catálogo semántico mantenido.
- SQL y planes dependen del motor.
- MCP requiere adaptador y pruebas de equivalencia.

## Seguridad obligatoria

La seguridad final no puede depender sólo del LLM o del agente validador. Debe existir parser AST, allowlist, permisos read-only, timeout, límites de filas, límites temporales, control de coste y auditoría.

## Compatibilidad MCP

MCP debe implementarse como un provider que expone metadata, validación, explicación y ejecución read-only con contratos equivalentes a los providers locales. La adopción futura debe cambiar transporte/configuración, no la semántica del workflow.

## Estado

Esta ADR autoriza Slice 10 y supersede, para ese slice, la prohibición absoluta de SQL generado por el LLM en `docs/CTX.md` y ADR-0002. No supersede las obligaciones de read-only, validación, allowlists, límites, auditoría y rechazo de SQL destructivo.
