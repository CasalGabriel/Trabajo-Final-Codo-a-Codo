import sqlite3
from flask import Flask,  jsonify, request
from flask_cors import CORS

# Configurar la conexión a la base de datos SQLite
DATABASE = 'datos.db'


def conectar():
    conn= sqlite3.connect (DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn

def crear_tabla():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS billetes (
            numero INTEGER PRIMARY KEY,
            fraccion INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()
    
# Verificar si la base de datos existe, si no, crearla y crear la tabla
def crear_database():
    conn = sqlite3.connect(DATABASE)
    conn.close()
    crear_tabla()

# Crear la base de datos y la tabla si no existen
crear_database()


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

class Inventario:
    def __init__(self):
        self.conexion = conectar()
        self.cursor = self.conexion.cursor()
        
    def agregar_producto(self, numero, fraccion, precio):
        producto_existente = self.consultar_producto(numero)
        if producto_existente:
            return jsonify({'message': 'Ya existe un producto con ese código.'}), 400
        
        
        nuevo_producto = Producto(numero, fraccion, precio)
        self.cursor.execute("INSERT INTO billetes VALUES (?, ?, ?)", (numero, fraccion, precio))
        self.conexion.commit()
        return jsonify({'message': 'Producto agregado correctamente.'}), 200
    
    
    def consultar_producto(self, numero):
        self.cursor.execute("SELECT * FROM billetes WHERE numero = ?", (numero,))
        row = self.cursor.fetchone()
        if row:
            numero, fraccion, precio = row
            return Producto(numero, fraccion, precio)
        return None
    
    
    def modificar_producto(self, numero, nueva_fraccion, nuevo_precio):
        producto = self.consultar_producto(numero)
        if producto:
            producto.modificar(nueva_fraccion, nuevo_precio)
            self.cursor.execute("UPDATE billetes SET fraccion = ?, precio = ? WHERE numero = ?",
                                (nueva_fraccion, nuevo_precio, numero))
            self.conexion.commit()
            return jsonify({'message': 'Producto modificado correctamente.'}), 200
        return jsonify({'message': 'Producto no encontrado.'}), 404

    def listar_productos(self):
        self.cursor.execute("SELECT * FROM billetes")
        rows = self.cursor.fetchall()
        productos = []
        for row in rows:
            numero, fraccion, precio = row
            producto = {'numero': numero, 'fraccion': fraccion, 'precio': precio}
            productos.append(producto)
        return jsonify(productos), 200
    
    def eliminar_producto(self, numero):
        self.cursor.execute("DELETE FROM billetes WHERE numero = ?", (numero,))
        if self.cursor.rowcount > 0:
            self.conexion.commit()
            return jsonify({'message': 'Producto eliminado correctamente.'}), 200
        return jsonify({'message': 'Producto no encontrado.'}), 404

# -------------------------------------------------------------------
# Definimos la clase "Carrito"
# -------------------------------------------------------------------
class Carrito:
    def __init__(self):
        self.conexion = conectar()
        self.cursor = self.conexion.cursor()
        self.items = []
        
    def agregar(self, numero, fraccion, inventario):
        producto = inventario.consultar_producto(numero)
        if producto is None:
            return jsonify({'message': 'El producto no existe.'}), 404
        if producto.fraccion < fraccion:
            return jsonify({'message': 'Cantidad en stock insuficiente.'}), 400
        
        for item in self.items:
            if item.numero == numero:
                item.fraccion += fraccion
                self.cursor.execute("UPDATE billetes SET fraccion = fraccion - ? WHERE numero = ?",
                                    (fraccion, numero))
                self.conexion.commit()
                return jsonify({'message': 'Producto agregado al carrito correctamente.'}), 200
        nuevo_item = Producto(numero, fraccion, producto.precio)
        self.items.append(nuevo_item)
        self.cursor.execute("UPDATE billetes SET fraccion = fraccion - ? WHERE numero = ?",
                            (fraccion, numero))
        self.conexion.commit()
        return jsonify({'message': 'Producto agregado al carrito correctamente.'}), 200
    
    def quitar(self, numero, fraccion, inventario): 
        for item in self.items:
            if item.numero == numero:
                if fraccion > item.fraccion:
                    return jsonify({'message': 'Cantidad a quitar mayor a la cantidad en el carrito.'}), 400
            item.fraccion -= fraccion
            if item.fraccion == 0:
                self.items.remove(item)
            self.cursor.execute("UPDATE billetes SET fraccion = fraccion + ? WHERE numero = ?",
                                    (fraccion, numero))
            self.conexion.commit()
            return jsonify({'message': 'Producto quitado del carrito correctamente.'}), 200
        return jsonify({'message': 'El producto no se encuentra en el carrito.'}), 404 
    
    def mostrar(self):
        productos_carrito = []
        for item in self.items:
            producto = {'numero': item.numero, 'fraccion': item.fraccion,
                        'precio': item.precio}
            productos_carrito.append(producto)
        return jsonify(productos_carrito), 200
  
  
app = Flask(__name__)
CORS(app)

carrito = Carrito()         # Instanciamos un carrito
inventario = Inventario()   # Instanciamos un inventario

# Ruta para obtener los datos de un producto según su código
@app.route('/productos/<int:numero>', methods=['GET'])
def obtener_producto(numero):
    producto = inventario.consultar_producto(numero)
    if producto:
        return jsonify({
            'numero': producto.numero,
            'fraccion': producto.fraccion,
            'precio': producto.precio
        }), 200
    return jsonify({'message': 'Producto no encontrado.'}), 404

# Ruta para obtener la lista de productos del inventario
@app.route('/billetes', methods=['GET'])
def obtener_productos():
    return inventario.listar_productos()

# Ruta para agregar un producto al inventario
@app.route('/billetes', methods=['POST'])
def agregar_producto():
    numero = request.json.get('numero')
    fraccion = request.json.get('fraccion')
    precio = request.json.get('precio')
    return inventario.agregar_producto(numero, fraccion, precio)

# Ruta para modificar un producto del inventario
@app.route('/billetes/<int:numero>', methods=['PUT'])
def modificar_producto(numero):
    nueva_fraccion = request.json.get('fraccion')
    nuevo_precio = request.json.get('precio')
    return inventario.modificar_producto(numero, nueva_fraccion, nuevo_precio)

# Ruta para eliminar un producto del inventario
@app.route('/billetes/<int:numero>', methods=['DELETE'])
def eliminar_producto(numero):
    return inventario.eliminar_producto(numero)

# Ruta para agregar un producto al carrito
@app.route('/carrito', methods=['POST'])
def agregar_carrito():
    numero = request.json.get('numero')
    fraccion = request.json.get('fraccion')
    inventario = Inventario()
    return carrito.agregar(numero, fraccion, inventario)

# Ruta para quitar un producto del carrito
@app.route('/carrito', methods=['DELETE'])
def quitar_carrito():
    numero = request.json.get('numero')
    fraccion = request.json.get('fraccion')
    inventario = Inventario()
    return carrito.quitar(numero, fraccion, inventario)

# Ruta para obtener el contenido del carrito
@app.route('/carrito', methods=['GET'])
def obtener_carrito():
    return carrito.mostrar()

# Ruta para obtener la lista de productos del inventario
@app.route('/')
def index():
    return 'API de Inventario'

# Finalmente, si estamos ejecutando este archivo, lanzamos app.
if __name__ == '__main__':
    app.run()