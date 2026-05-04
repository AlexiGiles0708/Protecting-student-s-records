from bd.conexionBD import connect_to_database
from crypto_utils.ecdsa import generate_key_pair


def registrar_llave_publica(id_usuario: int):
    llave_publica = generate_key_pair(id_usuario)

    conexion = connect_to_database()
    if conexion is None:
        return False

    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE Usuario
        SET llave_publica = ?
        WHERE id_usuario = ?
        """,
        (llave_publica, id_usuario)
    )

    conexion.commit()
    cursor.close()
    conexion.close()

    return True