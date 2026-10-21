from .producto import Producto


class Limpieza(Producto):
    def __init__(self, id_producto, nombre, descripcion, precio, stock_actual, tipo_uso=None):
        super().__init__(id_producto, nombre, descripcion, precio, stock_actual)
        self.tipo_uso = tipo_uso

    def mostrar_datos(self):
        super().mostrar_datos()
        print(f"  Tipo de uso: {self.tipo_uso or 'No informado'}")
