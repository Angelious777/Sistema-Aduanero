# 🔌 GUÍA RÁPIDA - API REST

## Base URL
```
http://localhost:5000/api
```

---

## 📊 DASHBOARD & MÉTRICAS

### Obtener Dashboard Completo
```http
GET /dashboard
```
**Respuesta**: Dashboard con métricas, nodos, topología, actividad

### Obtener Métricas
```http
GET /metricas
```
**Respuesta**: 
```json
{
  "success": true,
  "data": {
    "pendientes": 2,
    "nodos_activos": 3,
    "fragmentos": 4
  }
}
```

### Estado de Nodos
```http
GET /estado_nodos
```
**Respuesta**:
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

### Métricas de Nodo Específico
```http
GET /metricas_nodo/{nodo}
```
**Parámetros**: 
- `nodo`: "La Paz", "Santa Cruz", o "Coordinador"

---

## 📦 PAQUETES

### Obtener Todos los Paquetes
```http
GET /paquetes
```

### Paquetes de un Nodo
```http
GET /paquetes/{nodo}
```
**Parámetros**:
- `nodo`: "lapaz" o "scz"

### Buscar Paquete
```http
GET /paquete/buscar/{codigo}
```
**Parámetros**:
- `codigo`: Ej. "PK-2026-001"

**Respuesta**:
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

### Crear Paquete
```http
POST /paquete/crear
Content-Type: application/json

{
  "codigo": "PK-2026-050",
  "destino": "SCZ",
  "prioridad": "Media",
  "nodo": "lapaz"
}
```

### Tabla de Paquetes
```http
GET /tabla/paquete/{nodo}
```
**Parámetros**:
- `nodo`: "lapaz" o "scz"

**Respuesta**: Array con todos los campos de la tabla

---

## 🚚 MOVIMIENTOS

### Movimientos de un Nodo
```http
GET /movimientos/{nodo}
```
**Parámetros**:
- `nodo`: "lapaz" o "scz"

### Movimientos de un Paquete
```http
GET /movimientos/paquete/{codigo}/{nodo}
```
**Parámetros**:
- `codigo`: Ej. "PK-2026-001"
- `nodo`: "lapaz" o "scz"

### Registrar Movimiento
```http
POST /movimiento/registrar
Content-Type: application/json

{
  "id_movimiento": "MOV-441",
  "id_paquete": "PK-2026-009",
  "ubicacion": "La Paz",
  "estado": "Listo",
  "nodo": "lapaz"
}
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "mensaje": "Movimiento registrado exitosamente"
  }
}
```

### Tabla de Movimientos
```http
GET /tabla/movimiento/{nodo}
```
**Parámetros**:
- `nodo`: "lapaz" o "scz"

---

## 🔍 TRAZABILIDAD

### Obtener Trazabilidad Completa
```http
GET /trazabilidad/{codigo}
```
**Parámetros**:
- `codigo`: Ej. "PK-2026-001"

**Respuesta**:
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

---

## 📚 CATÁLOGO

### Obtener Catálogo de Fragmentos
```http
GET /catalogo
```

**Respuesta**: Lista de fragmentos y sus asignaciones

---

## 📋 OPERACIONES

### Obtener Pendientes
```http
GET /pendientes
```

### Actualizar Estado
```http
PUT /actualizar_estado
Content-Type: application/json

{
  "codigo": "PK-2026-001",
  "estado": "En ruta"
}
```

---

## 🧪 EJEMPLOS CON CURL

### Probar conexión
```bash
curl http://localhost:5000/api/metricas
```

### Buscar paquete
```bash
curl http://localhost:5000/api/paquete/buscar/PK-2026-001
```

### Registrar movimiento
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

### Obtener tabla de paquetes
```bash
curl http://localhost:5000/api/tabla/paquete/lapaz | python -m json.tool
```

### Obtener trazabilidad
```bash
curl http://localhost:5000/api/trazabilidad/PK-2026-001 | python -m json.tool
```

---

## 🎯 CÓDIGOS DE RESPUESTA

| Código | Significado |
|--------|---|
| 200 | OK - Solicitud exitosa |
| 400 | Bad Request - Parámetros inválidos |
| 404 | Not Found - Recurso no encontrado |
| 500 | Server Error - Error en el servidor |

---

## 📝 CÓDIGOS DE ESTADO DE PAQUETE

- `Registrado` - Paquete registrado en la BD
- `En ruta` - En tránsito entre nodos
- `Inspección` - Bajo revisión aduanal
- `Listo` - Listo para envío
- `En tránsito` - Viajando a destino
- `Entregado` - Llegó a destino

---

## 📝 VALIDACIONES

### Código de Paquete
- Debe empezar con "PK"
- Formato: `PK-AAAA-NNN`
- Ej: `PK-2026-001` ✅
- Ej: `LP-2026-001` ❌

### Prioridad
- `Alta`
- `Media`
- `Baja`

### Nodo
- `lapaz` (La Paz)
- `scz` (Santa Cruz)

---

## 💡 TIPS

1. **Auto-actualización**: Dashboard se actualiza cada 30s automáticamente
2. **CORS Habilitado**: Puedes llamar desde cualquier origen
3. **Sin Autenticación**: Los endpoints son públicos (agregar en prod)
4. **Formato JSON**: Todos los endpoints retornan JSON
5. **Transacciones 2PC**: Las actualizaciones son distribuidas

---

## 🔗 ENDPOINTS POR CATEGORÍA

### Resumen Rápido
```
Dashboard:      /dashboard, /metricas, /estado_nodos, /metricas_nodo/*
Paquetes:       /paquetes*, /paquete/*, /tabla/paquete/*
Movimientos:    /movimientos*, /movimiento/registrar, /tabla/movimiento/*
Trazabilidad:   /trazabilidad/*
Catálogo:       /catalogo
Otros:          /pendientes, /actualizar_estado
```

**Total: 24 endpoints funcionales**

---

**Última actualización**: 30 de Mayo de 2026  
**API Versión**: 1.0  
**Estado**: ✅ Producción
