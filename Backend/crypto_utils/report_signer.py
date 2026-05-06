from Backend.crypto_utils.ecdsa import sign_message, verify_signature
from Backend.bd.conexionBD import connect_to_database


def construir_mensaje_reporte(row):
    mensaje = f"{row.id_reporte}-{row.id_usuario}-{row.id_grupo}-{row.id_curso}-{row.fecha}"
    return mensaje.encode()


def firmar_reporte(id_reporte: int, id_usuario: int, rol: str):
    conexion = connect_to_database()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id_reporte, id_usuario, id_grupo, id_curso, fecha
        FROM Reporte
        WHERE id_reporte = ?
    """, (id_reporte,))

    row = cursor.fetchone()

    if not row:
        cursor.close()
        conexion.close()
        return False

    mensaje_bytes = construir_mensaje_reporte(row)
    firma = sign_message(mensaje_bytes, id_usuario)

    if rol == "profesor":
        cursor.execute("""
            UPDATE Reporte
            SET firma_profesor = ?
            WHERE id_reporte = ?
        """, (firma, id_reporte))

    elif rol == "director":
        cursor.execute("""
            UPDATE Reporte
            SET firma_director = ?
            WHERE id_reporte = ?
        """, (firma, id_reporte))

    else:
        cursor.close()
        conexion.close()
        return False

    conexion.commit()
    cursor.close()
    conexion.close()

    return True


def verificar_firma_reporte(id_reporte: int, id_usuario: int, rol: str):
    conexion = connect_to_database()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id_reporte, id_usuario, id_grupo, id_curso, fecha,
               firma_profesor, firma_director
        FROM Reporte
        WHERE id_reporte = ?
    """, (id_reporte,))

    reporte = cursor.fetchone()

    if not reporte:
        cursor.close()
        conexion.close()
        return False

    cursor.execute("""
        SELECT llave_publica
        FROM Usuario
        WHERE id_usuario = ?
    """, (id_usuario,))

    usuario = cursor.fetchone()

    if not usuario or not usuario.llave_publica:
        cursor.close()
        conexion.close()
        return False

    if rol == "profesor":
        firma = reporte.firma_profesor
    elif rol == "director":
        firma = reporte.firma_director
    else:
        cursor.close()
        conexion.close()
        return False

    if not firma:
        cursor.close()
        conexion.close()
        return False

    mensaje_bytes = construir_mensaje_reporte(reporte)

    resultado = verify_signature(
        usuario.llave_publica,
        mensaje_bytes,
        firma
    )

    cursor.close()
    conexion.close()

    return resultado