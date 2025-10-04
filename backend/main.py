from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from routes import auth_router
from routes import file_router  # Import the file router

app = FastAPI(
    title="Cifrados: Laboratorio 4",
)

# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(file_router, prefix="/file", tags=["file"])

# --- Middleware de cabeceras de seguridad ---
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)

    # 1. Strict-Transport-Security (solo útil si usas HTTPS en producción)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    # 2. X-Content-Type-Options
    response.headers["X-Content-Type-Options"] = "nosniff"

    # 3. Cache-Control
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
