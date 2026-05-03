

# Eliminación logica de un estudiante: se cambia su estatus a "eliminado" (id_estatus = 3) y se registra la acción en la auditoría.
def eliminar_estudiante(cursor, id_usuario,id_estudiante):
    try:
       
        # Cambiar estatus a "eliminado" (id_estatus = 3)
        cursor.execute("""
            UPDATE Usuario
            SET id_estatus = 3
            WHERE id_usuario = ?
        """, (id_usuario,))

        # Cambiar estatus a "eliminado" en la tabla Estudiante
        cursor.execute("""
            UPDATE Estudiante
            SET id_estatus = 3
            WHERE id_estudiante = ?
        """, (id_estudiante,))

    except Exception as e:
        print(f"Error al eliminar estudiante: {e}")
        raise