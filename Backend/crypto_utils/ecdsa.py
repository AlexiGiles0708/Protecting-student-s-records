import base64
import os

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


CURVE = ec.SECP256R1()  # Curva P-256 estandaralizada por NIST

def generate_key_pair():
    """Genera un par de claves ECDSA (privada y pública)."""
    private_key = ec.generate_private_key(CURVE)
    public_key  = private_key.public_key()
    
    # Serializar en formato DER y codificar en Base64
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

    with open("ecdsa_private_key.pem", "w") as f:
        f.write(priv_b64)
    with open("ecdsa_public_key.pem", "w") as f:
        f.write(pub_b64)
    return pub_b64

def sign_message(message:  bytes):
    # Cargar clave privada desde Base64
    base_dir = os.path.dirname(os.path.abspath(__file__))  # carpeta del script
    key_path = os.path.join(base_dir, "ecdsa_private_key.pem")

    with open(key_path, "r") as f:
        priv_b64 = f.read().strip()

    priv_der = base64.b64decode(priv_b64)
    private_key = serialization.load_der_private_key(priv_der, password=None)

    # Firmar el mensaje
    signature = private_key.sign(
        message,
        ec.ECDSA(Prehashed(hashes.SHA256()))  
    )

    firma_b64 = base64.b64encode(signature).decode()

    return firma_b64

def verify_signature(pub_b64,message : bytes, signature_b64):
    # Cargar clave pública desde Base64

    pub_der = base64.b64decode(pub_b64)
    public_key = serialization.load_der_public_key(pub_der)

    signature = base64.b64decode(signature_b64)

    try:
        public_key.verify(
                            signature,
                            message,
                            ec.ECDSA(Prehashed(hashes.SHA256()))
                        )
        return True
    except InvalidSignature:
        return False