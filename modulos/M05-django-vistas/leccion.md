# M5. Django: vistas, formularios y plantillas

**Objetivo:** construir pantallas de consulta y captura completas.

**Tiempo:** 20 h · **Requiere:** M4

En SSCReq de escritorio esto equivale a la tabla de requerimientos y a `requerimiento_dialog.py`, con una diferencia: **cada acción es una petición**.

---

## 1. Primera vista: de URL a HTML (3 h)

### La vista

`requerimientos/views.py`:

```python
from django.shortcuts import render

from .models import Requerimiento


def lista(request):
    requerimientos = Requerimiento.objects.select_related("dependencia", "proveedor")
    return render(request, "requerimientos/lista.html", {"requerimientos": requerimientos})
```

Una vista es **una función que recibe una petición (`request`) y devuelve una respuesta**. `render` toma una plantilla y un diccionario (el *contexto*) y produce HTML.

### Las URLs

Crea `requerimientos/urls.py`:

```python
from django.urls import path

from . import views

app_name = "requerimientos"

urlpatterns = [
    path("", views.lista, name="lista"),
]
```

Y conéctalo en `config/urls.py`:

```python
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="requerimientos:lista")),
    path("admin/", admin.site.urls),
    path("requerimientos/", include("requerimientos.urls")),
]
```

`name="lista"` permite escribir `{% url 'requerimientos:lista' %}` en vez de la ruta a mano: si la ruta cambia, los enlaces siguen funcionando.

### La plantilla

Crea `requerimientos/templates/requerimientos/lista.html` (sí, `requerimientos` dos veces: es la convención para que no choquen plantillas de apps distintas):

```html
<h1>Requerimientos</h1>
<ul>
  {% for r in requerimientos %}
    <li>{{ r.folio }} — {{ r.dependencia }} — ${{ r.monto }} — {{ r.get_estatus_display }}</li>
  {% empty %}
    <li>No hay requerimientos.</li>
  {% endfor %}
</ul>
```

`runserver` y abre http://127.0.0.1:8000. Ya es una página web generada desde la base.

### Lenguaje de plantillas

| Sintaxis | Qué hace |
|---|---|
| `{{ variable }}` | Imprime un valor (escapado: `<script>` se muestra como texto, protege contra XSS) |
| `{{ r.dependencia.nombre }}` | Atributos con punto |
| `{{ r.get_estatus_display }}` | Etiqueta legible de un campo con `choices` |
| `{{ valor\|default:"—" }}` | Filtro: transforma el valor |
| `{% for %} … {% empty %} … {% endfor %}` | Ciclo, con caso vacío |
| `{% if %} … {% elif %} … {% else %} … {% endif %}` | Condición |
| `{% url 'app:nombre' arg %}` | Genera la URL por nombre |
| `{% include "archivo.html" %}` | Inserta otra plantilla |

## 2. Herencia de plantillas (2 h)

Todas las pantallas comparten encabezado, menú y estilos. Se escriben una vez en `base.html`:

`requerimientos/templates/requerimientos/base.html`:

```html
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block titulo %}mini-SSCReq{% endblock %}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
</head>
<body>
  <nav class="navbar bg-dark" data-bs-theme="dark">
    <div class="container">
      <a class="navbar-brand" href="{% url 'requerimientos:lista' %}">mini-SSCReq</a>
      <a class="nav-link text-light" href="{% url 'admin:index' %}">Administración</a>
    </div>
  </nav>
  <main class="container py-4">
    {% for m in messages %}
      <div class="alert alert-{% if m.tags == 'error' %}danger{% else %}{{ m.tags }}{% endif %}">{{ m }}</div>
    {% endfor %}
    {% block contenido %}{% endblock %}
  </main>
</body>
</html>
```

Cada página **extiende** la base y rellena los `block`. Es la herencia de M1, aplicada a HTML.

## 3. La lista con filtros y paginación (4 h)

