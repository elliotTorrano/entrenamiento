# M0. Herramientas de trabajo

**Objetivo:** tener un entorno donde crear, correr y guardar versiones de un proyecto sin miedo a romper nada.

**Tiempo:** 8 h · **Requiere:** nada

---

## 1. Qué vas a instalar (1 h)

| Herramienta | Para qué | Dónde |
|---|---|---|
| Python 3.12 o 3.13 | El lenguaje de Django | python.org → Downloads. Marca **"Add python.exe to PATH"** |
| VS Code | Editor | code.visualstudio.com |
| Extensión *Python* (Microsoft) | Colores, errores y depuración | VS Code → Extensiones (Ctrl+Shift+X) |
| Git | Guardar versiones | git-scm.com → instalador con opciones por omisión |

Comprueba en una terminal nueva:

```powershell
python --version
git --version
```

Si alguno dice "no se reconoce como comando", cierra y abre la terminal. Si sigue igual, reinstala marcando la opción de PATH.

## 2. La terminal (1 h)

En VS Code: **Terminal → New Terminal** (Ctrl+ñ). Es PowerShell.

| Comando | Qué hace |
|---|---|
| `pwd` | Muestra en qué carpeta estás |
| `ls` | Lista lo que hay en la carpeta |
| `cd carpeta` | Entra a una carpeta |
| `cd ..` | Sube un nivel |
| `mkdir nombre` | Crea una carpeta |
| Tecla ↑ | Repite comandos anteriores |
| Tab | Completa nombres de archivos |

**Leer un error:** en Python el error útil está **al final**. La última línea dice *qué* pasó (`NameError`, `ModuleNotFoundError`…) y las líneas de arriba dicen *dónde* (archivo y número de línea).

## 3. Entornos virtuales (1.5 h)

Cada proyecto tiene sus propias librerías y versiones, igual que la carpeta `venv` de SSCReq. Así actualizar Django en un proyecto no rompe otro.

```powershell
cd ~
mkdir practica-m0
cd practica-m0
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloquea el script, ejecuta una sola vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Cuando el entorno está activo verás `(venv)` al inicio de la línea. Ahora:

```powershell
pip install requests
pip list
pip freeze > requirements.txt
deactivate
```

`requirements.txt` es la "lista de compras" del proyecto: otra persona reconstruye el mismo entorno con `pip install -r requirements.txt`.

> **Regla:** la carpeta `venv` nunca se sube a Git. Se reconstruye.

## 4. Git (4 h)

Git guarda fotos (*commits*) de tu proyecto. Puedes ver qué cambió entre fotos y regresar a cualquiera.

### Primera vez

```powershell
git config --global user.name "Tu Nombre"
git config --global user.email "tu@correo.com"
```

### Ciclo básico

Estos son los comandos que usarás siempre. En la práctica los usas paso a paso con archivos reales; aquí solo léelos:

```powershell
git init -b main          # convierte la carpeta en repositorio, con la rama principal llamada main
git status                # qué cambió y qué está listo para guardar
git add folios.py         # prepara un archivo para la foto
git add .                 # prepara todos los archivos
git commit -m "Mensaje"   # toma la foto
git log --oneline         # lista de fotos
git diff                  # cambios aún no preparados
```

> Si un comando como `git log` termina con `:` y no regresa a la terminal, presiona **q** para salir.

### Viajar en el tiempo

```powershell
git log --oneline                 # copia el código corto de un commit, p. ej. a1b2c3d
git diff a1b2c3d HEAD             # qué cambió desde ese commit hasta hoy
git restore folios.py             # descarta cambios no guardados de un archivo
git switch --detach a1b2c3d       # mira el proyecto como estaba (solo lectura)
git switch main                   # regresa al presente
git revert --no-edit a1b2c3d      # crea un commit nuevo que deshace ese commit
```

`git revert` es la forma segura de deshacer: **no borra historia**, agrega una corrección. Por eso no se pierde trabajo.

### Ramas

Una rama es una línea de trabajo paralela. Como tener **Beta** y **producción** de SSCReq:

```powershell
git switch -c prueba-folio   # crea la rama y entra
# ... cambios y commits ...
git switch main
git merge prueba-folio       # trae los cambios a main
```

### GitHub

Este mismo repositorio (`entrenamiento`) ya está en GitHub. Para bajarlo a tu computadora:

```powershell
cd ~
git clone https://github.com/elliotTorrano/entrenamiento.git
```

`~` es tu carpeta de usuario (por ejemplo `C:\Users\Elliot_user`).

Después de trabajar: `git add .`, `git commit -m "..."`, `git push`. Para traer cambios: `git pull`.

---

## Práctica

Es un proyecto pequeño solo para ensayar Git. Va en su propia carpeta, **fuera** de `entrenamiento`, para no meter un repositorio dentro de otro. Todos los comandos son en PowerShell.

### Paso 1. Crear la carpeta y su entorno virtual

Si ya la creaste en la sección 3, solo entra a ella y activa el `venv` (las dos últimas líneas).

```powershell
cd ~
mkdir practica-m0
cd practica-m0
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Paso 2. Crear el repositorio y el `.gitignore`

