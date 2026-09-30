# M8. Cambios en vivo y edición simultánea

> **Borrador.** Este módulo es un temario. La lección completa se escribe cuando termines los módulos que requiere (M6, M7), ajustada a tu avance y a tus notas.

**Objetivo:** Conservar la característica más importante de SSCReq: varias personas trabajando a la vez y viendo los cambios casi al instante.

**Tiempo:** 10 h · **Requiere:** M6, M7

## Temas

- Tres niveles, de simple a completo: revisión periódica con `hx-trigger="every 5s"`, eventos del servidor (SSE) y WebSockets con Django Channels.
- Control de conflictos: avisar si otra persona guardó el mismo registro mientras se editaba (bloqueo optimista con fecha de modificación).
- Transacciones y `select_for_update` para folios consecutivos sin duplicados.

## En SSCReq

Hoy se revisa la fecha del archivo cada 5 segundos y se avisa del conflicto al guardar (`ConflictoEdicion`); en web se hace lo mismo, sin el problema del archivo en red.

## Práctica

Dos navegadores abiertos con usuarios distintos; lo que guarda uno aparece en el otro, y editar el mismo requerimiento a la vez produce el aviso.

## Se domina cuando

Puedes explicar cuándo basta la revisión periódica y cuándo conviene pasar a SSE o WebSockets.
