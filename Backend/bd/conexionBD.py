import pyodbc
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

def connect_to_database():
    try:
        # Recuperar variables de entorno
        driver = os.getenv('DB_DRIVER')
        server = os.getenv('DB_SERVER')
        database = os.getenv('DB_NAME')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        yes='yes'
        
        # Construir la cadena de conexión
        connection_string = (
            f'DRIVER={driver};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={user};'
            f'PWD={password};'
            f'TrustServerCertificate={yes}'
        )

        connection = pyodbc.connect(connection_string)
        print("Conexión exitosa a la base de datos.")
        return connection
    except pyodbc.Error as e:
        print("Error conectando a la base de datos:", e)
        return None

if __name__ == "__main__":
    connect_to_database()