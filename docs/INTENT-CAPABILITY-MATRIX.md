# Matriz de intenciones y capacidades

La matriz es el contrato entre lenguaje natural, tools determinísticas y
respuesta. `Implementada` significa que existe una consulta y una prueba;
`Parcial` significa que existe parte de los datos pero falta una dimensión o
una respuesta dedicada; `Pendiente` significa que no se debe inventar la
respuesta.

| ID | Intención | Nivel | Tool principal | Estado |
|---|---|---|---|---|
| SALES-TOTAL | total de ventas del periodo | O | `get_sales_summary` | Implementada |
| SALES-DOC-COUNT | documentos de venta emitidos | O | `get_sales_document_count` | Implementada |
| SALES-TOP-PRODUCT | producto con mayor venta | O/G | `get_top_sales_product` | Implementada |
| SALES-VARIANCE | variación y explicación observada | G | `compare_sales_periods`, breakdowns | Implementada |
| SALES-BY-DIMENSION | ventas por cliente/producto/vendedor | O/G | breakdown tools | Implementada |
| CUSTOMER-HISTORY | historial de cliente | O/G | `get_customer_purchase_history` | Implementada |
| INVENTORY-STOCK | stock e historial | O | `get_stock_history` | Implementada |
| INVENTORY-STOCKOUT | quiebres y riesgo observable | O/G | stockout tools | Implementada |
| INVENTORY-MINIMUM | método de stock mínimo | O | `get_erp_concept` | Implementada (conceptual) |
| PURCHASE-TOTAL | importe de compras | O | `get_purchase_summary` | Implementada |
| PURCHASE-ORDER-COUNT | número de órdenes de compra | O | `get_purchase_order_count` | Implementada |
| PURCHASE-BY-DIMENSION | compras por proveedor/producto | O/G | purchase breakdown tools | Implementada |
| PURCHASE-BY-AREA | órdenes por área/centro de coste | O/G | — | Pendiente: el esquema no relaciona PO con área |
| PURCHASE-DELIVERY | retrasos y recepción | G | delivery/inbound tools | Implementada |
| PAYROLL-EMPLOYEE-COUNT | empleados agregados de nómina | O | `get_payroll_cost_summary` | Implementada |
| PAYROLL-COST | coste de nómina | O/G | payroll summary/comparison | Implementada |
| PAYROLL-BREAKDOWN | nómina por concepto/centro | O/G | payroll breakdown tools | Implementada |
| ACCOUNTING-SUMMARY | ingresos, costes, gastos y resultado | O | accounting summary | Implementada |
| ACCOUNTING-VARIANCE | evolución del resultado | G | accounting comparison | Implementada |
| ACCOUNTING-COST-OF-SALES | definición y cálculo conceptual | O | `get_erp_concept` | Implementada (conceptual) |
| ERP-CONCEPT | explicación de conceptos ERP | O | `get_erp_concept` | Implementada |
| STRATEGIC-RECOMMENDATION | recomendación estratégica | E | tools de evidencia + LLM | Parcial: requiere datos suficientes y no prueba causalidad |
| INVOICE-COUNT | facturas fiscales emitidas | O | — | Pendiente: el modelo sólo tiene `sales_document` |

## Reglas de cobertura

- Una respuesta cuantitativa debe incluir la tool utilizada y su periodo.
- Una pregunta conceptual no debe ejecutar una consulta ficticia ni inventar
  cifras de la empresa.
- Una pregunta sobre facturas no se responderá como documentos de venta hasta
  que exista una entidad o política explícita que establezca esa equivalencia.
- Las órdenes por área o centro de coste no se implementarán hasta que el
  modelo de datos tenga una relación verificable.
- Las preguntas estratégicas deben distinguir hechos, observaciones y
  recomendaciones; no deben afirmar causalidad sin evidencia experimental.
