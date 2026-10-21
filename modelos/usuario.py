class Usuario:
    """Representa a una persona que utiliza el sistema."""

    def __init__(self, id_usuario, nombre, apellido, email, contrasena):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.contrasena = contrasena
        self.movimientos = []

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def agregar_movimiento(self, movimiento):
        self.movimientos.append(movimiento)

    def mostrar_datos(self):
        print(f"Usuario {self.id_usuario}: {self.nombre_completo()} | {self.email}")
