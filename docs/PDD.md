# Proyecto 02 — ERP AI Analyst
## Project Definition Document (PDD)

**Estado:** Diseño activo  
**Rol en el portfolio:** Proyecto insignia  
**Producto conceptual:** Agentic Enterprise Analytics for ERP  
**Documento:** Definición del proyecto  
**Versión:** 1.1

## Propósito

ERP AI Analyst es el proyecto insignia del portfolio. Debe conectar experiencia en sistemas ERP con arquitecturas modernas de Agentic AI y demostrar cómo una capa de inteligencia empresarial puede operar sobre datos estructurados sin quedar acoplada al esquema propietario de un ERP concreto.

El sistema permitirá consultar y analizar información empresarial mediante lenguaje natural. Deberá interpretar la pregunta, decidir qué información necesita, seleccionar tools tipadas, ejecutar consultas y cálculos determinísticos, combinar resultados de varias áreas y producir conclusiones explicables con evidencia.

La aplicación pública funcionará sobre un **ERP ficticio con datos sintéticos y ground truth conocido**, pero su arquitectura se diseñará para evolucionar hacia ERPs reales mediante un **Canonical ERP Data Model** y una capa de integración desacoplada.

## Qué capacidad profesional demuestra

**Diseño de Enterprise Agentic AI Systems integrados con sistemas ERP y orientados a análisis empresarial multiárea.**

Debe aportar evidencia de:

- AI Solutions Architecture;
- Agentic AI sobre sistemas empresariales;
- LangGraph y LangSmith;
- OpenAI tool calling y structured outputs;
- arquitectura ERP-agnostic;
- Canonical ERP Data Model;
- tools y domain services determinísticos;
- análisis multi-step y multiárea;
- integración y modernización de sistemas legacy;
- evaluación y ground truth;
- trazabilidad y observabilidad;
- seguridad read-only;
- diseño production-oriented.

## ¿Para qué sirve?

Sirve para convertir datos operativos de un ERP en análisis empresarial accionable sin obligar al usuario a conocer tablas, SQL, reportes o navegación interna del sistema.

No debe limitarse a responder consultas simples. Debe poder:

- comprender preguntas empresariales;
- determinar qué información necesita;
- planificar análisis multi-step;
- seleccionar tools;
- consultar varias áreas;
- combinar resultados;
- calcular métricas de forma reproducible;
- detectar factores relevantes;
- distinguir hechos de inferencias;
- explicar hallazgos;
- mostrar evidencia;
- producir tablas o gráficos cuando aporten valor;
- reconocer cuándo los datos son insuficientes.

## Dominios funcionales

El producto se diseña alrededor de dominios ERP independientes pero combinables.

### Núcleo analítico
- Sales;
- Customers;
- Inventory.

### Expansión de alto valor
- Procurement / Purchases;
- Payroll Analytics.

### Alcance financiero controlado
- Accounts Receivable;
- Accounting Lite.

La incorporación de nuevos dominios no implica crear un agente por módulo. Los dominios se exponen principalmente mediante **tools y servicios determinísticos** reutilizables por el workflow agentic.

## ¿Qué tipo de preguntas responde?

### Ventas

- “¿Por qué disminuyeron las ventas este mes?”
- “¿Qué clientes explican la mayor parte de la caída?”
- “¿Qué vendedores están por debajo de su promedio histórico?”
- “¿Qué productos crecieron más respecto al mes anterior?”
- “¿Cuál es la tendencia de ventas de los últimos 12 meses?”
- “¿Qué productos explican el crecimiento de este trimestre?”

### Clientes

- “¿Qué clientes dejaron de comprar recientemente?”
- “¿Qué clientes redujeron más sus compras?”
- “¿Qué clientes concentran la mayor parte de las ventas?”
- “¿Cómo cambió el comportamiento de compra del cliente C-014?”
- “¿Qué clientes presentan simultáneamente caída de compras y deuda vencida?”