La tabla se divide en tres plantillas. Parece de más ahora, pero en M7 (HTMX) será **exactamente lo que necesitas** para actualizar solo la tabla o solo una fila.

```
lista.html      ← página completa: título, filtros y tabla
 └── _tabla.html   ← solo la tabla y la paginación
      └── _fila.html  ← solo una fila
```

(El guion bajo inicial indica "pedazo de página, no página completa".)

### Vista con filtros

Los filtros llegan por `GET` en la URL (`?estatus=pendiente&q=llanta`), como viste en M2:

```python
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from .models import Dependencia, Requerimiento


def lista(request):
    requerimientos = Requerimiento.objects.select_related("dependencia", "proveedor")

    estatus = request.GET.get("estatus", "")
    dependencia = request.GET.get("dependencia", "")
    q = request.GET.get("q", "").strip()
    if estatus:
        requerimientos = requerimientos.filter(estatus=estatus)
    if dependencia:
        requerimientos = requerimientos.filter(dependencia_id=dependencia)
    if q:
        requerimientos = requerimientos.filter(
            Q(folio__icontains=q) | Q(descripcion__icontains=q)
        )

    pagina = Paginator(requerimientos, 20).get_page(request.GET.get("page"))
    contexto = {
        "pagina": pagina,
        "estatus_opciones": Requerimiento.Estatus.choices,
        "dependencias": Dependencia.objects.all(),
        "filtros": {"estatus": estatus, "dependencia": dependencia, "q": q},
    }
    return render(request, "requerimientos/lista.html", contexto)
```

Nota que la consulta **no se ejecuta** hasta que la tabla se dibuja: cada `.filter()` solo agrega condiciones.

### `lista.html`

```html
{% extends "requerimientos/base.html" %}

{% block titulo %}Requerimientos{% endblock %}

{% block contenido %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h3 m-0">Requerimientos</h1>
  <a class="btn btn-primary" href="{% url 'requerimientos:nuevo' %}">Nuevo</a>
</div>

<form id="filtros" class="row g-2 mb-3" method="get">
  <div class="col-md-4">
    <input class="form-control" type="search" name="q" value="{{ filtros.q }}" placeholder="Buscar folio o descripción">
  </div>
  <div class="col-md-3">
    <select class="form-select" name="estatus">
      <option value="">Todos los estatus</option>
      {% for valor, etiqueta in estatus_opciones %}
        <option value="{{ valor }}" {% if filtros.estatus == valor %}selected{% endif %}>{{ etiqueta }}</option>
      {% endfor %}
    </select>
  </div>
  <div class="col-md-3">
    <select class="form-select" name="dependencia">
      <option value="">Todas las dependencias</option>
      {% for d in dependencias %}
        <option value="{{ d.pk }}" {% if filtros.dependencia == d.pk|stringformat:"s" %}selected{% endif %}>{{ d }}</option>
      {% endfor %}
    </select>
  </div>
  <div class="col-md-2">
    <button class="btn btn-outline-secondary">Filtrar</button>
  </div>
</form>

<div id="tabla">
  {% include "requerimientos/_tabla.html" %}
</div>
{% endblock %}
```

### `_tabla.html`

```html
<table class="table table-hover align-middle">
  <thead>
    <tr>
      <th>Folio</th><th>Dependencia</th><th>Proveedor</th>
      <th class="text-end">Monto</th><th>Estatus</th><th></th>
    </tr>
  </thead>
  <tbody>
    {% for r in pagina %}
      {% include "requerimientos/_fila.html" %}
    {% empty %}
      <tr><td colspan="6" class="text-center text-muted py-4">Sin requerimientos con esos filtros.</td></tr>
    {% endfor %}
  </tbody>
</table>

{% if pagina.has_other_pages %}
<nav>
  <ul class="pagination">
    {% if pagina.has_previous %}
      <li class="page-item"><a class="page-link" href="{% querystring page=pagina.previous_page_number %}">Anterior</a></li>
    {% endif %}
    <li class="page-item disabled"><span class="page-link">Página {{ pagina.number }} de {{ pagina.paginator.num_pages }}</span></li>
    {% if pagina.has_next %}
      <li class="page-item"><a class="page-link" href="{% querystring page=pagina.next_page_number %}">Siguiente</a></li>
    {% endif %}
  </ul>
</nav>
{% endif %}
```

