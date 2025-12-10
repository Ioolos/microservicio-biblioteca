# Sistema de Préstamo de Libros - Microservicio Portable

Un microservicio REST de gestión de biblioteca basado en Flask que se puede desplegar fácilmente en AWS, Azure y Google Cloud Platform.

## Características

- ✅ API REST completa para gestión de libros y préstamos
- ✅ Base de datos SQLite con modelos normalizados
- ✅ Validación de disponibilidad y multas automáticas
- ✅ Containerizado con Docker
- ✅ Health checks integrados
- ✅ Fácil de desplegar en múltiples plataformas cloud
- ✅ Documentación API completa

## Estructura del Proyecto

```
├── src/
│   └── app.py                    # Aplicación Flask con endpoints
├── deployment/
│   ├── aws-ecs-task-def.json     # Definición de tarea para ECS
│   ├── aws-cloudformation.yaml   # Template CloudFormation
│   ├── deploy-aws.sh             # Script de despliegue AWS
│   ├── azure-template.json       # ARM Template
│   ├── deploy-azure.sh           # Script de despliegue Azure
│   ├── gcp-k8s-deployment.yaml   # Manifests Kubernetes
│   ├── gcp-cloudbuild.yaml       # Cloud Build config
│   └── deploy-gcp.sh             # Script de despliegue GCP
├── Dockerfile                    # Configuración Docker
├── requirements.txt              # Dependencias Python
├── initialization.py             # Script para inicializar BD
├── test-biblioteca.sh            # Tests de la API
├── .env.example                  # Variables de ejemplo
├── API.md                        # Documentación completa de API
└── README.md                     # Este archivo
```

## Endpoints Principales

### Libros
- `GET /api/libros` - Listar todos los libros
- `GET /api/libros/{id}` - Obtener un libro
- `POST /api/libros` - Crear nuevo libro
- `PUT /api/libros/{id}` - Actualizar libro
- `DELETE /api/libros/{id}` - Eliminar libro

### Préstamos
- `GET /api/prestamos` - Listar préstamos
- `POST /api/prestamos` - Crear préstamo
- `GET /api/prestamos/usuario/{email}` - Préstamos de un usuario
- `POST /api/prestamos/{id}/devolver` - Devolver libro

### Otros
- `GET /health` - Health check
- `GET /api/info` - Información del servicio
- `GET /api/estadisticas` - Estadísticas de la biblioteca

## Configuración

Copiar `.env.example` a `.env` y ajustar las variables:

```bash
cp .env.example .env
```

### Variables de Entorno

| Variable | Valor por Defecto | Descripción |
|----------|------------------|-------------|
| SERVICE_NAME | Sistema de Préstamo de Libros | Nombre del servicio |
| SERVICE_VERSION | 1.0.0 | Versión del servicio |
| ENVIRONMENT | development | production o development |
| PORT | 5000 | Puerto de escucha |
| DEBUG | False | Modo debug |
| DATABASE_URL | sqlite:///libros.db | URL de la base de datos |

## Ejecución Local

### Con Python

```bash
# Crear ambiente virtual (opcional pero recomendado)
python -m venv venv

# Activar ambiente virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos con datos de ejemplo
python initialization.py

# Ejecutar aplicación
python src/app.py
```

El servicio estará disponible en `http://localhost:5000`

### Con Docker

```bash
# Construir imagen
docker build -t biblioteca-microservicio .

# Ejecutar contenedor
docker run -p 5000:5000 biblioteca-microservicio

# O con volumen para persistencia
docker run -p 5000:5000 -v $(pwd):/app biblioteca-microservicio
```

### Con Docker Compose (desarrollo)

```bash
# Iniciar servicios (microservicio + Nginx load balancer)
docker-compose up -d

# Ver logs
docker-compose logs -f microservicio

# Detener servicios
docker-compose down
```

## Testing Local

### Health Check
```bash
curl http://localhost:5000/health
```

### Listar todos los libros
```bash
curl http://localhost:5000/api/libros
```

### Crear un libro
```bash
curl -X POST http://localhost:5000/api/libros \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "El Quijote",
    "autor": "Miguel de Cervantes",
    "isbn": "978-8491810254",
    "cantidad_total": 2
  }'
```

