from .usuario import Usuario


class Administrador(Usuario):
    def __init__(self, id_usuario, nombre, apellido, email, contrasena):
        super().__init__(id_usuario, nombre, apellido, email, contrasena)

    def gestionar_inventario(self):
        return "El administrador puede gestionar el inventario."

    def mostrar_datos(self):
        print("Tipo: Administrador")
        super().mostrar_datos()
