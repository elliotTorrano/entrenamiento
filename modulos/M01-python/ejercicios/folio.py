def validar_folio(folio, formato):
    """Indica si un folio cumple el formato de su dependencia.

    El formato usa:
      #    → un dígito (0-9)
      AAAA → el año, cuatro dígitos
      cualquier otro carácter → debe aparecer igual

    Ejemplos:
      validar_folio("SSC-0012/2026", "SSC-####/AAAA")  → True
      validar_folio("SSC-12/2026",   "SSC-####/AAAA")  → False (faltan dígitos)
      validar_folio("DGT-0012/2026", "SSC-####/AAAA")  → False (otro prefijo)
      validar_folio("SSC-00A2/2026", "SSC-####/AAAA")  → False (A no es dígito)

    Pista: primero reemplaza "AAAA" por "####" en el formato; así solo
    tienes que comparar carácter por carácter con zip().
    """
    raise NotImplementedError
