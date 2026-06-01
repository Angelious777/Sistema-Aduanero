/**
 * db_local_nodo.js - Dataset Autoadaptable y Motor de Base de Datos por Región
 */

// 1. Capturamos la configuración real inyectada por Flask en el index.html
const configAduanera = window.CONFIG_NODO_ACTIVO || { id: "NODO_LA_PAZ", nombre: "Sede Occidental (La Paz)", motor: "PostgreSQL" };

// 2. Definición del entorno específico para LA PAZ (PostgreSQL)
const datasetLaPaz = {
    config: configAduanera,
    infraestructura: {
        motor_bd: "PostgreSQL 15",
        host: "192.168.0.2",
        puerto: "5432",
        base_datos: "aduanas_la_paz_db",
        esquema: "PAQUETE_OPERATIVO_LP"
    },
    paquetes: [
        { codigo: "PKT-LP-001", destino: "Cochabamba", estado: "Registrado", costo: 150.00, remitente: "Juan Pérez", descripcion: "Documentación Comercial" },
        { codigo: "PKT-LP-002", destino: "Oruro", estado: "En Tránsito", costo: 280.50, remitente: "Comercializadora El Alto", descripcion: "Repuestos Industriales" }
    ],
    movimientos: [
        { fecha: "2026-05-30 14:20", paquete: "PKT-LP-001", evento: "Control de Peso Físico", observacion: "Balanza 2 - Conforme (PostgreSQL)" },
        { fecha: "2026-05-31 09:15", paquete: "PKT-LP-002", evento: "Apertura y Aforo", observacion: "Revisión aduanera de rutina, sellos aprobados" }
    ],
    clientes_publicos: [
        { id: 1, nombre: "Corporación Minera San José", documento: "NIT-920192021", telefono: "2214950", correo: "contacto@sanjose.bo" }
    ],
    almacenes: [
        { codigo: "ALM-LP-01", nombre: "Depósito Aduanero Central El Alto", ubicacion: "Av. 6 de Marzo", capacidad: "4,500 m³" }
    ]
};

// 3. Definición del entorno específico para SANTA CRUZ (SQL Server)
const datasetSantaCruz = {
    config: configAduanera,
    infraestructura: {
        motor_bd: "Microsoft SQL Server 2022",
        host: "192.168.0.5",
        puerto: "1433",
        base_datos: "AduanasSantaCruzDB",
        esquema: "dbo.PAQUETE_OPERATIVO_SCZ"
    },
    paquetes: [
        { codigo: "PKT-SCZ-801", destino: "Trinidad", estado: "Registrado", costo: 420.00, remitente: "Agro Oriente", descripcion: "Semillas Certificadas" },
        { codigo: "PKT-SCZ-802", destino: "Yacuiba", estado: "Retenido", costo: 1150.00, remitente: "Importadora del Sur", descripcion: "Equipos Electrónicos" }
    ],
    movimientos: [
        { fecha: "2026-05-31 08:00", paquete: "PKT-SCZ-802", evento: "Clasificación Arancelaria", observacion: "Falta documentación de origen en SQL Server" }
    ],
    clientes_publicos: [
        // { id: 3, nombre: "Ingenio Azucarero Guabirá", documento: "NIT-440291023", telefono: "3922039", correo: "logistica@guabira.com" }
    ],
    almacenes: [
        { codigo: "ALM-SCZ-01", nombre: "Terminal de Carga Aeropuerto Viru Viru", ubicacion: "Carr. al Norte Km 13", capacidad: "12,000 m³" }
    ]
};

// 4. ASIGNACIÓN DINÁMICA FINAL EN EL OBJETO GLOBAL WINDOW
// Evaluamos estrictamente el ID inyectado por Flask para decidir el set de datos
if (configAduanera.id === "NODO_SANTA_CRUZ") {
    window.DB_NODO_LOCAL = datasetSantaCruz;
} else {
    window.DB_NODO_LOCAL = datasetLaPaz;
}

console.log("Instancia de Base de Datos Inicializada:", window.DB_NODO_LOCAL.infraestructura.motor_bd);