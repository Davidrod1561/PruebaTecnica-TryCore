# RUES API

API Flask para el sistema RUES - MVP para prueba técnica (sin auth, sin extras).

## Estructura del proyecto

```
rues_api/
├── app/
│   ├── __init__.py              # Factory de la aplicación Flask
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1.py                # Endpoints REST API (process-data, update-status, health, next)
│   ├── services/
│   │   ├── __init__.py
│   │   └── transactions_service.py  # Lógica de negocio para transacciones
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── transactions_repo.py     # Acceso a datos de transacciones
│   │   └── companies_repo.py        # Acceso a datos de empresas
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py            # Modelos SQLAlchemy (Company, Transaction, AuditLog)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Configuración y variables de entorno
│   │   └── errors.py            # Manejadores de errores HTTP
│   └── db/
│       ├── __init__.py
│       └── session.py           # Configuración de sesión SQLAlchemy
├── alembic/
│   ├── versions/                # Migraciones de base de datos
│   ├── env.py                   # Configuración de Alembic
│   └── script.py.mako           # Template para migraciones
├── migrations/                  # Directorio vacío para migraciones adicionales
├── tests/
│   └── test_api.py             # Tests unitarios con SQLite en memoria
├── scripts/
│   └── migrate.sh              # Script para ejecutar migraciones
├── alembic.ini                 # Configuración de Alembic
├── docker-compose.yml          # Orquestación de contenedores (PostgreSQL + API)
├── Dockerfile                  # Imagen Docker de la aplicación
├── requirements.txt            # Dependencias Python
├── .env.example               # Variables de entorno de ejemplo
├── README.md                  # Documentación
└── run.py                     # Punto de entrada de la aplicación
```

### Flujo de datos

1. **Request** → `app/api/v1.py` (endpoints)
2. **API** → `app/services/transactions_service.py` (lógica de negocio)
3. **Service** → `app/repositories/*.py` (acceso a datos)
4. **Repository** → `app/models/models.py` (modelos SQLAlchemy)
5. **Models** → PostgreSQL (base de datos)

## Variables de entorno

```bash
APP_ENV=dev
FLASK_DEBUG=1
DB_DSN=postgresql+psycopg2://postgres:postgres@db:5432/rues
API_KEY=changeme
```

## Instalación local (sin Docker)

```bash
pip install -r requirements.txt
python run.py
```

La aplicación estará disponible en http://localhost:8000

**Nota**: Para desarrollo se recomienda usar Docker para tener PostgreSQL configurado automáticamente.

## Ejecución con Docker

```bash
docker compose up -d
```

Luego ejecutar migraciones:

```bash
sh scripts/migrate.sh
```

La aplicación estará disponible en http://localhost:8000

## Comandos útiles para Docker

### Acceder al contenedor de la aplicación
```bash
# Listar contenedores en ejecución
docker ps

# Acceder al contenedor de la API
docker exec -it rues_api-app-1 bash

# O si el nombre del contenedor es diferente, usar:
docker exec -it $(docker ps --filter "ancestor=rues_api-app" --format "{{.Names}}") bash
```

### Ejecutar migraciones desde el contenedor
```bash
# Opción 1: Ejecutar el script desde fuera del contenedor
docker exec -it rues_api-api-1 sh scripts/migrate.sh

# Opción 2: Acceder al contenedor y ejecutar manualmente
docker exec -it rues_api-api-1 bash
cd /app
sh scripts/migrate.sh
```

### Acceder a PostgreSQL para monitorear tablas
```bash
# Acceder al contenedor de PostgreSQL
docker exec -it rues_api-db-1 psql -U postgres -d rues

# Verificar el nombre exacto del contenedor si es necesario
docker ps --filter "name=db"
```

### Comandos SQL útiles para monitoreo

#### Opción 1: Consultas directas desde CMD (recomendado)

