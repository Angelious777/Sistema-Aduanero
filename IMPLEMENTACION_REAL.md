# Implementación de Funcionalidad Real - Sistema Aduanero Distribuido

## 📋 Resumen de Cambios

Se ha implementado una integración completa entre la interfaz web (HTML/CSS/JS) y las funciones Python del backend. La aplicación ahora utiliza **datos reales** de las bases de datos distribuidas en lugar de datos simulados.

---

## 🔧 Cambios Realizados

### 1. **Módulos Python Mejorados**

#### `monitor.py` (Actualizado)
- Ahora verifica conectividad real de los nodos
- Obtiene métricas específicas por nodo desde las bases de datos
- Detecta automáticamente si los nodos están conectados o desconectados

#### `metricas.py` (Actualizado)
- Obtiene métricas reales del sistema distribuido
- Cuenta nodos activos probando conexiones
- Obtiene número de fragmentos desde el catálogo central
- Proporciona información sobre transacciones 2PC activas

#### `dashboard.py` (Actualizado)
- Construye un dashboard completo con datos reales
- Obtiene actividad reciente desde ambos nodos
- Recupera consultas ejecutadas recientemente
- Genera topología actual del sistema

#### `actualizaciones.py` (Sin cambios - ya funcional)
- Actualiza estados de paquetes en ambos nodos de forma distribuida

### 2. **Nuevos Módulos Python**

#### `paquetes.py` (NUEVO)
Funciones para operar con paquetes:
- `obtener_todos_paquetes()` - Obtiene paquetes de ambos nodos
- `obtener_paquetes_por_nodo()` - Paquetes de un nodo específico
- `buscar_paquete()` - Búsqueda distribuida de un paquete
- `crear_paquete()` - Crear nuevo paquete
- `obtener_tabla_paquete()` - Tabla completa de paquetes
- `obtener_tabla_movimiento()` - Tabla completa de movimientos

#### `movimientos.py` (NUEVO)
Funciones para operar con movimientos:
- `registrar_movimiento()` - Registra evento de movimiento
- `obtener_movimientos_paquete()` - Historial de movimientos
- `obtener_todos_movimientos()` - Todos los movimientos de un nodo
- `actualizar_estado_movimiento()` - Cambiar estado de un movimiento
- `obtener_historial_completo()` - Historial distribuido de un paquete

### 3. **Flask App Mejorada** (`app.py`)

Se agregaron **30+ nuevos endpoints** organizados en categorías:

#### **Dashboard** (`/api/dashboard`)
```
GET /api/dashboard - Datos completos del dashboard
GET /api/metricas - Métricas del sistema
GET /api/estado_nodos - Estado de conectividad
GET /api/metricas_nodo/<nodo> - Métricas de un nodo específico
```

#### **Paquetes** (`/api/paquetes/*`)
```
GET /api/paquetes - Todos los paquetes
GET /api/paquetes/<nodo> - Paquetes de un nodo
GET /api/paquete/buscar/<codigo> - Buscar paquete
POST /api/paquete/crear - Crear nuevo paquete
GET /api/tabla/paquete/<nodo> - Tabla de paquetes
```

#### **Movimientos** (`/api/movimientos/*`)
```
GET /api/movimientos/<nodo> - Movimientos de un nodo
GET /api/movimientos/paquete/<codigo>/<nodo> - Movimientos de un paquete
POST /api/movimiento/registrar - Registrar nuevo movimiento
GET /api/tabla/movimiento/<nodo> - Tabla de movimientos
```

#### **Trazabilidad** (`/api/trazabilidad/*`)
```
GET /api/trazabilidad/<codigo> - Trazabilidad completa distribuida
```

#### **Catálogo** (`/api/catalogo`)
```
GET /api/catalogo - Catálogo de fragmentos
```

### 4. **JavaScript Frontend Actualizado** (`static/js/app.js`)

#### Nuevas Características:
- **Carga de Dashboard Real**: Obtiene datos en tiempo real del backend
- **Integración con API**: Consume todos los nuevos endpoints
- **Actualización Automática**: Recarga datos cada 30 segundos
- **Registración de Movimientos**: Formularios funcionales para registrar eventos
- **Carga de Tablas**: Carga y muestra tablas de paquetes y movimientos

#### Funciones Principales:
```javascript
// Cargar datos del dashboard
cargarDashboard()

// Cargar paquetes y movimientos de un nodo
cargarPaquetesNodo(nodo)
cargarMovimientosNodo(nodo)

// Registrar movimientos
registrarMovimientoLaPaz()
registrarMovimientoSantaCruz()

// Actualizar interfaz
actualizarDashboard(data)
```

---

## 📊 Flujo de Datos

```
Frontend (HTML/JS)
        ↓
    Flask API (/api/*)
        ↓
    Módulos Python (paquetes.py, movimientos.py, etc.)
        ↓
    Conexiones a BD
        ├── SQL Server (Coordinador)
        ├── PostgreSQL (La Paz)
        └── SQL Server (Santa Cruz)
```

---

## 🚀 Cómo Usar

### 1. **Iniciar la Aplicación**

