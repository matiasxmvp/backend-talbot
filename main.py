# main.py - Punto de entrada principal de la aplicación FastAPI

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import auth, hotels
from app.core.config import settings

# Crear la instancia de la aplicación FastAPI
app = FastAPI(
    title="API TALBOT HOTELS",
    description="Sistema de gestión Talbot Hotels",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS para permitir peticiones desde el frontend
# Usa configuración dinámica desde variables de entorno
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Configuración dinámica desde .env
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Métodos específicos
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ],
)

# Incluir los routers de Talbot Hotels
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación Talbot Hotels"])
app.include_router(hotels.router, prefix="/api/v1", tags=["Gestión de Hoteles"])

# Endpoint de salud
@app.get("/")
async def root():
    """
    Endpoint raíz - Bienvenida a Talbot Hotels API
    
    Endpoint público que proporciona información básica sobre la API
    y enlaces útiles para desarrolladores. No requiere autenticación.
    
    Returns:
        dict: Información de bienvenida, versión y enlaces de documentación
        
    Example:
        GET /
        Response:
        {
            "message": "¡Bienvenido a Talbot Hotels API!",
            "version": "1.0.0",
            "hotel_chain": "Talbot Hotels",
            "documentation": "/docs"
        }
    """
    return {
        "message": "¡Bienvenido a Talbot Hotels API!", 
        "version": "1.0.0",
        "hotel_chain": "Talbot Hotels",
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud
    
    Endpoint utilizado para monitoreo y verificación del estado de la API.
    Útil para load balancers, sistemas de monitoreo y health checks automáticos.
    Siempre retorna un estado positivo si la aplicación está funcionando.
    
    Returns:
        dict: Estado de salud de la aplicación
        
    Use Cases:
        - Monitoreo de infraestructura
        - Health checks de contenedores Docker
        - Verificación de disponibilidad del servicio
        - Pruebas de conectividad básica
        
    Example:
        GET /health
        Response:
        {
            "status": "healthy"
        }
    """
    return {"status": "healthy"}

# if __name__ == "__main__":
#     import uvicorn
#     # Configuración del puerto para la aplicación
#     uvicorn.run(app, host="0.0.0.0", port=8000)