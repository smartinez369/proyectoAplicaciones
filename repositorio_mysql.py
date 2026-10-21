"""Acceso a datos MySQL. Los nombres de tablas/columnas se validan al usar el esquema."""
from modelos import Producto, Proveedor


class RepositorioMySQL:
    TABLA_PRODUCTOS = "productos"
    TABLA_PROVEEDORES = "proveedores"

    def __init__(self, conexion):
        self.conexion = conexion

    def _columnas(self, tabla):
        cursor = self.conexion.cursor()
        try:
            cursor.execute(f"SHOW COLUMNS FROM `{tabla}`")
            return {fila[0] for fila in cursor.fetchall()}
        finally:
            cursor.close()

    @staticmethod
    def _requerir(columnas, tabla, necesarias):
        faltan = set(necesarias) - columnas
        if faltan:
            raise RuntimeError(
                f"El esquema de {tabla} no coincide: faltan columnas {', '.join(sorted(faltan))}. "
                "Revisa la estructura real antes de adaptar el repositorio."
            )

    @staticmethod
    def _obj_producto(fila):
        return Producto(fila["idproducto"], fila["nombre"], fila.get("descripcion", ""),
                        fila["precio"], fila["stock_actual"])

    @staticmethod
    def _obj_proveedor(fila):
        return Proveedor(fila["idproveedor"], fila.get("nombre", fila.get("nombproveedor", "")), fila.get("telefono", ""),
                         fila.get("email", ""), fila.get("direccion", ""))

    @staticmethod
    def _columna(columnas, *opciones):
        return next((nombre for nombre in opciones if nombre in columnas), None)

    def _uno(self, consulta, parametros=()):
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(consulta, parametros)
            return cursor.fetchone()
        finally:
            cursor.close()

    def _muchos(self, consulta, parametros=()):
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(consulta, parametros)
            return cursor.fetchall()
        finally:
            cursor.close()

    def obtener_producto(self, id_producto):
        columnas = self._columnas("productos")
        self._requerir(columnas, "productos", {"idproducto", "nombre", "precio", "stock_actual"})
        fila = self._uno("SELECT * FROM productos WHERE idproducto=%s", (id_producto,))
        return self._obj_producto(fila) if fila else None

    def listar_productos(self):
        columnas = self._columnas("productos")
        self._requerir(columnas, "productos", {"idproducto", "nombre", "precio", "stock_actual"})
        return [self._obj_producto(f) for f in self._muchos("SELECT * FROM productos ORDER BY idproducto")]

    def crear_producto(self, nombre, descripcion, precio, stock, id_proveedor=None):
        columnas = self._columnas("productos")
        requeridas = {"nombre", "precio", "stock_actual"}
        self._requerir(columnas, "productos", requeridas)
        valores = {"nombre": nombre, "precio": precio, "stock_actual": stock}
        if "descripcion" in columnas:
            valores["descripcion"] = descripcion
        fk_proveedor = self.columna_proveedor_producto(columnas)
        if id_proveedor is not None:
            if not fk_proveedor:
                raise RuntimeError("La tabla productos no tiene una relación de proveedor detectada.")
            if not self.obtener_proveedor(id_proveedor):
                raise ValueError("El proveedor indicado no existe.")
            valores[fk_proveedor] = id_proveedor
        nombres = list(valores)
        cursor = self.conexion.cursor()
        try:
            cursor.execute(
                f"INSERT INTO productos ({', '.join(f'`{n}`' for n in nombres)}) "
                f"VALUES ({', '.join(['%s'] * len(nombres))})",
                tuple(valores[n] for n in nombres),
            )
            nuevo_id = cursor.lastrowid
            self.conexion.commit()
        except Exception:
            self.conexion.rollback()
            raise
        finally:
            cursor.close()
        producto = self.obtener_producto(nuevo_id)
        if id_proveedor is not None:
            proveedor = self.obtener_proveedor(id_proveedor)
            if proveedor:
                producto.asignar_proveedor(proveedor)
        return producto

    def actualizar_producto(self, id_producto, cambios):
        permitidas = {"nombre", "descripcion", "precio", "stock_actual"}
        columnas = self._columnas("productos")
        cambios = {k: v for k, v in cambios.items() if k in permitidas and k in columnas}
        if not cambios:
            raise ValueError("No hay campos válidos para modificar.")
        nombres = list(cambios)
        cursor = self.conexion.cursor()
        try:
            cursor.execute(f"UPDATE productos SET {', '.join(f'`{n}`=%s' for n in nombres)} WHERE idproducto=%s",
                           tuple(cambios[n] for n in nombres) + (id_producto,))
            if cursor.rowcount == 0 and not self.obtener_producto(id_producto):
                raise ValueError("No existe el producto indicado.")
            self.conexion.commit()
        except Exception:
            self.conexion.rollback()
            raise
        finally:
            cursor.close()
        return self.obtener_producto(id_producto)

    def eliminar_producto(self, id_producto):
        if not self.obtener_producto(id_producto):
            raise ValueError("No existe el producto indicado.")
        cursor = self.conexion.cursor()
        try:
            cursor.execute("DELETE FROM productos WHERE idproducto=%s", (id_producto,))
            self.conexion.commit()
        except Exception:
            self.conexion.rollback()
            raise RuntimeError("No se pudo eliminar: el producto puede tener movimientos u otras relaciones.")
        finally:
            cursor.close()

    def obtener_proveedor(self, id_proveedor):
        columnas = self._columnas("proveedores")
        nombre = self._columna(columnas, "nombre", "nombproveedor")
        self._requerir(columnas, "proveedores", {"idproveedor"})
        if not nombre:
            raise RuntimeError("La tabla proveedores no contiene nombre ni nombproveedor.")
        fila = self._uno("SELECT * FROM proveedores WHERE idproveedor=%s", (id_proveedor,))
        return self._obj_proveedor(fila) if fila else None

    def listar_proveedores(self):
        columnas = self._columnas("proveedores")
        self._requerir(columnas, "proveedores", {"idproveedor"})
        if not self._columna(columnas, "nombre", "nombproveedor"):
            raise RuntimeError("La tabla proveedores no contiene nombre ni nombproveedor.")
        return [self._obj_proveedor(f) for f in self._muchos("SELECT * FROM proveedores ORDER BY idproveedor")]

    def crear_proveedor(self, nombre, telefono, email, direccion):
        columnas = self._columnas("proveedores")
        columna_nombre = self._columna(columnas, "nombre", "nombproveedor")
        if not columna_nombre:
            raise RuntimeError("La tabla proveedores no contiene nombre ni nombproveedor.")
        valores = {k: v for k, v in {columna_nombre: nombre, "telefono": telefono,
                                     "email": email, "direccion": direccion}.items() if k in columnas}
        nombres = list(valores)
        cursor = self.conexion.cursor()
        try:
            cursor.execute(f"INSERT INTO proveedores ({', '.join(f'`{n}`' for n in nombres)}) "
                           f"VALUES ({', '.join(['%s'] * len(nombres))})", tuple(valores[n] for n in nombres))
            nuevo_id = cursor.lastrowid
            self.conexion.commit()
        except Exception:
            self.conexion.rollback()
            raise
        finally:
            cursor.close()
        return self.obtener_proveedor(nuevo_id)

    def actualizar_proveedor(self, id_proveedor, cambios):
        columnas = self._columnas("proveedores")
        nombre_col = self._columna(columnas, "nombre", "nombproveedor")
        cambios = {(nombre_col if k == "nombre" else k): v for k, v in cambios.items()
                   if (k in {"nombre", "telefono", "email", "direccion"} and
                       (k in columnas or (k == "nombre" and nombre_col)))}
        if not cambios:
            raise ValueError("No hay campos válidos para modificar.")
        nombres = list(cambios)
        cursor = self.conexion.cursor()
        try:
            cursor.execute(f"UPDATE proveedores SET {', '.join(f'`{n}`=%s' for n in nombres)} WHERE idproveedor=%s",
                           tuple(cambios[n] for n in nombres) + (id_proveedor,))
            if cursor.rowcount == 0 and not self.obtener_proveedor(id_proveedor):
                raise ValueError("No existe el proveedor indicado.")
            self.conexion.commit()
        except Exception:
            self.conexion.rollback()
            raise
        finally:
            cursor.close()
        return self.obtener_proveedor(id_proveedor)

    def eliminar_proveedor(self, id_proveedor):
        if not self.obtener_proveedor(id_proveedor):
            raise ValueError("No existe el proveedor indicado.")
        cursor = self.conexion.cursor()
        try:
            cursor.execute("DELETE FROM proveedores WHERE idproveedor=%s", (id_proveedor,))
            self.conexion.commit()
        except Exception:
            self.conexion.rollback()
            raise RuntimeError("No se pudo eliminar: el proveedor puede tener productos relacionados.")
        finally:
            cursor.close()

    def columna_proveedor_producto(self, columnas=None):
        columnas = columnas or self._columnas("productos")
        cursor = self.conexion.cursor()
        try:
            cursor.execute("""SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='productos'
                AND REFERENCED_TABLE_NAME='proveedores' AND REFERENCED_COLUMN_NAME='idproveedor'""")
            fila = cursor.fetchone()
            if fila:
                return fila[0]
            return next((n for n in ("idproveedor", "id_proveedor") if n in columnas), None)
        finally:
            cursor.close()

    def proveedor_de_producto(self, id_producto):
        columna = self.columna_proveedor_producto()
        if not columna:
            raise RuntimeError("El esquema no define una relación productos-proveedores.")
        fila = self._uno(f"SELECT * FROM productos WHERE idproducto=%s", (id_producto,))
        if not fila:
            raise ValueError("No existe el producto indicado.")
        producto = self._obj_producto(fila)
        proveedor = self.obtener_proveedor(fila[columna]) if fila.get(columna) is not None else None
        if proveedor:
            producto.asignar_proveedor(proveedor)
        return producto, proveedor

    def productos_de_proveedor(self, id_proveedor):
        proveedor = self.obtener_proveedor(id_proveedor)
        if not proveedor:
            raise ValueError("No existe el proveedor indicado.")
        columna = self.columna_proveedor_producto()
        if not columna:
            raise RuntimeError("El esquema no define una relación productos-proveedores.")
        filas = self._muchos(f"SELECT * FROM productos WHERE `{columna}`=%s", (id_proveedor,))
        productos = [self._obj_producto(f) for f in filas]
        for producto in productos:
            proveedor.agregar_producto(producto)
        return proveedor, productos

    def registrar_movimiento_stock(self, id_producto, id_usuario, tipo, cantidad):
        """Actualiza el stock y el movimiento en una transacción con bloqueo de fila."""
        self._requerir(self._columnas("productos"), "productos", {"idproducto", "stock_actual"})
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM productos WHERE idproducto=%s FOR UPDATE", (id_producto,))
            fila = cursor.fetchone()
            if not fila:
                raise ValueError("No existe el producto indicado.")
            producto = self._obj_producto(fila)
            producto.actualizar_stock(cantidad, tipo)
            cursor.execute("UPDATE productos SET stock_actual=%s WHERE idproducto=%s",
                           (producto.stock_actual, id_producto))
            catalogo = self.conexion.cursor()
            try:
                catalogo.execute("SHOW TABLES")
                tablas = [fila[0] for fila in catalogo.fetchall()]
            finally:
                catalogo.close()
            if any(str(t).lower() in ("stock", "movimientos_stock") for t in tablas):
                tabla = next(str(t) for t in tablas if str(t).lower() in ("stock", "movimientos_stock"))
                cols = self._columnas(tabla)
                requeridas = {"tipo_movimiento", "cantidad", "idproducto"}
                self._requerir(cols, tabla, requeridas)
                campos = {"tipo_movimiento": tipo, "cantidad": cantidad, "idproducto": id_producto}
                if "idusuario" in cols:
                    campos["idusuario"] = id_usuario
                if "fecha" in cols:
                    campos["fecha"] = __import__("datetime").datetime.now()
                nombres = list(campos)
                cursor.execute(f"INSERT INTO `{tabla}` ({', '.join(f'`{n}`' for n in nombres)}) "
                               f"VALUES ({', '.join(['%s'] * len(nombres))})", tuple(campos[n] for n in nombres))
            self.conexion.commit()
            return self.obtener_producto(id_producto)
        except Exception:
            self.conexion.rollback()
            raise
        finally:
            cursor.close()
