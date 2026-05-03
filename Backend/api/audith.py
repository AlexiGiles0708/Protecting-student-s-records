from fastapi import  APIRouter, HTTPException, status
from fastapi import Depends
from pydantic import BaseModel
from Backend.bd.conexionBD import connect_to_database
from Backend.crypto_utils.ecdsa import verify_signature

router = APIRouter()

class VerificarFirmaRequest(BaseModel):
    id_auditoria: int
    firma: str

@router.put("/verificar/firma")
def verificar_firma(request: VerificarFirmaRequest):  # ← recibe body
    id_auditoria = request.id_auditoria
    firma        = request.firma

    conn = None
    try:
        conn = connect_to_database()
        if not conn:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error de conexión a la base de datos"
            )
        
        cursor = conn.cursor()
        #Verificar que la auditoria exista y que no esté ya verificada ni tenga firma
        cursor.execute("""
            SELECT a.hash, u.llave_publica                       
            FROM Auditoria a
            JOIN Usuario u ON u.id_usuario = a.id_usuario
            WHERE a.id_auditoria = ?
            AND a.verificado = 0        -- que no esté ya verificada
            AND a.firma IS NULL         -- que no tenga firma aún
        """, (id_auditoria,))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Auditoría no encontrada o ya fue verificada"
            )

        hash_bytes = bytes(row[0])  # hash de Auditoria → bytes
        pub_b64    = row[1]         # llave pública de Usuario → Base64

        
         # Verificar firma
        es_valida = verify_signature(
            pub_b64       = pub_b64,
            message       = hash_bytes,  # ya hasheado
            signature_b64 = firma
        )

        if not es_valida:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Firma no válida"
            )

     # Guardar firma en Auditoría
        cursor.execute("""
            UPDATE Auditoria
            SET firma       = ?,
                verificado  = 1,
                fecha_firma = GETDATE()
            WHERE id_auditoria = ?
        """, (firma, id_auditoria))

        conn.commit()
        return {"message": "Firma verificada y registrada correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {e}"
        )
    finally:
        if conn:
            conn.close()