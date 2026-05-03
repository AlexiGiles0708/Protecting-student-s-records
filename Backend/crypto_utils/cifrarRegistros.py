from Crypto.Cipher import AES
import os
import base64
import bcrypt



NONCE_SIZE = 12
TAG_SIZE = 16

def get_aes_key() -> bytes:
    key_b64 = os.getenv('AES_KEY')
    if not key_b64:
        raise ValueError("AES_KEY no está definida en el .env")
    key = base64.b64decode(key_b64)
    if len(key) != 16:
        raise ValueError(f"AES_KEY debe ser 16 bytes, tiene {len(key)}")
    return key

def encrypt_aes(data: str, key: bytes) -> bytes:
    assert len(key) in (16, 24, 32)
    
    nonce = os.urandom(NONCE_SIZE)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    
    return nonce + tag + ciphertext


def decrypt_aes(data: bytes, key: bytes) -> str:
    assert len(key) in (16, 24, 32)
    
    nonce = data[:NONCE_SIZE]
    tag = data[NONCE_SIZE:NONCE_SIZE+TAG_SIZE]
    ciphertext = data[NONCE_SIZE+TAG_SIZE:]
    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    
    try:
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
    except ValueError:
        raise ValueError("Datos corruptos o clave incorrecta")
    
def set_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())



if __name__ == "__main__":
    # Ejemplo de uso
    key = os.urandom(16)  # Clave de 16 bytes para AES-128
    print(base64.b64encode(key).decode())
    original_data = "Hola, mundo!"
    encrypted_data = encrypt_aes(original_data, key)
    decrypted_data = decrypt_aes(encrypted_data, key)

    print("Original:", original_data)
    print("Encrypted:", encrypted_data)
    print("Decrypted:", decrypted_data)

    print("Contraseña hasheada:", set_password("Hola$12345"))
    print("Verificación de contraseña (correcta):", verify_password("Hola$12345", set_password("Hola$12345")))
    