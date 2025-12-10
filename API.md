# Documentación API - Sistema de Préstamo de Libros

## Base URL
```
http://localhost:5000
```

## Endpoints

### Health & Info

#### Health Check
```
GET /health
```
Respuesta:
```json
{
  "status": "healthy",
  "service": "Sistema de Préstamo de Libros",
  "version": "1.0.0",
  "environment": "production"
}
```

#### Información del Servicio
```
GET /api/info
```

---

### Gestión de Libros

#### Listar todos los libros
```
GET /api/libros
```
Respuesta:
```json
{
  "total": 5,
  "libros": [
    {
      "id": 1,
      "titulo": "Cien años de soledad",
      "autor": "Gabriel García Márquez",
      "isbn": "978-8401042015",
      "cantidad_total": 3,
      "cantidad_disponible": 2,
      "fecha_creacion": "2024-01-01T10:00:00",
      "prestamos_activos": 1
    }
  ]
}
```

#### Obtener un libro específico
```
GET /api/libros/{id}
```
Parámetros:
- `id` (integer, path) - ID del libro

#### Crear un nuevo libro
```
POST /api/libros
```
Body:
```json
{
  "titulo": "El Hobbit",
  "autor": "J.R.R. Tolkien",
  "isbn": "978-8445000695",
  "cantidad_total": 2
}
```

**Campos requeridos:**
- `titulo` (string)
- `autor` (string)

**Campos opcionales:**
- `isbn` (string)
- `cantidad_total` (integer, default: 1)

Respuesta: `201 Created`

#### Actualizar un libro
```
PUT /api/libros/{id}
```
Body:
```json
{
  "titulo": "Nuevo título",
  "autor": "Nuevo autor",
  "cantidad_total": 5
}
```

#### Eliminar un libro
```
DELETE /api/libros/{id}
```
Respuesta: `200 OK`

---

### Gestión de Préstamos

#### Listar todos los préstamos
```
GET /api/prestamos
```
Parámetros opcionales:
- `activos=true` - Solo préstamos sin devolver

Respuesta:
```json
{
  "total": 3,
  "prestamos": [
    {
      "id": 1,
      "libro_id": 1,
      "libro_titulo": "Cien años de soledad",
      "usuario_nombre": "Juan Pérez",
      "usuario_email": "juan@example.com",
      "fecha_prestamo": "2024-01-01T10:00:00",
      "fecha_vencimiento": "2024-01-15T10:00:00",
      "fecha_devolucion": null,
      "devuelto": false,
      "dias_restantes": 5
    }
  ]
}
```

#### Crear un préstamo
```
POST /api/prestamos
```
Body:
```json
{
  "libro_id": 1,
  "usuario_nombre": "Juan Pérez",
  "usuario_email": "juan@example.com",
  "dias_prestamo": 14
}
```

**Campos requeridos:**
- `libro_id` (integer)
- `usuario_nombre` (string)
- `usuario_email` (string)

**Campos opcionales:**
- `dias_prestamo` (integer, default: 14)

Respuesta: `201 Created`

#### Obtener préstamos de un usuario
```
GET /api/prestamos/usuario/{email}
```
Parámetros:
- `email` (string, path) - Email del usuario

#### Devolver un libro
```
POST /api/prestamos/{id}/devolver
```
Respuesta:
```json
{
  "id": 1,
  "libro_id": 1,
  "libro_titulo": "Cien años de soledad",
  "usuario_nombre": "Juan Pérez",
  "usuario_email": "juan@example.com",
  "fecha_prestamo": "2024-01-01T10:00:00",
  "fecha_vencimiento": "2024-01-15T10:00:00",
  "fecha_devolucion": "2024-01-10T15:30:00",
  "devuelto": true,
  "dias_restantes": 0,
  "multa": "Sin multa",
  "dias_retraso": 0
}
```

---

### Estadísticas

#### Obtener estadísticas de la biblioteca
```
GET /api/estadisticas
```
Respuesta:
```json
{
  "total_libros": 8,
  "total_copias": 20,
  "copias_disponibles": 15,
  "copias_prestadas": 5,
  "prestamos_activos": 5,
  "prestamos_vencidos": 1
}
```

---

## Códigos de Estado

| Código | Significado |
|--------|------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Datos inválidos |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Conflicto (ej: libro no disponible) |
| 500 | Internal Server Error - Error del servidor |

---

## Ejemplos de uso con cURL

### Crear un libro
```bash
curl -X POST http://localhost:5000/api/libros \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "1984",
    "autor": "George Orwell",
    "isbn": "978-0451524935",
    "cantidad_total": 3
  }'
```

### Crear un préstamo
```bash
curl -X POST http://localhost:5000/api/prestamos \
  -H "Content-Type: application/json" \
  -d '{
    "libro_id": 1,
    "usuario_nombre": "María García",
    "usuario_email": "maria@example.com",
    "dias_prestamo": 21
  }'
```

### Devolver un libro
```bash
curl -X POST http://localhost:5000/api/prestamos/1/devolver
```

### Obtener estadísticas
```bash
curl http://localhost:5000/api/estadisticas | python -m json.tool
```

---

## Notas Importantes

1. **Multas**: Se calcula automáticamente a razón de $2 por día de retraso
2. **Disponibilidad**: Se actualiza automáticamente al crear/devolver préstamos
3. **Validaciones**: 
   - No se puede prestar un libro sin disponibilidad
   - No se puede crear un libro con título duplicado
   - No se puede devolver un libro dos veces
