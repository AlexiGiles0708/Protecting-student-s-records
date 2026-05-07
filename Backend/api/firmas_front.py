from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import base64

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

router = APIRouter()

llaves_publicas = {}


class RegistrarLlaveRequest(BaseModel):
    usuario: str
    rol: str
    pub_b64: str


class VerificarRegistroRequest(BaseModel):
    usuario: str
    rol: str
    mensaje: str
    firma_b64: str


@router.get("/firmas")
def mostrar_firmas():
    ruta = Path(__file__).resolve().parents[1] / "crypto_utils" / "templates" / "firmas.html"
    return FileResponse(ruta)


@router.post("/api/registrar_llave")
def registrar_llave(request: RegistrarLlaveRequest):
    clave = f"{request.rol}:{request.usuario}"
    llaves_publicas[clave] = request.pub_b64

    return {
        "mensaje": "Llave pública registrada correctamente",
        "usuario": request.usuario,
        "rol": request.rol
    }


@router.post("/api/verificar_registro")
def verificar_registro(request: VerificarRegistroRequest):
    clave = f"{request.rol}:{request.usuario}"

    if clave not in llaves_publicas:
        raise HTTPException(
            status_code=400,
            detail="Primero debes registrar una llave pública para este usuario"
        )

    try:
        pub_der = base64.b64decode(llaves_publicas[clave])
        public_key = serialization.load_der_public_key(pub_der)

        firma = base64.b64decode(request.firma_b64)
        mensaje_bytes = request.mensaje.encode("utf-8")

        public_key.verify(
            firma,
            mensaje_bytes,
            ec.ECDSA(hashes.SHA256())
        )

        return {
            "mensaje": "Firma válida. El registro no fue alterado.",
            "firma_valida": True,
            "usuario": request.usuario,
            "rol": request.rol
        }

    except InvalidSignature:
        return {
            "mensaje": "Firma inválida.",
            "firma_valida": False,
            "usuario": request.usuario,
            "rol": request.rol
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error verificando firma: {str(e)}"
        )