```bash
# Ver todas las tablas
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "\dt"

# Ver estructura de las tablas principales
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "\d companies"
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "\d transactions"
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "\d audit_logs"

# Consultar transacciones recientes
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT id, nit, status, created_at, updated_at FROM transactions ORDER BY created_at DESC LIMIT 10;"

# Contar transacciones por estado
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT status, COUNT(*) as cantidad FROM transactions GROUP BY status;"

# Ver empresas registradas
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT id, nit, name, created_at FROM companies ORDER BY created_at DESC;"

# Ver logs de auditoría recientes
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT id, table_name, operation, old_values, new_values, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 5;"

# Consulta personalizada con formato mejorado
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT 'Estado: ' || status || ' - Cantidad: ' || COUNT(*) as resumen FROM transactions GROUP BY status;"

# ========== CONSULTAS PARA PAYLOADS ==========

# Ver transacciones que YA TIENEN payload enviado (result_payload no nulo)
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT id, nit, status, created_at, updated_at FROM transactions WHERE result_payload IS NOT NULL ORDER BY updated_at DESC;"

# Ver transacciones PROCESADAS con sus payloads completos
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT id, nit, status, result_payload FROM transactions WHERE status = 'PROCESADO' ORDER BY updated_at DESC LIMIT 5;"

# Ver solo los NITs que ya fueron procesados exitosamente
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT nit, updated_at FROM transactions WHERE status = 'PROCESADO' ORDER BY updated_at DESC;"

# Contar cuántos tienen payload vs cuántos no
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT CASE WHEN result_payload IS NOT NULL THEN 'Con Payload' ELSE 'Sin Payload' END as estado_payload, COUNT(*) as cantidad FROM transactions GROUP BY (result_payload IS NOT NULL);"

# Ver transacciones con ERROR y sus mensajes
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT id, nit, error_code, error_msg, updated_at FROM transactions WHERE status = 'ERROR' ORDER BY updated_at DESC;"

# Ver el payload completo de una transacción específica (cambiar el NIT)
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT result_payload FROM transactions WHERE nit = '901131770' AND result_payload IS NOT NULL;"

# Ver TODOS los 11 payloads de las transacciones PROCESADAS
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT id, nit, result_payload FROM transactions WHERE status = 'PROCESADO' ORDER BY updated_at DESC;"

# Ver solo los NITs de los 11 procesados (para elegir cuál consultar)
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT id, nit, updated_at FROM transactions WHERE status = 'PROCESADO' ORDER BY updated_at DESC;"

# Ver payload formateado más legible (con saltos de línea)
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT nit, jsonb_pretty(result_payload::jsonb) as payload_formateado FROM transactions WHERE status = 'PROCESADO' LIMIT 5;"

# Ver resumen completo: cuántos enviados, procesados, con error, etc.
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT status, COUNT(*) as cantidad, COUNT(result_payload) as con_payload FROM transactions GROUP BY status ORDER BY cantidad DESC;"
```

#### Opción 2: Sesión interactiva (para consultas múltiples)

```bash
# Entrar al shell de PostgreSQL para múltiples consultas
docker exec -it rues_api-db-1 psql -U postgres -d rues

# Una vez dentro, puedes usar:
# \dt                    -- Ver tablas
# \q                     -- Salir
# SELECT * FROM transactions LIMIT 5;
```

#### Monitoreo continuo desde CMD

```bash
# Script para monitorear estados cada 5 segundos (Windows)
# Crear un archivo monitor.bat con:
@echo off
:loop
echo ========== %date% %time% ==========
docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT status, COUNT(*) as cantidad FROM transactions GROUP BY status;"
timeout /t 5 /nobreak >nul
goto loop

# O ejecutar directamente en PowerShell:
while ($true) { 
    Write-Host "========== $(Get-Date) ==========" 
    docker exec -it rues_api-db-1 psql -U postgres -d rues -c "SELECT status, COUNT(*) as cantidad FROM transactions GROUP BY status;" 
    Start-Sleep 5 
}
```

### Ver logs de los contenedores
```bash
# Ver logs de la aplicación
docker logs -f rues_api-app-1

# Ver logs de PostgreSQL
docker logs -f rues_api-db-1

# Ver logs de todos los servicios
docker compose logs -f
```

