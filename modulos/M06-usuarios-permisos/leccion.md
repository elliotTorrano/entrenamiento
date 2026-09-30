# M6. Usuarios, roles y permisos por dependencia

> **Borrador.** Este módulo es un temario. La lección completa se escribe cuando termines los módulos que requiere (M5), ajustada a tu avance y a tus notas.

**Objetivo:** Que cada persona vea y haga solo lo que le corresponde.

**Tiempo:** 14 h · **Requiere:** M5

## Temas

- Autenticación de Django: inicio y cierre de sesión, contraseñas.
- Grupos y permisos: superusuario, administradora general de la SSC, administrador y usuario.
- Filtrar por dependencia en la consulta (`queryset`), no solo esconder botones.
- Bitácora de cambios con `django-simple-history`, equivalente al historial de cambios actual.
- Concepto de inicio de sesión con Active Directory (LDAP), si Informática lo permite.

## En SSCReq

La regla "cada quien ve solo lo de su dependencia, excepto la administradora general" y el historial por campo.

## Práctica

Tres usuarios de dependencias distintas; comprobar que ninguno ve ni puede abrir por URL los requerimientos de otro.

## Se domina cuando

Puedes demostrar que escribir a mano la URL de un requerimiento ajeno devuelve 403 o 404.
