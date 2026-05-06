import ecdsa

def main():
    # Datos simulados para la prueba
    id_usuario = 1
    mensaje_original = b"Este es un documento confidencial que necesita firma."
    mensaje_alterado = b"Este es un documento confidencial que necesita firma!" # Cambiamos el punto por !

    print("--- INICIANDO PRUEBA ECDSA ---")

    # Paso 1: Generar el par de llaves
    print(f"\n1. Generando llaves para el usuario {id_usuario}...")
    pub_b64 = ecdsa.generate_key_pair(id_usuario)
    print(f"   Llave pública generada (primeros 30 caracteres): {pub_b64[:30]}...")

    # Paso 2: Firmar el mensaje
    print("\n2. Firmando el mensaje original...")
    firma_b64 = ecdsa.sign_message(mensaje_original, id_usuario)
    print(f"   Firma generada (primeros 30 caracteres): {firma_b64[:30]}...")

    # Paso 3: Verificar la firma (Debe ser True)
    print("\n3. Verificando la firma con el mensaje original...")
    es_valida = ecdsa.verify_signature(pub_b64, mensaje_original, firma_b64)
    print(f"   ¿La firma es válida? -> {'Sí ✅' if es_valida else 'No ❌'}")

    # Paso 4: Probar la seguridad (alterar el mensaje y verificar)
    print("\n4. Verificando la firma con un mensaje alterado...")
    es_valida_falso = ecdsa.verify_signature(pub_b64, mensaje_alterado, firma_b64)
    print(f"   ¿La firma es válida? -> {'Sí ✅' if es_valida_falso else 'No ❌ (Como se esperaba)'}")

if __name__ == "__main__":
    main()