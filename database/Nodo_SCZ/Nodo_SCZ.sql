-- SCRIPT — NODO SANTA CRUZ (SQL Server)

CREATE DATABASE nodo_scz;
GO

USE nodo_scz;
GO

-- =========================================================
-- TABLA: CLIENTE_PUBLICO
-- =========================================================

CREATE TABLE CLIENTE_PUBLICO (
    id_cliente UNIQUEIDENTIFIER PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),

    telefono VARCHAR(20),

    fecha_registro DATETIME NOT NULL DEFAULT GETDATE()
);

-- =========================================================
-- TABLA: ALMACEN
-- =========================================================

CREATE TABLE almacen (
    id_almacen INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    direccion VARCHAR(200),
    nodo_responsable VARCHAR(20) NOT NULL
);

-- =========================================================
-- TABLA: ESTADO (REPLICA)
-- =========================================================

CREATE TABLE estado (
    id_estado INT IDENTITY(1,1) PRIMARY KEY,
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
-- TABLA: PAQUETE_OPERATIVO_SCZ
-- =========================================================

CREATE TABLE PAQUETE_OPERATIVO_SCZ (
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

    CONSTRAINT FK_POS_REMITENTE
        FOREIGN KEY (id_cliente_remitente)
        REFERENCES CLIENTE_PUBLICO(id_cliente),

    CONSTRAINT FK_POS_DESTINATARIO
        FOREIGN KEY (id_cliente_destinatario)
        REFERENCES CLIENTE_PUBLICO(id_cliente),

    CONSTRAINT FK_POS_ESTADO
        FOREIGN KEY (id_estado)
        REFERENCES ESTADO(id_estado),

    CONSTRAINT FK_POS_RUTA
        FOREIGN KEY (id_ruta)
        REFERENCES RUTA(id_ruta),

    CONSTRAINT FK_POS_ALMACEN
        FOREIGN KEY (id_almacen_actual)
        REFERENCES ALMACEN(id_almacen)
);

-- =========================================================
-- TABLA: PAQUETE_FINANCIERO_SCZ
-- =========================================================

CREATE TABLE PAQUETE_FINANCIERO_SCZ (
    id_paquete UNIQUEIDENTIFIER PRIMARY KEY,

    valor_declarado DECIMAL(12,2),

    seguro DECIMAL(12,2),

    costo_envio DECIMAL(12,2),

    CONSTRAINT FK_PFS_OPERATIVO
        FOREIGN KEY (id_paquete)
        REFERENCES PAQUETE_OPERATIVO_SCZ(id_paquete)
);

-- =========================================================
-- TABLA: MOVIMIENTO_SCZ
-- =========================================================

CREATE TABLE MOVIMIENTO_SCZ (
    id_movimiento UNIQUEIDENTIFIER PRIMARY KEY,

    id_paquete UNIQUEIDENTIFIER NOT NULL,

    id_almacen INT NOT NULL,

    fecha_movimiento DATETIME NOT NULL DEFAULT GETDATE(),

    observacion VARCHAR(300),

    CONSTRAINT FK_MSCZ_PAQUETE
        FOREIGN KEY (id_paquete)
        REFERENCES PAQUETE_OPERATIVO_SCZ(id_paquete),

    CONSTRAINT FK_MSCZ_ALMACEN
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
(2,'Almacén Central SCZ', 'Santa Cruz', 'Zona Industrial', 'SCZ');
GO
