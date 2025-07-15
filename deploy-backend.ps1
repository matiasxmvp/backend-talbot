# Script de despliegue del backend a AWS Elastic Beanstalk
# Ejecutar desde el directorio raíz del proyecto

Write-Host "🚀 Iniciando despliegue del backend de Talbot Hotels en AWS Elastic Beanstalk..." -ForegroundColor Green
Write-Host "📋 Verificando configuración de archivos..." -ForegroundColor Yellow

# Verificar archivos críticos
$criticalFiles = @(
    "backend/application.py",
    "backend/Procfile",
    "backend/.ebextensions/01_packages.config",
    "backend/.ebextensions/02_environment.config",
    "backend/requirements.txt"
)

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file encontrado" -ForegroundColor Green
    } else {
        Write-Host "❌ $file NO encontrado" -ForegroundColor Red
        exit 1
    }
}

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend\main.py")) {
    Write-Host "❌ Error: Ejecuta este script desde el directorio raíz del proyecto" -ForegroundColor Red
    exit 1
}

# Verificar que AWS CLI está instalado
try {
    aws --version | Out-Null
} catch {
    Write-Host "❌ Error: AWS CLI no está instalado. Instálalo desde https://aws.amazon.com/cli/" -ForegroundColor Red
    exit 1
}

# Verificar que EB CLI está instalado
try {
    eb --version | Out-Null
} catch {
    Write-Host "❌ Error: EB CLI no está instalado. Instálalo con: pip install awsebcli" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Verificaciones completadas" -ForegroundColor Green

# Cambiar al directorio backend
Set-Location backend

# Crear archivo .env para producción si no existe
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creando archivo .env para producción..." -ForegroundColor Yellow
    
    # Solicitar información al usuario
    $dbUrl = Read-Host "Ingresa la URL de la base de datos PostgreSQL (DATABASE_URL)"
    $secretKey = Read-Host "Ingresa una clave secreta segura (SECRET_KEY)"
    $corsOrigins = Read-Host "Ingresa el dominio de tu frontend en Amplify (ej: https://main.d1234567890.amplifyapp.com)"
    
    # Crear archivo .env
    @"
APP_NAME="Talbot Hotels API"
DEBUG=false
VERSION="1.0.0"
ENVIRONMENT="production"

DATABASE_URL="$dbUrl"

SECRET_KEY="$secretKey"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

PORT=8000
HOST="0.0.0.0"

CORS_ORIGINS="$corsOrigins"

LOG_LEVEL="INFO"
LOG_FILE="logs/app.log"

RATE_LIMIT_PER_MINUTE=60
SESSION_TIMEOUT_MINUTES=60

ENVIRONMENT="production"
"@ | Out-File -FilePath ".env" -Encoding UTF8
    
    Write-Host "✅ Archivo .env creado" -ForegroundColor Green
}

# Verificar que requirements.txt existe
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Error: No se encontró requirements.txt" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Preparando archivos para despliegue..." -ForegroundColor Yellow

# Crear archivo de aplicación EB si no existe
if (-not (Test-Path ".elasticbeanstalk\config.yml")) {
    Write-Host "🔧 Inicializando aplicación Elastic Beanstalk..." -ForegroundColor Yellow
    
    # Inicializar EB
    eb init --platform python-3.11 --region us-east-1 talbot-backend
    
    Write-Host "✅ Aplicación EB inicializada" -ForegroundColor Green
}

Write-Host "🚀 Desplegando a Elastic Beanstalk..." -ForegroundColor Yellow

# Crear entorno si no existe
try {
    eb status | Out-Null
} catch {
    Write-Host "🔧 Creando entorno de producción..." -ForegroundColor Yellow
    eb create production --instance-type t3.micro --platform-version "3.11"
}

# Desplegar
eb deploy

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ ¡Despliegue completado exitosamente!" -ForegroundColor Green
    Write-Host "🌐 Obteniendo URL de la aplicación..." -ForegroundColor Yellow
    eb status
    Write-Host "📋 Para ver los logs: eb logs" -ForegroundColor Cyan
    Write-Host "🔧 Para configurar variables de entorno: eb setenv VARIABLE=valor" -ForegroundColor Cyan
} else {
    Write-Host "❌ Error durante el despliegue. Revisa los logs con: eb logs" -ForegroundColor Red
}

# Volver al directorio raíz
Set-Location ..

Write-Host "🎉 Script de despliegue completado" -ForegroundColor Green