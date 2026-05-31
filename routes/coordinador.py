# -*- coding: utf-8 -*-
"""
coordinador.py
Controlador de Rutas (Backend Flask) para el Nodo Coordinador Central.
Simula la abstracción, fragmentación y orquestación distribuida de la red nacional.
"""

from flask import Blueprint, render_template, jsonify, request, session
from datetime import datetime
import random

# Definición del Blueprint para el módulo del coordinador
coordinador_bp = Blueprint('coordinador', __name__, template_folder='templates')

# ==========================================================================
# SIMULACIÓN DE FRAGMENTOS AISLADOS (Bases de Datos Regionales Remotas)
# ==========================================================================

# FRAGMENTO DE OCCIDENTE (Alojado en Sede La Paz - Motor: PostgreSQL)
DB_REMOTA_LA_PAZ = {
    # Fragmentación Vertical / Horizontal Híbrida de PAQUETE (Solo Datos Logísticos y de Origen LP)
    "PAQUETE_OPERATIVO_LP": {
        "PK-LP-2026-001": {"codigo": "PK-LP-2026-001", "descripcion": "Componentes electrónicos de alta precisión", "origen": "La Paz", "destino": "Santa Cruz", "estado": "En Tránsito"},
        "PK-LP-2026-003": {"codigo": "PK-LP-2026-003", "descripcion": "Textiles artesanales y manufacturas locales", "origen": "La Paz", "destino": "Santa Cruz", "estado": "Registrado"},
    },
    # Fragmentación Vertical de PAQUETE (Precios y Seguros aislados por seguridad financiera)
    "PAQUETE_FINANCIERO_LP": {
        "PK-LP-2026-001": {"costo": 450.00, "seguro": 25.00, "impuesto": 45.00},
        "PK-LP-2026-003": {"costo": 180.00, "seguro": 0.00, "impuesto": 0.00},
    },
    # Fragmentación Horizontal de MOVIMIENTO (Tránsitos capturados físicamente en el almacén de El Alto)
    "MOVIMIENTO_LP": [
        {"fecha": "2026-05-31 08:30", "codigo": "PK-LP-2026-001", "almacen": "Almacén Central El Alto (LP)", "accion": "Registro e Inspección", "observacion": "Documentación aduanera aprobada."},
        {"fecha": "2026-05-31 11:00", "codigo": "PK-LP-2026-001", "almacen": "Punto de Control Tránsito Occidental", "accion": "Despacho de Salida", "observacion": "Ruta troncal hacia el oriente autorizada."}
    ]
}

# FRAGMENTO DE ORIENTE (Alojado en Sede Santa Cruz - Motor: MS SQL Server)
DB_REMOTA_SANTA_CRUZ = {
    # Fragmentación Vertical / Horizontal Híbrida de PAQUETE (Solo Datos Logísticos y de Origen SCZ)
    "PAQUETE_OPERATIVO_SCZ": {
        "PK-SCZ-2026-002": {"codigo": "PK-SCZ-2026-002", "descripcion": "Maquinaria agrícola e insumos de producción", "origen": "Santa Cruz", "destino": "La Paz", "estado": "Retenido por Aduana"},
        "PK-SCZ-2026-004": {"codigo": "PK-SCZ-2026-004", "descripcion": "Repuestos industriales automotrices", "origen": "Santa Cruz", "destino": "Cochabamba", "estado": "Entregado"},
    },
    # Fragmentación Vertical de PAQUETE (Precios e Impuestos aislados en el nodo SCZ)
    "PAQUETE_FINANCIERO_SCZ": {
        "PK-SCZ-2026-002": {"costo": 1250.00, "seguro": 80.00, "impuesto": 125.00},
        "PK-SCZ-2026-004": {"costo": 890.00, "seguro": 40.00, "impuesto": 0.00},
    },
    # Fragmentación Horizontal de MOVIMIENTO (Tránsitos capturados en rampa Oriente)
    "MOVIMIENTO_SCZ": [
        {"fecha": "2026-05-31 09:15", "codigo": "PK-SCZ-2026-002", "almacen": "Almacén Regional Oriente (SCZ)", "accion": "Retención Preventiva", "observacion": "Verificación de valores declarados en póliza."},
        {"fecha": "2026-05-31 13:45", "codigo": "PK-SCZ-2026-004", "almacen": "Almacén Regional Oriente (SCZ)", "accion": "Confirmación de Recepción", "observacion": "Entrega final conforme a guía de aduana."}
    ]
}

# Diccionario complementario de Clientes (Demostración de reconstrucción vertical pura en el Coordinador)
DB_CLIENTES_CENTRAL = {
    "PK-LP-2026-001": {"nombres": "Juan Carlos", "apellidoPaterno": "Mamani", "apellidoMaterno": "Quispe", "documento": "4892019 LP", "telefono": "71548291", "direccion": "Av. Civica Nro 450, El Alto", "email": "j.mamani@mail.bo"},
    "PK-SCZ-2026-002": {"nombres": "Maria Elena", "apellidoPaterno": "Suarez", "apellidoMaterno": "Vargas", "documento": "3940192 SCZ", "telefono": "60849201", "direccion": "Barrio Equipetrol, Calle 4 Ost", "email": "m.suarez@mail.bo"},
    "PK-LP-2026-003": {"nombres": "Pedro", "apellidoPaterno": "Flores", "apellidoMaterno": "Cruz", "documento": "6102934 LP", "telefono": "73029104", "direccion": "Zona Sopocachi Calle Méndez", "email": "p.flores@mail.bo"},
    "PK-SCZ-2026-004": {"nombres": "Alejandro", "apellidoPaterno": "Pinto", "apellidoMaterno": "Prado", "documento": "8394012 SCZ", "telefono": "67719204", "direccion": "Av. Las Americas, Edif El Sol", "email": "a.pinto@mail.bo"}
}