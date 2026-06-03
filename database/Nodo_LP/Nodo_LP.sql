# SCRIPT — NODO LA PAZ (PostgreSQL)


CREATE DATABASE nodo_lp;

\c nodo_lp;

-- =========================================================
-- TABLA: CLIENTE_PUBLICO
-- =========================================================

CREATE TABLE cliente_publico (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20)
);

-- =========================================================
-- TABLA: ALMACEN
-- =========================================================

CREATE TABLE almacen (
    id_almacen SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    direccion VARCHAR(200),
    nodo_responsable VARCHAR(20) NOT NULL
);

-- =========================================================
-- TABLA: ESTADO (REPLICA)
-- =========================================================

CREATE TABLE estado (
    id_estado SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

-- =========================================================
-- TABLA: RUTA (REPLICA)
-- =========================================================

CREATE TABLE ruta (
    id_ruta SERIAL PRIMARY KEY,
    origen VARCHAR(50) NOT NULL,
    destino VARCHAR(50) NOT NULL,
    descripcion TEXT
);

-- =========================================================
-- TABLA: PAQUETE_OPERATIVO_LP
-- =========================================================

CREATE TABLE paquete_operativo_lp (
    id_paquete SERIAL PRIMARY KEY,
    codigo_rastreo VARCHAR(50) UNIQUE NOT NULL,

    id_cliente_remitente INT NOT NULL,
    id_cliente_destinatario INT NOT NULL,

    peso DECIMAL(10,2),
    volumen DECIMAL(10,2),
    prioridad VARCHAR(20),

    id_estado_actual INT,
    id_ruta INT,

    id_almacen_origen INT,
    id_almacen_destino INT,
    id_almacen_actual INT,

    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    nodo_origen VARCHAR(20) DEFAULT 'LP',

    FOREIGN KEY (id_cliente_remitente)
        REFERENCES cliente_publico(id_cliente),

    FOREIGN KEY (id_cliente_destinatario)
        REFERENCES cliente_publico(id_cliente),

    FOREIGN KEY (id_estado_actual)
        REFERENCES estado(id_estado),

    FOREIGN KEY (id_ruta)
        REFERENCES ruta(id_ruta),

    FOREIGN KEY (id_almacen_origen)
        REFERENCES almacen(id_almacen),

    FOREIGN KEY (id_almacen_destino)
        REFERENCES almacen(id_almacen),

    FOREIGN KEY (id_almacen_actual)
        REFERENCES almacen(id_almacen)
);

-- =========================================================
-- TABLA: PAQUETE_FINANCIERO_LP
-- =========================================================

CREATE TABLE paquete_financiero_lp (
    id_paquete INT PRIMARY KEY,

    valor_declarado DECIMAL(12,2),
    costo_envio DECIMAL(12,2),
    seguro DECIMAL(12,2),

    FOREIGN KEY (id_paquete)
        REFERENCES paquete_operativo_lp(id_paquete)
);

-- =========================================================
-- TABLA: MOVIMIENTO_LP
-- =========================================================

CREATE TABLE movimiento_lp (
    id_movimiento SERIAL PRIMARY KEY,

    id_paquete INT NOT NULL,

    descripcion VARCHAR(200) NOT NULL,
    ubicacion VARCHAR(100),

    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    nodo_responsable VARCHAR(20) DEFAULT 'LP',

    FOREIGN KEY (id_paquete)
        REFERENCES paquete_operativo_lp(id_paquete)
);

-- =========================================================
-- DATOS BASE
-- =========================================================

INSERT INTO estado(nombre) VALUES
('Registrado'),
('En almacén'),
('En tránsito'),
('Llegó a destino'),
('Entregado');

INSERT INTO almacen(nombre, ciudad, direccion, nodo_responsable)
VALUES
('Almacén Central LP', 'La Paz', 'Zona Central', 'LP');
