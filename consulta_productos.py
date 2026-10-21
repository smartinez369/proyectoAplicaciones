"""Demostracion sencilla de conversion de filas MySQL a objetos Producto."""
import mysql.connector

from conexion import conectar_bd
from modelos import Producto


CONSULTA_PRODUCTOS = (
    "SELECT idproducto, nombre, descripcion, precio, stock_actual "
    "FROM productos"
)


def obtener_productos_desde_mysql():
    """Consulta MySQL y devuelve una lista de objetos Producto."""
    conexion = None
    cursor = None
    try:
        # Aqui Python establece la conexion con la base de datos supermercado.
        conexion = conectar_bd()
        print("Conexion con MySQL realizada correctamente.")

        # El cursor ejecuta el SELECT sobre la tabla productos.
        cursor = conexion.cursor()
        cursor.execute(CONSULTA_PRODUCTOS)

        # fetchall recupera las filas que devuelve MySQL como tuplas.
        resultados = cursor.fetchall()
        productos = []
        for fila in resultados:
            # Cada tupla se transforma inmediatamente en un objeto Producto.
            producto = Producto(fila[0], fila[1], fila[2], fila[3], fila[4])
            productos.append(producto)

        return productos
    except mysql.connector.Error as error:
        print(f"Error al conectar o consultar MySQL: {error}")
        return []
    finally:
        # Se liberan los recursos, incluso si ocurrio un error.
        if cursor is not None:
            cursor.close()
        if conexion is not None and conexion.is_connected():
            conexion.close()
            print("Conexion con MySQL cerrada.")


def demostrar_productos_desde_mysql():
    """Muestra que los datos recuperados se usan como objetos Python."""
    productos = obtener_productos_desde_mysql()
    if not productos:
        print("No se recuperaron productos.")
        return productos

    print("\nProductos creados a partir de datos de MySQL:")
    for producto in productos:
        # El programa utiliza el objeto llamando a su propio metodo.
        producto.mostrar_datos()
    return productos
