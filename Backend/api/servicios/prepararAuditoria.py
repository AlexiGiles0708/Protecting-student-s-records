import hashlib
import json
from datetime import datetime
import uuid

def obtener_ultimo_hash(cursor) -> bytes:
    cursor.execute("""
        SELECT TOP 1 hash 
        FROM Auditoria 
        ORDER BY id_auditoria DESC
    """)
    row = cursor.fetchone()
    
    if row is None:
        # Primer registro — hash genesis en ceros
        return bytes(32)  # 32 bytes de ceros
    
    hash_valor = row[0]
    
    # Normalizar cualquier tipo que regrese pyodbc
    if isinstance(hash_valor, bytes):
        return hash_valor          #
    elif isinstance(hash_valor, bytearray):
        return bytes(hash_valor) 
    elif isinstance(hash_valor, str):
        # Si viene como hex string
        cleaned = hash_valor.replace(" ", "")
        if len(cleaned) % 2 != 0:
            cleaned = "0" + cleaned  
        return bytes.fromhex(cleaned)
    else:
        return bytes(32)

def preparar_auditoria(cursor, id_usuario, accion, entidad, id_entidad, descripcion, estado):
    hash_anterior = obtener_ultimo_hash(cursor)

    # ── Normalizar hash_anterior a bytes siempre ──────────────────────────────
    if isinstance(hash_anterior, str):
        hash_anterior = bytes.fromhex(hash_anterior)  # str hex → bytes
    elif isinstance(hash_anterior, (bytearray, memoryview)):
        hash_anterior = bytes(hash_anterior)           # otros tipos → bytes

    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    nonce     = uuid.uuid4().bytes

    datos = {
        "id_usuario":    id_usuario,
        "accion":        accion,
        "entidad":       entidad,
        "id_entidad":    id_entidad,
        "descripcion":   descripcion,
        "estado":        estado,
        "timestamp":     timestamp,
        "hash_anterior": hash_anterior,
        "nonce":         nonce,
    }

    datos_serializados = json.dumps(
        {
            **datos,
            "hash_anterior": hash_anterior.hex(),  
            "nonce":         nonce.hex()
        },
        sort_keys=True,
        separators=(",", ":")
    )

    hash_actual    = hashlib.sha256(datos_serializados.encode("utf-8")).digest()
    datos["hash"]  = hash_actual
    return datos

def registrar_auditoria(cursor, datos):
    try:
        cursor.execute("""
            INSERT INTO Auditoria
                (id_usuario, accion, entidad, id_entidad, descripcion, estado,
                 timestamp, hash_anterior, nonce, hash)
            OUTPUT INSERTED.id_auditoria          
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datos["id_usuario"],
            datos["accion"],
            datos["entidad"],
            datos["id_entidad"],
            datos["descripcion"],
            datos["estado"],
            datos["timestamp"],
            datos["hash_anterior"],
            datos["nonce"],
            datos["hash"]
        ))
        row = cursor.fetchone()
        return int(row[0]) if row else None
    except Exception as e:
        raise Exception(f"Error al registrar auditoría: {e}")