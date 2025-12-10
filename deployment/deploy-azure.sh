#!/bin/bash
# Script de despliegue en Azure Container Registry y Container Instances

set -e

echo "=== Despliegue en Azure ==="

# Variables
RESOURCE_GROUP="microservicio-rg"
REGISTRY_NAME="microsrvregistry"
SERVICE_NAME="microservicio-simple"
LOCATION="eastus"
CONTAINER_NAME="microservicio-simple"

# 1. Crear grupo de recursos si no existe
echo "Creando grupo de recursos..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# 2. Crear Azure Container Registry
echo "Creando Azure Container Registry..."
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic

# 3. Obtener credenciales del registro
REGISTRY_URL=$(az acr show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
echo "Registry URL: $REGISTRY_URL"

# 4. Login en ACR
echo "Login en Azure Container Registry..."
az acr login --name $REGISTRY_NAME

# 5. Construir imagen Docker
echo "Construyendo imagen Docker..."
docker build -t $SERVICE_NAME:latest .
docker tag $SERVICE_NAME:latest $REGISTRY_URL/$SERVICE_NAME:latest

# 6. Subir imagen a ACR
echo "Subiendo imagen a ACR..."
docker push $REGISTRY_URL/$SERVICE_NAME:latest

# 7. Desplegar Container Instance
echo "Desplegando Container Instance..."
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --image $REGISTRY_URL/$SERVICE_NAME:latest \
  --registry-login-server $REGISTRY_URL \
  --registry-username $(az acr credential show --name $REGISTRY_NAME --query username -o tsv) \
  --registry-password $(az acr credential show --name $REGISTRY_NAME --query "passwords[0].value" -o tsv) \
  --ports 5000 \
  --environment-variables SERVICE_NAME=$SERVICE_NAME ENVIRONMENT=production \
  --cpu 1 \
  --memory 1

# 8. Obtener IP pública
CONTAINER_IP=$(az container show \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --query ipAddress.ip -o tsv)

echo "=== Despliegue completado ==="
echo "Servicio disponible en: http://$CONTAINER_IP:5000"
echo "Health check: http://$CONTAINER_IP:5000/health"
