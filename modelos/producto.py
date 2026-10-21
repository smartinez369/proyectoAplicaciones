from decimal import Decimal


class Producto:
    """Entidad de inventario asociable a un proveedor y a movimientos."""

    def __init__(self, id_producto, nombre, descripcion, precio, stock_actual):
        self.id_producto = id_producto
        self.nombre = str(nombre).strip()
        if not self.nombre:
            raise ValueError("El nombre del producto no puede estar vacío.")
        self.descripcion = descripcion or ""
        self.precio = Decimal(str(precio))
        if not self.precio.is_finite() or self.precio < 0:
            raise ValueError("El precio no puede ser negativo ni inválido.")
        self.stock_actual = stock_actual
        self.proveedor = None
        self.movimientos = []

    @property
    def stock_actual(self):
        return self._stock_actual

    @stock_actual.setter
    def stock_actual(self, valor):
        if isinstance(valor, bool):
            raise ValueError("El stock debe ser un entero no negativo.")
        try:
            numero = Decimal(str(valor))
            if not numero.is_finite() or numero != numero.to_integral_value():
                raise ValueError
            cantidad = int(numero)
        except (TypeError, ValueError, OverflowError, ArithmeticError) as error:
            raise ValueError("El stock debe ser un entero no negativo.") from error
        if cantidad < 0:
            raise ValueError("El stock debe ser un entero no negativo.")
        self._stock_actual = cantidad

    def asignar_proveedor(self, proveedor):
        self.proveedor = proveedor
        if self not in proveedor.productos:
            proveedor.productos.append(self)

    def actualizar_stock(self, cantidad, tipo_movimiento):
        if isinstance(cantidad, bool):
            raise ValueError("La cantidad debe ser un entero positivo.")
        try:
            numero = Decimal(str(cantidad))
            if not numero.is_finite() or numero != numero.to_integral_value():
                raise ValueError
            cantidad = int(numero)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("La cantidad debe ser un entero positivo.") from error
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        if tipo_movimiento == "entrada":
            self.stock_actual += cantidad
        elif tipo_movimiento == "salida":
            if cantidad > self.stock_actual:
                raise ValueError("No hay stock suficiente para registrar la salida.")
            self.stock_actual -= cantidad
        else:
            raise ValueError("El movimiento debe ser 'entrada' o 'salida'.")

    def aumentar_stock(self, cantidad):
        self.actualizar_stock(cantidad, "entrada")

    def disminuir_stock(self, cantidad):
        self.actualizar_stock(cantidad, "salida")

    def agregar_movimiento(self, movimiento):
        self.movimientos.append(movimiento)

    def mostrar_datos(self):
        proveedor = self.proveedor.nombre if self.proveedor else "Sin asignar"
        print(
            f"Producto {self.id_producto}: {self.nombre} | {self.descripcion} | "
            f"${self.precio:.2f} | Stock: {self.stock_actual} | Proveedor: {proveedor}"
        )
