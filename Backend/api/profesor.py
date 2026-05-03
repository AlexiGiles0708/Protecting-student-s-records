from fastapi import  APIRouter, HTTPException, status
from fastapi import Depends
from Backend.bd.conexionBD import connect_to_database
from Backend.api.servicios.crud.insertarDatos import insertar_usuario
from Backend.api.servicios.rbac import *
from Backend.api.auth import UsuarioRequest

router = APIRouter()

class ProfesorRequest(UsuarioRequest):
    rol: str = "profesor"
    id_grupo: int

@router.post("/registro")
def register_profesor(profesor_data: ProfesorRequest,
                      user: dict = Depends(require_permiso("profesores:escribir"))
                      ):
    conn = None
    try:
        conn = connect_to_database()
        if not conn:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error de conexión a la base de datos"
            )

        cursor = conn.cursor()

        # Verificar si el username ya existe
        cursor.execute(
            "SELECT id_usuario FROM Usuario WHERE username = ?",
            profesor_data.username
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está registrado"
            )

        # Insertar usuario y obtener su ID
        id_usuario = insertar_usuario(
            cursor          = cursor,
            nombre_completo = profesor_data.nombre_completo,
            username        = profesor_data.username,
            rol             = profesor_data.rol,
            id_estatus      = profesor_data.id_estatus,
            contrasena      = profesor_data.contrasena
        )

        # Insertar profesor
        cursor.execute("""
            INSERT INTO Profesor (id_usuario, id_grupo)
            VALUES (?, ?)
        """,
            id_usuario,
            profesor_data.id_grupo
        )

        conn.commit()

        return {"message": "Profesor registrado correctamente"}

    except HTTPException as e:
        raise e  # Re-lanzar excepciones HTTP para que FastAPI las maneje

    except Exception as e:
        if conn:
            conn.rollback()  # Revertir cambios en caso de error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar el profesor: {str(e)}"
        )

    finally:
        if conn:
            conn.close()