### Reiniciar servicios
```bash
# Reiniciar solo la aplicación
docker compose restart app

# Reiniciar todos los servicios
docker compose restart

# Reconstruir y reiniciar (útil después de cambios en código)
docker compose up -d --build
```

### Limpiar y resetear
```bash
# Parar y eliminar contenedores
docker compose down

# Eliminar también los volúmenes (CUIDADO: borra la base de datos)
docker compose down -v

# Reconstruir desde cero
docker compose up -d --build
```

### Verificar estado de Docker
```bash
# Ver todos los contenedores (activos e inactivos)
docker ps -a

# Ver solo contenedores del proyecto RUES
docker ps --filter "name=rues"

# Verificar uso de recursos
docker stats

# Ver redes de Docker
docker network ls

# Ver volúmenes
docker volume ls

# Inspeccionar un contenedor específico
docker inspect rues_api-app-1
```

### Troubleshooting común
```bash
# Si los contenedores no inician correctamente
docker compose logs

# Verificar si los puertos están ocupados
netstat -an | findstr :8000
netstat -an | findstr :5432

# Limpiar imágenes no utilizadas
docker image prune

# Limpiar todo el sistema Docker (CUIDADO)
docker system prune -a

# Verificar conectividad entre contenedores
docker exec -it rues_api-app-1 ping db
docker exec -it rues_api-app-1 nc -zv db 5432
```

## Autenticación

La API requiere autenticación mediante API Key en el header `X-API-Key` para la mayoría de endpoints.

### Obtener API Key temporal

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

Respuesta:
```json
{
  "api_key": "550e8400-e29b-41d4-a716-446655440000",
  "expires_in_minutes": 60
}
```

### Usar API Key en requests

```bash
curl -X POST http://localhost:8000/api/v1/process-data \
  -H "X-API-Key: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"nit":"900123456"}'
```

**Nota**: Los endpoints `/health` y `/auth/login` no requieren autenticación.

## Flujo de procesamiento completo

### Paso 1: Autenticación
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

**Respuesta:**
```json
{
  "api_key": "d68aefd4-ac86-4a62-a136-f41fdfade18c",
  "expires_in_minutes": 60
}
```

### Paso 2: Enviar NITs a la cola (Estado PENDIENTE)

Envía múltiples NITs que quedarán en cola para procesamiento:

```bash
# NIT 1
curl -X POST http://localhost:8000/api/v1/process-data \
  -H "Content-Type: application/json" \
  -H "X-API-Key: d68aefd4-ac86-4a62-a136-f41fdfade18c" \
  -d '{"nit":"900123456"}'

# NIT 2  
curl -X POST http://localhost:8000/api/v1/process-data \
  -H "Content-Type: application/json" \
  -H "X-API-Key: d68aefd4-ac86-4a62-a136-f41fdfade18c" \
  -d '{"nit":"900987654"}'

# NIT 3
curl -X POST http://localhost:8000/api/v1/process-data \
  -H "Content-Type: application/json" \
  -H "X-API-Key: d68aefd4-ac86-4a62-a136-f41fdfade18c" \
  -d '{"nit":"900555777"}'
```

**Respuesta (cada NIT):**
```json
{
  "id": 1,
  "company_id": 1,
  "nit": "900123456",
  "status": "PENDIENTE",
  "payload_in": "{\"nit\": \"900123456\"}",
  "created_at": "2025-09-28T00:45:23.186021"
}
```

### Paso 3: Obtener siguiente NIT para procesar (Estado PROCESANDO)

El worker/procesador obtiene el siguiente NIT pendiente:

```bash
curl -H "X-API-Key: d68aefd4-ac86-4a62-a136-f41fdfade18c" \
  http://localhost:8000/api/v1/next
```

**Respuesta:**
```json
{
  "id": 1,
  "company_id": 1,
  "nit": "900123456",
  "status": "PROCESANDO",
  "payload_in": "{\"nit\": \"900123456\"}",
  "updated_at": "2025-09-28T00:46:15.442837"
}
```

### Paso 4: Actualizar con datos completos (Estado PROCESADO)

Después de consultar fuentes externas (RUES, Cámara de Comercio, etc.), envía todos los datos:

