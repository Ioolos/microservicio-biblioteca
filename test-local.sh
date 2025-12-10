#!/bin/bash
# Script local para probar el microservicio

set -e

echo "=== Testing Local Microservicio ==="

SERVICE_URL="http://localhost:5000"

echo "Esperando a que el servicio esté listo..."
for i in {1..10}; do
  if curl -s $SERVICE_URL/health > /dev/null; then
    echo "✓ Servicio está listo"
    break
  fi
  echo "Intento $i/10..."
  sleep 2
done

echo ""
echo "=== Testing Endpoints ==="

echo -e "\n1. Health Check:"
curl -s $SERVICE_URL/health | python -m json.tool

echo -e "\n2. Info del Servicio:"
curl -s $SERVICE_URL/api/info | python -m json.tool

echo -e "\n3. Saludo:"
curl -s $SERVICE_URL/api/greet | python -m json.tool

echo -e "\n4. Endpoint no existente (404):"
curl -s $SERVICE_URL/api/inexistente || true

echo -e "\n\n=== Tests Completados ==="
