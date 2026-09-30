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
