# Sistema de supermercado

Aplicación de consola en Python con entidades orientadas a objetos y persistencia MySQL.

## Preparación y ejecución

```powershell
pip install -r requirements.txt
$env:MYSQL_HOST = "localhost"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "tu_contrasena"
python main.py
```

La base de datos debe llamarse `supermercado`. `conexion.py` obtiene credenciales del entorno y no imprime ni guarda una contraseña predeterminada.

## Esquema

El proyecto conserva las tablas `productos` y `proveedores` y comprueba sus columnas en tiempo de ejecución. El CRUD parte de `productos(idproducto, nombre, descripcion, precio, stock_actual)` y admite `proveedores(idproveedor, nombre o nombproveedor, telefono, email, direccion)`, según los nombres mencionados en las etapas previas. Las columnas opcionales se escriben solo si existen. La relación se detecta mediante una clave foránea a `proveedores.idproveedor` (o una columna `idproveedor`/`id_proveedor` existente). No se crean tablas ni se alteran restricciones.

Los movimientos se insertan en `stock` o `movimientos_stock` solo si esa tabla existe y tiene `tipo_movimiento`, `cantidad` e `idproducto`; `idusuario` y `fecha` se guardan si existen. Comprueba el esquema real antes de usar estas opciones. La base de datos no está incluida en el proyecto.

## Organización

- `modelos/`: entidades y subclases existentes. `Producto` valida su stock encapsulado.
- `conexion.py`: configuración centralizada de conexión.
- `repositorio_mysql.py`: consultas parametrizadas, CRUD, relaciones y transacción del stock.
- `main.py`: menú de consola.
