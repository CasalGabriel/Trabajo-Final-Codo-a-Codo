import sqlite3

DATABASE = "datos.db"

def conectar():
    conn= sqlite3.connect (DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn
conn = conectar()
cursor = conn.cursor()
cursor.execute ("CREATE TABLE IF NOT EXISTS billetes (numero INTEGER PRIMARY KEY, fraccion INTEGER NOT NULL, precio REAL NOT NULL)")
conn.commit()
cursor.close()
conn.close

# -------------------------------------------------------------------
# Definimos la clase "Producto"
# -------------------------------------------------------------------
class Producto:
    def __init__(self, numero, fraccion, precio):
        self.numero = numero
        self.fraccion = fraccion
        self.precio = precio

    def modificar(self, nueva_fraccion, nuevo_precio):
        
        self.fraccion = nueva_fraccion
        self.precio = nuevo_precio


# -------------------------------------------------------------------
# Definimos la clase "Inventario"
# -------------------------------------------------------------------
class Inventario:
    def __init__(self):
        self.conexion = conectar()
        self.cursor = self.conexion.cursor()

    def agregar_producto(self, numero, fraccion, precio):
        producto_existente = self.consultar_producto(numero)
        if producto_existente:
            print("Ya existe un producto con ese código.")
            return False

        nuevo_producto = Producto(numero, fraccion, precio)
        self.cursor.execute("INSERT INTO billetes VALUES (?, ?, ?)", (numero, fraccion, precio))
        self.conexion.commit()
        return True

    def consultar_producto(self, numero):
        self.cursor.execute("SELECT * FROM billetes WHERE numero = ?", (numero,))
        row = self.cursor.fetchone()
        if row:
            numero, fraccion, precio = row
            return Producto(numero, fraccion, precio)
        return False

    def modificar_producto(self, numero, nueva_fraccion, nuevo_precio):
        producto = self.consultar_producto(numero)
        if producto:
            producto.modificar(nueva_fraccion, nuevo_precio)
            self.cursor.execute("UPDATE billetes SET fraccion = ?, precio = ? WHERE numero = ?",
                                (nueva_fraccion, nuevo_precio, numero))
            self.conexion.commit()

    def listar_productos(self):
        print("-" * 30)
        self.cursor.execute("SELECT * FROM billetes")
        rows = self.cursor.fetchall()
        for row in rows:
            numero, fraccion, precio = row
            print(f"Número: {numero}")
           
            print(f"Fracción: {fraccion}")
            print(f"Precio: {precio}")
            print("-" * 30)

    def eliminar_producto(self, numero):
        self.cursor.execute("DELETE FROM billetes WHERE numero = ?", (numero,))
        if self.cursor.rowcount > 0:
            print("Producto eliminado.")
            self.conexion.commit()
        else:
            print("Producto no encontrado.")
        
# -------------------------------------------------------------------
# Definimos la clase "Carrito"
# -------------------------------------------------------------------
class Carrito:
    def __init__(self):
        self.conexion = sqlite3.connect("datos.db")  # Conexión a la base de datos
        self.cursor = self.conexion.cursor()
        self.items = []

    def agregar(self, numero, fraccion, inventario):
        producto = inventario.consultar_producto(numero)
        if producto is False:
            print("El producto no existe.")
            return False
        if producto.fraccion < fraccion:
            print("Cantidad en stock insuficiente.")
            return False

        for item in self.items:
            if item.numero == numero:
                item.fraccion += fraccion
                self.cursor.execute("UPDATE billetes SET fraccion = fraccion - ? WHERE numero = ?",
                                    (fraccion, numero))
                self.conexion.commit()
                return True

        nuevo_item = Producto(numero, fraccion, producto.precio)
        self.items.append(nuevo_item)
        self.cursor.execute("UPDATE billetes SET fraccion = fraccion - ? WHERE numero = ?",
                            (fraccion, numero))
        self.conexion.commit()
        return True

    def quitar(self, numero, fraccion, inventario): #Revisar
        for item in self.items:
            if item.numero == numero:
                if fraccion > item.fraccion:
                    print("Cantidad a quitar mayor a la cantidad en el carrito.")
                    return False
                item.fraccion -= fraccion
                if item.fraccion == 0:
                    self.items.remove(item)
                self.cursor.execute("UPDATE billetes SET fraccion = fraccion + ? WHERE numero = ?",
                                    (fraccion, numero))
                self.conexion.commit()
                return True

        print("El producto no se encuentra en el carrito.")
        return False

    def mostrar(self):
        print("-" * 30)
        for item in self.items:
            print(f"Numero: {item.numero}")
            print(f"Fracción: {item.fraccion}")
            print(f"Precio: {item.precio}")
            print("-" * 30)


# -------------------------------------------------------------------
# Ejemplo de uso de las clases y objetos definidos antes:
# -------------------------------------------------------------------
# Crear una instancia de la clase Inventario
x = Inventario()

# Crear una instancia de la clase Carrito
mi_carrito = Carrito()

mi_carrito.agregar(36670, 2, x)  # Agregar 2 unidades del producto con código 1 al carrito
mi_carrito.agregar(36672, 1, x)  # Agregar 1 unidad del producto con código 3 al carrito
mi_carrito.mostrar()
x.listar_productos()





