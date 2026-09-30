# Entrenamiento Django + HTMX

Programa de estudio para entender Django y HTMX lo suficiente para diseñar, leer, revisar y mantener la versión web de SSCReq.

- 13 módulos (M0 a M12) y un proyecto integrador, unas 212 h.
- Cada módulo se practica sobre un caso de SSCReq con **datos ficticios**.
- Cada módulo termina con una prueba concreta: **"Se domina cuando"**.

## Ruta

| Etapa | Módulos | Estado del material |
|---|---|---|
| 1. Bases | M0 Herramientas · M1 Python · M2 Web · M3 PostgreSQL | Lecciones completas |
| 2. Django | M4 Modelos · M5 Vistas y formularios · M6 Usuarios y permisos | M4 y M5 completas; M6 temario |
| 3. Interfaz y tiempo real | M7 HTMX · M8 Cambios en vivo · M9 Documentos | M7 completa; M8 y M9 temario |
| 4. Producción | M10 Seguridad · M11 Pruebas · M12 Despliegue | Temario |
| 5. Proyecto | mini-SSCReq web | Temario |

**Lo básico de Django + HTMX** es el camino M0 → M1 → M2 → M3 → M4 → M5 → M7. Los temarios se convierten en lecciones completas conforme avanzas, ajustadas a tus notas y dudas.

## Empezar

Requisitos: Python 3.12+ y Git (M0 explica cómo instalarlos). En PowerShell:

```powershell
cd C:\cursos
git clone https://github.com/elliotTorrano/entrenamiento.git
cd entrenamiento
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python plataforma\manage.py runserver
```

Abre http://127.0.0.1:8000.

La próxima vez solo necesitas:

```powershell
cd C:\cursos\entrenamiento
.\venv\Scripts\Activate.ps1
python plataforma\manage.py runserver
```

## La plataforma de estudio

Es una aplicación Django + HTMX que corre en tu computadora:

- **Ruta:** avance general, módulos por etapa y el siguiente paso recomendado.
- **Módulo:** la lección, los criterios "Se domina cuando" para marcar, la autoevaluación, tus notas y las horas que dedicas.
- Un módulo queda **dominado** cuando marcas todos sus criterios y apruebas la autoevaluación (80 %).

Todo se guarda en `progreso.json`. **Súbelo a Git** al terminar cada sesión:

```powershell
git add progreso.json practica
git commit -m "Avance M1"
git push
```

Así, en la siguiente sesión con Claude, el programa se ajusta a tu avance real, tus dudas y tu ritmo.

La plataforma también es material de estudio: en M7 puedes leer `plataforma/estudio/views.py` y sus plantillas para ver HTMX en un proyecto real (marcar criterios, responder preguntas y guardar notas sin recargar la página).

## Estructura

```
modulos/             lecciones, autoevaluaciones y ejercicios
plataforma/          la aplicación de estudio
practica/            tu trabajo (mini_sscreq desde M4)
soluciones/          mini_sscreq terminado al final de M7, para comparar
progreso.json        tu avance (se crea al usarse la plataforma)
```