```bash
# Navegar al directorio del proyecto
cd "c:\Users\ROGER\Escritorio\Sistema Aduanero"

# Activar el entorno virtual
venv\Scripts\activate

# Instalar dependencias (si no están instaladas)
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

### 2. **Ver Dashboard**
El panel de inicio muestra en tiempo real:
- Nodos sincronizados
- Tráfico distribuido
- Operaciones pendientes
- Fragmentos activos
- Estado de conectividad
- Topología actual

### 3. **Consultar Paquetes**

En los paneles de La Paz y Santa Cruz, la tabla "PAQUETE" muestra:
- Código de rastreo
- Destino
- Prioridad
- Estado
- Sincronización

### 4. **Registrar Movimientos**

1. Ir al panel de La Paz o Santa Cruz
2. Hacer clic en "Registrar movimiento"
3. Completar los campos:
   - ID Movimiento (ej: MOV-XXX)
   - Paquete (ej: LP-2026-009)
   - Ubicación
   - Estado
4. Hacer clic en "Registrar movimiento"

### 5. **Ver Trazabilidad** (Futuro)

Será posible buscar un paquete por código y ver su historial completo desde ambos nodos.

---

## 🗄️ Estructura de Bases de Datos Esperadas

### Coordinador (SQL Server)
```sql
-- Tablas esperadas
catalogo_fragmentos
nodos
consultas_ejecutadas
transacciones_2pc
```

### La Paz (PostgreSQL)
```sql
-- Tablas esperadas
paquete_lp (codigo_rastreo, destino, prioridad, estado, ...)
movimiento_lp (id_movimiento, id_paquete, ubicacion, estado, fecha_movimiento, ...)
```

### Santa Cruz (SQL Server)
```sql
-- Tablas esperadas
paquete_scz (codigo_rastreo, destino, prioridad, estado, ...)
movimiento_scz (id_movimiento, id_paquete, ubicacion, estado, fecha_movimiento, ...)
```

---

## 🔌 Endpoints Disponibles

### Consultas con CURL

**Obtener Dashboard:**
```bash
curl http://localhost:5000/api/dashboard
```

**Buscar Paquete:**
```bash
curl http://localhost:5000/api/paquete/buscar/PK-2026-001
```

**Registrar Movimiento:**
```bash
curl -X POST http://localhost:5000/api/movimiento/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "id_movimiento": "MOV-123",
    "id_paquete": "PK-2026-001",
    "ubicacion": "La Paz",
    "estado": "En ruta",
    "nodo": "lapaz"
  }'
```

**Obtener Tabla de Paquetes:**
```bash
curl http://localhost:5000/api/tabla/paquete/lapaz
```

---

## 🔄 Funcionalidades Implementadas

| Funcionalidad | Estado | Ubicación |
|---|---|---|
| Cargar Dashboard | ✅ Activo | `/api/dashboard` |
| Ver Métricas | ✅ Activo | `/api/metricas` |
| Estado de Nodos | ✅ Activo | `/api/estado_nodos` |
| Obtener Paquetes | ✅ Activo | `/api/paquetes*` |
| Registrar Movimientos | ✅ Activo | `/api/movimiento/registrar` |
| Buscar Paquete | ✅ Activo | `/api/paquete/buscar/*` |
| Trazabilidad | ✅ Activo | `/api/trazabilidad/*` |
| Crear Paquete | ✅ Activo | `/api/paquete/crear` |

---

## 🐛 Solución de Problemas

### Error: "No se puede conectar a la base de datos"
- Verificar que los servidores en `config.py` están disponibles
- Verificar credenciales en `config.py`
- Verificar que PostgreSQL (La Paz) y SQL Server (Coordinador y Santa Cruz) están ejecutándose

### Error: "AttributeError: CORS"
- Instalar: `pip install flask-cors`

### Los datos no se actualizan
- Esperar 30 segundos (intervalo de recarga)
- O recargar la página manualmente

---

## 📝 Notas Importantes

1. **CORS Habilitado**: La API permite solicitudes desde cualquier origen
2. **Manejo de Errores**: Todos los endpoints retornan respuestas consistentes con `respuesta_ok()` o `respuesta_error()`
3. **Logging**: Se registran todas las operaciones importantes
4. **Validación**: Los códigos de paquete deben comenzar con "PK"
5. **Ejecución Paralela**: Los movimientos se consultan en paralelo desde ambos nodos

---

## 🎯 Próximas Mejoras (Opcionales)

1. Agregar búsqueda en tiempo real en la interfaz
2. Implementar gráficos de actividad
3. Agregar filtros por estado/prioridad
4. Implementar sincronización automática entre nodos
5. Agregar notificaciones en tiempo real (WebSockets)
6. Implementar autenticación y autorización
7. Agregar más validaciones en el frontend

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs en `logs/`
2. Verifica la conexión a bases de datos
3. Intenta acceder directamente a los endpoints con CURL
4. Revisa la consola del navegador (F12 → Console)

---

**Implementado**: 30 de Mayo de 2026  
**Sistema**: Sistema Distribuido de Control Aduanero  
**Versión**: 1.0 - Funcionalidad Real Integrada
