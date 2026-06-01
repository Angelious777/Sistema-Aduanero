# 🌍 Sistema Aduanero Distribuido - Documentación de Uso

## 📌 Descripción General

Este es un **Sistema de Control Aduanero Distribuido** que utiliza una arquitectura heterogénea con:
- **Nodo Coordinador** (SQL Server) - Orquestación central
- **Nodo La Paz** (PostgreSQL) - Fragmentos regionales
- **Nodo Santa Cruz** (SQL Server) - Fragmentos regionales

El sistema implementa **fragmentación horizontal** de datos de paquetes y movimientos, con capacidad de ejecutar consultas distribuidas y sincronizar datos entre nodos.

---

## 🚀 Inicio Rápido

### 1. Requisitos Previos
- Python 3.8+
- PostgreSQL (para La Paz)
- SQL Server (para Coordinador y Santa Cruz)
- Flask
- Librerías en `requirements.txt`

### 2. Instalación

```bash
# Navegar al directorio del proyecto
cd "c:\Users\ROGER\Escritorio\Sistema Aduanero"

# Crear/activar entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración

Editar `config.py` con los datos de conexión reales:

```python
LP_CONFIG = {
    "host": "TU_IP_POSTGRESQL",
    "database": "lapaz_db",
    "user": "postgres",
    "password": "tu_password",
    "port": "5432"
}

SCZ_CONFIG = {
    "driver": "ODBC Driver 17 for SQL Server",
    "server": "TU_IP_SQL_SERVER",
    "database": "santacruz_db",
    "user": "sa",
    "password": "tu_password"
}
```

### 4. Ejecutar Aplicación

```bash
python app.py
```

Acceder a: **http://localhost:5000**

---

## 📊 Interfaz Web

### Panel 1: Dashboard
Muestra el estado general del sistema:
- ✅ Nodos sincronizados
- 📦 Tráfico distribuido (transacciones)
- ⏳ Operaciones pendientes
- 🔗 Fragmentos activos
- 🌐 Topología de la red
- 📋 Actividad reciente

### Panel 2: Coordinador
Visualiza la orquestación central:
- Query Parser y decisión de fragmentos
- Planificador de subconsultas
- Ensamblador de resultados
- Catálogo de fragmentación
- Reconstrucción distribuida

### Panel 3: La Paz
Nodo regional con datos horizontalmente fragmentados:
- 📋 Tabla PAQUETE_LP
- 🚚 Tabla MOVIMIENTO_LP
- ➕ Opción para registrar nuevos movimientos
- 🔄 Sincronización regional

### Panel 4: Santa Cruz
Similar a La Paz pero para la región SCZ:
- 📋 Tabla PAQUETE_SCZ
- 🚚 Tabla MOVIMIENTO_SCZ
- ➕ Registrar eventos
- 🔄 Sincronización

---

## 🎯 Funcionalidades Principales

### 1. Búsqueda de Paquetes
```
GET /api/paquete/buscar/PK-2026-001
```
Busca un paquete en ambos nodos y retorna su ubicación actual.

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "codigo": "PK-2026-001",
    "destino": "SCZ",
    "prioridad": "Alta",
    "estado": "En tránsito",
    "nodo": "La Paz"
  }
}
```

### 2. Ver Trazabilidad Completa
```
GET /api/trazabilidad/PK-2026-001
```
Obtiene el historial completo desde ambos nodos en orden cronológico.

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "codigo": "PK-2026-001",
    "historial": [
      {
        "ubicacion": "La Paz",
        "estado": "Registrado",
        "fecha": "2026-05-30 10:00:00",
        "observacion": "Paquete ingresado",
        "nodo": "La Paz"
      },
      {
        "ubicacion": "El Alto",
        "estado": "En ruta",
        "fecha": "2026-05-30 11:30:00",
        "observacion": "Enviado a Santa Cruz",
        "nodo": "La Paz"
      }
    ]
  }
}
```

### 3. Registrar Movimiento
```
POST /api/movimiento/registrar
Content-Type: application/json

