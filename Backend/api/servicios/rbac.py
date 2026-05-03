from fastapi import HTTPException, Depends, status
from Backend.crypto_utils.tokenAuth import get_current_user


PERMISOS = {
    "estudiante": [
        "perfil:leer_propio",
        "calificaciones:leer_propio",
        "materias:leer",
    ],
    "profesor": [
        "perfil:leer_propio",
        "estudiantes:leer",
        "calificaciones:leer",
        "calificaciones:escribir",
        "materias:leer",
        "reporte:escribir"
    ],
    "control_escolar": [          
        "perfil:leer_propio",
        "estudiantes:leer",
        "estudiantes:escribir", 
        "materias:leer",
    ],
    "director": [
        "perfil:leer_propio",
        "estudiantes:leer",
        "profesores:leer",
        "audit:leer"
        "profesores:escribir",
        "calificaciones:leer",
        "materias:leer",
        "reportes:leer",
    ],
}

def tiene_permiso(rol: str, permiso: str) -> bool:
    permisos_rol = PERMISOS.get(rol, [])
    return permiso in permisos_rol

def require_permiso(permiso: str):
    def _guard(current_user: dict = Depends(get_current_user)) -> dict:

        rol = current_user.get("rol")
        if not tiene_permiso(rol, permiso):
            raise HTTPException(403, "No autorizado")

        return current_user
    return _guard

def require_propio_o_permiso(permiso: str):
    def _guard(
        id_usuario: int,
        current_user: dict = Depends(get_current_user),
    ):
        es_propio = int(current_user["id_usuario"]) == id_usuario
        tiene_permiso = tiene_permiso(current_user["rol"], permiso)

        if not es_propio and not tiene_permiso:
            raise HTTPException(403, "No autorizado")

        return current_user

    return _guard
