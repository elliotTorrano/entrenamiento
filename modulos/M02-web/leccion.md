# M2. Cómo funciona la web

**Objetivo:** entender la diferencia de fondo con el programa de escritorio: en web, **cada clic es una petición al servidor y una respuesta**.

**Tiempo:** 12 h · **Requiere:** M0

---

## 1. Cliente, servidor, petición y respuesta (2 h)

En SSCReq de escritorio, el programa y sus pantallas viven en tu computadora y leen la base directo de la carpeta de red.

En web:

```
Navegador (cliente)                         Servidor (Django)
───────────────────                         ─────────────────
1. Escribes una URL o das clic   ──petición──▶  2. Lee qué pides
                                                3. Consulta la base
5. Dibuja la página              ◀─respuesta──  4. Arma el HTML
```

- El **navegador nunca toca la base de datos**. Solo el servidor.
- Entre una petición y otra el servidor **no recuerda nada** por sí mismo (ver cookies abajo).
- Todos los usuarios ven la misma versión del programa: se actualiza una vez, en el servidor.

### Anatomía de una URL

```
https://sscreq.celaya.local:8000/requerimientos/?estatus=Pendiente&page=2
└─┬─┘   └────────┬─────────┘ └┬─┘└──────┬──────┘ └───────────┬──────────┘
protocolo     servidor      puerto    ruta            parámetros (query string)
```

## 2. HTTP: métodos y códigos (3 h)

| Método | Uso | Ejemplo en SSCReq |
|---|---|---|
| `GET` | **Consultar**. No debe cambiar nada. | Ver la lista, filtrar, abrir un requerimiento |
| `POST` | **Guardar o cambiar**. | Alta, edición, cambio de estatus, borrar |

Regla: si una acción cambia datos, es `POST`. Un `GET` se puede repetir, guardar en favoritos o recargar sin consecuencias.

| Código | Significa | Cuándo lo verás |
|---|---|---|
| 200 | OK | La página cargó bien |
| 302 | Redirección | Después de guardar: "ve a la lista" |
| 403 | Prohibido | Intentas abrir algo que no te toca |
| 404 | No encontrado | La URL o el registro no existe |
| 500 | Error del servidor | Un error en el código de Python |

**Patrón Post/Redirect/Get:** después de guardar con `POST`, el servidor responde `302` a la lista. Así, si recargas la página, no se guarda dos veces.

## 3. Cookies y sesiones (1 h)

¿Cómo sabe el servidor quién eres si "no recuerda nada"?

1. Inicias sesión con `POST` (usuario y contraseña).
2. El servidor guarda "sesión abc123 = Elliot" y responde con una **cookie** `sessionid=abc123`.
3. El navegador envía esa cookie **en cada petición siguiente**.
4. El servidor lee la cookie y sabe que eres tú.

Por eso cerrar sesión borra la sesión en el servidor, y por eso la cookie nunca debe compartirse.

## 4. HTML (3 h)

HTML describe **qué hay** en la página. Etiquetas que usarás siempre:

```html
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Requerimientos</title>
</head>
<body>
  <h1>Requerimientos</h1>
  <p>Texto normal. <a href="/requerimientos/nuevo/">Un enlace</a></p>

  <table>
    <thead>
      <tr><th>Folio</th><th>Dependencia</th><th>Estatus</th></tr>
    </thead>
    <tbody>
      <tr><td>SSC-0001/2026</td><td>SSC</td><td>Pendiente</td></tr>
    </tbody>
  </table>
</body>
</html>
```

### Formularios

```html
<form method="post" action="/requerimientos/nuevo/">
  <label for="folio">Folio</label>
  <input id="folio" name="folio" required>

  <label for="dependencia">Dependencia</label>
  <select id="dependencia" name="dependencia">
    <option value="1">SSC</option>
    <option value="2">Tránsito</option>
  </select>

  <label for="monto">Monto</label>
  <input id="monto" name="monto" type="number" step="0.01" min="0">

  <label for="descripcion">Descripción</label>
  <textarea id="descripcion" name="descripcion"></textarea>

  <button type="submit">Guardar</button>
</form>
```

- `name` es lo que viaja al servidor: `folio=SSC-0001/2026&dependencia=1&monto=1500`.
- `method="post"` → los datos van en el cuerpo de la petición. Con `get` irían en la URL.
- `required`, `min`, `type="number"` validan en el navegador, pero **el servidor siempre valida de nuevo**: cualquiera puede saltarse el navegador.

## 5. CSS y Bootstrap (1 h)

CSS define **cómo se ve**. No lo vas a dominar; vas a usar Bootstrap, que ya trae estilos listos con clases:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">

<table class="table table-striped table-hover">...</table>
<button class="btn btn-primary">Guardar</button>
<span class="badge text-bg-warning">Pendiente</span>
<input class="form-control">
```

## 6. Herramientas del navegador: F12 (2 h)

Es tu herramienta principal para entender qué pasa. En Chrome o Edge, presiona **F12**:

- **Red (Network):** cada petición, su método, código y lo que se envió y recibió. Marca *Preserve log* para no perderlas al cambiar de página.
- **Consola (Console):** errores de JavaScript (útil en M7 con HTMX).
- **Elementos (Elements):** el HTML actual de la página; puedes editarlo en vivo para probar.

---

## Práctica

1. Abre `practica/requerimientos.html` en el navegador (doble clic). Tiene la estructura pero le faltan cosas.
2. Completa lo marcado con `TODO`:
   - 3 filas más en la tabla, con datos ficticios.
   - Los campos que faltan en el formulario de alta.
   - Clases de Bootstrap para que se vea ordenado.
3. Guarda, recarga el navegador y revisa el resultado.
4. Abre F12 → **Red**, marca *Preserve log*, llena el formulario y presiona **Guardar**.
   - Busca la petición (dirá error porque no hay servidor; es normal).
   - Revisa **Payload**: ahí están los `name=valor` que enviaste.
5. Cambia `method="post"` por `method="get"`, guarda y repite. Observa que ahora los datos aparecen en la URL.

## Se domina cuando

Puedes seguir en la pestaña **Red** de F12 qué se envía al guardar un formulario, y explicar por qué guardar usa `POST` y filtrar usa `GET`.
