from flask import Flask, request, jsonify, render_template
import ecdsa  # Tu archivo original

app = Flask(__name__)

# Simulamos una base de datos en memoria
BASE_DE_DATOS = {
    "usuario_1": {
        "pub_b64": "" 
    }
}

# 1. Esta ruta muestra tu HTML cuando entras a la página principal
@app.route('/')
def inicio():
    # ¡Aquí está la corrección! Flask buscará "firmas.html"
    return render_template('firmas.html') 

# 2. Recibe la llave pública del frontend
@app.route('/api/registrar_llave', methods=['POST'])
def registrar_llave():
    data = request.json
    BASE_DE_DATOS["usuario_1"]["pub_b64"] = data.get('pub_b64')
    print(f"🔒 Llave pública guardada en DB: {data.get('pub_b64')[:20]}...")
    return jsonify({"mensaje": "Llave pública registrada exitosamente"}), 200

# 3. Recibe la firma y la verifica
@app.route('/api/verificar_registro', methods=['POST'])
def verificar():
    data = request.json
    mensaje = data.get('mensaje').encode('utf-8')
    firma_b64 = data.get('firma_b64')

    pub_b64 = BASE_DE_DATOS["usuario_1"]["pub_b64"]

    # Aquí ocurre la magia con tu ecdsa.py
    es_valida = ecdsa.verify_signature(pub_b64, mensaje, firma_b64)

    if es_valida:
        print("✅ Firma válida. Guardando registro...")
        return jsonify({"status": "Éxito", "mensaje": "Firma matemática validada."}), 200
    else:
        print("❌ Firma inválida detectada.")
        return jsonify({"status": "Error", "mensaje": "Firma inválida o datos alterados."}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)