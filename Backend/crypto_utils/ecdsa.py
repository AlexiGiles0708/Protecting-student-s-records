import base64
import os

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


CURVE = ec.SECP256R1()


def hash_message(message: bytes) -> bytes:
    digest = hashes.Hash(hashes.SHA256())
    digest.update(message)
    return digest.finalize()


def generate_key_pair(id_usuario: int):
    private_key = ec.generate_private_key(CURVE)
    public_key = private_key.public_key()

    priv_der = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    pub_der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    priv_b64 = base64.b64encode(priv_der).decode()
    pub_b64 = base64.b64encode(pub_der).decode()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    keys_dir = os.path.join(base_dir, "..", "keys")

    os.makedirs(keys_dir, exist_ok=True)

    # Guardar llave privada por usuario
    priv_path = os.path.join(keys_dir, f"usuario_{id_usuario}_private.pem")

    with open(priv_path, "w") as f:
        f.write(priv_b64)

    return pub_b64


def sign_message(message: bytes, id_usuario: int):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(base_dir, "..", "keys", f"usuario_{id_usuario}_private.pem")

    with open(key_path, "r") as f:
        priv_b64 = f.read().strip()

    priv_der = base64.b64decode(priv_b64)
    private_key = serialization.load_der_private_key(priv_der, password=None)

    message_hash = hash_message(message)

    signature = private_key.sign(
        message_hash,
        ec.ECDSA(Prehashed(hashes.SHA256()))
    )

    return base64.b64encode(signature).decode()


def verify_signature(pub_b64, message: bytes, signature_b64):
    pub_der = base64.b64decode(pub_b64)
    public_key = serialization.load_der_public_key(pub_der)

    signature = base64.b64decode(signature_b64)
    message_hash = hash_message(message)

    try:
        public_key.verify(
            signature,
            message_hash,
            ec.ECDSA(Prehashed(hashes.SHA256()))
        )
        return True
    except InvalidSignature:
        return False