```bash
curl -X POST http://localhost:8000/api/v1/update-status \
  -H "Content-Type: application/json" \
  -H "X-API-Key: d68aefd4-ac86-4a62-a136-f41fdfade18c" \
  -d '{
    "nit": "900123456",
    "status": "PROCESADO",
    "result_payload": {
      "nit": "900123456",
      "name": "ACME Corporation S.A.S",
      "address": "Calle 123 #45-67, Edificio Torre Norte, Piso 15",
      "phone": "601-555-1234",
      "email": "info@acme.com",
      "legal_representative": "Juan Carlos Pérez Rodríguez",
      "economic_activity": "Comercio al por mayor de productos tecnológicos",
      "employees_count": 150,
      "annual_revenue": 5500000000,
      "city": "Bogotá",
      "department": "Cundinamarca",
      "website": "www.acme.com",
      "founded_year": "2015",
      "tax_regime": "Régimen Común",
      "bank_account": "123456789012",
      "contact_person": "María García López",
      "secondary_phone": "601-555-5678",
      "business_type": "Sociedad por Acciones Simplificada",
      "ciiu_code": "4651",
      "rues_status": "ACTIVA",
      "verification_date": "2025-09-28",
      "data_source": "RUES + Cámara de Comercio",
      "observations": "Empresa verificada exitosamente"
    }
  }'
```

**Respuesta final:**
```json
{
  "id": 1,
  "company_id": 1,
  "nit": "900123456",
  "status": "PROCESADO",
  "result_payload": "{\"nit\": \"900123456\", \"name\": \"ACME Corporation S.A.S\", \"address\": \"Calle 123 #45-67, Edificio Torre Norte, Piso 15\", \"phone\": \"601-555-1234\", \"email\": \"info@acme.com\", \"legal_representative\": \"Juan Carlos Pérez Rodríguez\", \"economic_activity\": \"Comercio al por mayor de productos tecnológicos\", \"employees_count\": 150, \"annual_revenue\": 5500000000, \"city\": \"Bogotá\", \"department\": \"Cundinamarca\", \"website\": \"www.acme.com\", \"founded_year\": \"2015\", \"tax_regime\": \"Régimen Común\", \"bank_account\": \"123456789012\", \"contact_person\": \"María García López\", \"secondary_phone\": \"601-555-5678\", \"business_type\": \"Sociedad por Acciones Simplificada\", \"ciiu_code\": \"4651\", \"rues_status\": \"ACTIVA\", \"verification_date\": \"2025-09-28\", \"data_source\": \"RUES + Cámara de Comercio\", \"observations\": \"Empresa verificada exitosamente\"}",
  "updated_at": "2025-09-28T00:47:32.891245"
}
```

### Paso 5: Manejo de errores (Estado ERROR)

Si ocurre un error durante el procesamiento:

```bash
curl -X POST http://localhost:8000/api/v1/update-status \
  -H "Content-Type: application/json" \
  -H "X-API-Key: d68aefd4-ac86-4a62-a136-f41fdfade18c" \
  -d '{
    "nit": "900555777",
    "status": "ERROR",
    "error_code": "RUES_NOT_FOUND",
    "error_msg": "NIT no encontrado en base de datos RUES",
    "result_payload": {
      "attempted_validations": ["rues_verification", "chamber_commerce"],
      "failed_at": "rues_verification",
      "external_error": "404 - Entity not found in RUES database",
      "retry_recommended": true
    }
  }'
```

## Resumen del flujo

1. **Cola de NITs**: Envía solo NITs → Estado `PENDIENTE`
2. **Worker obtiene NIT**: `/next` → Estado `PROCESANDO`
3. **Worker consulta fuentes externas** (RUES, Cámara de Comercio, etc.)
4. **Worker actualiza con datos completos**: `/update-status` → Estado `PROCESADO` o `ERROR`

## Health check
```bash
curl http://localhost:8000/api/v1/health
```

## Documentación de endpoints

### POST /api/v1/process-data
**Función**: Crea una nueva transacción en estado PENDIENTE.

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/process-data \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: optional-key" \
  -d '{"nit":"900123456","name":"ACME Corp"}'
