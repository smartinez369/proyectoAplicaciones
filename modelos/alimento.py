from .producto import Producto


class Alimento(Producto):
    def __init__(self, id_producto, nombre, descripcion, precio, stock_actual, fecha_vencimiento=None):
        super().__init__(id_producto, nombre, descripcion, precio, stock_actual)
        self.fecha_vencimiento = fecha_vencimiento

    def mostrar_datos(self):
        super().mostrar_datos()
        print(f"  Fecha de vencimiento: {self.fecha_vencimiento or 'No informada'}")
