"""Acceso a datos MySQL. Los nombres de tablas/columnas se validan al usar el esquema."""
from modelos import Producto, Proveedor


# Clase RepositorioMySQL: A?sla el acceso a MySQL. Recibe una conexi?n ya abierta y proporciona operaciones de consulta, CRUD, relaciones y stock.
# M?todos definidos: __init__, _columnas, _requerir, _obj_producto, _obj_proveedor, _columna, _uno, _muchos, obtener_producto, listar_productos, crear_producto, actualizar_producto, eliminar_producto, obtener_proveedor, listar_proveedores, crear_proveedor, actualizar_proveedor, eliminar_proveedor, columna_proveedor_producto, proveedor_de_producto, productos_de_proveedor, registrar_movimiento_stock.
class RepositorioMySQL:
    TABLA_PRODUCTOS = "productos"
    TABLA_PROVEEDORES = "proveedores"

    # __init__: Implementa el comportamiento de __init__ seg?n las operaciones de su cuerpo y la clase o m?dulo que la contiene.
    # Par?metros: conexion.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: Consultar el cuerpo: no se agrega ni altera un valor de retorno.
    def __init__(self, conexion):
        self.conexion = conexion

    # _columnas: Consulta los nombres de columnas de la tabla mediante SHOW COLUMNS y devuelve un conjunto; siempre cierra el cursor.
    # Par?metros: tabla.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def _columnas(self, tabla):
        cursor = self.conexion.cursor()
        try:
            cursor.execute(f"SHOW COLUMNS FROM `{tabla}`")
            return {fila[0] for fila in cursor.fetchall()}
        finally:
            cursor.close()

    # _requerir: Compara columnas disponibles con las necesarias y produce RuntimeError si falta alguna; de lo contrario no devuelve valor significativo.
    # Par?metros: columnas, tabla, necesarias.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    @staticmethod
    def _requerir(columnas, tabla, necesarias):
        faltan = set(necesarias) - columnas
        if faltan:
            raise RuntimeError(
                f"El esquema de {tabla} no coincide: faltan columnas {', '.join(sorted(faltan))}. "
                "Revisa la estructura real antes de adaptar el repositorio."
            )

    # _obj_producto: Transforma una fila diccionario de MySQL en Producto, usando descripci?n vac?a cuando no est? presente.
    # Par?metros: fila.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    @staticmethod
    def _obj_producto(fila):
        return Producto(fila["idproducto"], fila["nombre"], fila.get("descripcion", ""),
                        fila["precio"], fila["stock_actual"])

    # _obj_proveedor: Transforma una fila diccionario en Proveedor, aceptando nombre o nombproveedor y valores vac?os para datos opcionales.
    # Par?metros: fila.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    @staticmethod
    def _obj_proveedor(fila):
        return Proveedor(fila["idproveedor"], fila.get("nombre", fila.get("nombproveedor", "")), fila.get("telefono", ""),
                         fila.get("email", ""), fila.get("direccion", ""))

    # _columna: Devuelve la primera opci?n de nombre que exista en el conjunto de columnas, o None.
    # Par?metros: columnas, *opciones.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    @staticmethod
    def _columna(columnas, *opciones):
        return next((nombre for nombre in opciones if nombre in columnas), None)

    # _uno: Ejecuta una consulta parametrizada con cursor de diccionario y devuelve una fila o None; cierra el cursor incluso ante error.
    # Par?metros: consulta, parametros.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def _uno(self, consulta, parametros=()):
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(consulta, parametros)
            return cursor.fetchone()
        finally:
            cursor.close()

    # _muchos: Ejecuta una consulta parametrizada con cursor de diccionario y devuelve todas las filas; cierra el cursor incluso ante error.
    # Par?metros: consulta, parametros.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def _muchos(self, consulta, parametros=()):
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(consulta, parametros)
            return cursor.fetchall()
        finally:
            cursor.close()

    # obtener_producto: Verifica el esquema, busca el ID con SELECT parametrizado y devuelve Producto o None.
    # Par?metros: id_producto.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def obtener_producto(self, id_producto):
        columnas = self._columnas("productos")
        self._requerir(columnas, "productos", {"idproducto", "nombre", "precio", "stock_actual"})
        fila = self._uno("SELECT * FROM productos WHERE idproducto=%s", (id_producto,))
        return self._obj_producto(fila) if fila else None

    # listar_productos: Verifica columnas y devuelve los productos ordenados por ID como una lista de objetos Producto.
    # Par?metros: No recibe par?metros expl?citos..
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def listar_productos(self):
        columnas = self._columnas("productos")
        self._requerir(columnas, "productos", {"idproducto", "nombre", "precio", "stock_actual"})
        return [self._obj_producto(f) for f in self._muchos("SELECT * FROM productos ORDER BY idproducto")]

    # crear_producto: Prepara un INSERT compatible con las columnas existentes, valida proveedor opcional, confirma la transacci?n y devuelve el producto recuperado. Ante error revierte y propaga la excepci?n.
    # Par?metros: nombre, descripcion, precio, stock, id_proveedor.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def crear_producto(self, nombre, descripcion, precio, stock, id_proveedor=None, id_usuario=None):
        columnas = self._columnas("productos")
        requeridas = {"nombre", "precio", "stock_actual"}
        self._requerir(columnas, "productos", requeridas)
        valores = {"nombre": nombre, "precio": precio, "stock_actual": stock}
        if "descripcion" in columnas:
            valores["descripcion"] = descripcion
        if id_proveedor is not None:
            if id_usuario is None:
                raise ValueError("Debe indicar el ID del usuario que registra el producto.")
            columnas_stock = self._columnas("stock")
            self._requerir(columnas_stock, "stock", {"idproducto", "idusuario", "idproveedor"})
            if not self.obtener_proveedor(id_proveedor):
                raise ValueError("El proveedor indicado no existe.")
            if not self._uno("SELECT idusuario FROM usuarios WHERE idusuario=%s", (id_usuario,)):
                raise ValueError("El usuario indicado no existe.")
        nombres = list(valores)
        cursor = self.conexion.cursor()
        try:
            cursor.execute(
                f"INSERT INTO productos ({', '.join(f'`{n}`' for n in nombres)}) "
                f"VALUES ({', '.join(['%s'] * len(nombres))})",
                tuple(valores[n] for n in nombres),
            )
            nuevo_id = cursor.lastrowid
            if id_proveedor is not None:
                cursor.execute(
                    "INSERT INTO stock (idproducto, idusuario, idproveedor) VALUES (%s, %s, %s)",
                    (nuevo_id, id_usuario, id_proveedor),
                )
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

    # actualizar_producto: Filtra cambios a campos permitidos y existentes, ejecuta UPDATE parametrizado, confirma y devuelve el producto actualizado; revierte ante error.
    # Par?metros: id_producto, cambios.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
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

    # eliminar_producto: Comprueba existencia, elimina y confirma. Si MySQL rechaza el borrado revierte y comunica el posible conflicto de relaciones.
    # Par?metros: id_producto.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def eliminar_producto(self, id_producto):
        if not self.obtener_producto(id_producto):
            raise ValueError("No existe el producto indicado.")
        cursor = self.conexion.cursor()
        try:
            cursor.execute("DELETE FROM stock WHERE idproducto=%s", (id_producto,))
            cursor.execute("DELETE FROM productos WHERE idproducto=%s", (id_producto,))
            self.conexion.commit()
        except Exception:
            self.conexion.rollback()
            raise RuntimeError("No se pudo eliminar: el producto puede tener movimientos u otras relaciones.")
        finally:
            cursor.close()

    # obtener_proveedor: Comprueba las columnas de identificaci?n y nombre, consulta por ID y devuelve Proveedor o None.
    # Par?metros: id_proveedor.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def obtener_proveedor(self, id_proveedor):
        columnas = self._columnas("proveedores")
        nombre = self._columna(columnas, "nombre", "nombproveedor")
        self._requerir(columnas, "proveedores", {"idproveedor"})
        if not nombre:
            raise RuntimeError("La tabla proveedores no contiene nombre ni nombproveedor.")
        fila = self._uno("SELECT * FROM proveedores WHERE idproveedor=%s", (id_proveedor,))
        return self._obj_proveedor(fila) if fila else None

    # listar_proveedores: Comprueba el esquema y devuelve proveedores ordenados por ID como objetos.
    # Par?metros: No recibe par?metros expl?citos..
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def listar_proveedores(self):
        columnas = self._columnas("proveedores")
        self._requerir(columnas, "proveedores", {"idproveedor"})
        if not self._columna(columnas, "nombre", "nombproveedor"):
            raise RuntimeError("La tabla proveedores no contiene nombre ni nombproveedor.")
        return [self._obj_proveedor(f) for f in self._muchos("SELECT * FROM proveedores ORDER BY idproveedor")]

    # crear_proveedor: Selecciona la columna de nombre compatible, inserta los campos disponibles, confirma y devuelve el proveedor recuperado; revierte ante error.
    # Par?metros: nombre, telefono, email, direccion.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
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

    # actualizar_proveedor: Filtra los campos permitidos, adapta el nombre l?gico al nombre real de columna, actualiza y devuelve el objeto; revierte ante error.
    # Par?metros: id_proveedor, cambios.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
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

    # eliminar_proveedor: Comprueba existencia, elimina y confirma; ante restricciones de MySQL revierte y produce RuntimeError.
    # Par?metros: id_proveedor.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def eliminar_proveedor(self, id_proveedor):
        if not self.obtener_proveedor(id_proveedor):
            raise ValueError("No existe el proveedor indicado.")
        cursor = self.conexion.cursor()
        try:
            cursor.execute("DELETE FROM stock WHERE idproveedor=%s", (id_proveedor,))
            cursor.execute("DELETE FROM proveedores WHERE idproveedor=%s", (id_proveedor,))
            self.conexion.commit()
        except Exception:
            self.conexion.rollback()
            raise RuntimeError("No se pudo eliminar: el proveedor puede tener productos relacionados.")
        finally:
            cursor.close()

    # columna_proveedor_producto: Busca la clave for?nea en information_schema y, como alternativa, detecta idproveedor/id_proveedor; devuelve el nombre o None y cierra el cursor.
    # Par?metros: columnas.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
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

    # proveedor_de_producto: Detecta la relaci?n, busca producto y proveedor, vincula los objetos en memoria y devuelve la pareja. Falla si producto o relaci?n no existen.
    # Par?metros: id_producto.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def proveedor_de_producto(self, id_producto):
        fila = self._uno("""SELECT p.*, pr.idproveedor AS relacion_idproveedor,
                           pr.nombproveedor AS relacion_nombre, pr.email AS relacion_email,
                           pr.direccion AS relacion_direccion
                           FROM productos p
                           LEFT JOIN stock s ON p.idproducto=s.idproducto
                           LEFT JOIN proveedores pr ON s.idproveedor=pr.idproveedor
                           WHERE p.idproducto=%s ORDER BY s.idmovimiento DESC LIMIT 1""", (id_producto,))
        if not fila:
            raise ValueError("No existe el producto indicado.")
        producto = self._obj_producto(fila)
        proveedor = (Proveedor(fila["relacion_idproveedor"], fila.get("relacion_nombre", ""), "",
                               fila.get("relacion_email", ""), fila.get("relacion_direccion", ""))
                     if fila.get("relacion_idproveedor") is not None else None)
        if proveedor:
            producto.asignar_proveedor(proveedor)
        return producto, proveedor

    # productos_de_proveedor: Comprueba proveedor y relaci?n, consulta productos asociados, enlaza cada objeto con el proveedor y devuelve la pareja proveedor/lista.
    # Par?metros: id_proveedor.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def productos_de_proveedor(self, id_proveedor):
        proveedor = self.obtener_proveedor(id_proveedor)
        if not proveedor:
            raise ValueError("No existe el proveedor indicado.")
        filas = self._muchos("""SELECT DISTINCT p.* FROM productos p
                              JOIN stock s ON p.idproducto=s.idproducto
                              WHERE s.idproveedor=%s ORDER BY p.idproducto""", (id_proveedor,))
        productos = [self._obj_producto(f) for f in filas]
        for producto in productos:
            proveedor.agregar_producto(producto)
        return proveedor, productos

    # registrar_movimiento_stock: Bloquea la fila del producto, valida y actualiza el saldo, inserta movimiento si hay tabla compatible y confirma los cambios juntos. Revierte ante error y devuelve el producto actualizado.
    # Par?metros: id_producto, id_usuario, tipo, cantidad.
    # Relaci?n: forma parte de RepositorioMySQL y colabora con los componentes indicados en la descripci?n.
    # Retorno: El valor descrito arriba; puede propagarse la excepci?n indicada.
    def registrar_movimiento_stock(self, id_producto, id_usuario, tipo, cantidad):
        """Actualiza el saldo y registra el movimiento en una sola transacci?n."""
        self._requerir(self._columnas("productos"), "productos", {"idproducto", "stock_actual"})
        columnas_stock = self._columnas("stock")
        self._requerir(columnas_stock, "stock", {
            "idmovimiento", "idproducto", "idusuario", "idproveedor",
            "cantidad", "tipo_movimiento",
        })
        cursor = self.conexion.cursor(dictionary=True)
        try:
            tipo_normalizado = str(tipo).strip().lower()
            if tipo_normalizado not in ("entrada", "salida"):
                raise ValueError("El movimiento debe ser 'entrada' o 'salida'.")
            tipo_guardado = "Entrada" if tipo_normalizado == "entrada" else "Salida"

            cursor.execute("SELECT * FROM productos WHERE idproducto=%s FOR UPDATE", (id_producto,))
            fila = cursor.fetchone()
            if not fila:
                raise ValueError("No existe el producto indicado.")

            cursor.execute("SELECT idusuario FROM usuarios WHERE idusuario=%s", (id_usuario,))
            if not cursor.fetchone():
                raise ValueError("No existe el usuario indicado.")

            cursor.execute("""SELECT idproveedor FROM stock
                              WHERE idproducto=%s
                              ORDER BY idmovimiento DESC LIMIT 1""", (id_producto,))
            relacion = cursor.fetchone()
            if not relacion:
                raise ValueError("El producto no tiene un proveedor relacionado en stock.")
            id_proveedor = relacion["idproveedor"]

            producto = self._obj_producto(fila)
            producto.actualizar_stock(cantidad, tipo_normalizado)
            cursor.execute("UPDATE productos SET stock_actual=%s WHERE idproducto=%s",
                           (producto.stock_actual, id_producto))
            cursor.execute("""INSERT INTO stock
                              (idproducto, idusuario, idproveedor, cantidad, tipo_movimiento)
                              VALUES (%s, %s, %s, %s, %s)""",
                           (id_producto, id_usuario, id_proveedor, cantidad, tipo_guardado))
            self.conexion.commit()
            return self.obtener_producto(id_producto)
        except Exception:
            self.conexion.rollback()
            raise
        finally:
            cursor.close()
