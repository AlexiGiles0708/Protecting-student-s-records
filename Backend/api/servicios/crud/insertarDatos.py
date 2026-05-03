from Backend.crypto_utils.cifrarRegistros import encrypt_aes, set_password
from Backend.bd.conexionBD import connect_to_database
import os
import base64

def insertar_usuario(cursor, nombre_completo, username, rol, id_estatus, contrasena):
    cursor.execute("""
        INSERT INTO Usuario 
            (nombre_completo, username, rol, id_estatus, contrasena)
        VALUES (?, ?, ?, ?, ?)
    """,
        nombre_completo,
        username,
        rol,
        id_estatus,
        set_password(contrasena)
    )
    cursor.execute("SELECT @@IDENTITY")
    row = cursor.fetchone()
    return int(row[0])

def insertar_estudiante(cursor, key, id_usuario, calle, colonia,
                        codigo_postal, telefono, fecha_nacimiento):

    if not codigo_postal.isdigit() or len(codigo_postal) != 5:
        raise ValueError(f"Código postal inválido: {codigo_postal}")

    cursor.execute("""
        INSERT INTO Estudiante 
            (calle, colonia, codigo_postal, telefono, fecha_nacimiento, id_usuario)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        encrypt_aes(calle,                 key),
        encrypt_aes(colonia,               key),
        encrypt_aes(codigo_postal,         key),
        encrypt_aes(telefono,              key),
        encrypt_aes(str(fecha_nacimiento), key),
        id_usuario
    )


if __name__ == "__main__":

    #key = get_aes_key()
    """insertar_usuario(
        nombre_completo="Juan Pérez",
        username="juanperez",
        rol="estudiante",
        id_estatus=1,
        contrasena="hola123"
    )

    insertar_estudiante(
        key=key,
        id_usuario=2,
        calle="Calle Falsa 123",
        colonia="Colonia Inventada",
        codigo_postal="54321",
        telefono="555-1234",
        fecha_nacimiento="2000-01-01"
    )"""

    insertar_usuario(
        nombre_completo="María López",
        username="marialopez",
        rol="director",
        id_estatus=1,
        contrasena="hola123"
    )

