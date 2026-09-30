-- Práctica M3: tablas y datos ficticios.
-- Ejecuta todo en pgAdmin (Query Tool, F5) sobre la base practica_m3.

DROP TABLE IF EXISTS requerimientos;
DROP TABLE IF EXISTS proveedores;
DROP TABLE IF EXISTS dependencias;

CREATE TABLE dependencias (
    id      SERIAL PRIMARY KEY,
    nombre  VARCHAR(100) NOT NULL UNIQUE,
    formato VARCHAR(30)  NOT NULL
);

CREATE TABLE proveedores (
    id     SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    rfc    VARCHAR(13)  NOT NULL UNIQUE
);

CREATE TABLE requerimientos (
    id             SERIAL PRIMARY KEY,
    folio          VARCHAR(30)   NOT NULL UNIQUE,
    dependencia_id INTEGER       NOT NULL REFERENCES dependencias(id),
    proveedor_id   INTEGER       REFERENCES proveedores(id),
    descripcion    TEXT          NOT NULL DEFAULT '',
    monto          NUMERIC(12,2) NOT NULL CHECK (monto >= 0),
    estatus        VARCHAR(20)   NOT NULL DEFAULT 'Pendiente'
                   CHECK (estatus IN ('Pendiente', 'Autorizado', 'Pagado', 'Cancelado')),
    fecha          DATE          NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX idx_requerimientos_estatus ON requerimientos (estatus);

INSERT INTO dependencias (nombre, formato) VALUES
    ('SSC',        'SSC-####/AAAA'),
    ('Tránsito',   'DGT/##/AAAA'),
    ('Protección Civil', 'PC-###-AAAA');

INSERT INTO proveedores (nombre, rfc) VALUES
    ('Papelería Ficticia S.A. de C.V.',  'PFI010101AAA'),
    ('Llantas Imaginarias S.A.',         'LIM020202BBB'),
    ('Uniformes de Prueba S. de R.L.',   'UPR030303CCC');

INSERT INTO requerimientos (folio, dependencia_id, proveedor_id, descripcion, monto, estatus, fecha) VALUES
    ('SSC-0001/2026', 1, 1, 'Hojas y tóner',          1500.00, 'Pagado',     '2026-01-15'),
    ('SSC-0002/2026', 1, 3, 'Uniformes operativos',  48000.00, 'Autorizado', '2026-02-03'),
    ('SSC-0003/2026', 1, 2, 'Llantas patrulla 12',    9800.50, 'Cancelado',  '2026-02-20'),
    ('SSC-0004/2026', 1, 1, 'Carpetas',                 640.00, 'Pendiente',  '2026-03-01'),
    ('DGT/01/2026',   2, 2, 'Llantas grúa',           12500.00, 'Autorizado', '2026-01-22'),
    ('DGT/02/2026',   2, 1, 'Formatos de infracción',  3200.00, 'Cancelado',  '2026-02-11'),
    ('DGT/03/2026',   2, 3, 'Chalecos reflejantes',    7400.00, 'Pendiente',  '2026-03-09'),
    ('PC-001-2026',   3, 3, 'Equipo de protección',   15300.00, 'Pagado',     '2026-01-30'),
    ('PC-002-2026',   3, NULL, 'Por cotizar',              0.00, 'Pendiente',  '2026-03-12');
