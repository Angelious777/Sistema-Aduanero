# SCRIPT — NODO CENTRAL (SQL Server)

CREATE DATABASE nodo_central;
GO

USE nodo_central;
GO

-- =========================================================
-- TABLA: CLIENTE_GLOBAL
-- =========================================================

CREATE TABLE cliente_global (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),

    ci VARCHAR(30),
    direccion VARCHAR(200),
    email VARCHAR(100)
);

-- =========================================================
-- TABLA: ALMACEN
-- =========================================================

CREATE TABLE almacen (
    id_almacen INT IDENTITY(1,1) PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(50),
    direccion VARCHAR(200),

    nodo_responsable VARCHAR(20)
);

-- =========================================================
-- TABLA: ESTADO
-- =========================================================

CREATE TABLE estado (
    id_estado INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

-- =========================================================
-- TABLA: RUTA
-- =========================================================

CREATE TABLE ruta (
    id_ruta INT IDENTITY(1,1) PRIMARY KEY,

    origen VARCHAR(50),
    destino VARCHAR(50),

    descripcion TEXT
);

-- =========================================================
-- TABLA: PAQUETE_GLOBAL
-- =========================================================

CREATE TABLE paquete_global (
    id_paquete INT IDENTITY(1,1) PRIMARY KEY,

    codigo_rastreo VARCHAR(50) UNIQUE NOT NULL,

    id_cliente_remitente INT NOT NULL,
    id_cliente_destinatario INT NOT NULL,

    peso DECIMAL(10,2),
    volumen DECIMAL(10,2),

    prioridad VARCHAR(20),

    valor_declarado DECIMAL(12,2),
    costo_envio DECIMAL(12,2),
    seguro DECIMAL(12,2),

    id_estado_actual INT,
    id_ruta INT,

    id_almacen_origen INT,
    id_almacen_destino INT,
    id_almacen_actual INT,

    nodo_origen VARCHAR(20),

    fecha_registro DATETIME DEFAULT GETDATE(),

    FOREIGN KEY (id_cliente_remitente)
        REFERENCES cliente_global(id_cliente),

    FOREIGN KEY (id_cliente_destinatario)
        REFERENCES cliente_global(id_cliente),

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
-- TABLA: MOVIMIENTO_GLOBAL
-- =========================================================

CREATE TABLE movimiento_global (
    id_movimiento INT IDENTITY(1,1) PRIMARY KEY,

    id_paquete INT NOT NULL,

    descripcion VARCHAR(200),
    ubicacion VARCHAR(100),

    fecha_movimiento DATETIME DEFAULT GETDATE(),

    nodo_responsable VARCHAR(20),

    FOREIGN KEY (id_paquete)
        REFERENCES paquete_global(id_paquete)
);

-- =========================================================
-- TABLAS DE INFRAESTRUCTURA DISTRIBUIDA
-- =========================================================

CREATE TABLE catalogo_fragmentacion (
    id_fragmento INT IDENTITY(1,1) PRIMARY KEY,

    nombre_fragmento VARCHAR(100),
    nodo VARCHAR(50),
    motor_bd VARCHAR(50),

    tabla_base VARCHAR(50),
    tipo_fragmentacion VARCHAR(50)
);

CREATE TABLE log_sincronizacion (
    id_log INT IDENTITY(1,1) PRIMARY KEY,

    nodo_origen VARCHAR(20),
    operacion VARCHAR(100),

    tabla_afectada VARCHAR(100),

    fecha_log DATETIME DEFAULT GETDATE(),

    estado VARCHAR(30),
    mensaje VARCHAR(300)
);

CREATE TABLE cola_pendientes (
    id_pendiente INT IDENTITY(1,1) PRIMARY KEY,

    nodo_origen VARCHAR(20),

    operacion VARCHAR(50),
    tabla_afectada VARCHAR(50),

    id_registro INT,

    fecha_registro DATETIME DEFAULT GETDATE(),

    estado VARCHAR(30)
);

CREATE TABLE transacciones_distribuidas (
    id_transaccion INT IDENTITY(1,1) PRIMARY KEY,

    operacion VARCHAR(100),

    nodos_involucrados VARCHAR(100),

    fecha_inicio DATETIME DEFAULT GETDATE(),

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

INSERT INTO almacen(nombre, ciudad, direccion, nodo_responsable)
VALUES
('Almacén Central LP', 'La Paz', 'Zona Central', 'LP'),
('Almacén Central SCZ', 'Santa Cruz', 'Zona Industrial', 'SCZ');
GO

