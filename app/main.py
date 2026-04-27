from fastapi import FastAPI
from app.modules.auth.presentation.router import router as auth_router
from app.modules.users.presentation.router import router as users_router

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="MatchDay API",
    description="Backend en Clean Architecture para la gestión de retos y equipos de fútbol",
    version="1.0.0",
)

@app.get("/", tags=["Health"])
async def health_check():
    """
    Endpoint base para verificar que el servidor está arriba.
    """
    return {
        "status": "online",
        "message": "MatchDay Backend is up and running!",
        "architecture": "Clean Architecture / Layered Monolith"
    }

# Registrar los "routers" de cada módulo
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])