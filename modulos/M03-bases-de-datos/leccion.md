# M3. Bases de datos relacionales y PostgreSQL

**Objetivo:** entender tablas, relaciones y transacciones, y por qué un servidor de base de datos resuelve lo que hoy falla con el archivo en red.

**Tiempo:** 14 h · **Requiere:** M1

---

## 1. Por qué un servidor de base de datos (1 h)

Hoy SSCReq usa SQLite cifrado en una carpeta compartida. Cada computadora abre **el mismo archivo** por la red:

- Si dos personas guardan a la vez, el archivo se bloquea o, en el peor caso, se daña.
- Por eso existe la revisión cada 5 segundos y el aviso de conflicto.

Con PostgreSQL hay **un solo programa** (el servidor de base de datos) que recibe todas las peticiones, las ordena y garantiza que no se pisen. Django habla con ese servidor; nadie abre el archivo directamente.

## 2. Tablas, claves e índices (3 h)

```
dependencias                    requerimientos
────────────                    ──────────────
id  │ nombre     │ formato      id │ folio         │ dependencia_id │ monto   │ estatus
────┼────────────┼──────────    ───┼───────────────┼────────────────┼─────────┼──────────
1   │ SSC        │ SSC-####/AAAA 1  │ SSC-0001/2026 │ 1              │ 1500.00 │ Pendiente
2   │ Tránsito   │ DGT/##/AAAA   2  │ DGT/01/2026   │ 2              │  800.00 │ Cancelado
```

- **Clave primaria (`id`)**: identifica cada fila; nunca se repite.
- **Clave foránea (`dependencia_id`)**: apunta al `id` de otra tabla. Así no se repite "SSC" en cada requerimiento, y si la dependencia cambia de nombre, cambia en un solo lugar.
- **Índice**: como el índice de un libro; acelera búsquedas por una columna (por ejemplo, `folio`).
- **Restricción `UNIQUE`**: impide folios duplicados a nivel de base, aunque el programa falle.

## 3. Instalar PostgreSQL (1 h)

1. Descarga el instalador de postgresql.org → Download → Windows (versión 16 o 17).
2. Instala con pgAdmin incluido. **Anota la contraseña** del usuario `postgres`.
3. Abre **pgAdmin** → Servers → PostgreSQL → clic derecho en Databases → Create → Database: `practica_m3`.
4. Clic derecho en `practica_m3` → **Query Tool**. Ahí escribirás SQL.

## 4. SQL (6 h)

### Crear tablas

```sql
CREATE TABLE dependencias (
    id      SERIAL PRIMARY KEY,
    nombre  VARCHAR(100) NOT NULL UNIQUE,
    formato VARCHAR(30)  NOT NULL
);
```

`SERIAL` = número que se asigna solo. `NOT NULL` = obligatorio.

### Insertar, consultar, actualizar

```sql
INSERT INTO dependencias (nombre, formato)
VALUES ('SSC', 'SSC-####/AAAA'), ('Tránsito', 'DGT/##/AAAA');

SELECT * FROM dependencias;
SELECT nombre FROM dependencias WHERE formato LIKE 'SSC%';

UPDATE dependencias SET formato = 'SSC-#####/AAAA' WHERE nombre = 'SSC';
```

> **Cuidado:** `UPDATE` o `DELETE` **sin `WHERE`** cambian o borran todas las filas.

### JOIN: unir tablas

```sql
SELECT r.folio, d.nombre AS dependencia, r.monto
FROM requerimientos r
JOIN dependencias d ON d.id = r.dependencia_id
WHERE r.estatus = 'Pendiente'
ORDER BY r.folio;
```

`JOIN` usa la clave foránea para traer el nombre de la dependencia junto al requerimiento.

### GROUP BY: totales

```sql
SELECT d.nombre, COUNT(*) AS cantidad, SUM(r.monto) AS total
FROM requerimientos r
JOIN dependencias d ON d.id = r.dependencia_id
GROUP BY d.nombre;
```

Agrupa las filas por dependencia y calcula una cifra por grupo. En Django esto será `annotate`.

## 5. Transacciones y concurrencia (2 h)

Una **transacción** agrupa varios cambios que deben pasar **todos o ninguno**:

```sql
BEGIN;
UPDATE presupuestos SET disponible = disponible - 1500 WHERE id = 1;
INSERT INTO requerimientos (...) VALUES (...);
COMMIT;      -- si algo falló antes, se usa ROLLBACK y nada cambia
```

**Caso SSCReq, folios consecutivos:** si dos personas piden "el siguiente folio" al mismo tiempo, ambas podrían recibir el 13. La solución (en M8, con `select_for_update`) es bloquear la fila del contador dentro de una transacción: la segunda persona espera milisegundos y recibe el 14.

## 6. Respaldos (1 h)

Desde una terminal (ajusta la ruta a tu versión de PostgreSQL):

```powershell
& "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe" -U postgres -F c -f respaldo.dump practica_m3
& "C:\Program Files\PostgreSQL\16\bin\pg_restore.exe" -U postgres -d practica_m3_copia respaldo.dump
```

(Antes de restaurar, crea la base vacía `practica_m3_copia` en pgAdmin.) Un respaldo que nunca se ha restaurado **no está probado**.

---

## Práctica

1. En pgAdmin, abre `practica/esquema.sql`, cópialo al Query Tool y ejecútalo (F5). Crea las tablas y datos ficticios.
2. Resuelve las consultas de `practica/consultas.sql`. Escribe cada una debajo de su enunciado.
3. Respalda `practica_m3` con `pg_dump`, crea `practica_m3_copia`, restaura y verifica que tiene los mismos datos.

Si todavía no instalas PostgreSQL, puedes practicar las consultas en https://sqliteonline.com eligiendo PostgreSQL.

## Se domina cuando

Puedes escribir sin ayuda la consulta "total de requerimientos no cancelados por dependencia".