Las métricas como rentabilidad de cliente solo se ofrecerán cuando existan datos de costos suficientes para calcularlas correctamente.

### Inventario

- “¿Qué productos tienen riesgo de quiebre de stock?”
- “¿Qué productos estuvieron sin stock este mes?”
- “¿Cuántos días estuvo sin stock el producto P-104?”
- “¿Qué productos tienen sobrestock?”
- “¿Qué artículos tienen baja rotación?”
- “¿Qué inventario está inmovilizando más capital?”

### Compras / Procurement

- “¿Cuánto compramos este mes y cómo se compara con el anterior?”
- “¿Qué proveedores concentran la mayor parte de las compras?”
- “¿Qué productos incrementaron más su costo de compra?”
- “¿Qué órdenes de compra permanecen pendientes o parcialmente atendidas?”
- “¿Qué proveedores presentan mayores retrasos de entrega?”
- “¿Qué productos con riesgo de quiebre tienen órdenes pendientes?”
- “¿Cómo evolucionó el precio promedio de compra de P-104?”
- “¿Qué proveedores abastecen productos críticos para las ventas?”

### Payroll Analytics

El alcance de payroll en ERP AI Analyst será **operativo-financiero y agregado**, no un reemplazo de PeopleOps AI.

- “¿Cuál fue el costo total de nómina este mes?”
- “¿Cómo se compara con el mes anterior?”
- “¿Qué conceptos explican la variación del costo de nómina?”
- “¿Qué centros de costo explican el mayor incremento?”
- “¿Cómo evolucionó el costo de horas extra?”
- “¿Qué proporción corresponde a remuneración fija, variable y otros conceptos?”
- “¿Qué áreas explican la mayor parte del cambio mensual?”

ERP AI Analyst evitará análisis sensibles de desempeño individual, políticas de RRHH, contratos, vacaciones o decisiones sobre personas. Esas capacidades corresponden a **PeopleOps AI**.

### Finanzas / cuentas por cobrar

- “¿Cuánto tenemos vencido por cobrar?”
- “¿Qué clientes concentran la deuda vencida?”
- “¿Cómo evolucionó el plazo promedio de cobranza?”
- “¿Qué documentos deberían priorizarse para gestión de cobro?”
- “¿Qué clientes redujeron compras pero mantienen deuda vencida?”

### Contabilidad — Accounting Lite

Contabilidad se incorpora con un alcance deliberadamente pequeño. El objetivo no es construir un copiloto contable completo.

Preguntas previstas:

- “¿Cuál es el resumen de ingresos, costos y gastos del período?”
- “¿Cómo evolucionó el resultado operativo respecto al mes anterior?”
- “¿Qué grupos de gasto explican la mayor variación?”
- “¿Cómo se distribuyen los gastos por centro de costo?”
- “¿Qué cuentas presentan las mayores variaciones entre períodos?”
- “¿Cómo evolucionó el margen bruto?”

Accounting Lite trabajará sobre **saldos y agregados contables previamente estructurados**. Quedan fuera del alcance inicial la generación de asientos, interpretación tributaria, cierre contable automatizado, conciliación integral y modificación del libro mayor.

### Análisis combinado

Aquí se encuentra una de las capacidades más importantes del proyecto:

- “¿Por qué disminuyeron las ventas este mes?”
- “¿La caída de ventas coincide con falta de stock?”
- “¿Qué productos venden bien pero presentan problemas de abastecimiento?”
- “¿Qué productos con quiebre de stock tienen compras pendientes?”
- “¿El aumento del costo de compra está deteriorando el margen?”
- “¿Qué clientes compran menos pero mantienen deuda vencida?”
- “¿Qué factores explican el deterioro del margen bruto?”
- “¿Cuánto del aumento de gastos operativos corresponde al costo de nómina?”
- “¿Qué centros de costo explican el crecimiento de gastos y payroll?”
- “¿Qué proveedores están afectando la disponibilidad de productos de mayor venta?”

