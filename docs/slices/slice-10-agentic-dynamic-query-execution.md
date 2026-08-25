# Slice 10 — Agentic Dynamic Query Execution

## 1. Objetivo

Evolucionar ERP AI Analyst desde un catálogo cerrado de intents y tools de preguntas predefinidas hacia un sistema agentic capaz de descubrir el modelo analítico ERP, generar consultas SQL dinámicas, validarlas, ejecutarlas de forma read-only y responder con evidencia auditable.

El objetivo no es entregar al LLM acceso irrestricto a PostgreSQL. El objetivo es que el LLM pueda explorar y combinar datos nuevos dentro de un contrato controlado de metadatos, seguridad y operación.

```text
pregunta → agente analista → metadata + SQL candidato → agente validador
→ guardrails deterministas → ejecución read-only → síntesis + evidencia
```

## 2. Dependencias

- Slices 0–9 existentes y repositorio ejecutable.
- Modelo canónico ERP sintético migrado y poblado.
- API FastAPI y workflow LangGraph existentes.
- OpenAI configurado para structured outputs/tool calling.
- LangSmith disponible para tracing.
- ADR-0002 debe revisarse: la prohibición absoluta de SQL generado por el LLM será sustituida por SQL generado por el LLM pero validado antes de ejecutarse.

## 3. Decisión de alcance

Esta slice reemplaza el routing productivo basado en una lista de preguntas por un agente de consulta dinámico. No elimina de inmediato las tools estáticas:

- las tools estáticas existentes se conservarán durante la migración;
- las métricas críticas y cálculos complejos podrán seguir usando servicios determinísticos especializados;
- el agente dinámico será la ruta principal para agregaciones, filtros, dimensiones y combinaciones nuevas;
- la suite anterior de 36 casos seguirá como regresión, pero dejará de ser la única evidencia de cobertura.

No se implementará un agente separado por dominio ERP.

## 4. Arquitectura objetivo

### 4.1 Agente analista

Responsabilidades:

- interpretar la pregunta empresarial;
- identificar entidad, métrica, dimensiones, filtros y periodo;
- solicitar metadatos cuando no los conozca;
- construir SQL candidato;
- declarar tablas, columnas, joins y propósito;
- declarar supuestos y ambigüedades;
- no ejecutar SQL directamente.

Contrato mínimo:

```json
{
  "question": "...",
  "analysis_goal": "...",
  "sql": "SELECT ...",
  "tables": ["purchase_order", "supplier"],
  "columns": ["supplier.name", "purchase_order.status"],
  "joins": ["purchase_order.supplier_id = supplier.id"],
  "metrics": ["count"],
  "filters": ["status IN ('open', 'partial')"],
  "period": {"start": "2025-04-01", "end": "2025-04-30"},
  "assumptions": [],
  "needs_clarification": false
}
```

El SQL es un artefacto generado por el LLM, no una instrucción autorizada.

### 4.2 Tools de metadata

Las tools deben exponer descubrimiento del modelo, no preguntas individuales:

- `list_erp_tables`
- `describe_erp_table`
- `list_erp_columns`
- `list_erp_relationships`
- `list_erp_indexes`
- `get_table_row_estimate`
- `get_available_periods`
- `get_allowed_metrics`
- `get_allowed_dimensions`
- `get_data_classification`

Cada respuesta debe indicar versión del catálogo, origen, timestamp, límites y si la información es estructural o estimada. No debe devolver secretos ni datos individuales sensibles por defecto.

### 4.3 Agente validador

Responsabilidades:

- comprobar que la consulta responde al objetivo declarado;
- comprobar tablas, columnas y relaciones;
- detectar joins incompletos o multiplicativos;
- revisar agregación, agrupación y periodo;
- solicitar corrección al analista;
- explicar el motivo del rechazo.

El agente validador no puede aprobar una consulta rechazada por la capa determinista.

### 4.4 Capa determinista de seguridad

Debe ejecutarse siempre, aunque exista agente validador:

