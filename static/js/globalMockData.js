// Variable unificada compartida en memoria
window.DB_PROYECTO_GLOBAL = {
    paquetes: [
        { codigo: "PK-LP-2026-001", remitente: "Juan Carlos Mamani", destinatario: "Carlos Condori", origen: "La Paz", destino: "Santa Cruz", costo: 450.00, pago: "Tarjeta de Crédito", impuestos: 45.00, estado: "En Tránsito", fecha: "2026-05-30 08:30", nodo: "NODO_LA_PAZ" },
        { codigo: "PK-SCZ-2026-002", remitente: "Maria Elena Suarez", destinatario: "Jorge Roca", origen: "Santa Cruz", destino: "La Paz", costo: 1250.00, pago: "Efectivo / Depósito", impuestos: 125.00, estado: "Retenido por Aduana", fecha: "2026-05-30 09:15", nodo: "NODO_SANTA_CRUZ" },
        { codigo: "PK-LP-2026-003", remitente: "Pedro Flores Cruz", destinatario: "Ana Banzer", origen: "La Paz", destino: "Santa Cruz", costo: 180.00, pago: "QR Simple", impuestos: 0.00, estado: "Registrado", fecha: "2026-05-31 10:00", nodo: "NODO_LA_PAZ" },
        { codigo: "PK-SCZ-2026-004", remitente: "Alejandro Pinto Prado", destinatario: "Ramiro Quispe", origen: "Santa Cruz", destino: "Cochabamba", costo: 890.00, pago: "Transferencia", impuestos: 40.00, estado: "Entregado", fecha: "2026-05-31 11:20", nodo: "NODO_SANTA_CRUZ" }
    ],
    movimientos: [
        { fecha: "2026-05-31 08:30", paquete: "PK-LP-2026-001", evento: "Registro e Inspección", almacen: "Almacén Central El Alto (LP)", nodo: "NODO_LA_PAZ" },
        { fecha: "2026-05-31 09:15", paquete: "PK-SCZ-2026-002", evento: "Retención Preventiva", almacen: "Almacén Regional Oriente (SCZ)", nodo: "NODO_SANTA_CRUZ" },
        { fecha: "2026-05-31 11:00", paquete: "PK-LP-2026-001", evento: "Despacho de Salida", almacen: "Punto de Control Tránsito", nodo: "NODO_LA_PAZ" },
        { fecha: "2026-05-31 13:45", paquete: "PK-SCZ-2026-004", evento: "Confirmación de Recepción", almacen: "Almacén Regional Oriente (SCZ)", nodo: "NODO_SANTA_CRUZ" }
    ],
    clientes: [
        { nombre: "Juan Carlos Mamani Quispe", documento: "4892019 LP", telefono: "71548291", correo: "j.mamani@mail.bo", registro: "2026-01-15", tipo: "CLIENTE_PRIVADO (Importador)" },
        { nombre: "Maria Elena Suarez Vargas", documento: "3940192 SCZ", telefono: "60849201", correo: "m.suarez@mail.bo", registro: "2026-02-20", tipo: "CLIENTE_PUBLICO (General)" },
        { nombre: "Pedro Flores Cruz", documento: "6102934 LP", telefono: "73029104", correo: "p.flores@mail.bo", registro: "2026-03-05", tipo: "CLIENTE_PUBLICO (General)" },
        { nombre: "Alejandro Pinto Prado", documento: "8394012 SCZ", telefono: "67719204", correo: "a.pinto@mail.bo", registro: "2026-04-12", tipo: "CLIENTE_PRIVADO (Empresarial)" }
    ]
};