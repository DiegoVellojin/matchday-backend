import os
import firebase_admin
from firebase_admin import credentials
from fastapi import FastAPI
from app.modules.auth.presentation.router import router as auth_router
from app.modules.users.presentation.router import router as users_router
from app.modules.teams.presentation.router import router as teams_router
from app.modules.catalogs.presentation.router import router as catalogs_router
from app.modules.notifications.presentation.router import router as notifications_router

import json

# Inicializar Firebase Admin SDK
cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "firebase-service-account.json")
firebase_env = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")

if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
elif firebase_env:
    try:
        cred_dict = json.loads(firebase_env)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Error al inicializar Firebase desde ENV en Render: {e}")


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
app.include_router(teams_router, prefix="/api/v1/teams", tags=["Teams"])
app.include_router(catalogs_router, prefix="/api/v1/catalogs", tags=["Catalogs"])
app.include_router(notifications_router, prefix="/api/v1", tags=["Notifications"])