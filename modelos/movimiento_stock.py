class MovimientoStock:
    """Registra una entrada o salida y mantiene vinculados producto y usuario."""

    def __init__(self, id_movimiento, tipo_movimiento, cantidad, fecha, producto, usuario):
        if tipo_movimiento not in ("entrada", "salida"):
            raise ValueError("El tipo de movimiento debe ser 'entrada' o 'salida'.")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        self.id_movimiento = id_movimiento
        self.tipo_movimiento = tipo_movimiento
        self.cantidad = int(cantidad)
        self.fecha = fecha
        self.producto = producto
        self.usuario = usuario

    def aplicar(self):
        self.producto.actualizar_stock(self.cantidad, self.tipo_movimiento)
        self.producto.agregar_movimiento(self)
        self.usuario.agregar_movimiento(self)

    def mostrar_datos(self):
        print(
            f"Movimiento {self.id_movimiento}: {self.tipo_movimiento} de {self.cantidad} "
            f"unidades | Fecha: {self.fecha} | Producto: {self.producto.nombre} | "
            f"Usuario: {self.usuario.nombre_completo()}"
        )
