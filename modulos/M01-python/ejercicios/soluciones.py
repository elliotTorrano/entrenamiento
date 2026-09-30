# Solo para comparar después de intentarlo. Escríbelo tú primero.
from decimal import Decimal


def validar_folio(folio, formato):
    patron = formato.replace("AAAA", "####")
    if len(folio) != len(patron):
        return False
    for letra, esperado in zip(folio, patron):
        if esperado == "#":
            if not letra.isdigit():
                return False
        elif letra != esperado:
            return False
    return True


def saldo_presupuesto(asignado, requerimientos):
    total = Decimal("0")
    for r in requerimientos:
        if r["monto"] < 0:
            raise ValueError("El monto no puede ser negativo")
        if r["estatus"] != "Cancelado":
            total += r["monto"]
    return asignado - total
