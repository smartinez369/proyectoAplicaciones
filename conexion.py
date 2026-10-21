
import os
import mysql.connector


def conectar_bd():
    """Abre una conexión a supermercado usando variables de entorno."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database="supermercado",
        use_pure=True
    )
    

def crear_conexion():
    """Conserva el nombre usado por el resto del proyecto."""
    return conectar_bd()
