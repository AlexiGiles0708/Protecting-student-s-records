from crypto_utils.ecdsa import sign_message
from bd.conexionBD import connect_to_database


def firmar_reporte(id_reporte: int, id_usuario: int, rol: str):
    conexion = connect_to_database()
    cursor = conexion.cursor()

    # Obtener datos del reporte (lo que se firma)
    cursor.execute("""
        SELECT id_reporte, id_usuario, id_grupo, id_curso, fecha
        FROM Reporte
        WHERE id_reporte = ?
    """, (id_reporte,))

    row = cursor.fetchone()

    if not row:
        return False

    # Crear mensaje a firmar
    mensaje = f"{row.id_reporte}-{row.id_usuario}-{row.id_grupo}-{row.id_curso}-{row.fecha}"
    mensaje_bytes = mensaje.encode()

    firma = sign_message(mensaje_bytes, id_usuario)

    # Guardar firma según rol
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

    conexion.commit()
    cursor.close()
    conexion.close()

    return True