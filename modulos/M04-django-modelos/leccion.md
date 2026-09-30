# M4. Django: fundamentos, modelos y administración

**Objetivo:** entender cómo está organizado un proyecto Django y cómo se define la base de datos desde Python.

**Tiempo:** 24 h · **Requiere:** M1, M2, M3

A partir de aquí construyes **mini_sscreq**, el proyecto que crecerá en M5, M7 y los módulos siguientes. Vive en `practica/mini_sscreq` dentro de este repositorio, así tu avance queda en Git y se puede revisar.

Si te atoras, la versión terminada (al final de M7) está en `soluciones/mini_sscreq`. Úsala para comparar, no para copiar.

---

## 1. La idea central: el recorrido de una petición (1 h)

```
Navegador ──GET /requerimientos/──▶ urls.py ──▶ vista (views.py)
                                                   │
                                                   ├──▶ modelo (models.py) ──▶ base de datos
                                                   │
                                                   └──▶ plantilla (.html) ──▶ HTML ──▶ Navegador
```

Django llama a esto **MTV**:

| Pieza | Archivo | Responsabilidad | Equivalente en SSCReq de escritorio |
|---|---|---|---|
| **M**odelo | `models.py` | Qué datos hay y sus reglas | Tablas SQLite + funciones de acceso |
| **T**emplate (plantilla) | `templates/*.html` | Cómo se ve | Diálogos y tablas de PySide6 |
| **V**ista | `views.py` | Qué hacer con cada petición | Lo que pasa al presionar un botón |

En este módulo te enfocas en **M** y en el panel de administración. Vistas y plantillas son M5.

## 2. Crear el proyecto (2 h)

Desde la raíz de este repositorio, con el `venv` activo:

```powershell
mkdir practica\mini_sscreq
cd practica\mini_sscreq
django-admin startproject config .
python manage.py startapp requerimientos
python manage.py runserver
```

Abre http://127.0.0.1:8000: verás el cohete de Django. `Ctrl+C` detiene el servidor.

> El punto final en `startproject config .` significa "créalo aquí mismo". Sin él se crea una carpeta de más.

### Qué se creó

```
mini_sscreq/
├── manage.py              ← el "control remoto": runserver, migrate, shell…
├── config/                ← configuración del PROYECTO
│   ├── settings.py        ← apps instaladas, base de datos, idioma
│   └── urls.py            ← la tabla de rutas principal
└── requerimientos/        ← una APP (un módulo de SSCReq)
    ├── models.py          ← tablas
    ├── admin.py           ← qué aparece en el panel de administración
    ├── views.py           ← vistas (M5)
    └── migrations/        ← historial de cambios a la base
```

**Proyecto vs. app:** el proyecto es SSCReq completo; cada app es un módulo (Requerimientos, Oficios, Control Escolar…). Las apps se pueden mover entre proyectos.

### Ajustar `config/settings.py`

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    # … las que ya estaban …
    "django.contrib.staticfiles",
    "requerimientos",          # ← agrega tu app
]

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
```

## 3. Modelos (6 h)

Un modelo es una **clase de Python que describe una tabla**. Cada atributo es una columna. Reemplaza todo el contenido de `requerimientos/models.py`:

```python
from datetime import date
from decimal import Decimal

from django.db import models


