# Proyecto 02 — ERP AI Analyst
## Product Requirements Document (PRD)

**Estado:** Diseño activo  
**Rol en el portfolio:** Proyecto insignia  
**Producto conceptual:** Agentic Enterprise Analytics for ERP  
**Versión:** 1.1

## 1. Product Vision

ERP AI Analyst será una plataforma agentic de análisis empresarial sobre un **Canonical ERP Data Model**. Permitirá formular preguntas en lenguaje natural y ejecutar workflows controlados que seleccionan tools tipadas, obtienen datos, realizan cálculos determinísticos, combinan dominios ERP y generan conclusiones trazables.

La aplicación pública será reproducible con un ERP ficticio y datos sintéticos. La arquitectura quedará preparada para integrar ERPs reales mediante una capa desacoplada y, potencialmente, MCP.

## 2. Objetivos

1. Demostrar Agentic AI aplicada a sistemas ERP.
2. Resolver análisis multi-step y multiárea.
3. Separar razonamiento LLM de cálculo determinístico.
4. Proporcionar evidencia para cifras y conclusiones.
5. Evaluar el sistema contra ground truth.
6. Mantener la capa agentic independiente del esquema propietario del ERP.
7. Incorporar progresivamente dominios con valor empresarial real sin convertir el proyecto en un ERP o BI completo.

## 3. Usuarios

- gerencia/dirección;
- ventas;
- inventario;
- compras;
- finanzas;
- payroll para análisis agregado;
- controllers/contabilidad para Accounting Lite;
- analistas de negocio;
- usuarios ERP no técnicos.

## 4. Principios

- ERP-agnostic.
- Read-only.
- No SQL libre generado por el LLM.
- LLM razona; código calcula.
- No crear un agente por módulo.
- Evidencia antes que afirmación.
- Datos sintéticos en el repositorio público.
- Correlación no se presentará como causalidad.
- Extensiones reales no deben retrasar el MVP Core.

## 5. Capas de alcance

### 5.1 MVP — obligatorio para primera versión pública

**Sales + Customers + Inventory + Purchases + Payroll Analytics + Accounting Lite**

Debe soportar la pregunta insignia:

> “¿Por qué disminuyeron las ventas este mes?”

y análisis multi-step relacionados.

### 5.2 Secuencia interna del MVP

**Purchases + Payroll Analytics** se implementarán después de estabilizar Sales + Customers + Inventory, pero siguen siendo parte obligatoria del mismo MVP.

### 5.3 Accounting Lite — alcance obligatorio y controlado del MVP

Contabilidad se limita a análisis de:

- ingresos;
- costos;
- gastos;
- resultado operativo;
- margen bruto;
- saldos agregados por cuenta/grupo;
- variaciones entre períodos;
- centros de costo.

No incluye:

- generación/modificación de asientos;
- cierre automatizado;
- conciliación integral;
- impuestos;
- interpretación tributaria;
- contabilidad estatutaria completa.

### 5.4 Extensiones posteriores

- Accounts Receivable completo;
- otros módulos;
- ERP adapters reales;
- BIZAG Reference Adapter;
- MCP Integration Server.

## 6. Requisitos funcionales transversales

- **RF-01:** aceptar preguntas empresariales en lenguaje natural.
- **RF-02:** estructurar intención, período, entidades y restricciones.
- **RF-03:** construir/adaptar un plan multi-step.
- **RF-04:** seleccionar solo tools autorizadas.
- **RF-05:** validar argumentos mediante schemas tipados.
- **RF-06:** ejecutar cálculos mediante domain services determinísticos.
- **RF-07:** combinar resultados de varios dominios.
- **RF-08:** sintetizar hallazgos sin alterar cifras.
- **RF-09:** asociar evidencia a hallazgos cuantitativos.
- **RF-10:** producir datos estructurados para tablas/gráficos.
- **RF-11:** reconocer datos insuficientes.
- **RF-12:** manejar tool failures, timeouts y retries limitados.
- **RF-13:** mantener request/execution ID.
- **RF-14:** soportar demo reproducible sin ERP real.
- **RF-15:** distinguir hechos, inferencias y advertencias.
- **RF-16:** soportar contexto conversacional únicamente cuando sea funcionalmente necesario.

## 7. Requisitos por dominio

