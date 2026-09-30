from decimal import Decimal


def saldo_presupuesto(asignado, requerimientos):
    """Calcula el saldo disponible de un presupuesto.

    asignado: Decimal con el presupuesto asignado.
    requerimientos: lista de diccionarios con "estatus" y "monto" (Decimal).

    Reglas:
      - Un requerimiento "Cancelado" cuenta 0.
      - Si algún monto es negativo, lanza ValueError.
      - Devuelve asignado menos la suma de los montos que sí cuentan.

    Ejemplo:
      saldo_presupuesto(Decimal("1000"), [
          {"estatus": "Autorizado", "monto": Decimal("300.50")},
          {"estatus": "Cancelado",  "monto": Decimal("200")},
      ])  → Decimal("699.50")
    """
    raise NotImplementedError
