from fastapi import FastAPI
from Backend.api.auth import router as auth_router
from Backend.api.estudiante import router as estudiante_router
from Backend.api.profesor import router as profesor_router
from Backend.api.audith import router as audith_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(estudiante_router, prefix="/estudiante", tags=["estudiante"])
app.include_router(profesor_router, prefix="/profesor", tags=["profesor"])
app.include_router(audith_router, prefix="/auditoria", tags=["auditoria"])

@app.get('/')
async def read_root():
    return {"message": "API funcionando correctamente"}
