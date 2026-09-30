# M1. Python esencial

**Objetivo:** leer con comodidad el código que se escriba para SSCReq web y hacer cambios pequeños.

**Tiempo:** 20 h · **Requiere:** M0

Abre una terminal con tu `venv` activo y escribe `python` para entrar a la consola interactiva (`>>>`). Prueba cada ejemplo ahí mismo. Para salir: `exit()`.

---

## 1. Tipos de datos (3 h)

```python
folio = "SSC-0012/2026"        # str: texto
cantidad = 3                    # int: entero
activo = True                   # bool: True / False
proveedor = None                # None: "sin valor"

estatus = ["Pendiente", "Autorizado", "Cancelado"]    # list: lista ordenada
requerimiento = {                                     # dict: clave → valor
    "folio": "SSC-0012/2026",
    "dependencia": "SSC",
    "estatus": "Pendiente",
}

requerimiento["estatus"]            # 'Pendiente'
requerimiento.get("proveedor")      # None, sin error si no existe
estatus.append("Pagado")
len(estatus)                        # 4
"Cancelado" in estatus              # True
folio.split("/")                    # ['SSC-0012', '2026']
folio.startswith("SSC")             # True
```

### Dinero: siempre `Decimal`, nunca `float`

```python
>>> 0.1 + 0.2
0.30000000000000004              # float tiene errores de redondeo

>>> from decimal import Decimal
>>> Decimal("0.10") + Decimal("0.20")
Decimal('0.30')                  # exacto
```

Crea los `Decimal` **desde texto** (`Decimal("1500.50")`), no desde float. En Django el equivalente es `DecimalField`.

## 2. Control de flujo (2 h)

```python
if requerimiento["estatus"] == "Cancelado":
    monto = Decimal("0")
elif requerimiento["estatus"] in ("Pendiente", "Autorizado"):
    monto = Decimal("1500.00")
else:
    monto = None

for e in estatus:
    print(e)

for i, e in enumerate(estatus, start=1):
    print(i, e)
```

La **sangría** (4 espacios) define qué está dentro de qué. No hay llaves `{}` como en otros lenguajes.

## 3. Funciones (3 h)

```python
def formatear_folio(prefijo, numero, anio=2026):
    """Devuelve un folio como SSC-0012/2026."""
    return f"{prefijo}-{numero:04d}/{anio}"

formatear_folio("SSC", 12)                   # 'SSC-0012/2026'
formatear_folio("SSC", 12, anio=2025)        # parámetro con nombre
formatear_folio(numero=7, prefijo="DGT")     # todos con nombre, cualquier orden
```

- `anio=2026` es un **valor por omisión**.
- `f"...{variable}..."` es un **f-string**; `{numero:04d}` rellena con ceros a 4 dígitos.
- El texto entre `"""` es la documentación de la función.

### Listas por comprensión

```python
reqs = [
    {"folio": "A", "estatus": "Pendiente", "monto": Decimal("100")},
    {"folio": "B", "estatus": "Cancelado", "monto": Decimal("50")},
]
activos = [r for r in reqs if r["estatus"] != "Cancelado"]
total = sum(r["monto"] for r in activos)       # Decimal('100')
```

Se lee: "dame `r` por cada `r` en `reqs` si no está cancelado".

## 4. Clases y herencia (4 h)

**En Django todo modelo, formulario y vista es una clase que hereda de otra.** Esta sección es la más importante del módulo.

```python
class Documento:
    def __init__(self, folio, dependencia):
        self.folio = folio              # atributo del objeto
        self.dependencia = dependencia

    def descripcion(self):              # método
        return f"{self.folio} ({self.dependencia})"


class Requerimiento(Documento):         # hereda de Documento
    def __init__(self, folio, dependencia, monto):
        super().__init__(folio, dependencia)   # usa el __init__ del padre
        self.monto = monto

    def descripcion(self):              # sobrescribe el método del padre
        base = super().descripcion()
        return f"{base} por ${self.monto}"


r = Requerimiento("SSC-0001/2026", "SSC", Decimal("1500"))
r.descripcion()     # 'SSC-0001/2026 (SSC) por $1500'
r.folio             # heredado de Documento
```

- `self` es "este objeto".
- `super()` llama al padre.
- Heredar = recibir todo lo del padre y cambiar solo lo necesario.

Así se verá en Django (no lo corras aún, es para reconocer el patrón):

```python
class Requerimiento(models.Model):      # hereda todo lo de guardar/consultar
    folio = models.CharField(max_length=30)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
```

## 5. Módulos, excepciones y `with` (3 h)

```python
# archivo: reglas.py
def es_cancelado(estatus):
    return estatus == "Cancelado"
```

```python
# archivo: main.py (misma carpeta)
from reglas import es_cancelado
from decimal import Decimal, InvalidOperation
```

### Excepciones

```python
def leer_monto(texto):
    try:
        monto = Decimal(texto)
    except InvalidOperation:
        raise ValueError(f"'{texto}' no es un monto válido")
    if monto < 0:
        raise ValueError("El monto no puede ser negativo")
    return monto
```

`raise` lanza un error; `try/except` lo atrapa. En Django, una validación de formulario hace exactamente esto con `ValidationError`.

### `with`: abrir y cerrar solo

```python
with open("notas.txt", "w", encoding="utf-8") as f:
    f.write("Hola")
# aquí el archivo ya está cerrado, aunque haya habido error
```

## 6. Decoradores: saber leerlos (1 h)

```python
@login_required
def lista_requerimientos(request):
    ...
```

Un decorador **envuelve** la función: antes de ejecutarla, `login_required` revisa si hay sesión; si no, redirige al inicio de sesión. No necesitas escribir decoradores, solo reconocer que la línea `@algo` agrega un comportamiento.

## 7. Fechas (1 h)

```python
from datetime import date, datetime, timedelta

hoy = date.today()
vence = hoy + timedelta(days=30)
hoy.year                          # 2026
hoy.strftime("%d/%m/%Y")          # '30/09/2026'
datetime.strptime("15/10/2026", "%d/%m/%Y").date()
```

---

## Práctica

En la carpeta `ejercicios/` hay dos archivos incompletos y sus pruebas:

| Archivo | Qué completar |
|---|---|
| `folio.py` | `validar_folio(folio, formato)` |
| `presupuesto.py` | `saldo_presupuesto(asignado, requerimientos)` |

1. Lee el comentario de cada función: dice exactamente qué debe hacer.
2. Borra la línea `raise NotImplementedError` y escribe tu código.
3. Corre las pruebas desde la carpeta `ejercicios`:

```powershell
cd modulos\M01-python\ejercicios
python test_ejercicios.py
```

Cuando todo diga `OK`, terminaste. Si te atoras más de 30 minutos, compara con `soluciones.py`, pero **escríbelo tú** después sin verlo.

## Se domina cuando

Puedes leer `app/numero_a_letras.py` de SSCReq y explicar qué hace cada función.

Anota en la plataforma las partes que no entiendas; se repasan antes de M4.
