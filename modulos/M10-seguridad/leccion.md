# M10. Seguridad y datos personales

> **Borrador.** Este módulo es un temario. La lección completa se escribe cuando termines los módulos que requiere (M6), ajustada a tu avance y a tus notas.

**Objetivo:** Reconocer los errores de seguridad más comunes en web y cómo Django ayuda a evitarlos.

**Tiempo:** 8 h · **Requiere:** M6

## Temas

- Los riesgos principales: control de acceso roto, inyección SQL, XSS y CSRF, y qué protege Django por omisión.
- Configuración de producción: `DEBUG=False`, `SECRET_KEY` fuera del código, `ALLOWED_HOSTS`, HTTPS.
- Contraseñas, bloqueo tras intentos fallidos, cierre por inactividad (hoy existe en SSCReq).
- Bitácora de consultas a expedientes y salarios; aviso de privacidad.

## Práctica

Correr `manage.py check --deploy` sobre el proyecto de práctica y corregir cada advertencia.

## Se domina cuando

Puedes explicar por qué esconder un botón no es un permiso, y dónde debe ir la validación real.
