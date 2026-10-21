"""Menú de consola para el CRUD del supermercado."""
import re
from decimal import Decimal, InvalidOperation

import mysql.connector

from conexion import crear_conexion
from repositorio_mysql import RepositorioMySQL


def entero(mensaje, permitir_vacio=False):
    valor = input(mensaje).strip()
    if permitir_vacio and not valor:
        return None
    numero = int(valor)
    return numero


def texto(mensaje, obligatorio=False):
    valor = input(mensaje).strip()
    if obligatorio and not valor:
        raise ValueError("Este campo es obligatorio.")
    return valor


def correo(valor):
    if valor and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor):
        raise ValueError("El formato del correo electrónico no es válido.")
    return valor


class SistemaSupermercado:
    def _con_repositorio(self, accion):
        conexion = None
        try:
            conexion = crear_conexion()
            return accion(RepositorioMySQL(conexion))
        except (mysql.connector.Error, ValueError, RuntimeError) as error:
            print(f"Error: {error}")
            return None
        finally:
            if conexion is not None and conexion.is_connected():
                conexion.close()

    @staticmethod
    def _mostrar(objeto):
        if objeto is None:
            print("No se encontró el registro.")
        elif isinstance(objeto, list):
            if not objeto:
                print("La lista está vacía.")
            for registro in objeto:
                registro.mostrar_datos()
        else:
            objeto.mostrar_datos()

    def producto_crear(self, repo):
        nombre = texto("Nombre: ", True)
        descripcion = texto("Descripción: ")
        precio = Decimal(texto("Precio: "))
        stock = entero("Stock inicial: ")
        idp = entero("ID proveedor (Enter para omitir): ", True)
        if precio < 0 or stock < 0:
            raise ValueError("El precio y el stock no pueden ser negativos.")
        self._mostrar(repo.crear_producto(nombre, descripcion, precio, stock, idp))

    def producto_actualizar(self, repo):
        idp = entero("ID producto: ")
        if not repo.obtener_producto(idp):
            print("No existe el producto indicado."); return
        cambios = {}
        print("Deja vacío un campo para conservar su valor.")
        for campo in ("nombre", "descripcion", "precio", "stock_actual"):
            valor = input(f"{campo}: ").strip()
            if valor:
                if campo in ("precio", "stock_actual"):
                    cambios[campo] = Decimal(valor) if campo == "precio" else int(valor)
                    if cambios[campo] < 0:
                        raise ValueError("Precio y stock deben ser no negativos.")
                else:
                    cambios[campo] = valor
        self._mostrar(repo.actualizar_producto(idp, cambios))

    def proveedor_crear(self, repo):
        nombre = texto("Nombre: ", True)
        telefono = texto("Teléfono: ")
        email = correo(texto("Email: "))
        direccion = texto("Dirección: ")
        self._mostrar(repo.crear_proveedor(nombre, telefono, email, direccion))

    def proveedor_actualizar(self, repo):
        idp = entero("ID proveedor: ")
        if not repo.obtener_proveedor(idp):
            print("No existe el proveedor indicado."); return
        cambios = {}
        print("Deja vacío un campo para conservar su valor.")
        for campo in ("nombre", "telefono", "email", "direccion"):
            valor = input(f"{campo}: ").strip()
            if valor:
                cambios[campo] = correo(valor) if campo == "email" else valor
        self._mostrar(repo.actualizar_proveedor(idp, cambios))

    def ejecutar(self):
        acciones = {
            "1": lambda r: self.producto_crear(r),
            "2": lambda r: self._mostrar(r.listar_productos()),
            "3": lambda r: self._mostrar(r.obtener_producto(entero("ID producto: "))),
            "4": self.producto_actualizar,
            "5": lambda r: self._borrar_producto(r),
            "6": self.proveedor_crear,
            "7": lambda r: self._mostrar(r.listar_proveedores()),
            "8": lambda r: self._mostrar(r.obtener_proveedor(entero("ID proveedor: "))),
            "9": self.proveedor_actualizar,
            "10": lambda r: self._borrar_proveedor(r),
            "11": lambda r: self._relacion_producto(r),
            "12": lambda r: self._relacion_proveedor(r),
            "13": lambda r: self._stock(r, "entrada"),
            "14": lambda r: self._stock(r, "salida"),
        }
        while True:
            print("\n--- Supermercado ---\n1 Registrar producto\n2 Listar productos\n3 Buscar producto\n"
                  "4 Modificar producto\n5 Eliminar producto\n6 Registrar proveedor\n7 Listar proveedores\n"
                  "8 Buscar proveedor\n9 Modificar proveedor\n10 Eliminar proveedor\n"
                  "11 Proveedor de un producto\n12 Productos de un proveedor\n"
                  "13 Entrada de stock\n14 Salida de stock\n0 Salir")
            opcion = input("Opción: ").strip()
            if opcion == "0":
                return
            if opcion not in acciones:
                print("Opción inválida."); continue
            try:
                self._con_repositorio(acciones[opcion])
            except (ValueError, InvalidOperation, TypeError) as error:
                print(f"Dato inválido: {error}")

    def _borrar_producto(self, repo):
        ident = entero("ID producto: ")
        producto = repo.obtener_producto(ident)
        if not producto:
            print("No existe el producto indicado."); return
        producto.mostrar_datos()
        if input("¿Confirmas eliminarlo? (s/N): ").strip().lower() == "s":
            repo.eliminar_producto(ident); print("Producto eliminado.")

    def _borrar_proveedor(self, repo):
        ident = entero("ID proveedor: ")
        proveedor = repo.obtener_proveedor(ident)
        if not proveedor:
            print("No existe el proveedor indicado."); return
        proveedor.mostrar_datos()
        if input("¿Confirmas eliminarlo? (s/N): ").strip().lower() == "s":
            repo.eliminar_proveedor(ident); print("Proveedor eliminado.")

    def _relacion_producto(self, repo):
        producto, proveedor = repo.proveedor_de_producto(entero("ID producto: "))
        producto.mostrar_datos()
        if proveedor:
            proveedor.mostrar_datos()
        else:
            print("El producto no tiene proveedor asociado.")

    def _relacion_proveedor(self, repo):
        proveedor, productos = repo.productos_de_proveedor(entero("ID proveedor: "))
        proveedor.mostrar_datos()
        self._mostrar(productos)

    def _stock(self, repo, tipo):
        producto = repo.registrar_movimiento_stock(entero("ID producto: "),
                                                   entero("ID usuario (0 si no aplica): "),
                                                   tipo, entero("Cantidad: "))
        self._mostrar(producto)


if __name__ == "__main__":
    SistemaSupermercado().ejecutar()