{
  "id_movimiento": "MOV-441",
  "id_paquete": "PK-2026-009",
  "ubicacion": "La Paz",
  "estado": "Listo",
  "nodo": "lapaz"
}
```

### 4. Obtener Métricas del Sistema
```
GET /api/metricas
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "pendientes": 2,
    "nodos_activos": 3,
    "fragmentos": 4,
    "motor_lp": "PostgreSQL",
    "motor_scz": "SQL Server"
  }
}
```

### 5. Ver Estado de Nodos
```
GET /api/estado_nodos
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "La Paz": "Conectado",
    "Santa Cruz": "Conectado",
    "Coordinador": "Conectado"
  }
}
```

---

## 📁 Estructura de Proyectos

### Backend (Python)
```
├── app.py                 # Aplicación Flask principal
├── conexiones.py          # Gestión de conexiones BD
├── consultas.py           # Consultas distribuidas
├── ejecutor.py            # Ejecución paralela
├── parser.py              # Análisis de consultas
├── planificador.py        # Planificación distribuida
├── actualizaciones.py     # Actualización de estados
├── monitor.py             # Monitoreo de nodos
├── metricas.py            # Métricas del sistema
├── dashboard.py           # Construcción del dashboard
├── paquetes.py            # Operaciones con paquetes
├── movimientos.py         # Operaciones con movimientos
├── catalogo.py            # Catálogo de fragmentos
├── sincronizacion.py      # Cola de sincronización
├── validaciones.py        # Validaciones de datos
├── tolerancia.py          # Estado de nodos
├── respuestas.py          # Formato de respuestas
├── config.py              # Configuración de conexiones
├── logs/
│   └── logger.py          # Sistema de logging
```

### Frontend (JavaScript/HTML/CSS)
```
├── templates/
│   └── index.html         # Interfaz web principal
├── static/
│   ├── css/
│   │   ├── styles.css     # Estilos principales
│   │   └── prototype.css  # Estilos alternativos
│   └── js/
│       ├── app.js         # Lógica principal (ACTUALIZADO)
│       └── prototype.js   # Script adicional
```

---

## 🔐 Validaciones

### Código de Paquete
- Debe comenzar con "PK"
- Ejemplo válido: `PK-2026-001`

### Campos Requeridos
- **Código**: Identificador único del paquete
- **Destino**: Región destino (LP, SCZ)
- **Prioridad**: Alta, Media, Baja
- **Estado**: Registrado, En tránsito, Inspección, Listo

---

## 🔧 API REST Completa

| Método | Endpoint | Descripción |
|--------|----------|---|
| GET | `/api/dashboard` | Dashboard completo |
| GET | `/api/metricas` | Métricas del sistema |
| GET | `/api/estado_nodos` | Estado de conectividad |
| GET | `/api/metricas_nodo/<nodo>` | Métricas de un nodo |
| GET | `/api/paquetes` | Todos los paquetes |
| GET | `/api/paquetes/<nodo>` | Paquetes de un nodo |
| GET | `/api/paquete/buscar/<codigo>` | Buscar paquete |
| POST | `/api/paquete/crear` | Crear paquete |
| GET | `/api/tabla/paquete/<nodo>` | Tabla de paquetes |
| GET | `/api/tabla/movimiento/<nodo>` | Tabla de movimientos |
| GET | `/api/movimientos/<nodo>` | Movimientos de un nodo |
| GET | `/api/movimientos/paquete/<codigo>/<nodo>` | Movimientos de paquete |
| POST | `/api/movimiento/registrar` | Registrar movimiento |
| GET | `/api/trazabilidad/<codigo>` | Trazabilidad completa |
| GET | `/api/catalogo` | Catálogo de fragmentos |
| GET | `/api/pendientes` | Operaciones pendientes |
| PUT | `/api/actualizar_estado` | Actualizar estado |

---

## 🐛 Resolución de Problemas

### Error: "Connection refused"
**Causa**: BD no disponible  
**Solución**: Verificar que PostgreSQL y SQL Server estén ejecutándose

### Error: "ODBC Driver not found"
**Causa**: Driver SQL Server no instalado  
**Solución**: Instalar "ODBC Driver 17 for SQL Server"

### Error: "Module not found"
**Causa**: Dependencia no instalada  
**Solución**: `pip install -r requirements.txt`

### Los datos no se actualizan
**Causa**: Caché o intervalo de actualización  
**Solución**: Recargar página (F5) o esperar 30 segundos

---

## 📈 Ejemplos de Uso

### Ejemplo 1: Obtener Dashboard en Python
```python
import requests

response = requests.get('http://localhost:5000/api/dashboard')
data = response.json()

print(f"Nodos activos: {data['data']['metricas']['nodos_activos']}")
print(f"Pendientes: {data['data']['metricas']['operaciones_pendientes']}")
```

### Ejemplo 2: Registrar Movimiento en cURL
```bash
curl -X POST http://localhost:5000/api/movimiento/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "id_movimiento": "MOV-999",
    "id_paquete": "PK-2026-050",
    "ubicacion": "Santa Cruz",
    "estado": "En ruta",
    "nodo": "scz"
  }'
```

### Ejemplo 3: Buscar Paquete en JavaScript
```javascript
fetch('/api/paquete/buscar/PK-2026-001')
  .then(r => r.json())
  .then(data => {
    console.log(`Paquete en: ${data.data.ubicacion}`);
    console.log(`Estado: ${data.data.estado}`);
  });
```

---

## 📞 Soporte Técnico

**Log de la aplicación**: `logs/`  
**Documentación detallada**: `IMPLEMENTACION_REAL.md`

---

**Última actualización**: 30 de Mayo de 2026  
**Versión**: 1.0 - Funcionalidad Real  
**Estado**: ✅ Producción
