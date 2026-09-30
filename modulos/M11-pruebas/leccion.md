# M11. Pruebas automáticas

> **Borrador.** Este módulo es un temario. La lección completa se escribe cuando termines los módulos que requiere (M6), ajustada a tu avance y a tus notas.

**Objetivo:** Que cada cambio se pueda comprobar en segundos sin probar todo a mano.

**Tiempo:** 8 h · **Requiere:** M6

## Temas

- `pytest-django`: probar modelos, vistas y permisos.
- Datos de prueba generados (fixtures o factories), nunca datos reales.
- Qué vale la pena probar: reglas de negocio, permisos por dependencia, cálculos de dinero.

## En SSCReq

Reglas como "un requerimiento cancelado cuenta 0" o "nadie ve lo de otra dependencia" se vuelven pruebas que corren solas antes de cada versión.

## Práctica

Pruebas para la validación de folio, la regla de cancelado en cero y el filtro por dependencia de M6.

## Se domina cuando

Rompes a propósito una regla y una prueba lo detecta.
