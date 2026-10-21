from .proveedor import Proveedor


class ProveedorAlimentos(Proveedor):
    def __init__(self, id_proveedor, nombre, telefono, email, direccion):
        super().__init__(id_proveedor, nombre, telefono, email, direccion)

    def mostrar_datos(self):
        print("Rubro: Alimentos")
        super().mostrar_datos()
