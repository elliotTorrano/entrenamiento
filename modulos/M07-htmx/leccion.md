# M7. HTMX

**Objetivo:** que las pantallas respondan sin recargar la página completa, escribiendo casi nada de JavaScript.

**Tiempo:** 18 h · **Requiere:** M5

---

## 1. La idea (2 h)

Sin HTMX, cada clic pide **una página completa** y el navegador redibuja todo. Con HTMX:

```
Clic en el combo de estatus
   │
   ▼
HTMX envía POST /requerimientos/5/estatus/        (con hx-post)
   │
   ▼
Django responde SOLO con el HTML de esa fila       (_fila.html)
   │
   ▼
HTMX reemplaza la fila vieja por la nueva          (hx-target + hx-swap)
```

Lo que cambia respecto a M5:

- **Del lado del navegador:** atributos `hx-*` en el HTML. Nada de JavaScript propio.
- **Del lado de Django:** la misma vista devuelve la página completa **o** solo un pedazo, según quién pregunte.

Por eso en M5 separaste `_tabla.html` y `_fila.html`: son los pedazos.

## 2. Instalar (1 h)

```powershell
pip install django-htmx
```

`config/settings.py`:

```python
INSTALLED_APPS = [
    # …
    "django_htmx",
    "requerimientos",
]

MIDDLEWARE = [
    # … al final:
    "django_htmx.middleware.HtmxMiddleware",
]
```

El middleware agrega `request.htmx`: vale `True` si la petición la hizo HTMX.

Descarga HTMX **una vez** y guárdalo en el proyecto (así funciona aunque la red de la oficina bloquee internet):

```powershell
mkdir requerimientos\static
Invoke-WebRequest https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js -OutFile requerimientos\static\htmx.min.js
```

En `base.html`:

```html
{% load static %}<!doctype html>
<html lang="es">
<head>
  …
  <script src="{% static 'htmx.min.js' %}" defer></script>
</head>
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
```

`hx-headers` en `<body>` hace que **toda** petición HTMX lleve el token CSRF. Sin él, cada `hx-post` daría 403.

## 3. Los cinco atributos básicos (3 h)

| Atributo | Pregunta que responde | Ejemplo |
|---|---|---|
| `hx-get` / `hx-post` | ¿A qué URL y con qué método? | `hx-post="/requerimientos/5/estatus/"` |
| `hx-trigger` | ¿Cuándo? | `change`, `click`, `submit`, `input delay:300ms`, `every 5s` |
| `hx-target` | ¿Dónde pongo la respuesta? | `#tabla`, `closest tr`, `this` |
| `hx-swap` | ¿Cómo la pongo? | `innerHTML` (adentro, por omisión), `outerHTML` (reemplaza el elemento) |
| `hx-push-url` | ¿Actualizo la URL del navegador? | `true` → los filtros quedan en la URL y se pueden compartir |

Si no pones `hx-trigger`, se usa el natural: `click` en botones y enlaces, `change` en combos, `submit` en formularios.

Otros que usarás: `hx-confirm` (pregunta antes), `hx-indicator` (muestra "cargando"), `hx-boost` (convierte enlaces normales en peticiones HTMX).

## 4. Patrón 1: filtros sin recargar (3 h)

### La vista decide: página o pedazo

En `lista`, cambia el final:

```python
    if request.htmx:
        return render(request, "requerimientos/_tabla.html", contexto)
    return render(request, "requerimientos/lista.html", contexto)
```

Es la **misma vista** y la **misma consulta**. Solo cambia la plantilla. Si alguien abre la URL directamente o recarga (F5), recibe la página completa: nada se rompe.

### El formulario de filtros

En `lista.html`, al `<form id="filtros">` agrégale:

```html
<form id="filtros" class="row g-2 mb-3" method="get"
      hx-get="{% url 'requerimientos:lista' %}"
      hx-trigger="submit, input delay:300ms"
      hx-target="#tabla"
      hx-push-url="true"
      hx-indicator="#cargando">
```

Y junto al botón Filtrar, el indicador:

```html
<span id="cargando" class="htmx-indicator spinner-border spinner-border-sm"></span>
```