- parsear SQL mediante AST;
- permitir sólo `SELECT` y CTEs read-only controladas;
- bloquear `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `COPY`, funciones de escritura y múltiples statements;
- permitir sólo tablas y columnas del catálogo autorizado;
- bloquear tablas de sistema, secretos y columnas sensibles;
- exigir filtros temporales en tablas transaccionales grandes;
- limitar rango temporal, tablas, joins, filas, bytes y timeout;
- ejecutar `EXPLAIN` o estimación equivalente;
- rechazar cardinalidad o coste excesivos;
- ejecutar con usuario PostgreSQL sin permisos de escritura;
- registrar SQL normalizado, hash, decisión y motivo.

Resultado estructurado:

```json
{
  "status": "approved|rejected|needs_revision",
  "normalized_sql": "...",
  "reasons": [],
  "estimated_rows": 120,
  "estimated_cost": "...",
  "tables": ["purchase_order"],
  "columns": ["status"],
  "limits_applied": ["max_rows", "read_only_role"]
}
```

### 4.5 Ejecutor

El ejecutor sólo recibe consultas aprobadas:

- conexión read-only;
- timeout y cancelación;
- columnas, filas, tipos y metadatos;
- límites explícitos sin truncar silenciosamente;
- distinción entre cero filas y error;
- periodo, SQL hash, row count y timestamp;
- nunca ejecuta una consulta sin aprobación vigente.

### 4.6 Sintetizador

Recibe sólo resultados y evidencia. Debe conservar números, distinguir hechos de recomendaciones, declarar insuficiencia, evitar causalidad no demostrada y mantener la consulta completa en auditoría aunque no siempre la muestre al usuario.

## 5. Modelo semántico ERP

Crear un catálogo versionado con:

- tablas, columnas y tipos;
- claves primarias y foráneas;
- relaciones permitidas;
- columnas temporales;
- métricas y fórmulas;
- dimensiones agrupables;
- filtros válidos;
- sensibilidad de datos;
- índices y cardinalidad aproximada;
- sinónimos y etiquetas de negocio;
- dominio funcional.

El catálogo debe separar metadata estructural, semántica empresarial, permisos y límites operativos. El LLM puede recibirlo mediante tools, pero no debe descubrir por sí solo convenciones críticas de negocio.

## 6. Ciclo de corrección

1. Analista genera plan y SQL.
2. Validador revisa semántica.
3. Guardrail determinista revisa seguridad y coste.
4. Si hay corrección posible, devuelve diagnóstico al analista.
5. Se permiten como máximo dos revisiones.
6. Si no hay aprobación, se responde `insufficient_data`, `needs_clarification` o `unsafe_query` sin ejecutar.

No se permite un ciclo indefinido.

## 7. Auditoría y observabilidad

Crear `analysis_interactions` con:

- `request_id`, `conversation_id` y timestamp;
- pregunta original;
- goal/intención estructurada;
- versión del modelo semántico;
- agente y modelo;
- SQL candidato y hash;
- decisiones del validador y guardrail;
- SQL normalizado ejecutado;
- tablas y columnas;
- filas estimadas y reales;
- latencia por etapa;
- estado, respuesta, warnings y errores;
- tokens/coste cuando estén disponibles.

No guardar chain-of-thought. Guardar decisiones, artefactos técnicos, resúmenes y evidencia necesarios para auditoría.

La auditoría debe identificar preguntas sin métricas, consultas rechazadas, solicitudes de aclaración, consultas costosas, columnas ausentes, errores de joins y nuevas necesidades recurrentes.

## 8. Compatibilidad futura con MCP

Desacoplar el workflow de la implementación local mediante una interfaz `ToolProvider` para metadata, validación, estimación, ejecución y evidencia.

```text
Workflow LangGraph
        ↓
ToolProvider
        ├── LocalProvider → PostgreSQL local
        └── MCPProvider   → MCP server / ERP externo
