# Informe de cobertura conversacional

## Qué se validó

La suite anterior de Agentic v2 validaba 36 preguntas congeladas y sus
repeticiones. Esta ampliación agrega un catálogo de 300 preguntas (50 por cada
una de las seis áreas), una matriz de capacidades y una suite explícita para
preguntas simples y conceptuales.

Las verificaciones ejecutadas en esta ampliación fueron:

- 58 tests automatizados del backend: todos pasan.
- Ruff: sin errores.
- Mypy: sin errores.
- Tools contra la base sintética: payroll, documentos de venta, producto líder,
  órdenes de compra y conceptos ERP.
- Workflow real con OpenAI + LangGraph para cinco preguntas nuevas.

## Evidencia end-to-end

| Pregunta | Resultado observado | Tool |
|---|---|---|
| ¿Cuántos empleados tiene la nómina? | 33 empleados | `get_payroll_cost_summary` |
| ¿Cuántas órdenes de compra se emitieron? | 4 órdenes no canceladas | `get_purchase_order_count` |
| ¿Cuál es el producto que tiene mayor venta? | Premium Filter | `get_top_sales_product` |
| ¿Cómo se calcula el costo de venta? | Inventario inicial + compras netas - inventario final | `get_erp_concept` |
| ¿Cómo determinar el stock mínimo? | Demanda durante lead time + stock de seguridad | `get_erp_concept` |

## Brechas que permanecen intencionalmente

1. **Facturas fiscales:** el esquema sólo contiene `sales_document` con estados
   `posted` y `cancelled`; no contiene una entidad fiscal de factura, serie,
   folio, impuestos ni tipo documental. La aplicación puede contar documentos
   de venta publicados, pero no debe llamarlos facturas sin una decisión de
   modelo de datos.
2. **Órdenes por área o centro de coste:** `purchase_order` no tiene una
   relación con `cost_center` ni con `area`. No se implementó una agrupación
   ficticia. Requiere ampliar el modelo y los datos sintéticos primero.
3. **Preguntas estratégicas:** el catálogo las define, pero una recomendación
   sólo es válida cuando existen suficientes hechos, periodos comparables y
   dimensiones relevantes. El modelo debe separar evidencia, observación y
   recomendación, sin afirmar causalidad.
4. **Métricas avanzadas ERP:** rotación, cobertura, stock de seguridad numérico,
   margen por producto y coste unitario por empleado requieren nuevas medidas
   o datos adicionales; las explicaciones conceptuales sí están disponibles.

## Interpretación correcta

La cobertura no se demuestra por el número de tools registradas. Se demuestra
por preguntas de aceptación que cubren cada intención, argumentos, respuesta,
periodo, evidencia y comportamiento cuando faltan datos. El catálogo y la
matriz son ahora la base para ampliar la evaluación Agentic v2 sin confundir
una evaluación cerrada con cobertura total del producto.
