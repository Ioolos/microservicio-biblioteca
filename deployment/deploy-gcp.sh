#!/bin/bash
# Script de despliegue en Google Cloud (GCP)

set -e

echo "=== Despliegue en Google Cloud ==="

# Variables
PROJECT_ID=${GCP_PROJECT_ID:-my-project}
REGION="us-central1"
ZONE="${REGION}-a"
SERVICE_NAME="microservicio-simple"
CLUSTER_NAME="microservicio-cluster"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# 1. Configurar proyecto GCP
echo "Configurando proyecto GCP..."
gcloud config set project $PROJECT_ID

# 2. Habilitar APIs necesarias
echo "Habilitando APIs..."
gcloud services enable container.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 3. Crear cluster GKE (si no existe)
echo "Creando cluster GKE..."
gcloud container clusters create $CLUSTER_NAME \
  --zone $ZONE \
  --num-nodes 2 \
  --machine-type n1-standard-1 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 3 \
  --enable-autorepair \
  --enable-autoupgrade || echo "Cluster ya existe"

# 4. Obtener credenciales del cluster
echo "Obteniendo credenciales del cluster..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE

# 5. Construir y subir imagen a Container Registry
echo "Construyendo y subiendo imagen..."
gcloud builds submit \
  --config=deployment/gcp-cloudbuild.yaml \
  --substitutions="_SERVICE_NAME=$SERVICE_NAME,_REGION=$REGION"

# 6. Actualizar deployment manifest
echo "Actualizando manifest con PROJECT_ID..."
sed "s/PROJECT_ID/$PROJECT_ID/g" deployment/gcp-k8s-deployment.yaml > /tmp/deployment.yaml

# 7. Desplegar en GKE
echo "Desplegando en GKE..."
kubectl apply -f /tmp/deployment.yaml

# 8. Esperar a que esté listo
echo "Esperando a que el servicio esté listo..."
kubectl rollout status deployment/microservicio-simple

# 9. Obtener IP externa
echo "Obteniendo IP externa..."
SERVICE_IP=$(kubectl get service microservicio-simple-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -z "$SERVICE_IP" ]; then
  echo "Asignando IP externa, por favor espere..."
  sleep 10
  SERVICE_IP=$(kubectl get service microservicio-simple-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
fi

echo "=== Despliegue completado ==="
echo "Servicio disponible en: http://$SERVICE_IP"
echo "Health check: http://$SERVICE_IP/health"
echo ""
echo "Comandos útiles:"
echo "  Ver logs: kubectl logs -f deployment/microservicio-simple"
echo "  Ver estado: kubectl get pods"
echo "  Escalar: kubectl scale deployment microservicio-simple --replicas=3"
