CREATE DATABASE nodo_scz;
GO

USE nodo_scz;
GO

-- =========================================================
-- TABLA: cliente_publico
-- =========================================================

CREATE TABLE cliente_publico (
    id_cliente UNIQUEIDENTIFIER PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),

    telefono VARCHAR(20),

    fecha_registro DATETIME NOT NULL DEFAULT GETDATE()
);

-- =========================================================
-- TABLA: almacen
-- =========================================================

CREATE TABLE almacen (
    id_almacen INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    direccion VARCHAR(200),
    nodo_responsable VARCHAR(20) NOT NULL
);

-- =========================================================
-- TABLA: estado
-- =========================================================

CREATE TABLE estado (
    id_estado INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

-- =========================================================
-- TABLA: ruta
-- =========================================================

CREATE TABLE ruta (
    id_ruta INT PRIMARY KEY,

    id_almacen_origen INT NOT NULL,

    id_almacen_destino INT NOT NULL,

    descripcion VARCHAR(300),

    CONSTRAINT fk_ruta_origen
        FOREIGN KEY (id_almacen_origen)
        REFERENCES almacen(id_almacen),

    CONSTRAINT fk_ruta_destino
        FOREIGN KEY (id_almacen_destino)
        REFERENCES almacen(id_almacen),

    CONSTRAINT uq_ruta
        UNIQUE(id_almacen_origen, id_almacen_destino)
);

-- =========================================================
-- TABLA: paquete_operativo_scz
-- =========================================================

CREATE TABLE paquete_operativo_scz (
    id_paquete UNIQUEIDENTIFIER PRIMARY KEY,

    codigo_rastreo VARCHAR(30) NOT NULL UNIQUE,

    id_cliente_remitente UNIQUEIDENTIFIER NOT NULL,

    id_cliente_destinatario UNIQUEIDENTIFIER NOT NULL,

    id_estado INT NOT NULL,

    id_ruta INT NOT NULL,

    id_almacen_actual INT NOT NULL,

    peso DECIMAL(10,2),

    volumen DECIMAL(10,2),

    descripcion VARCHAR(300),

    prioridad VARCHAR(20),

    fecha_registro DATETIME NOT NULL DEFAULT GETDATE(),

    CONSTRAINT fk_pos_remitente
        FOREIGN KEY (id_cliente_remitente)
        REFERENCES cliente_publico(id_cliente),

    CONSTRAINT fk_pos_destinatario
        FOREIGN KEY (id_cliente_destinatario)
        REFERENCES cliente_publico(id_cliente),

    CONSTRAINT fk_pos_estado
        FOREIGN KEY (id_estado)
        REFERENCES estado(id_estado),

    CONSTRAINT fk_pos_ruta
        FOREIGN KEY (id_ruta)
        REFERENCES ruta(id_ruta),

    CONSTRAINT fk_pos_almacen
        FOREIGN KEY (id_almacen_actual)
        REFERENCES almacen(id_almacen)
);

-- =========================================================
-- TABLA: paquete_financiero_scz
-- =========================================================

CREATE TABLE paquete_financiero_scz (
    id_paquete UNIQUEIDENTIFIER PRIMARY KEY,

    valor_declarado DECIMAL(12,2),

    seguro DECIMAL(12,2),

    costo_envio DECIMAL(12,2),

    CONSTRAINT fk_pfs_operativo
        FOREIGN KEY (id_paquete)
        REFERENCES paquete_operativo_scz(id_paquete)
);

-- =========================================================
-- TABLA: movimiento_scz
-- =========================================================

CREATE TABLE movimiento_scz (
    id_movimiento UNIQUEIDENTIFIER PRIMARY KEY,

    id_paquete UNIQUEIDENTIFIER NOT NULL,

    id_almacen INT NOT NULL,

    fecha_movimiento DATETIME NOT NULL DEFAULT GETDATE(),

    observacion VARCHAR(300),

    CONSTRAINT fk_mscz_paquete
        FOREIGN KEY (id_paquete)
        REFERENCES paquete_operativo_scz(id_paquete),

    CONSTRAINT fk_mscz_almacen
        FOREIGN KEY (id_almacen)
        REFERENCES almacen(id_almacen)
);

-- =========================================================
-- TABLA: cola_pendientes
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

INSERT INTO estado(id_estado, nombre) VALUES
(1, 'Registrado'),
(2, 'En almacén'),
(3, 'En tránsito'),
(4, 'Llegó a destino'),
(5, 'Entregado');

INSERT INTO almacen(id_almacen, nombre, ciudad, direccion, nodo_responsable)
VALUES
(2, 'Almacén Central SCZ', 'Santa Cruz', 'Zona Industrial', 'SCZ');
GO