### Sales
- ventas por período;
- comparación;
- tendencia;
- cliente;
- producto;
- vendedor;
- contribución a variaciones.

### Customers
- historial;
- concentración;
- reducción/abandono de compra;
- contribución a cambios.

### Inventory
- stock;
- movimientos;
- stockout;
- rotación;
- sobrestock;
- riesgo de quiebre.

### Purchases
- compras por período;
- compras por proveedor/producto;
- evolución de costos;
- órdenes pendientes/parciales;
- recepción;
- lead time/retrasos;
- relación compras–inventario.

### Payroll Analytics
- costo total de nómina;
- variación por período;
- costo por centro de costo/área;
- conceptos de nómina agregados;
- horas extra;
- componentes fijos/variables;
- contribución de payroll a gastos operativos.

Payroll en este proyecto no cubrirá contratos, vacaciones, políticas, desempeño ni decisiones individuales sensibles; esa frontera corresponde a PeopleOps AI.

### Accounts Receivable
Inicialmente secundario:
- saldo;
- vencido;
- aging;
- concentración por cliente;
- evolución de cobranza.

### Accounting Lite
- balances agregados por período;
- ingresos/costos/gastos;
- margen bruto;
- resultado operativo;
- variaciones;
- centros de costo.

## 8. Preguntas de aceptación funcional

La suite de producto debe incluir, entre otras:

- “¿Por qué disminuyeron las ventas este mes?”
- “¿La caída de P-104 coincide con falta de stock?”
- “¿Qué productos con riesgo de quiebre tienen órdenes de compra pendientes?”
- “¿Qué proveedores presentan mayores retrasos?”
- “¿Cómo evolucionó el costo de compra de P-104?”
- “¿Cuál fue el costo total de nómina y qué conceptos explican la variación?”
- “¿Qué centros de costo explican el aumento de payroll?”
- “¿Cuánto del aumento de gastos operativos corresponde a payroll?”
- “¿Qué grupos de gasto explican la variación del resultado operativo?”
- “¿El aumento del costo de compra coincide con deterioro del margen bruto?”

## 9. Modelo ERP canónico

Modelo conceptual:

```text
Customer
Product
Salesperson
SalesDocument
SalesDocumentLine
InventoryMovement
StockBalance
Supplier
PurchaseOrder
PurchaseOrderLine
GoodsReceipt
EmployeePayrollSummary
PayrollConcept
CostCenter
Receivable
AccountingPeriod
AccountBalance
```

Solo se implementarán entidades requeridas por la fase activa.

## 10. ERP ficticio y synthetic business scenario

El ERP ficticio será la fuente oficial para desarrollo, tests, demo y evaluación.

Los datos deberán contener patrones deliberados y relaciones cross-domain.

Ejemplo:

```text
Supplier delay
→ Purchase order delayed
→ Stockout
→ Sales decline
```

Ejemplo financiero:

```text
Payroll overtime increase
→ Payroll cost increase
→ Operating expenses increase
→ Accounting Lite period variance
```

Los escenarios conocidos conformarán el ground truth.

## 11. Arquitectura

```text
User
 ↓
FastAPI / Conversation Layer
 ↓
Intent + Context
 ↓
Planner / Orchestrator — LangGraph
 ↓
Conditional Tool Routing
 ├─ Sales
 ├─ Customers
 ├─ Inventory
 ├─ Purchases
 ├─ Payroll
 ├─ Receivables
 └─ Accounting Lite
 ↓
Domain Services
 ↓
Canonical PostgreSQL
 ↓
Deterministic Results
 ↓
Evidence / State
 ↓
Synthesis
 ↓
Structured Answer
 ↓
LangSmith + Logs
```

## 12. Agent vs Tool

### Agentic / LLM
- interpretación;
- planificación;
- routing;
- selección de tools;
- decisión de análisis adicional;
- síntesis;
- explicación.

### Determinístico
- SQL/control de acceso;
- agregaciones;
- variaciones;
- rankings;
- stockouts;
- lead times;
- aging;
- payroll totals;
- account balances;
- márgenes;
- persistencia.

## 13. Tools iniciales

### Core
```text
get_sales_summary(...)
compare_sales_periods(...)
get_sales_by_customer(...)
get_sales_by_product(...)
get_customer_purchase_history(...)
find_customers_with_sales_decline(...)
get_stock_history(...)
get_out_of_stock_periods(...)
find_stockout_products(...)
```

