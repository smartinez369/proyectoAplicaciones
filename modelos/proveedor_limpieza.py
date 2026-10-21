from .proveedor import Proveedor


class ProveedorLimpieza(Proveedor):
    def __init__(self, id_proveedor, nombre, telefono, email, direccion):
        super().__init__(id_proveedor, nombre, telefono, email, direccion)

    def mostrar_datos(self):
        print("Rubro: Limpieza")
        super().mostrar_datos()