- `input delay:300ms`: al escribir o cambiar un combo, espera 300 ms sin cambios y entonces pide. Así la búsqueda funciona **mientras escribes** sin una petición por letra.
- El formulario envía todos sus campos: `?q=…&estatus=…&dependencia=…`.
- La respuesta (`_tabla.html`) se coloca **dentro** de `<div id="tabla">`.

### La paginación

En `_tabla.html`, cambia `<nav>` por:

```html
<nav hx-boost="true" hx-target="#tabla">
```

`hx-boost` convierte los enlaces normales en peticiones HTMX. Los enlaces no cambian; siguen funcionando sin HTMX.

**Pruébalo:** F12 → Red → filtra por **Fetch/XHR**. Cambia el estatus del filtro. Da clic en la petición → **Response**: es solo la tabla, no la página.

## 5. Patrón 2: cambiar estatus en línea (3 h)

Hoy en SSCReq el estatus se cambia con un combo dentro de la tabla. Igual aquí, y solo esa fila se actualiza.

### Vista

```python
from django.views.decorators.http import require_POST


@require_POST
def cambiar_estatus(request, pk):
    requerimiento = get_object_or_404(Requerimiento, pk=pk)
    nuevo = request.POST.get("estatus")
    if nuevo in Requerimiento.Estatus.values:
        requerimiento.estatus = nuevo
        requerimiento.save(update_fields=["estatus", "modificado"])
    return render(
        request,
        "requerimientos/_fila.html",
        {"r": requerimiento, "estatus_opciones": Requerimiento.Estatus.choices},
    )
```

- `@require_POST`: si alguien la abre con `GET`, responde 405. Cambiar datos siempre es `POST` (M2).
- `if nuevo in …values`: **nunca** confíes en lo que llega del navegador; se valida en el servidor.

Ruta:

```python
    path("<int:pk>/estatus/", views.cambiar_estatus, name="cambiar_estatus"),
```

### En `_fila.html`

Reemplaza `<td>{{ r.get_estatus_display }}</td>` por:

```html
  <td>
    <select class="form-select form-select-sm" name="estatus"
            hx-post="{% url 'requerimientos:cambiar_estatus' r.pk %}"
            hx-target="closest tr" hx-swap="outerHTML">
      {% for valor, etiqueta in estatus_opciones %}
        <option value="{{ valor }}" {% if r.estatus == valor %}selected{% endif %}>{{ etiqueta }}</option>
      {% endfor %}
    </select>
  </td>
```

`closest tr` = "la fila que contiene este combo". `outerHTML` = reemplaza la fila completa por la que devolvió el servidor. Cambia un requerimiento a **Cancelado**: el monto pasa a `$0.00` sin recargar, porque la fila nueva usa `monto_efectivo`.

## 6. Patrón 3: borrar con confirmación (1 h)

```python
from django.http import HttpResponse


@require_POST
def borrar(request, pk):
    requerimiento = get_object_or_404(Requerimiento, pk=pk)
    requerimiento.delete()
    if request.htmx:
        return HttpResponse("")
    messages.success(request, f"Requerimiento {requerimiento.folio} borrado.")
    return redirect("requerimientos:lista")
```

Ruta: `path("<int:pk>/borrar/", views.borrar, name="borrar"),`

En `_fila.html`, junto a Editar:

```html
    <button class="btn btn-sm btn-outline-danger"
            hx-post="{% url 'requerimientos:borrar' r.pk %}"
            hx-confirm="¿Borrar el requerimiento {{ r.folio }}?"
            hx-target="closest tr" hx-swap="outerHTML">Borrar</button>
```

El servidor responde vacío y la fila se reemplaza por nada: desaparece.

## 7. Patrón 4: edición en ventana modal (4 h)

Como `requerimiento_dialog.py`, pero en web. Es el patrón más completo: úsalo para repasar todo.

### El recorrido

1. Clic en **Editar** → `hx-get` pide el formulario → se coloca dentro de un `<dialog>` y se abre.
2. **Guardar** → `hx-post` envía el formulario.
3. **Si hay errores:** el servidor devuelve el formulario con errores → reemplaza el contenido del diálogo.
4. **Si se guardó:** el servidor responde `204` (sin contenido) con el encabezado `HX-Trigger: requerimiento-guardado`.
5. Ese **evento** hace dos cosas: cierra el diálogo y recarga la tabla con los filtros actuales.