class Dependencia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    formato_folio = models.CharField(
        max_length=30, help_text="# = un dígito, AAAA = año. Ejemplo: SSC-####/AAAA"
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    rfc = models.CharField("RFC", max_length=13, unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "proveedores"

    def __str__(self):
        return self.nombre


class Requerimiento(models.Model):
    class Estatus(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        AUTORIZADO = "autorizado", "Autorizado"
        PAGADO = "pagado", "Pagado"
        CANCELADO = "cancelado", "Cancelado"

    folio = models.CharField(max_length=30, unique=True)
    dependencia = models.ForeignKey(
        Dependencia, on_delete=models.PROTECT, related_name="requerimientos"
    )
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT, null=True, blank=True
    )
    descripcion = models.TextField("descripción", blank=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    estatus = models.CharField(
        max_length=20, choices=Estatus.choices, default=Estatus.PENDIENTE
    )
    fecha = models.DateField(default=date.today)
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha", "folio"]

    def __str__(self):
        return self.folio

    @property
    def monto_efectivo(self):
        if self.estatus == self.Estatus.CANCELADO:
            return Decimal("0")
        return self.monto
```

### Cómo leerlo (compáralo con `esquema.sql` de M3)

| Python | SQL que genera | Por qué |
|---|---|---|
| `class Requerimiento(models.Model)` | `CREATE TABLE requerimientos_requerimiento` | Herencia (M1): recibe guardar, borrar, consultar |
| (nada) | `id` autonumérico | Django agrega la clave primaria solo |
| `CharField(max_length=30, unique=True)` | `VARCHAR(30) UNIQUE` | Folio sin duplicados |
| `ForeignKey(Dependencia, …)` | `dependencia_id INTEGER REFERENCES …` | Clave foránea |
| `on_delete=models.PROTECT` | — | No deja borrar una dependencia con requerimientos |
| `null=True, blank=True` | columna sin `NOT NULL` | `null` = la base lo permite; `blank` = el formulario lo permite |
| `DecimalField(max_digits=12, decimal_places=2)` | `NUMERIC(12,2)` | Dinero exacto |
| `choices=Estatus.choices` | `VARCHAR(20)` | Lista cerrada de estatus; en pantalla se ve "Pendiente" |
| `auto_now_add` / `auto_now` | — | Fecha de creación y de última modificación, automáticas |
| `__str__` | — | Cómo se muestra el objeto en listas y combos |
| `@property monto_efectivo` | — | Regla "cancelado cuenta 0" en un solo lugar |

## 4. Migraciones (3 h)

Hoy SSCReq cambia la base a mano con `ALTER TABLE`. Django lo hace con **migraciones**: archivos que describen cada cambio, en orden, y que se aplican igual en tu PC, en Beta y en producción.

```powershell
python manage.py makemigrations     # compara models.py con la última migración y crea 0001_initial.py
python manage.py migrate            # aplica a la base las migraciones pendientes
python manage.py showmigrations     # cuáles están aplicadas [X] y cuáles no [ ]
python manage.py sqlmigrate requerimientos 0001   # muestra el SQL exacto, sin ejecutarlo
```

Dos pasos siempre: **`makemigrations`** (escribir el plan) y **`migrate`** (ejecutarlo). Las migraciones **sí se suben a Git**; la base (`db.sqlite3`) no.

## 5. Panel de administración (3 h)

Reemplaza `requerimientos/admin.py`:

```python
from django.contrib import admin

from .models import Dependencia, Proveedor, Requerimiento


@admin.register(Dependencia)
class DependenciaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "formato_folio"]


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ["nombre", "rfc"]
    search_fields = ["nombre", "rfc"]


@admin.register(Requerimiento)
class RequerimientoAdmin(admin.ModelAdmin):
    list_display = ["folio", "dependencia", "proveedor", "monto", "estatus", "fecha"]
    list_filter = ["estatus", "dependencia"]
    search_fields = ["folio", "descripcion"]
    date_hierarchy = "fecha"
```

```powershell
python manage.py createsuperuser
python manage.py runserver
```

Entra a http://127.0.0.1:8000/admin. Con **cero pantallas programadas** ya tienes catálogos con alta, edición, búsqueda y filtros. En SSCReq web, los catálogos (dependencias, áreas, proveedores) vivirán aquí.

### Cargar datos ficticios

```powershell
mkdir requerimientos\fixtures
copy ..\..\modulos\M04-django-modelos\datos_ficticios.json requerimientos\fixtures\
python manage.py loaddata datos_ficticios
```

Son 3 dependencias, 3 proveedores y 34 requerimientos inventados.

## 6. El ORM: consultar sin escribir SQL (6 h)

El ORM traduce Python a SQL. Ábrelo con:

```powershell
python manage.py shell
```

```python
from requerimientos.models import Dependencia, Proveedor, Requerimiento
from django.db.models import Sum, Count, Q

# Todos / uno
Requerimiento.objects.all()
Requerimiento.objects.get(folio="SSC-0001/2026")        # error si no existe o hay varios
Requerimiento.objects.count()

# filter / exclude  (≈ WHERE)
Requerimiento.objects.filter(estatus="pendiente")
Requerimiento.objects.exclude(estatus="cancelado")
Requerimiento.objects.filter(monto__gt=10000)                    # gt, gte, lt, lte
Requerimiento.objects.filter(folio__startswith="SSC")
Requerimiento.objects.filter(descripcion__icontains="llanta")    # sin importar mayúsculas
Requerimiento.objects.filter(dependencia__nombre="Tránsito")     # __ cruza la relación (JOIN)
Requerimiento.objects.filter(Q(estatus="pendiente") | Q(estatus="autorizado"))   # OR

# order_by
Requerimiento.objects.order_by("-monto")[:5]      # los 5 más caros

# Relaciones
r = Requerimiento.objects.get(folio="DGT/01/2026")
r.dependencia.nombre                              # adelante
ssc = Dependencia.objects.get(nombre="SSC")
ssc.requerimientos.count()                        # atrás, gracias a related_name

# Totales: annotate / aggregate  (≈ GROUP BY / SUM)
Requerimiento.objects.exclude(estatus="cancelado").aggregate(total=Sum("monto"))
(Requerimiento.objects.exclude(estatus="cancelado")
    .values("dependencia__nombre")
    .annotate(total=Sum("monto"), cantidad=Count("id")))

# Crear, cambiar, borrar
nuevo = Requerimiento.objects.create(folio="PC-003-2026", dependencia=Dependencia.objects.get(nombre="Protección Civil"), monto="250.00")
nuevo.estatus = "autorizado"
nuevo.save()
nuevo.delete()

# Ver el SQL que genera una consulta
print(Requerimiento.objects.filter(estatus="pendiente").query)
```

### `select_related`: evitar cientos de consultas

```python
for r in Requerimiento.objects.all():
    print(r.dependencia.nombre)      # ¡una consulta extra por cada requerimiento!

for r in Requerimiento.objects.select_related("dependencia"):
    print(r.dependencia.nombre)      # una sola consulta con JOIN
```

Cuando una tabla muestre datos de otra tabla relacionada, usa `select_related`.

## 7. Pasar a PostgreSQL (3 h)

Hasta aquí usaste SQLite, que viene incluido y es perfecto para practicar. Para acercarte a producción:

1. En pgAdmin crea la base `mini_sscreq`.
2. `pip install "psycopg[binary]"`
3. En `config/settings.py`, arriba agrega `import os` y reemplaza `DATABASES` por:

```python
if os.environ.get("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
```

4. En la terminal (solo para esa sesión):

```powershell
$env:POSTGRES_DB = "mini_sscreq"
$env:POSTGRES_PASSWORD = "la-que-pusiste-al-instalar"
python manage.py migrate
python manage.py loaddata datos_ficticios
python manage.py createsuperuser
```

La contraseña va en una **variable de entorno**, nunca escrita en el código (M10). Si cierras la terminal sin definir `POSTGRES_DB`, el proyecto vuelve a usar SQLite.

---

## Práctica

1. Crea el proyecto, la app y los modelos de este módulo; migra y entra al panel.
2. Captura desde el panel 2 dependencias, 2 proveedores y 3 requerimientos inventados. Después carga `datos_ficticios`.
3. Agrega a `Requerimiento` el campo `observaciones = models.TextField(blank=True)`. Crea la migración, aplícala y revisa el SQL con `sqlmigrate requerimientos 0002`.
4. En el shell, resuelve con el ORM las consultas 1 a 6 de `consultas.sql` de M3.
5. Commit: `git add practica` y `git commit -m "M4: modelos de mini_sscreq"`.

## Se domina cuando

Puedes agregar un campo nuevo a `Requerimiento`, crear su migración y explicar qué SQL generó (`sqlmigrate`).
