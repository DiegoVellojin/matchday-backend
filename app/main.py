import os
import firebase_admin
from firebase_admin import credentials
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.exceptions import MatchDayException
from app.core.database import SessionLocal

# Importación de Routers
from app.modules.auth.presentation.router import router as auth_router
from app.modules.users.presentation.router import router as users_router
from app.modules.teams.presentation.router import router as teams_router
from app.modules.catalogs.presentation.router import router as catalogs_router
from app.modules.notifications.presentation.router import router as notifications_router
from app.modules.payments.presentation.router import router as payments_router
from app.modules.matches.presentation.router import router as matches_router
from app.modules.rankings.presentation.router import router as rankings_router
from app.modules.finance.presentation.router import router as finance_router

# Importación de Servicios y Handlers
from app.modules.finance.infrastructure.bcv_service import BCVService
from app.modules.matches.application.event_handlers import register_match_event_handlers

# Inicializar Firebase Admin SDK
cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "firebase-service-account.json")
if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="MatchDay API",
    description="Backend en Clean Architecture para la gestión de retos y equipos de fútbol",
    version="1.0.0",
)

# Configuración de Tareas Programadas (BCV Sync con Zona Horaria de Venezuela)
def sync_bcv_rates_task():
    db = SessionLocal()
    try:
        service = BCVService(db)
        service.sync_rates()
    finally:
        db.close()

# Añadimos explícitamente la zona horaria para evitar desfases en servidores de Render/Heroku
scheduler = BackgroundScheduler(timezone="America/Caracas")

# 1. Apertura de la mañana (9:00 AM)
scheduler.add_job(sync_bcv_rates_task, 'cron', hour=9, minute=0)

# 2. El Cierre Estándar (4:30 PM / 16:30)
# Le damos 30 minutos de margen al BCV por si no publica a las 4:00 en punto.
scheduler.add_job(sync_bcv_rates_task, 'cron', hour=16, minute=30)

# 3. El Salvavidas Nocturno (7:00 PM / 19:00)
# Cubre cualquier retraso extremo. Si a las 4:30 PM ya se había capturado con éxito, 
# este intento se cancelará solo por tu regla de las 2 horas de caché.
scheduler.add_job(sync_bcv_rates_task, 'cron', hour=19, minute=0)

scheduler.start()

# Sincronización inicial al arrancar el servidor
@app.on_event("startup")
def startup_event():
    sync_bcv_rates_task()

@app.exception_handler(MatchDayException)
async def matchday_exception_handler(request: Request, exc: MatchDayException):
    return JSONResponse(
        status_code=exc.code,
        content={"detail": exc.message},
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
app.include_router(payments_router, prefix="/api/v1", tags=["Payments"])
app.include_router(matches_router, prefix="/api/v1", tags=["Matches"])
app.include_router(rankings_router, prefix="/api/v1", tags=["Rankings"])
app.include_router(finance_router, prefix="/api/v1/config", tags=["Finance"])

# Inicializar despachadores de eventos de dominio
register_match_event_handlers()