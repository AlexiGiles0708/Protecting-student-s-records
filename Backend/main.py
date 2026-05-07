from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from Backend.api.auth import router as auth_router
from Backend.api.estudiante import router as estudiante_router
from Backend.api.profesor import router as profesor_router
from Backend.api.audith import router as audith_router
from Backend.api.firmas_front import router as firmas_front_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(estudiante_router, prefix="/estudiante", tags=["estudiante"])
app.include_router(profesor_router, prefix="/profesor", tags=["profesor"])
app.include_router(audith_router, prefix="/auditoria", tags=["auditoria"])
app.include_router(firmas_front_router, tags=["firmas_front"])

@app.get("/firmas")
def mostrar_firmas():
    ruta = Path(__file__).resolve().parent / "crypto_utils" / "templates" / "firmas.html"
    return FileResponse(ruta)

@app.get("/")
async def read_root():
    return {"message": "API funcionando correctamente"}