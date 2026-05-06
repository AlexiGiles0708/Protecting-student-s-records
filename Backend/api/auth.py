from fastapi import  APIRouter, HTTPException, status
from fastapi import Depends
from pydantic import BaseModel
from Backend.crypto_utils.cifrarRegistros import verify_password, get_aes_key
from Backend.api.servicios.crud.obtenerDatos import obtener_datos_estudiante, obtener_datos_usuario
from Backend.api.servicios.crud.insertarDatos import insertar_usuario
from Backend.bd.conexionBD import connect_to_database
from Backend.api.servicios.rbac import *
from typing import Optional
from Backend.crypto_utils.tokenAuth import create_access_token
from datetime import timedelta


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

router = APIRouter()

class UsuarioRequest(BaseModel):
    nombre_completo: str
    username: str
    rol: str
    id_estatus: int = 1
    contrasena: str

class EstudianteRequest(UsuarioRequest):
    rol: str = "estudiante"
    calle: str
    colonia: str
    codigo_postal: str
    telefono: str
    fecha_nacimiento: str

class LoginRequest(BaseModel):
    username: str
    contrasena: str

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre_completo: str
    username: str
    rol: str

class EstudianteResponse(UsuarioResponse):
    id_estudiante: int
    calle: str
    colonia: str
    codigo_postal: str
    telefono: str
    fecha_nacimiento: str

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    connection = None
    try:
        
        connection = connect_to_database()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id_usuario, contrasena, rol
            FROM Usuario
            WHERE username = ?
        """, (request.username,))
        user = cursor.fetchone()

        if not user or not verify_password(request.contrasena, user[1]):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        id_usuario, _, rol = user[0], user[1], user[2]

        key = get_aes_key()

        # Crea el payload del token con rol, para implementar el servicio de autorización
        token_payload = {
            "sub":        str(id_usuario),
            "rol":        rol,
        }
    
        access_token = create_access_token(
            data=token_payload,
            expires_delta=timedelta(minutes=120),
        )

        if rol == "estudiante":
            
            datos = obtener_datos_estudiante(id_usuario=id_usuario, key=key)
           
            user_data = EstudianteResponse(**datos)
        else:
         
            datos = obtener_datos_usuario(id_usuario=id_usuario)
      
            user_data = UsuarioResponse(
                id_usuario      = id_usuario,
                nombre_completo = datos["nombre_completo"],
                username        = datos["username"],
                rol             = datos["rol"]
            )

        return TokenResponse(access_token=access_token, user=user_data)

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        print(traceback.format_exc())   
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {e}",
        )
    finally:
        if connection:
            connection.close()

@router.post("/register")
def register(user_data: UsuarioRequest):
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
            user_data.username
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está registrado"
            )

        insertar_usuario(
            cursor          = cursor,
            nombre_completo = user_data.nombre_completo,
            username        = user_data.username,
            rol             = user_data.rol,
            id_estatus      = user_data.id_estatus,
            contrasena      = user_data.contrasena
        )

        conn.commit()
        return {"message": "Usuario registrado exitosamente"}

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

