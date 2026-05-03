import requests
import base64
from Backend.crypto_utils.ecdsa import sign_message

print("\nIniciando cliente de prueba para Control Escolar...")

BASE_URL = "http://127.0.0.1:8000"
ID_USUARIO_CLIENTE = 1008  # El usuario que ya está registrado y tiene llaves




def print_step(titulo: str):
    print(f"\n{'═'*50}")
    print(f"  {titulo}")
    print(f"{'═'*50}")



# PASO 1: LOGIN

def login(username: str, contrasena: str) -> str:
    print_step("PASO 1: LOGIN")

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username":   username,
            "contrasena": contrasena
        }
    )

    data = response.json()
    print(f"Status:  {response.status_code}")
    print(f"Usuario: {data.get('user', {})}")

    if response.status_code != 200:
        raise Exception(f"Login fallido: {data}")

    token = data["access_token"]
    print(f"Token:   {token[:40]}...")
    return token


# PASO 2: REGISTRAR PROFESOR

def registrar_profesor(token: str):
    print_step("PASO 2: REGISTRAR PROFESOR")

    response = requests.post(
        f"{BASE_URL}/profesor/registro",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nombre_completo": "Martin Ramirez",
            "username":        "mramirez",
            "id_estatus":      1,
            "contrasena":      "Password123!",
            "id_grupo":        3
        }
    )

    print(f"Status:    {response.status_code}")
    print(f"Respuesta: {response.json()}")


# PASO 3: REGISTRAR ESTUDIANTE


def registrar_estudiante(token: str):
    print_step("PASO 3: REGISTRAR ESTUDIANTE")

    response = requests.post(
        f"{BASE_URL}/estudiante/registro",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nombre_completo":  "Jorge Perez",
            "username":         "Joest123",
            "contrasena":       "Password123!",
            "id_estatus":       1,
            "rol":              "estudiante",
            "calle":            "Av. Siempre Viva 123",
            "colonia":          "Centro",
            "codigo_postal":    "01000",
            "telefono":         "5512345678",
            "fecha_nacimiento": "2000-05-10"
        }
    )

    print(f"Status:    {response.status_code}")
    print(f"Respuesta: {response.json()}")



# PASO 4: ACTUALIZAR ESTUDIANTE


def actualizar_estudiante(token: str, id_estudiante: int) -> dict:
    print_step("PASO 4: ACTUALIZAR ESTUDIANTE")

    response = requests.put(
        f"{BASE_URL}/estudiante/actualizar",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id_usuario": id_estudiante,
            "telefono":   "5512345678",
            "calle":      "Av. Ermita 123",
        }
    )

    data = response.json()
    print(f"Status:    {response.status_code}")
    print(f"Respuesta: {data}")

    if response.status_code != 200:
        raise Exception(f"Actualización fallida: {data}")

    return data["firma_requerida"]  # { id_auditoria, hash }


# PASO 5: FIRMAR Y VERIFICAR


def firmar_y_verificar(token: str, firma_requerida: dict):
    print_step("PASO 5: FIRMAR Y VERIFICAR AUDITORÍA")

    id_auditoria = firma_requerida["id_auditoria"]
    hash_hex     = firma_requerida["hash"]

    # ← Convertir hex a bytes antes de firmar
    hash_bytes = bytes.fromhex(hash_hex)
    print(f"Hash (hex):  {hash_hex}")
    print(f"Hash (bytes): {hash_bytes[:10]}...")

    # Firmar con llave privada local
    firma_b64 = sign_message(hash_bytes)
    print(f"Firma (b64): {firma_b64[:40]}...")

    # Enviar firma al servidor
    response = requests.put(
        f"{BASE_URL}/auditoria/verificar/firma",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id_auditoria": id_auditoria,
            "firma":        firma_b64
        }
    )

    print(f"Status:    {response.status_code}")
    print(f"Respuesta: {response.json()}")

if __name__ == "__main__":

    # 1. Login
    token = login(
        username="jperez",
        contrasena="Password123!"
    )

    # 2. Registrar profesor
    #registrar_profesor(token)

    # 3. Registrar estudiante 
    #registrar_estudiante(token)

    # 4. Actualizar estudiante y obtener hash para firmar
    firma_requerida = actualizar_estudiante(token, id_estudiante=1010)

    # 5. Firmar el hash y verificar en el servidor
    firmar_y_verificar(token, firma_requerida)

    print("\nFlujo completo ejecutado correctamente")