"""
Aplicación principal FastAPI para sistema de gestión de archivos con firmas digitales.
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from routes import auth_router, file_router
from config.settings import ALLOWED_ORIGINS
from utils.logging_config import setup_logger

# Configurar logger de la aplicación
app_logger = setup_logger("main")

app = FastAPI(
    title="Cifrados: Laboratorio 4",
    description="Sistema de gestión de archivos con firmas digitales RSA y ECC",
    version="1.0.0"
)

# ==================== CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app_logger.info(f"CORS configurado con orígenes: {ALLOWED_ORIGINS}")


# ==================== MIDDLEWARE DE SEGURIDAD ====================


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Middleware para agregar cabeceras de seguridad a todas las respuestas.
    
    Cabeceras incluidas:
    - Strict-Transport-Security: Forzar HTTPS
    - X-Content-Type-Options: Prevenir MIME sniffing
    - Cache-Control: Controlar caché del navegador
    """
    response: Response = await call_next(request)

    # 1. Strict-Transport-Security (HSTS)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    # 2. X-Content-Type-Options
    response.headers["X-Content-Type-Options"] = "nosniff"

    # 3. Cache-Control
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# ==================== ROUTERS ====================
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(file_router, prefix="/file", tags=["file"])
app_logger.info("Routers configurados: /auth, /file")


# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la aplicación."""
    return {"status": "ok", "service": "cifrados-lab4"}


# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Evento ejecutado al iniciar la aplicación."""
    app_logger.info("=" * 50)
    app_logger.info("Aplicación FastAPI iniciada")
    app_logger.info("Título: Cifrados - Laboratorio 4")
    app_logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento ejecutado al detener la aplicación."""
    app_logger.info("Aplicación FastAPI detenida")


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn

    app_logger.info("Iniciando servidor Uvicorn...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )