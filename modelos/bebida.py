from .producto import Producto


class Bebida(Producto):
    def __init__(self, id_producto, nombre, descripcion, precio, stock_actual, tamanio_ml=None):
        super().__init__(id_producto, nombre, descripcion, precio, stock_actual)
        self.tamanio_ml = tamanio_ml

    def mostrar_datos(self):
        super().mostrar_datos()
        print(f"  Tamano en ml: {self.tamanio_ml or 'No informado'}")
