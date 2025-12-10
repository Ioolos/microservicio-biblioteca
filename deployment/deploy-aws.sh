#!/bin/bash
# Script de despliegue en AWS ECR y ECS

set -e

echo "=== Despliegue en AWS ==="

# Variables
AWS_REGION=${AWS_REGION:-us-east-1}
ECR_REPO_NAME="microservicio-simple"
SERVICE_NAME="microservicio-simple"
CLUSTER_NAME="default"

# 1. Obtener URL de ECR
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "ECR Registry: $ECR_REGISTRY"

# 2. Crear repositorio si no existe
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION || \
aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION

# 3. Login en ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# 4. Construir imagen Docker
echo "Construyendo imagen Docker..."
docker build -t $ECR_REPO_NAME:latest .
docker tag $ECR_REPO_NAME:latest $ECR_REGISTRY/$ECR_REPO_NAME:latest

# 5. Subir imagen a ECR
echo "Subiendo imagen a ECR..."
docker push $ECR_REGISTRY/$ECR_REPO_NAME:latest

# 6. Actualizar task definition
echo "Actualizando task definition..."
sed "s|YOUR_ECR_REGISTRY|$ECR_REGISTRY|g" deployment/aws-ecs-task-def.json > /tmp/task-def.json
aws ecs register-task-definition --cli-input-json file:///tmp/task-def.json --region $AWS_REGION

echo "=== Despliegue completado ==="
echo "Pasos siguientes:"
echo "1. Crear/actualizar servicio ECS:"
echo "   aws ecs create-service --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --task-definition $SERVICE_NAME --desired-count 1 --launch-type FARGATE --network-configuration awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx]}"
echo "2. O actualizar servicio existente:"
echo "   aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment"
