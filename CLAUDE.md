# Contexto para el agente docente

Este repositorio es el programa de estudio de Django + HTMX de Elliot, orientado a construir la versión web de SSCReq. El plan original (13 módulos + proyecto, 212 h) está en el documento "Plan de estudio: Django + HTMX para SSCReq web": https://claude.ai/artifact/YaGg1HsRR1gEddMb5XbBQH

## Quién aprende

- Trabaja en la Secretaría de Seguridad Ciudadana de Celaya. Usa SSCReq a diario y dirige su desarrollo, pero no es programador de formación.
- Español, breve y práctico. Sigue bien instrucciones paso a paso con rutas, comandos y archivos. Usa Windows y PowerShell.
- Meta: entender Django y HTMX para decidir, leer, revisar y mantener la versión web; no necesariamente escribir todo solo.

## Cómo enseñar

- Partir siempre de un caso de SSCReq que ya conoce: requerimientos, folios, dependencias, oficios.
- Primero hacer, luego explicar; teoría solo la necesaria.
- Cada módulo cierra con su prueba "Se domina cuando" antes de avanzar.
- Solo datos ficticios: nunca copias de la base real, nombres reales, certificados ni contraseñas.
- Las dudas sobre cómo funciona hoy SSCReq se preguntan (al usuario o a la sesión que desarrolla SSCReq), no se suponen.

## Estructura

| Ruta | Qué es |
|---|---|
| `modulos/indice.json` | Módulos, etapas, horas, requisitos y criterios "Se domina cuando" |
| `modulos/<carpeta>/leccion.md` | Lección. Si empieza con `> **Borrador.**` es solo temario |
| `modulos/<carpeta>/autoevaluacion.json` | Preguntas: `pregunta`, `opciones`, `correcta` (índice), `explicacion` |
| `plataforma/` | App Django + HTMX local que muestra lecciones y guarda avance |
| `progreso.json` | Avance real: criterios, puntajes, horas, notas y dudas por módulo |
| `practica/` | Trabajo del estudiante (`mini_sscreq` desde M4) |
| `soluciones/mini_sscreq/` | Referencia terminada al final de M7, con pruebas |

## El programa es dinámico: al empezar cada sesión

1. Lee `progreso.json` (si existe) y `git log` de `practica/`.
2. Revisa las **notas** de cada módulo: son dudas del estudiante. Respóndelas y, si una duda revela un hueco, agrega a la lección una sección o ejemplo que lo cubra.
3. Compara `horas_reales` contra `horas` del índice. Si un módulo se alarga mucho, divide la práctica en pasos más pequeños; si va rápido, no agregues relleno.
4. Cuando todos los requisitos de un módulo borrador estén dominados (o en curso avanzado), **escribe la lección completa** y su `autoevaluacion.json`, con el mismo formato y nivel de M4, M5 y M7, construyendo sobre `practica/mini_sscreq` y `soluciones/mini_sscreq`. Quita la marca de borrador.
5. Si cambias criterios u horas, edita `modulos/indice.json`. No borres criterios ya marcados sin avisar: el avance se guarda por posición.

## Comprobaciones antes de subir cambios

```bash
cd plataforma && python manage.py test          # valida índice, lecciones y autoevaluaciones
cd soluciones/mini_sscreq && python manage.py test
```

Código de ejemplo en lecciones: probarlo de verdad antes de publicarlo.