```

La sustitución no será literalmente de cero cambios: habrá que implementar el cliente MCP, mapear autenticación y errores, verificar schemas, preservar guardrails y auditoría, y decidir dónde se ejecuta la validación final. La meta es que sean cambios de provider y configuración, no cambios de prompts o de una tool por pregunta.

Tools MCP recomendadas:

- `metadata.list_tables`
- `metadata.describe_table`
- `metadata.list_relationships`
- `metadata.list_indexes`
- `query.validate`
- `query.explain`
- `query.execute_readonly`

La política de seguridad debe existir en cliente y servidor cuando se conecte un ERP externo.

## 9. Migración

### Fase A — contratos y catálogo

- congelar catálogo semántico inicial;
- definir schema del plan SQL;
- definir parser/validator y límites;
- agregar auditoría;
- mantener la ruta actual como fallback.

### Fase B — metadata

- implementar descubrimiento de tablas, campos, relaciones e índices;
- agregar allowlist y tests;
- exponer cardinalidad y periodos.

### Fase C — generación y validación

- agregar agente analista;
- agregar agente validador;
- implementar corrección limitada;
- implementar guardrails deterministas;
- probar exclusivamente SELECT sobre datos sintéticos.

### Fase D — ejecución y síntesis

- ejecutar sólo SQL aprobado;
- devolver evidencia y resultados tipados;
- registrar auditoría;
- comparar resultados dinámicos contra ground truth independiente.

### Fase E — adopción

- migrar consultas simples de compras, ventas e inventario;
- comparar ruta estática y dinámica;
- migrar cross-domain;
- conservar tools especializadas para métricas complejas;
- retirar rutas estáticas sólo con evidencia suficiente.

## 10. Evaluación

La evaluación debe medir más que coincidencia exacta de tools:

- SQL válido;
- intención, tablas, columnas y joins correctos;
- filtros temporales correctos;
- cálculo frente a ground truth independiente;
- evidencia suficiente;
- rechazo de SQL peligroso, tablas sensibles y consultas costosas;
- tasa de aclaración correcta;
- cardinalidad estimada frente a real;
- latencia, coste y estabilidad entre reformulaciones;
- preguntas nuevas fuera del dataset original.

Casos mínimos:

- 50 preguntas nuevas de compras;
- 50 de ventas;
- 50 de inventario;
- dimensiones, filtros y periodos variados;
- cero resultados;
- columnas inexistentes;
- SQL destructivo;
- rango excesivo;
- consulta sin filtro temporal;
- tabla sensible;
- cardinalidad alta;
- ambigüedad que requiere aclaración.

La suite Agentic v2 actual se conserva como regresión histórica, pero no será la única métrica de generalización.

## 11. Seguridad y privacidad

- sólo datos sintéticos en el repositorio;
- usuario read-only;
- sin secretos en prompts, metadata o logs;
- allowlist de tablas/columnas;
- clasificación de datos sensibles;
- muestras enmascaradas;
- auditoría de acceso;
- el LLM no cambia permisos, schema ni configuración;
- rechazo de datos individuales sensibles de payroll.

## 12. Fuera de alcance

- escrituras en ERP;
- generación de asientos o modificaciones contables;
- SQL multi-statement;
- administración del schema;
- acceso a tablas sin catálogo;
- conectores MCP reales en esta primera implementación;
- reemplazo inmediato de todas las tools determinísticas;
- claims de producción sin evidencia operativa equivalente.

## 13. Archivos y componentes esperados

Posibles componentes:

- `backend/app/query/`
- `backend/app/metadata/`
- `backend/app/guardrails/`
- `backend/app/audit/`
- `backend/app/tools/`
- `backend/tests/test_query_validation.py`
- `backend/tests/test_metadata_tools.py`
- `backend/tests/test_dynamic_execution.py`
- `backend/evaluation/dynamic_cases.jsonl`
- `docs/adr/ADR-0006-dynamic-agentic-query-execution.md`

La estructura puede variar si conserva responsabilidades separadas.

## 14. Criterios de aceptación

1. Una pregunta no prevista genera un plan SQL estructurado sin una tool específica nueva.
2. El agente descubre tablas, campos y relaciones mediante metadata tools.
3. El validador corrige una columna o relación inválida en el límite de iteraciones.
4. Ningún SQL destructivo llega al ejecutor.
5. Ninguna consulta sin límites consume recursos ilimitados.
6. Consultas con campos inexistentes o joins inválidos son rechazadas o corregidas explícitamente.
7. El ejecutor usa read-only y timeout.
8. Cada ejecución produce SQL hash, evidencia, row count y auditoría.
9. La respuesta distingue cero resultados, datos insuficientes, rechazo y error técnico.
10. La ruta dinámica responde preguntas nuevas de al menos tres dominios sin crear tools por pregunta.
11. Las tools estáticas siguen funcionando durante la migración.
12. Un `ToolProvider` permite posteriormente un provider MCP sin cambiar el workflow de negocio.
13. La suite cubre comandos destructivos, tablas no permitidas, rangos excesivos, cardinalidad alta y columnas sensibles.
14. La evaluación compara resultados dinámicos con ground truth independiente.

## 15. Riesgos y mitigaciones

- SQL válido pero empresarialmente incorrecto → catálogo semántico y ground truth independiente.
- Joins que duplican importes → relaciones permitidas y validación de cardinalidad.
- Métricas ambiguas → definición versionada de métricas y aclaración.
- Cardinalidad estimada inexacta → `EXPLAIN`, límites estrictos y timeout.
- Prompt injection en metadata o datos → tratar metadata/resultados como datos no confiables.
- Columnas sensibles → clasificación y allowlist.
- Divergencia local/MCP → contrato `ToolProvider` y pruebas de equivalencia.

## 16. Definition of Done

Un tercero puede formular una pregunta analítica no incluida en el dataset, observar cómo el sistema descubre el modelo, inspeccionar el SQL candidato, verificar su validación, comprobar que sólo se ejecutó después de los guardrails y recibir una respuesta con evidencia. El mismo contrato puede implementarse con provider local o MCP sin reescribir el workflow.

## 17. Prohibiciones

- No reintroducir un diccionario de preguntas para aparentar generalización.
- No permitir SQL libre sin parser, permisos read-only y límites.
- No confiar sólo en el agente validador para seguridad.
- No crear una tool estática por cada pregunta durante esta slice.
- No afirmar compatibilidad MCP completa hasta probar el provider real.
- No eliminar ground truth ni sustituirlo por evaluación subjetiva del LLM.
