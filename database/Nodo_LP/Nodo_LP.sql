-- SCRIPT — NODO LA PAZ (PostgreSQL)


CREATE DATABASE nodo_lp;

\c nodo_lp;

-- =========================================================
-- TABLA: CLIENTE_PUBLICO
-- =========================================================

CREATE TABLE CLIENTE_PUBLICO (
    id_cliente UUID PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),

    telefono VARCHAR(20),

    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- =========================================================
-- TABLA: ALMACEN
-- =========================================================

CREATE TABLE almacen (
    id_almacen PRIMARY KEY,
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
    id_ruta PRIMARY KEY,

    id_almacen_origen INT NOT NULL,

    id_almacen_destino INT NOT NULL,

    descripcion VARCHAR(300),

    CONSTRAINT FK_RUTA_ORIGEN
        FOREIGN KEY (id_almacen_origen)
        REFERENCES almacen(id_almacen),

    CONSTRAINT FK_RUTA_DESTINO
        FOREIGN KEY (id_almacen_destino)
        REFERENCES almacen(id_almacen),

    CONSTRAINT UQ_RUTA
        UNIQUE(id_almacen_origen, id_almacen_destino)
);

-- =========================================================
-- TABLA: PAQUETE_OPERATIVO_LP
-- =========================================================

CREATE TABLE PAQUETE_OPERATIVO_LP (
    id_paquete UUID PRIMARY KEY,

    codigo_rastreo VARCHAR(30) NOT NULL UNIQUE,

    id_cliente_remitente UUID NOT NULL,

    id_cliente_destinatario UUID NOT NULL,

    id_estado INT NOT NULL,

    id_ruta INT NOT NULL,

    id_almacen_actual INT NOT NULL,

    peso NUMERIC(10,2),

    volumen NUMERIC(10,2),

    descripcion VARCHAR(300),

    prioridad VARCHAR(20),

    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT FK_POP_REMITENTE
        FOREIGN KEY (id_cliente_remitente)
        REFERENCES CLIENTE_PUBLICO(id_cliente),

    CONSTRAINT FK_POP_DESTINATARIO
        FOREIGN KEY (id_cliente_destinatario)
        REFERENCES CLIENTE_PUBLICO(id_cliente),

    CONSTRAINT FK_POP_ESTADO
        FOREIGN KEY (id_estado)
        REFERENCES ESTADO(id_estado),

    CONSTRAINT FK_POP_RUTA
        FOREIGN KEY (id_ruta)
        REFERENCES RUTA(id_ruta),

    CONSTRAINT FK_POP_ALMACEN
        FOREIGN KEY (id_almacen_actual)
        REFERENCES ALMACEN(id_almacen)
);

-- =========================================================
-- TABLA: PAQUETE_FINANCIERO_LP
-- =========================================================

CREATE TABLE PAQUETE_FINANCIERO_LP (
    id_paquete UUID PRIMARY KEY,

    valor_declarado NUMERIC(12,2),

    seguro NUMERIC(12,2),

    costo_envio NUMERIC(12,2),

    CONSTRAINT FK_PFP_OPERATIVO
        FOREIGN KEY (id_paquete)
        REFERENCES PAQUETE_OPERATIVO_LP(id_paquete)
);

-- =========================================================
-- TABLA: MOVIMIENTO_LP
-- =========================================================

CREATE TABLE MOVIMIENTO_LP (
    id_movimiento UUID PRIMARY KEY,

    id_paquete UUID NOT NULL,

    id_almacen INT NOT NULL,

    fecha_movimiento TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    observacion VARCHAR(300),

    CONSTRAINT FK_MLP_PAQUETE
        FOREIGN KEY (id_paquete)
        REFERENCES PAQUETE_OPERATIVO_LP(id_paquete),

    CONSTRAINT FK_MLP_ALMACEN
        FOREIGN KEY (id_almacen)
        REFERENCES ALMACEN(id_almacen)
);

-- =========================================================
-- TABLA: COLA_PENDIENTES
-- =========================================================

CREATE TABLE cola_pendientes (
    id_pendiente INT IDENTITY(1,1) PRIMARY KEY,

    nodo_origen VARCHAR(20),

    operacion VARCHAR(50),
    tabla_afectada VARCHAR(50),

    id_registro VARCHAR(50),

    fecha_registro DATETIME DEFAULT GETDATE(),

    estado VARCHAR(30)
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

INSERT INTO almacen(id_almacen,nombre, ciudad, direccion, nodo_responsable)
VALUES
(1,'Almacén Central LP', 'La Paz', 'Zona Central', 'LP');
