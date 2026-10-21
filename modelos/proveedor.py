class Proveedor:
    """Representa al proveedor de uno o varios productos."""

    def __init__(self, id_proveedor, nombre, telefono, email, direccion):
        self.id_proveedor = id_proveedor
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.productos = []

    def agregar_producto(self, producto):
        producto.asignar_proveedor(self)

    def mostrar_datos(self):
        print(f"Proveedor {self.id_proveedor}: {self.nombre} | Tel: {self.telefono} | "
              f"Email: {self.email} | Dirección: {self.direccion}")