```

**Campos**:
- `nit` (string, requerido): NIT de la empresa
- `name` (string, opcional): Nombre de la empresa
- Header `Idempotency-Key` (opcional): Clave para evitar duplicados

**Respuestas**:
- `201`: Transacción creada exitosamente
- `400`: JSON inválido o Content-Type incorrecto
- `422`: Campo `nit` faltante

**Ejemplo respuesta exitosa**:
```json
{
  "id": 1,
  "nit": "900123456",
  "status": "PENDIENTE",
  "payload_in": "{\"nit\":\"900123456\",\"name\":\"ACME Corp\"}",
  "created_at": "2025-09-28T00:24:39.240004",
  "updated_at": "2025-09-28T00:24:39.240004"
}
```

### POST /api/v1/update-status
**Función**: Actualiza el estado de una transacción existente.

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/update-status \
  -H "Content-Type: application/json" \
  -d '{
    "nit": "900123456",
    "status": "PROCESADO",
    "result_payload": {"success": true},
    "error_code": null,
    "error_msg": null
  }'
```

**Campos**:
- `id` o `nit` (requerido): Identificador de la transacción
- `status` (string, requerido): Nuevo estado ("PENDIENTE", "PROCESANDO", "PROCESADO", "ERROR")
- `result_payload` (object, opcional): Resultado del procesamiento
- `error_code` (string, opcional): Código de error si aplica
- `error_msg` (string, opcional): Mensaje de error si aplica

**Respuestas**:
- `200`: Estado actualizado exitosamente
- `400`: JSON inválido
- `404`: Transacción no encontrada
- `422`: Campos requeridos faltantes o status inválido

### GET /api/v1/next
**Función**: Obtiene la siguiente transacción pendiente y la marca como PROCESANDO automáticamente.

**Request**:
```bash
curl http://localhost:8000/api/v1/next
```

**Respuestas**:
- `200`: Transacción encontrada y marcada como PROCESANDO
- `204`: No hay transacciones pendientes

**Ejemplo respuesta exitosa**:
```json
{
  "id": 2,
  "nit": "900987654",
  "status": "PROCESANDO",
  "payload_in": "{\"nit\":\"900987654\",\"name\":\"TEST COMPANY\"}",
  "updated_at": "2025-09-28T00:25:20.477837"
}
```

### GET /api/v1/health
**Función**: Verifica que la API esté funcionando correctamente.

**Request**:
```bash
curl http://localhost:8000/api/v1/health
```

**Respuestas**:
- `200`: API funcionando correctamente

**Respuesta**:
```json
{
  "status": "ok"
}
```

## Control de errores

### Códigos de error HTTP
- **400 Bad Request**: JSON malformado o Content-Type incorrecto
- **404 Not Found**: Recurso no encontrado (transacción inexistente)
- **422 Unprocessable Entity**: Validaciones fallidas (campos requeridos faltantes, valores inválidos)

### Formato de errores
Todos los errores devuelven JSON con el formato:
```json
{
  "error": "Descripción del error"
}
```

### Ejemplos de errores comunes

**Campo requerido faltante**:
```bash
# Request sin nit
curl -X POST http://localhost:8000/api/v1/process-data \
  -H "Content-Type: application/json" \
  -d '{"name":"Test"}'

# Response: 422
{
  "error": "Campo 'nit' es requerido"
}
```

**Status inválido**:
```bash
# Request con status inválido
curl -X POST http://localhost:8000/api/v1/update-status \
  -H "Content-Type: application/json" \
  -d '{"nit":"123","status":"INVALID"}'

# Response: 422
{
  "error": "Status debe ser uno de: PENDIENTE, PROCESANDO, PROCESADO, ERROR"
}
```

**Transacción no encontrada**:
```bash
# Request con ID inexistente
curl -X POST http://localhost:8000/api/v1/update-status \
  -H "Content-Type: application/json" \
  -d '{"id":999,"status":"PROCESADO"}'

# Response: 404
{
  "error": "Transacción no encontrada"
}
```
