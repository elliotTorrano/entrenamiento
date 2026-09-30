from decimal import Decimal

from folio import validar_folio
from presupuesto import saldo_presupuesto


def test_folio_valido():
    assert validar_folio("SSC-0012/2026", "SSC-####/AAAA") is True


def test_folio_otro_formato():
    assert validar_folio("DGT/15/2025", "DGT/##/AAAA") is True


def test_folio_faltan_digitos():
    assert validar_folio("SSC-12/2026", "SSC-####/AAAA") is False


def test_folio_otro_prefijo():
    assert validar_folio("DGT-0012/2026", "SSC-####/AAAA") is False


def test_folio_letra_en_lugar_de_digito():
    assert validar_folio("SSC-00A2/2026", "SSC-####/AAAA") is False


def test_folio_vacio():
    assert validar_folio("", "SSC-####/AAAA") is False


def test_saldo_basico():
    reqs = [
        {"estatus": "Autorizado", "monto": Decimal("300.50")},
        {"estatus": "Cancelado", "monto": Decimal("200")},
    ]
    assert saldo_presupuesto(Decimal("1000"), reqs) == Decimal("699.50")


def test_saldo_sin_requerimientos():
    assert saldo_presupuesto(Decimal("500"), []) == Decimal("500")


def test_saldo_es_decimal():
    reqs = [{"estatus": "Pendiente", "monto": Decimal("0.10")},
            {"estatus": "Pendiente", "monto": Decimal("0.20")}]
    resultado = saldo_presupuesto(Decimal("1"), reqs)
    assert isinstance(resultado, Decimal)
    assert resultado == Decimal("0.70")


def test_saldo_monto_negativo():
    try:
        saldo_presupuesto(Decimal("100"), [{"estatus": "Pendiente", "monto": Decimal("-1")}])
    except ValueError:
        return
    raise AssertionError("Debió lanzar ValueError")


if __name__ == "__main__":
    pruebas = [(n, f) for n, f in globals().items() if n.startswith("test_")]
    fallas = 0
    for nombre, prueba in pruebas:
        try:
            prueba()
            print(f"OK     {nombre}")
        except NotImplementedError:
            fallas += 1
            print(f"FALTA  {nombre}  (la función aún no está escrita)")
        except Exception as e:
            fallas += 1
            print(f"FALLA  {nombre}  {type(e).__name__}: {e}")
    print(f"\n{len(pruebas) - fallas} de {len(pruebas)} pruebas pasan.")
