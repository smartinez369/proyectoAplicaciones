from .usuario import Usuario


class Cliente(Usuario):
    def __init__(self, id_usuario, nombre, apellido, email, contrasena):
        super().__init__(id_usuario, nombre, apellido, email, contrasena)

    def consultar_historial(self):
        return self.movimientos

    def mostrar_datos(self):
        print("Tipo: Cliente")
        super().mostrar_datos()