### Purchases
```text
get_purchase_summary(...)
get_purchases_by_supplier(...)
get_purchase_price_history(...)
get_pending_purchase_orders(...)
get_supplier_delivery_performance(...)
get_product_inbound_supply(...)
```

### Payroll
```text
get_payroll_cost_summary(...)
compare_payroll_periods(...)
get_payroll_cost_by_cost_center(...)
get_payroll_cost_by_concept(...)
get_overtime_cost_trend(...)
```

### Accounting Lite
```text
get_accounting_period_summary(...)
compare_accounting_periods(...)
get_expense_variance_by_group(...)
get_cost_center_expenses(...)
get_gross_margin_summary(...)
```

Los nombres son conceptuales y se cerrarán al diseñar schemas.

## 14. Respuesta estructurada

Debe separar:

- answer;
- key findings;
- evidence;
- analysis performed;
- warnings/limitations.

Toda cifra importante debe vincularse a tool results.

## 15. LangGraph

Debe demostrar:

- state;
- conditional routing;
- tool execution;
- workflow multi-step;
- iteración basada en resultados;
- límites de iteración;
- manejo de errores;
- retries controlados.

No será wrapper de una única llamada al modelo.

## 16. OpenAI

Uso explícito para:

- tool calling;
- structured outputs;
- intent;
- planning;
- synthesis;
- controlled generation;
- evaluación asistida cuando corresponda.

No se utilizará para cálculos reproducibles.

## 17. LangSmith y observabilidad

Registrar/inspeccionar:

- input;
- plan;
- routing;
- tool calls;
- argumentos;
- resultados;
- errores;
- latencia;
- model calls;
- final answer.

## 18. Evaluación

ERP Analysis Evaluation Dataset:

```text
question
expected_intent
expected_tools
expected_key_facts
expected_calculations
expected_answer_characteristics
difficulty
category
```

Métricas candidatas:

- tool selection accuracy;
- calculation correctness;
- key fact coverage;
- unsupported quantitative claim rate;
- unnecessary tool-call rate;
- successful workflow rate;
- latency;
- token/cost metrics.

Debe haber casos negativos y tool failures.

## 19. Seguridad

- read-only;
- typed tools;
- queries controladas/parametrizadas;
- sin SQL libre generado por LLM;
- secretos por entorno;
- límites de resultados;
- timeouts;
- logs seguros;
- datos sintéticos públicos.

Payroll debe tratarse como dominio sensible incluso en demos sintéticas; una futura conexión real requerirá controles de autorización específicos.

## 20. Integración ERP real

Fuera del MVP Core, pero requisito de extensibilidad:

```text
ERP
 ↓
Integration / Adapter Layer
 ↓
Canonical ERP Contract
 ↓
ERP AI Analyst
```

La primera estrategia recomendada será un **Replicated / Analytical Store** con carga inicial, data quality checks y sincronización incremental.

## 21. Mappings configurables

Una integración deberá mapear entidades del ERP origen al modelo canónico sin introducir nombres propietarios en la agentic layer.

El formato concreto se decidirá posteriormente.

## 22. BIZAG Reference Adapter

BIZAG podrá ser el primer reference adapter después del MVP, sin publicar:

- esquema propietario;
- datos de clientes;
- código privado;
- credenciales;
- configuraciones sensibles.

## 23. MCP

Evolución posible:

```text
ERP AI Analyst — MCP Client
        ↓
ERP Integration MCP Server
        ├─ BIZAG Adapter
        ├─ SAP Adapter
        ├─ Dynamics Adapter
        └─ Other Adapter
```

No forma parte del MVP ni constituye actualmente un sexto proyecto oficial.

## 24. Requisitos no funcionales

- seguridad;
- reproducibilidad;
- testabilidad;
- observabilidad;
- configuración por entorno;
- resiliencia;
- extensibilidad;
- documentación;
- Docker;
- orientación a producción sin afirmar production-ready.

## 25. Testing

- unit tests de domain services/cálculos;
- tool contract tests;
- integration tests;
- agentic routing/tool-selection tests;
- evaluation regression suite.

## 26. UX

Interfaz mínima:

- pregunta;
- respuesta;
- key findings;
- tabla/gráfico cuando corresponda;
- evidencia;
- análisis ejecutado;
- warnings.