`{% querystring page=2 %}` conserva los filtros actuales y solo cambia la página.

### `_fila.html`

```html
<tr id="req-{{ r.pk }}">
  <td>{{ r.folio }}</td>
  <td>{{ r.dependencia }}</td>
  <td>{{ r.proveedor|default:"—" }}</td>
  <td class="text-end">${{ r.monto_efectivo|floatformat:"2g" }}</td>
  <td>{{ r.get_estatus_display }}</td>
  <td class="text-end">
    <a class="btn btn-sm btn-outline-primary" href="{% url 'requerimientos:editar' r.pk %}">Editar</a>
  </td>
</tr>
```

> Al abrir la lista verás el error **`NoReverseMatch`**: los enlaces "Nuevo" y "Editar" apuntan a rutas que todavía no existen. Es normal; léelo (última línea, M0) y sigue a la sección 4, donde se crean.

## 4. Formularios con `ModelForm` (6 h)

Un `ModelForm` genera el formulario a partir del modelo: campos, tipos, obligatorios y validación básica. Tú agregas las **reglas de negocio**.

### La regla de folio

Copia tu función `validar_folio` de M1 a `requerimientos/reglas.py`. Es la misma regla, ahora usada por Django.

### `requerimientos/forms.py`

```python
from django import forms

from .models import Requerimiento
from .reglas import validar_folio


class RequerimientoForm(forms.ModelForm):
    class Meta:
        model = Requerimiento
        fields = ["folio", "dependencia", "proveedor", "descripcion", "monto", "estatus", "fecha"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            clase = "form-select" if isinstance(campo.widget, forms.Select) else "form-control"
            campo.widget.attrs.setdefault("class", clase)

    def clean_monto(self):
        monto = self.cleaned_data["monto"]
        if monto < 0:
            raise forms.ValidationError("El monto no puede ser negativo.")
        return monto

    def clean(self):
        datos = super().clean()
        folio = datos.get("folio")
        dependencia = datos.get("dependencia")
        if folio and dependencia and not validar_folio(folio, dependencia.formato_folio):
            self.add_error(
                "folio",
                f"El folio no cumple el formato de {dependencia}: {dependencia.formato_folio}",
            )
        return datos
```

- `clean_<campo>` valida **un** campo.
- `clean` valida campos **combinados** (el folio depende de la dependencia).
- `__init__` solo pone clases de Bootstrap a cada campo.

### Una vista para alta y edición

```python
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RequerimientoForm


def formulario(request, pk=None):
    requerimiento = get_object_or_404(Requerimiento, pk=pk) if pk else None
    form = RequerimientoForm(
        request.POST or None, request.FILES or None, instance=requerimiento
    )
    if request.method == "POST" and form.is_valid():
        guardado = form.save()
        messages.success(request, f"Requerimiento {guardado.folio} guardado.")
        return redirect("requerimientos:lista")

    return render(request, "requerimientos/formulario.html",
                  {"form": form, "requerimiento": requerimiento})
```

Léela en voz alta:

1. Si hay `pk`, busca el requerimiento (o responde 404). Si no, es alta.
2. Crea el formulario: con los datos enviados si es `POST`; vacío o con los datos actuales si es `GET`.
3. Si es `POST` **y** pasa todas las validaciones: guarda, deja un mensaje y **redirige** (Post/Redirect/Get, M2).
4. En cualquier otro caso, muestra el formulario (con errores si los hubo).

Agrega las rutas en `requerimientos/urls.py`:

```python
    path("nuevo/", views.formulario, name="nuevo"),
    path("<int:pk>/editar/", views.formulario, name="editar"),
```

`<int:pk>` toma el número de la URL y lo pasa a la vista como `pk`.

### `_campos.html` (reutilizable)

```html
{% csrf_token %}
{{ form.non_field_errors }}
{% for campo in form %}
  <div class="mb-3">
    <label class="form-label" for="{{ campo.id_for_label }}">{{ campo.label|capfirst }}</label>
    {{ campo }}
    {% for error in campo.errors %}<div class="text-danger small">{{ error }}</div>{% endfor %}
    {% if campo.help_text %}<div class="form-text">{{ campo.help_text }}</div>{% endif %}
  </div>
{% endfor %}
```

`{% csrf_token %}` es **obligatorio** en todo formulario `POST`: evita que otra página envíe formularios a tu nombre (M10).

### `formulario.html`

```html
{% extends "requerimientos/base.html" %}

{% block titulo %}{% if requerimiento %}Editar {{ requerimiento }}{% else %}Nuevo requerimiento{% endif %}{% endblock %}

{% block contenido %}
<h1 class="h3">{% if requerimiento %}Editar {{ requerimiento }}{% else %}Nuevo requerimiento{% endif %}</h1>
<form method="post" enctype="multipart/form-data" class="col-lg-6">
  {% include "requerimientos/_campos.html" %}
  <button class="btn btn-primary">Guardar</button>
  <a class="btn btn-link" href="{% url 'requerimientos:lista' %}">Cancelar</a>
</form>
{% endblock %}
```

## 5. Adjuntos (2 h)

1. En el modelo `Requerimiento` agrega:

   ```python
   adjunto = models.FileField(upload_to="adjuntos/%Y/", blank=True)
   ```

   y corre `makemigrations` y `migrate`. Agrega también `"adjunto"` a la lista `fields` de `RequerimientoForm`.

2. En `settings.py`:

   ```python
   MEDIA_URL = "media/"
   MEDIA_ROOT = BASE_DIR / "media"
   ```

3. En `config/urls.py`, para servir los archivos **solo en desarrollo**:

   ```python
   from django.conf import settings
   from django.conf.urls.static import static

   urlpatterns = [
       # … las rutas que ya tenías …
   ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```

El archivo se guarda en disco (`media/adjuntos/2026/...`) y la base solo guarda la ruta. Para subir archivos el formulario necesita `enctype="multipart/form-data"` y la vista, `request.FILES`. Agrega `media/` a `.gitignore`.

## 6. Qué pasa al presionar "Guardar" (2 h)

Abre F12 → Red y sigue esto con un alta real:

1. El navegador envía `POST /requerimientos/nuevo/` con los campos y la cookie de sesión y el token CSRF.
2. `config/urls.py` → `requerimientos/urls.py` → `views.formulario`.
3. `RequerimientoForm(request.POST)` convierte texto en tipos de Python (`"1500"` → `Decimal("1500")`).
4. `form.is_valid()` corre validaciones del modelo, `clean_monto` y `clean`.
5. **Si falla:** la vista devuelve `200` con el formulario y los errores. Nada se guardó.
6. **Si pasa:** `form.save()` hace el `INSERT`; la vista responde `302` a la lista.
7. El navegador pide `GET /requerimientos/` → la lista se dibuja con el mensaje verde.

---

## Práctica

1. Construye la lista con filtros por estatus, dependencia y búsqueda.
2. Construye alta y edición con validación de folio y monto.
3. Prueba a propósito: folio con formato de otra dependencia, monto negativo, folio repetido. Cada uno debe mostrar su error sin guardar.
4. Adjunta un PDF inventado a un requerimiento y ábrelo desde el panel.
5. Commit.

## Se domina cuando

Puedes explicar, paso por paso, qué pasa desde que se presiona "Guardar" hasta que se ve la lista actualizada.
