from fastapi import  APIRouter, HTTPException, status
from fastapi import Depends
from Backend.bd.conexionBD import connect_to_database
from Backend.api.auth import UsuarioRequest
from Backend.api.servicios.crud.insertarDatos import insertar_usuario, insertar_estudiante
from Backend.api.servicios.crud.obtenerDatos import obtener_datos_estudiante
from Backend.api.servicios.crud.eliminarUsuario import eliminar_estudiante
from Backend.api.servicios.rbac import *
from Backend.crypto_utils.cifrarRegistros import encrypt_aes, get_aes_key, decrypt_aes
from Backend.api.servicios.prepararAuditoria import preparar_auditoria, registrar_auditoria
from pydantic import BaseModel
from typing import Optional

class EstudianteRequest(UsuarioRequest):
    rol: str = "estudiante"
    calle: str
    colonia: str
    codigo_postal: str
    telefono: str
    fecha_nacimiento: str

class EstudianteUpdateRequest(BaseModel):
    id_usuario: int

    calle: str | None = None
    colonia: str | None = None
    codigo_postal: str | None = None
    telefono: str | None = None
    fecha_nacimiento: str | None = None

router = APIRouter()

@router.post("/registro")
def register_estudiante(          
    estudiante_data: EstudianteRequest,
    user: dict = Depends(require_permiso("estudiantes:escribir"))
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
            estudiante_data.username
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está registrado"
            )

        # Insertar usuario y obtener su ID
        id_usuario = insertar_usuario(
            cursor          = cursor,
            nombre_completo = estudiante_data.nombre_completo,
            username        = estudiante_data.username,
            rol             = "estudiante",
            id_estatus      = estudiante_data.id_estatus,
            contrasena      = estudiante_data.contrasena
        )
        
        # Insertar estudiante, como parametro la key para cifrar los datos sensibles
        insertar_estudiante(
            cursor           = cursor,
            key              = get_aes_key(),
            id_usuario       = id_usuario,
            calle            = estudiante_data.calle,
            colonia          = estudiante_data.colonia,
            codigo_postal    = estudiante_data.codigo_postal,
            telefono         = estudiante_data.telefono,
            fecha_nacimiento = estudiante_data.fecha_nacimiento
        )

        conn.commit()

    
        return {"message": "Estudiante registrado exitosamente"}

    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {e}"
        )
    finally:
        if conn:
            conn.close()


@router.put("/actualizar")
async def actualizar_estudiante(
    estudiante_data: EstudianteUpdateRequest,
    user: dict = Depends(require_permiso("estudiantes:escribir"))
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
        key = get_aes_key()

        # verificar existencia
        cursor.execute(
            "SELECT id_usuario FROM Usuario WHERE id_usuario = ? AND rol = 'estudiante'",
            estudiante_data.id_usuario
        )

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Estudiante no encontrado"
            )


        campos = []
        valores = []

        if estudiante_data.calle is not None:
            campos.append("calle = ?")
            valores.append(encrypt_aes(estudiante_data.calle, key))

        if estudiante_data.colonia is not None:
            campos.append("colonia = ?")
            valores.append(encrypt_aes(estudiante_data.colonia, key))

        if estudiante_data.codigo_postal is not None:
            campos.append("codigo_postal = ?")
            valores.append(encrypt_aes(estudiante_data.codigo_postal, key))

        if estudiante_data.telefono is not None:
            campos.append("telefono = ?")
            valores.append(encrypt_aes(estudiante_data.telefono, key))

        if estudiante_data.fecha_nacimiento is not None:
            campos.append("fecha_nacimiento = ?")
            valores.append(encrypt_aes(estudiante_data.fecha_nacimiento, key))

        if not campos:
            raise HTTPException(
                status_code=400,
                detail="No se enviaron campos para actualizar"
            )

        query = f"""
            UPDATE Estudiante
            SET {", ".join(campos)}
            WHERE id_usuario = ?
        """

        valores.append(estudiante_data.id_usuario)

        cursor.execute(query, valores)
        

        datos_auditoria = preparar_auditoria(
            cursor=cursor,
            id_usuario=user["id_usuario"],  
            accion="UPDATE",
            entidad="Estudiante",
            id_entidad= estudiante_data.id_usuario,
            descripcion="Actualización de datos del estudiante",
            estado="EXITOSO"
        )

        id_auditoria = registrar_auditoria(cursor, datos_auditoria)
        conn.commit()

        return {
            "message": "Estudiante actualizado correctamente",
            "firma_requerida": {
                "id_auditoria": id_auditoria,
                "hash": datos_auditoria["hash"].hex()
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {e}"
        )

    finally:
        if conn:
            conn.close()

@router.delete("/eliminar/{id_usuario}")
async def eliminar_estudiante(          
    estudiante_data: EstudianteRequest,
    user: dict = Depends(require_permiso("estudiantes:escribir"))
):
    try:
        conn = connect_to_database()
        if not conn:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error de conexión a la base de datos"
            )

        cursor = conn.cursor()

        # Verificar si el estudiante existe
        cursor.execute(
            "SELECT id_usuario FROM Usuario WHERE id_usuario = ? AND rol = 'estudiante'",
            estudiante_data.id_usuario
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado"
            )

        eliminar_estudiante(cursor, estudiante_data.id_usuario, estudiante_data.id_estudiante)

        datos_autditoria = preparar_auditoria(
            cursor=cursor,
            id_usuario=user["id_usuario"],  
            accion="DELETE",
            entidad="Estudiante",
            id_entidad= estudiante_data.id_usuario,
            descripcion="Eliminación del estudiante",
            estado="EXITOSO"
        )
        id_auditoria = registrar_auditoria(cursor, datos_autditoria)
        conn.commit()

        return {
                    "message": "Estudiante eliminado correctamente",
                    "firma_requerida": {
                        "id_auditoria": id_auditoria,   
                        "hash": datos_autditoria["hash"].hex()
                    }
                }
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {e}"
        )
    finally:
        if conn:
            conn.close()