### Crear un préstamo
```bash
curl -X POST http://localhost:5000/api/prestamos \
  -H "Content-Type: application/json" \
  -d '{
    "libro_id": 1,
    "usuario_nombre": "Juan Pérez",
    "usuario_email": "juan@example.com",
    "dias_prestamo": 14
  }'
```

### Obtener estadísticas
```bash
curl http://localhost:5000/api/estadisticas
```

### Script completo de testing
```bash
chmod +x test-biblioteca.sh
./test-biblioteca.sh
```

### Más ejemplos en [API.md](API.md)

## Despliegue en AWS

### Opción 1: Con Script

```bash
chmod +x deployment/deploy-aws.sh
./deployment/deploy-aws.sh
```

### Opción 2: Con CloudFormation

```bash
aws cloudformation create-stack \
  --stack-name biblioteca-microservicio \
  --template-body file://deployment/aws-cloudformation.yaml \
  --region us-east-1
```

**Requisitos:**
- AWS CLI configurado
- Permisos para ECR, ECS y CloudFormation

## Despliegue en Azure

```bash
chmod +x deployment/deploy-azure.sh
./deployment/deploy-azure.sh
```

**Requisitos:**
- Azure CLI instalado y autenticado
- Suscripción activa

## Despliegue en Google Cloud

```bash
# Configurar variables
export GCP_PROJECT_ID="tu-proyecto-gcp"

chmod +x deployment/deploy-gcp.sh
./deployment/deploy-gcp.sh
```

**Requisitos:**
- Google Cloud SDK instalado y autenticado
- Proyecto GCP creado
- APIs habilitadas (Container Registry, GKE, Cloud Build)

## Testing

### Verificar que está corriendo

```bash
curl http://localhost:5000/health
```

### Obtener información del servicio

```bash
curl http://localhost:5000/api/info
```

### Saludar

```bash
curl http://localhost:5000/api/greet
```

## Escalado

### AWS ECS
```bash
aws ecs update-service --cluster default --service microservicio-simple --desired-count 3
```

### Azure Container Instances
```bash
az container create ... # Crear nuevas instancias
```

### Google Cloud GKE
```bash
kubectl scale deployment microservicio-simple --replicas=3
```

## Logs

### AWS
```bash
aws logs tail /ecs/microservicio-simple --follow
```

### Azure
```bash
az container logs --resource-group microservicio-rg --name microservicio-simple
```

### Google Cloud
```bash
kubectl logs -f deployment/microservicio-simple
```

## Limpieza

### AWS
```bash
aws cloudformation delete-stack --stack-name microservicio-simple
```

### Azure
```bash
az group delete --name microservicio-rg
```

### Google Cloud
```bash
kubectl delete deployment microservicio-simple
kubectl delete service microservicio-simple-service
gcloud container clusters delete microservicio-cluster --zone us-central1-a
```

## Monitoreo

Todos los servicios incluyen health checks que se ejecutan automáticamente:
- AWS ECS: Health checks cada 30 segundos
- Azure: Monitoreo integrado en Container Instances
- GCP: Liveness y Readiness probes en Kubernetes

## Costos Estimados (Aproximados)

### AWS
- ECR: ~$0.07 por GB almacenado
- ECS Fargate: ~$0.04522 por vCPU/hora + $0.004731 por GB/hora

### Azure
- ACR: ~$5-100 USD/mes según almacenamiento
- Container Instances: ~$0.0000231 por GB/segundo

### Google Cloud
- Container Registry: ~$0.026 por GB/mes
- GKE: Gratis el cluster + costo de instancias (~$20-100/mes)

## Troubleshooting

### Contenedor no inicia
- Verificar logs: `docker logs <container_id>`
- Validar variables de entorno
- Confirmar que el puerto 5000 está disponible

### Health check falla
- Verificar que la aplicación está corriendo
- Validar endpoint `/health`
- Revisar logs del contenedor

### Imagen no encuentra en registro
- Confirmar que la imagen fue pusheada correctamente
- Verificar credenciales del registro
- Validar nombre y tag de la imagen

## Licencia

MIT

## Soporte

Para problemas o sugerencias, revisar los logs específicos de cada plataforma cloud.