El sistema debe distinguir **correlación observada** de **causalidad demostrada**.

### Seguimiento conversacional

Cuando exista contexto suficiente:

- “Analiza las ventas de julio.”
- “Ahora compáralas con junio.”
- “¿Qué productos explican la diferencia?”
- “Revisa si tuvieron problemas de stock.”
- “¿Hay órdenes de compra pendientes para esos productos?”

La memoria solo se incorporará cuando resuelva casos funcionales como este.

### Preguntas que debe rechazar o limitar

- consultas que requieran escribir o modificar datos ERP;
- conclusiones no sustentadas por datos;
- SQL arbitrario solicitado para ejecutarse directamente;
- decisiones laborales sensibles;
- asesoría contable, tributaria o legal que exceda los datos disponibles;
- preguntas fuera de los dominios implementados.

## Usuarios objetivo

- gerentes y dirección;
- jefaturas comerciales;
- responsables de inventario;
- responsables de compras;
- responsables financieros;
- responsables de payroll interesados en análisis agregado;
- controllers y analistas contables para consultas limitadas;
- analistas de negocio;
- usuarios ERP sin conocimientos técnicos.

## Principio Agent vs Tool

No se crearán agentes por cada módulo ERP.

### Razonamiento agentic
Adecuado para:
- interpretación;
- planificación;
- selección de tools;
- routing;
- análisis iterativo;
- síntesis;
- explicación.

### Código determinístico
Adecuado para:
- consultas;
- agregaciones;
- cálculos;
- comparaciones;
- rankings;
- variaciones;
- aging;
- stockouts;
- lead times;
- costos de nómina;
- saldos contables;
- persistencia;
- validación.

## Arquitectura conceptual

```text
Usuario
  ↓
API / Conversation Layer
  ↓
Planner / Orchestrator — LangGraph
  ↓
Domain Tools
  ├── Sales
  ├── Customers
  ├── Inventory
  ├── Purchases
  ├── Payroll
  ├── Receivables
  └── Accounting Lite
  ↓
Domain Services
  ↓
Canonical ERP Data Model
  ↓
PostgreSQL / Analytical Store
  ↓
Resultados determinísticos
  ↓
Evidence + Synthesis
  ↓
Respuesta / tablas / gráficos
```

Preferencia de seguridad:

```text
LLM → Typed Tool → Domain Service → Controlled Query
```

en vez de:

```text
LLM → SQL libre → Database
```

## Modelo ERP canónico

Modelo conceptual ampliable:

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

Solo se implementarán las entidades necesarias en cada fase.

## ERP ficticio y datos

El ERP ficticio será la fuente oficial para:

- demo pública;
- desarrollo;
- tests;
- evaluación;
- ground truth.

Los datos serán sintéticos pero diseñados con escenarios empresariales coherentes. No serán ruido aleatorio.

El escenario deberá permitir crear relaciones reales entre dominios, por ejemplo:

```text
Supplier delay
   ↓
Purchase order delayed
   ↓
Stockout
   ↓
Product sales decline
   ↓
Margin / business impact
```

y:

```text
Payroll cost increase
   ↓
Operating expense increase
   ↓
Accounting Lite explains period variance
```

## Integración con ERPs reales

La arquitectura se diseñará desde el inicio para admitir fuentes externas sin acoplar la capa agentic al esquema propietario.

```text
ERP real
  ↓
Integration / Adapter Layer
  ↓
Canonical ERP Contract
  ↓
ERP AI Analyst
```

Una primera integración real debería favorecer un **Replicated / Analytical Store** antes que acceso directo del agente al ERP transaccional.

BIZAG podrá evaluarse como primer **Reference Adapter**, sin convertirlo en dependencia del producto y sin publicar datos, esquemas, código o credenciales propietarias.

## Evolución mediante MCP

Se contempla como evolución:

