#!/bin/bash
# Script de testing para el sistema de préstamo de libros

set -e

API_URL="http://localhost:5000"

echo "=== Testing Sistema de Préstamo de Libros ==="
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Esperando a que el servicio esté listo...${NC}"
for i in {1..10}; do
  if curl -s $API_URL/health > /dev/null; then
    echo -e "${GREEN}✓ Servicio está listo${NC}"
    break
  fi
  echo "Intento $i/10..."
  sleep 2
done

echo ""
echo -e "${BLUE}=== 1. Health Check ===${NC}"
curl -s $API_URL/health | python -m json.tool

echo ""
echo -e "${BLUE}=== 2. Información del Servicio ===${NC}"
curl -s $API_URL/api/info | python -m json.tool

echo ""
echo -e "${BLUE}=== 3. Obtener todos los libros ===${NC}"
curl -s $API_URL/api/libros | python -m json.tool

echo ""
echo -e "${BLUE}=== 4. Crear un nuevo libro ===${NC}"
LIBRO_RESPONSE=$(curl -s -X POST $API_URL/api/libros \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "El Hobbit",
    "autor": "J.R.R. Tolkien",
    "isbn": "978-8445000695",
    "cantidad_total": 2
  }')
echo $LIBRO_RESPONSE | python -m json.tool
LIBRO_ID=$(echo $LIBRO_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "ID del libro creado: $LIBRO_ID"

echo ""
echo -e "${BLUE}=== 5. Obtener un libro específico ===${NC}"
curl -s $API_URL/api/libros/$LIBRO_ID | python -m json.tool

echo ""
echo -e "${BLUE}=== 6. Crear un préstamo ===${NC}"
PRESTAMO_RESPONSE=$(curl -s -X POST $API_URL/api/prestamos \
  -H "Content-Type: application/json" \
  -d "{
    \"libro_id\": $LIBRO_ID,
    \"usuario_nombre\": \"Ana Rodríguez\",
    \"usuario_email\": \"ana@example.com\",
    \"dias_prestamo\": 7
  }")
echo $PRESTAMO_RESPONSE | python -m json.tool
PRESTAMO_ID=$(echo $PRESTAMO_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "ID del préstamo creado: $PRESTAMO_ID"

echo ""
echo -e "${BLUE}=== 7. Obtener todos los préstamos ===${NC}"
curl -s $API_URL/api/prestamos | python -m json.tool

echo ""
echo -e "${BLUE}=== 8. Obtener préstamos de un usuario ===${NC}"
curl -s "$API_URL/api/prestamos/usuario/ana@example.com" | python -m json.tool

echo ""
echo -e "${BLUE}=== 9. Obtener prestamos activos ===${NC}"
curl -s "$API_URL/api/prestamos?activos=true" | python -m json.tool

echo ""
echo -e "${BLUE}=== 10. Estadísticas ===${NC}"
curl -s $API_URL/api/estadisticas | python -m json.tool

echo ""
echo -e "${BLUE}=== 11. Devolver un libro ===${NC}"
curl -s -X POST $API_URL/api/prestamos/$PRESTAMO_ID/devolver | python -m json.tool

echo ""
echo -e "${BLUE}=== 12. Verificar disponibilidad actualizada ===${NC}"
curl -s $API_URL/api/libros/$LIBRO_ID | python -m json.tool

echo ""
echo -e "${GREEN}=== Tests Completados ===${NC}"
