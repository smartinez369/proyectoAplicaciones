from .usuario import Usuario


class Invitado(Usuario):
    def __init__(self, id_usuario, nombre, apellido, email, contrasena):
        super().__init__(id_usuario, nombre, apellido, email, contrasena)

    def consultar_productos(self):
        return "El invitado puede consultar productos."

    def mostrar_datos(self):
        print("Tipo: Invitado")
        super().mostrar_datos()
