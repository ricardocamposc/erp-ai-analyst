"""Small, explicit ERP reference answers for non-transactional questions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConceptAnswer:
    topic: str
    title: str
    explanation: str
    formula: str
    caveats: list[str]


_ANSWERS: dict[str, ConceptAnswer] = {
    "cost_of_sales": ConceptAnswer(
        "cost_of_sales",
        "Costo de venta",
        "El costo de venta representa el costo de los productos vendidos durante el periodo.",
        "Inventario inicial + compras netas - inventario final",
        ["La fórmula debe ajustarse por devoluciones, mermas y ajustes de inventario."],
    ),
    "gross_margin": ConceptAnswer(
        "gross_margin",
        "Margen bruto",
        "El margen bruto muestra lo que queda de las ventas después de restar el costo de venta.",
        "Ventas netas - costo de venta; margen porcentual = margen bruto / ventas netas × 100",
        ["No incluye todos los gastos operativos."],
    ),
    "operating_result": ConceptAnswer(
        "operating_result",
        "Resultado operativo",
        "El resultado operativo mide el resultado generado por la operación antes de partidas financieras e impuestos.",
        "Margen bruto - gastos operativos",
        ["La clasificación exacta depende del plan contable."],
    ),
    "minimum_stock": ConceptAnswer(
        "minimum_stock",
        "Stock mínimo",
        "El stock mínimo es el nivel de inventario que activa una reposición para evitar un quiebre durante el plazo de abastecimiento.",
        "Demanda media durante el plazo de entrega + stock de seguridad",
        ["Para calcular una cifra se necesitan demanda histórica, lead time y nivel de servicio."],
    ),
    "reorder_point": ConceptAnswer(
        "reorder_point",
        "Punto de pedido",
        "El punto de pedido indica cuándo lanzar una orden de compra.",
        "Demanda media durante lead time + stock de seguridad",
        ["No es necesariamente igual al stock máximo ni al lote económico."],
    ),
    "inventory_turnover": ConceptAnswer(
        "inventory_turnover",
        "Rotación de inventario",
        "La rotación indica cuántas veces se renueva el inventario en un periodo.",
        "Costo de venta / inventario promedio",
        ["Debe utilizarse el mismo periodo y una valoración consistente."],
    ),
    "average_ticket": ConceptAnswer(
        "average_ticket",
        "Ticket medio",
        "El ticket medio es el valor medio de cada documento de venta.",
        "Ventas netas / número de documentos de venta",
        ["No debe confundirse con el valor medio de una línea de venta."],
    ),
}


def get_erp_concept(topic: str) -> ConceptAnswer:
    key = topic.strip().lower().replace("-", "_").replace(" ", "_")
    if key not in _ANSWERS:
        raise ValueError("concepto ERP no disponible")
    return _ANSWERS[key]
