-- SCRIPT — NODO CENTRAL (SQL Server)

CREATE DATABASE nodo_central;
GO

USE nodo_central;
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
-- TABLA: CLIENTE_PRIVADO
-- =========================================================

CREATE TABLE CLIENTE_PRIVADO (
    id_cliente UNIQUEIDENTIFIER PRIMARY KEY,

    documento_identidad VARCHAR(30) NOT NULL UNIQUE,

    direccion VARCHAR(250),

    email VARCHAR(100) UNIQUE,

    CONSTRAINT FK_CLIENTE_PRIVADO
        FOREIGN KEY (id_cliente)
        REFERENCES CLIENTE_PUBLICO(id_cliente)
);

-- =========================================================
-- TABLA: CLIENTE_PRIVADO
-- =========================================================

CREATE VIEW CLIENTE_GLOBAL
AS
SELECT
    cp.id_cliente,
    cp.nombre,
    cp.apellido_paterno,
    cp.apellido_materno,
    cp.telefono,
    cp.fecha_registro,

    cv.documento_identidad,
    cv.direccion,
    cv.email

FROM CLIENTE_PUBLICO cp
INNER JOIN CLIENTE_PRIVADO cv
    ON cp.id_cliente = cv.id_cliente;


-- =========================================================
-- TABLA: ALMACEN
-- =========================================================

CREATE TABLE almacen (
    id_almacen INT PRIMARY KEY,

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
    id_ruta INT PRIMARY KEY,

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
-- TABLA: PAQUETE_GLOBAL
-- =========================================================

CREATE TABLE PAQUETE_GLOBAL (
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

    valor_declarado DECIMAL(12,2),

    seguro DECIMAL(12,2),

    costo_envio DECIMAL(12,2),

    fecha_registro DATETIME NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_PG_REMITENTE
        FOREIGN KEY (id_cliente_remitente)
        REFERENCES CLIENTE_PUBLICO(id_cliente),

    CONSTRAINT FK_PG_DESTINATARIO
        FOREIGN KEY (id_cliente_destinatario)
        REFERENCES CLIENTE_PUBLICO(id_cliente),

    CONSTRAINT FK_PG_ESTADO
        FOREIGN KEY (id_estado)
        REFERENCES ESTADO(id_estado),

    CONSTRAINT FK_PG_RUTA
        FOREIGN KEY (id_ruta)
        REFERENCES RUTA(id_ruta),

    CONSTRAINT FK_PG_ALMACEN
        FOREIGN KEY (id_almacen_actual)
        REFERENCES ALMACEN(id_almacen)
);

-- =========================================================
-- TABLA: MOVIMIENTO_GLOBAL
-- =========================================================

CREATE TABLE MOVIMIENTO_GLOBAL (
    id_movimiento UNIQUEIDENTIFIER PRIMARY KEY,

    id_paquete UNIQUEIDENTIFIER NOT NULL,

    id_almacen INT NOT NULL,

    fecha_movimiento DATETIME NOT NULL DEFAULT GETDATE(),

    observacion VARCHAR(300),

    CONSTRAINT FK_MG_PAQUETE
        FOREIGN KEY (id_paquete)
        REFERENCES PAQUETE_GLOBAL(id_paquete),

    CONSTRAINT FK_MG_ALMACEN
        FOREIGN KEY (id_almacen)
        REFERENCES ALMACEN(id_almacen)
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

INSERT INTO almacen(id_almacen,nombre, ciudad, direccion, nodo_responsable)
VALUES
(1,'Almacén Central LP', 'La Paz', 'Zona Central', 'LP'),
(2,'Almacén Central SCZ', 'Santa Cruz', 'Zona Industrial', 'SCZ');
GO


INSERT INTO catalogo_fragmentacion
(nombre_fragmento, nodo, motor_bd, tabla_base, tipo_fragmentacion)
VALUES

-- ==========================================
-- CLIENTE (fragmentación vertical)
-- ==========================================

('CLIENTE_PUBLICO_LP',      'LP',      'PostgreSQL', 'CLIENTE', 'Vertical'),
('CLIENTE_PUBLICO_SCZ',     'SCZ',     'SQL Server', 'CLIENTE', 'Vertical'),
('CLIENTE_PUBLICO_CENTRAL', 'CENTRAL', 'SQL Server', 'CLIENTE', 'Vertical'),

('CLIENTE_PRIVADO_CENTRAL', 'CENTRAL', 'SQL Server', 'CLIENTE', 'Vertical'),

-- ==========================================
-- PAQUETE (fragmentación hibrida)
-- ==========================================

('PAQUETE_OPERATIVO_LP',  'LP',      'PostgreSQL', 'PAQUETE', 'Hibrida'),
('PAQUETE_FINANCIERO_LP', 'LP',      'PostgreSQL', 'PAQUETE', 'Hibrida'),

('PAQUETE_OPERATIVO_SCZ',  'SCZ',     'SQL Server', 'PAQUETE', 'Hibrida'),
('PAQUETE_FINANCIERO_SCZ', 'SCZ',     'SQL Server', 'PAQUETE', 'Hibrida'),

('PAQUETE_GLOBAL', 'CENTRAL', 'SQL Server', 'PAQUETE', 'Integración'),

-- ==========================================
-- MOVIMIENTO (fragmentación horizontal)
-- ==========================================

('MOVIMIENTO_LP',  'LP',  'PostgreSQL', 'MOVIMIENTO', 'Horizontal'),
('MOVIMIENTO_SCZ', 'SCZ', 'SQL Server', 'MOVIMIENTO', 'Horizontal'),

('MOVIMIENTO_GLOBAL', 'CENTRAL', 'SQL Server', 'MOVIMIENTO', 'Integración'),

-- ==========================================
-- TABLAS REPLICADAS
-- ==========================================

('ESTADO_LP',      'LP',      'PostgreSQL', 'ESTADO', 'Replicada'),
('ESTADO_SCZ',     'SCZ',     'SQL Server', 'ESTADO', 'Replicada'),
('ESTADO_CENTRAL', 'CENTRAL', 'SQL Server', 'ESTADO', 'Replicada'),

('ALMACEN_LP',      'LP',      'PostgreSQL', 'ALMACEN', 'Replicada'),
('ALMACEN_SCZ',     'SCZ',     'SQL Server', 'ALMACEN', 'Replicada'),
('ALMACEN_CENTRAL', 'CENTRAL', 'SQL Server', 'ALMACEN', 'Replicada'),

('RUTA_LP',      'LP',      'PostgreSQL', 'RUTA', 'Replicada'),
('RUTA_SCZ',     'SCZ',     'SQL Server', 'RUTA', 'Replicada'),
('RUTA_CENTRAL', 'CENTRAL', 'SQL Server', 'RUTA', 'Replicada');



-- 1. Insert en CLIENTE_PUBLICO
DECLARE @id UNIQUEIDENTIFIER = NEWID();

INSERT INTO CLIENTE_PUBLICO (
    id_cliente,
    nombre,
    apellido_paterno,
    apellido_materno,
    telefono
)
VALUES (
    @id,
    'Juan',
    'Perez',
    'Lopez',
    '71234567'
);

-- 2. Insert en CLIENTE_PRIVADO usando el mismo ID
INSERT INTO CLIENTE_PRIVADO (
    id_cliente,
    documento_identidad,
    direccion,
    email
)
VALUES (
    @id,
    '1234567LP',
    'Zona Sopocachi, La Paz',
    'juan.perez@email.com'
);