No será un BI completo.

## 27. Criterios de aceptación — MVP Core

1. Demo ejecutable sin ERP real.
2. Sales + Customers + Inventory implementados.
3. Modelo canónico.
4. Tools determinísticas.
5. Sin SQL libre del LLM.
6. Workflow LangGraph multi-step.
7. Pregunta insignia multiárea.
8. Ground truth y cálculos correctos.
9. Evidence.
10. LangSmith.
11. Evaluation suite.
12. Tests.
13. FastAPI/UX mínima.
14. Docker y `.env.example`.
15. Datos exclusivamente sintéticos.

## 28. Criterios de aceptación — MVP+

### Purchases
- al menos un escenario compras → inventario → ventas;
- tools de órdenes, proveedores y costo;
- evaluación cross-domain.

### Payroll
- costos agregados;
- variaciones;
- conceptos;
- centros de costo;
- al menos un escenario payroll → gastos operativos;
- sin invadir PeopleOps.

### Accounting Lite
- resumen por período;
- ingresos/costos/gastos;
- margen bruto;
- variaciones;
- centros de costo;
- sin escritura contable ni automatización de cierres.

## 29. Roadmap

### Fase 0 — Diseño
PDD/PRD, empresa ficticia, modelo canónico, escenarios, tools, LangGraph y evaluation design.

### Fase 1 — Synthetic ERP Core
Sales + Customers + Inventory data, services y tests.

### Fase 2 — Core Tools
Tools tipadas y determinísticas.

### Fase 3 — Agentic Core
LangGraph + OpenAI.

### Fase 4 — Evaluation & Observability
LangSmith, dataset, métricas y regresión.

### Fase 5 — API/UX
FastAPI, frontend, evidence y visualizaciones.

### Fase 6 — Portfolio Release
Docker, README, ADRs, screenshots, demo y resultados.

### Fase 7 — Purchases
Modelo, datos, tools y escenario cross-domain.

### Fase 8 — Payroll Analytics
Modelo agregado, tools, seguridad y escenario financiero.

### Fase 9 — Accounting Lite
Saldos/agregados, margen, gastos y centros de costo.

### Fase 10 — ERP Integration
Contrato, analytical store, mappings y posible BIZAG adapter.

### Fase 11 — MCP Exploration
MCP Client/Server y adapters.

## 30. Definition of Done para portfolio

La primera versión pública del MVP requiere completar Sales, Customers, Inventory, Purchases, Payroll Analytics y Accounting Lite, además de arquitectura agentic, tools, evidencia, evaluación y observabilidad. Los adapters ERP reales, BIZAG Reference Adapter y MCP quedan como evolución posterior.

## 31. Decisiones pendientes antes de programar

1. empresa ficticia e industria;
2. período, moneda y unidades;
3. escenarios Core;
4. escenarios Purchases;
5. escenarios Payroll;
6. escenario mínimo Accounting Lite;
7. modelo físico canónico;
8. catálogo y schemas de tools Core;
9. schemas futuros de Purchases/Payroll/Accounting;
10. diseño LangGraph;
11. state;
12. evidence format;
13. evaluation dataset;
14. métricas;
15. UX;
16. arquitectura física/repositorio;
17. política de datos sensibles para futura integración real.

## 32. Frontera con PeopleOps AI

Payroll aparece en ambos proyectos con objetivos distintos.

**ERP AI Analyst:** payroll como dimensión económico-operativa del ERP: costos, conceptos, centros de costo, variaciones y relación con resultados.

**PeopleOps AI:** dominio de RRHH: empleados, contratos, asistencia, vacaciones, políticas, documentos y workflows sensibles con Human-in-the-loop.

Esta frontera debe mantenerse explícita para evitar duplicación.

## 33. Declaración final de alcance

El producto evolucionará en capas:

> **MVP:** Agentic ERP Analytics sobre Sales + Customers + Inventory + Purchases + Payroll Analytics + Accounting Lite.

> Purchases, Payroll y Accounting Lite se implementan incrementalmente dentro del mismo MVP. Los adapters ERP reales y MCP son evolución posterior.

La arquitectura permanecerá ERP-agnostic y preparada para integraciones reales, pero los adapters y MCP no deben retrasar la evidencia principal del proyecto.
