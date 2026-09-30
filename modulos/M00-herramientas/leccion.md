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
mkdir C:\cursos\practica-m0
cd C:\cursos\practica-m0
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

```powershell
git init                  # convierte la carpeta en repositorio
git status                # qué cambió y qué está listo para guardar
git add archivo.py        # prepara un archivo para la foto
git add .                 # prepara todo
git commit -m "Mensaje"   # toma la foto
git log --oneline         # lista de fotos
git diff                  # cambios aún no preparados
```

Crea un archivo `.gitignore` con:

```
venv/
__pycache__/
*.sqlite3
.env
```

### Viajar en el tiempo

```powershell
git log --oneline                 # copia el código corto de un commit, p. ej. a1b2c3d
git diff a1b2c3d HEAD             # qué cambió desde ese commit hasta hoy
git restore archivo.py            # descarta cambios no guardados de un archivo
git switch --detach a1b2c3d       # mira el proyecto como estaba (solo lectura)
git switch main                   # regresa al presente
git revert a1b2c3d                # crea un commit nuevo que deshace ese commit
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
cd C:\cursos
git clone https://github.com/elliotTorrano/entrenamiento.git
```

Después de trabajar: `git add .`, `git commit -m "..."`, `git push`. Para traer cambios: `git pull`.

---

## Práctica

1. Crea `C:\cursos\practica-m0` con su `venv` y su `.gitignore`.
2. Crea `folios.py` con una línea: `print("SSC-001")`. Commit 1.
3. Cámbialo a `SSC-002`. Commit 2. Repite hasta tener **5 commits**.
4. Con `git diff` compara el commit 1 con el último y explica en voz alta qué cambió.
5. Haz un cambio que "rompa" algo, haz commit y después deshazlo con `git revert`.
6. Crea una rama, cambia algo, regresa a `main` y fusiónala.

## Se domina cuando

Puedes explicar qué cambió entre dos versiones usando `git diff` y deshacer un cambio sin perder trabajo.

## Cómo levantar la plataforma de estudio

Con lo aprendido ya puedes correr la plataforma de este repositorio (ver `README.md` en la raíz). Desde ahí marcas tu avance y haces las autoevaluaciones.