### `base.html`, antes de `</body>`

```html
  <dialog id="modal" class="border-0 rounded shadow p-0" style="width: min(640px, 95vw)"
          hx-on:requerimiento-guardado="this.close()">
    <div id="modal-contenido"
         hx-on:htmx:after-swap="const m = document.getElementById('modal'); if (!m.open) m.showModal()">
    </div>
  </dialog>
```

`hx-on:evento="…"` ejecuta una línea cuando ocurre ese evento. Es todo el JavaScript de este módulo.

### Vista `formulario`

```python
def formulario(request, pk=None):
    requerimiento = get_object_or_404(Requerimiento, pk=pk) if pk else None
    form = RequerimientoForm(
        request.POST or None, request.FILES or None, instance=requerimiento
    )
    if request.method == "POST" and form.is_valid():
        guardado = form.save()
        if request.htmx:
            return HttpResponse(status=204, headers={"HX-Trigger": "requerimiento-guardado"})
        messages.success(request, f"Requerimiento {guardado.folio} guardado.")
        return redirect("requerimientos:lista")

    contexto = {"form": form, "requerimiento": requerimiento}
    if request.htmx:
        return render(request, "requerimientos/_form_modal.html", contexto)
    return render(request, "requerimientos/formulario.html", contexto)
```

### `_form_modal.html`

```html
<form method="post" enctype="multipart/form-data" class="p-4"
      hx-post="{{ request.path }}" hx-target="#modal-contenido">
  <h2 class="h5 mb-3">{% if requerimiento %}Editar {{ requerimiento }}{% else %}Nuevo requerimiento{% endif %}</h2>
  {% include "requerimientos/_campos.html" %}
  <button class="btn btn-primary">Guardar</button>
  <button type="button" class="btn btn-link" onclick="this.closest('dialog').close()">Cancelar</button>
</form>
```

Reutiliza `_campos.html` de M5: los errores se ven igual en página y en modal.

### Los botones

En `_fila.html`, el enlace Editar:

```html
    <a class="btn btn-sm btn-outline-primary" href="{% url 'requerimientos:editar' r.pk %}"
       hx-get="{% url 'requerimientos:editar' r.pk %}" hx-target="#modal-contenido">Editar</a>
```

En `lista.html`, el botón Nuevo:

```html
  <a class="btn btn-primary" href="{% url 'requerimientos:nuevo' %}"
     hx-get="{% url 'requerimientos:nuevo' %}" hx-target="#modal-contenido">Nuevo</a>
```

Y en `<form id="filtros">`, agrega el evento al `hx-trigger` para recargar la tabla al guardar:

```html
      hx-trigger="submit, input delay:300ms, requerimiento-guardado from:body"
```

Conservan `href`: sin HTMX (o con clic derecho → abrir en otra pestaña) siguen abriendo la página de M5.

## 8. Cómo depurar HTMX (1 h)

| Síntoma | Revisa |
|---|---|
| No pasa nada al dar clic | F12 → Consola: ¿se cargó `htmx.min.js`? (error 404) |
| 403 en la petición | Falta `hx-headers` con el token CSRF en `<body>` |
| La página completa aparece dentro de la tabla | La vista no está revisando `request.htmx` |
| La respuesta llega pero no se ve | `hx-target` apunta a un `id` que no existe |
| 405 | Usaste `hx-get` en una vista con `@require_POST` |

En la pestaña **Red**, las peticiones de HTMX llevan el encabezado `HX-Request: true`.

---

## Práctica

1. Agrega a la lista de M5: filtros sin recargar, búsqueda mientras escribes y paginación con `hx-boost`.
2. Cambio de estatus en línea.
3. Borrar con confirmación.
4. Alta y edición en ventana modal, con errores de validación dentro de la ventana.
5. Recarga con F5 en cualquier momento: la página debe verse bien y con los filtros de la URL.
6. Commit.

Compara tu resultado con `soluciones/mini_sscreq`. Sus pruebas automáticas (`python manage.py test`) describen cada comportamiento; léelas.

## Se domina cuando

Puedes señalar en la pestaña **Red** de F12 qué fragmento de HTML devolvió el servidor y en qué parte de la página quedó.
