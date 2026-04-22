from fastapi import FastAPI

app = FastAPI(
    title="MatchDay API",
    description="Backend para la gestión de canchas y partidos",
    version="1.0.0"
)

@app.get("/")
def ruta_principal():
    return {"mensaje": "¡El backend de MatchDay está vivo y respirando!"}

@app.get("/ping")
def ping_test():
    return {"status": "ok", "framework": "FastAPI"}