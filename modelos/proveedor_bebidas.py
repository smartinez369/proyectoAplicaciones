from .proveedor import Proveedor


class ProveedorBebidas(Proveedor):
    def __init__(self, id_proveedor, nombre, telefono, email, direccion):
        super().__init__(id_proveedor, nombre, telefono, email, direccion)

    def mostrar_datos(self):
        print("Rubro: Bebidas")
        super().mostrar_datos()