```powershell
git init -b main
Set-Content .gitignore "venv/", "__pycache__/", "*.sqlite3", ".env"
git status
```

`Set-Content` crea un archivo de texto; cada texto entre comillas es una línea. `git status` debe mostrar solo `.gitignore` en rojo: la carpeta `venv` ya no aparece porque Git la ignora.

### Paso 3. Crear `folios.py` y el commit 1

```powershell
Set-Content folios.py 'print("SSC-001")'
python folios.py
git add .
git commit -m "Primer folio"
```

`python folios.py` debe imprimir `SSC-001`.

También puedes crear y editar archivos en VS Code: `code .` abre la carpeta; en el panel izquierdo usa el ícono **Nuevo archivo**. Guarda con Ctrl+S.

### Paso 4. Commits 2 a 5

Repite cuatro veces, cambiando el número cada vez (`SSC-002`, `SSC-003`, …):

```powershell
Set-Content folios.py 'print("SSC-002")'
git diff
git add .
git commit -m "Folio 002"
```

Antes de cada `git add`, `git diff` te muestra el cambio: en rojo con `-` lo que se quitó, en verde con `+` lo que se agregó.

Al final:

```powershell
git log --oneline
```

Debes ver 5 commits, el más reciente arriba.

### Paso 5. Comparar versiones

Copia de `git log --oneline` el código del commit **más antiguo** (el de hasta abajo, por ejemplo `a1b2c3d`):

```powershell
git diff a1b2c3d HEAD
```

`HEAD` significa "la versión actual". Explica en voz alta qué cambió entre ambas.

### Paso 6. Romper algo y deshacerlo

```powershell
Set-Content folios.py 'print("SSC-005"'
python folios.py
```

Falta un paréntesis: Python marca `SyntaxError`. Guarda el error de todos modos:

```powershell
git add .
git commit -m "Cambio con error"
git log --oneline
```

Copia el código de ese último commit y deshazlo:

```powershell
git revert --no-edit <codigo>
python folios.py
git log --oneline
```

`folios.py` vuelve a funcionar y el log muestra **los dos** commits: el del error y el que lo corrige. No se perdió nada.

### Paso 7. Ramas

```powershell
git switch -c prueba-folio
Set-Content folios.py 'print("SSC-0006/2026")'
git add .
git commit -m "Nuevo formato de folio"
git switch main
python folios.py
git merge prueba-folio
python folios.py
```

El primer `python folios.py` en `main` todavía imprime el formato viejo: el cambio vive solo en la rama. Después de `git merge` ya imprime `SSC-0006/2026`.

## Se domina cuando

Puedes explicar qué cambió entre dos versiones usando `git diff` y deshacer un cambio sin perder trabajo.

## Cómo levantar la plataforma de estudio

Con lo aprendido ya puedes correr la plataforma de este repositorio (ver `README.md` en la raíz). Desde ahí marcas tu avance y haces las autoevaluaciones.
