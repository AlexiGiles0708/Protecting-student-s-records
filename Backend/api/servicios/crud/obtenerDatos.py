from Backend.crypto_utils.cifrarRegistros import decrypt_aes
from Backend.bd.conexionBD import connect_to_database
import os
import base64

def obtener_datos_usuario(id_usuario):        
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()        
        cursor.execute("""
            SELECT nombre_completo, username, rol 
            FROM Usuario
            WHERE id_usuario = ?
        """, (id_usuario,))
        row = cursor.fetchone()
        if row:
            return {
                "nombre_completo": row[0],
                "username":        row[1],
                "rol":             row[2],
            }
        return None
    except Exception as e:
        print(f"Error al obtener datos del usuario: {e}")
        return None
    finally:
        if connection:
            connection.close()


def obtener_datos_estudiante(id_usuario, key):  # ← quita cursor del parámetro
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()             
        cursor.execute("""
            SELECT u.id_usuario, e.id_estudiante,
                   u.nombre_completo, u.username, u.rol,
                   e.calle, e.colonia, e.codigo_postal, e.telefono, e.fecha_nacimiento
            FROM Usuario u
                JOIN Estudiante e ON u.id_usuario = e.id_usuario
            WHERE u.id_usuario = ?
        """, (id_usuario,))
        row = cursor.fetchone()
        if row:
            return {
                "id_usuario":       row[0],
                "id_estudiante":    row[1],
                "nombre_completo":  row[2],
                "username":         row[3],
                "rol":              row[4],
                "calle":            decrypt_aes(row[5], key),
                "colonia":          decrypt_aes(row[6], key),
                "codigo_postal":    decrypt_aes(row[7], key),
                "telefono":         decrypt_aes(row[8], key),
                "fecha_nacimiento": decrypt_aes(row[9], key),
            }
        return None
    except Exception as e:
        print(f"Error al obtener datos del estudiante: {e}")
        return None
    finally:
        if connection:
            connection.close()
