# M12. Despliegue

> **Borrador.** Este módulo es un temario. La lección completa se escribe cuando termines los módulos que requiere (M10, M11), ajustada a tu avance y a tus notas.

**Objetivo:** Entender cómo se pone en marcha y se mantiene el sistema en un servidor.

**Tiempo:** 16 h · **Requiere:** M10, M11

## Temas

- Linux básico: usuarios, permisos, servicios, registros.
- Docker y `docker compose`: la aplicación, PostgreSQL y el servidor web en contenedores iguales en pruebas y producción.
- Gunicorn o Uvicorn detrás de Nginx; archivos estáticos.
- Variables de entorno, respaldos automáticos de PostgreSQL y cómo restaurarlos.
- Entorno de pruebas y entorno de producción, como hoy Beta y producción.

## Práctica

Levantar el proyecto con `docker compose` en una máquina virtual, respaldar la base, borrarla y restaurarla.

## Se domina cuando

Puedes publicar una versión nueva y regresar a la anterior si algo falla.