```text
ERP AI Analyst
   │ MCP Client
   ▼
ERP Integration MCP Server
   ├── BIZAG Adapter
   ├── SAP Adapter
   ├── Dynamics Adapter
   └── Other ERP Adapter
```

El MCP Server no forma parte del MVP ni se considera actualmente un sexto proyecto oficial.

## Tecnologías principales

- LangGraph;
- LangSmith;
- OpenAI;
- FastAPI;
- PostgreSQL;
- Docker;
- frontend web.

pgvector o RAG solo se incorporarán si un caso de uso concreto lo justifica. Este proyecto debe concentrarse principalmente en **datos estructurados + tools + workflows agentic**.

## OpenAI

Cuando corresponda:

- tool calling;
- structured outputs;
- interpretación;
- planificación;
- síntesis fundamentada;
- generación controlada;
- evaluación asistida por modelo.

Los cálculos reproducibles permanecerán en código.

## Observabilidad y evaluación

LangSmith debe permitir inspeccionar:

- pregunta;
- plan;
- rutas;
- tools;
- argumentos;
- resultados;
- errores;
- latencia;
- llamadas al modelo;
- respuesta.

Se construirá un evaluation dataset con preguntas, tools esperadas, cálculos esperados y key facts conocidos.

## Seguridad

- read-only en el MVP;
- tools autorizadas;
- contratos tipados;
- queries parametrizadas/controladas;
- sin SQL arbitrario generado por el LLM;
- secretos por entorno;
- `.env.example`;
- timeouts;
- límites de resultados;
- logging sin información sensible;
- datos públicos exclusivamente sintéticos.

## Límites

- no usar datos ni código de clientes reales;
- no exponer esquemas propietarios;
- no automatizar decisiones críticas;
- no afirmar causalidad cuando solo exista correlación;
- no construir un ERP completo;
- no construir un BI completo;
- no convertir Payroll en PeopleOps AI;
- no convertir Accounting Lite en un sistema contable;
- no construir un ETL universal dentro del MVP;
- no añadir MCP antes de justificar su valor.

## Estrategia de alcance

Para mantener el proyecto terminable se utilizarán capas de alcance:

### MVP — alcance obligatorio
- Sales;
- Customers;
- Inventory;
- Purchases;
- Payroll Analytics agregado;
- Accounting Lite;
- pregunta insignia multi-step;
- LangGraph;
- LangSmith;
- evaluation;
- evidence.

### MVP+ — valor ERP adicional
- Purchases;
- Payroll Analytics agregado.

### Accounting Lite
- saldos/agregados por período;
- ingresos/costos/gastos;
- variaciones;
- centros de costo;
- margen bruto.

### Extensiones posteriores
- Accounts Receivable completo;
- integraciones ERP reales;
- BIZAG Reference Adapter;
- MCP Integration Server;
- otros módulos ERP.

La prioridad será construir el MVP por incrementos internos, pero la publicación que marque el MVP como completo requerirá Sales, Customers, Inventory, Purchases, Payroll Analytics y Accounting Lite.

## Qué debe mostrar el repositorio

- README profesional;
- PDD y PRD;
- arquitectura;
- modelo ERP canónico;
- datos sintéticos reproducibles;
- escenarios y ground truth;
- tools y contratos;
- workflow LangGraph;
- tracing LangSmith;
- preguntas por dominio;
- demo multiárea;
- evidencia;
- tests;
- evaluation suite;
- resultados de evaluación;
- FastAPI;
- frontend;
- Docker;
- `.env.example`;
- seguridad;
- limitaciones;
- roadmap;
- ADRs;
- licencia.

## Criterio de éxito

ERP AI Analyst debe demostrar que una aplicación agentic puede investigar una pregunta empresarial compleja utilizando datos ERP estructurados de forma segura, reproducible y explicable, y que su arquitectura puede evolucionar desde un ERP ficticio hacia sistemas reales sin reescribir la capa de inteligencia.

La amplitud funcional no debe comprometer esta evidencia central.
