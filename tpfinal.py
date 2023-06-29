#----------------------------------------------
# Importamos el módulo necesario para gestionar
# la base de datos, y los elementos necesarios
# del framework Flask.
#----------------------------------------------
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

# Nombre del objeto flask.
app = Flask(__name__)
CORS(app)


# Nombre del archivo que contiene la base de datos.
DATABASE = "datos.db"


#----------------------------------------------
# Conectamos con la base de datos. 
# Retornamos el conector (conn)
#----------------------------------------------
def conectar():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

#----------------------------------------------
# Esta funcion crea la tabla "productos" en la
# base de datos, en caso de que no exista.
#----------------------------------------------
def crear_tabla():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS billetes (
                    numero INT PRIMARY KEY,
                    stock INT,
                    precio FLOAT)
            """)
    conn.commit()
    cursor.close()
    conn.close()


#----------------------------------------------
# Esta funcion da de alta un producto en la
# base de datos.
#----------------------------------------------

@app.route('/billetes', methods=['POST'])
def alta_producto():
    data = request.get_json()
    if 'numero' not in data or 'fraccion' not in data or 'precio' not in data:
        return jsonify({'error': 'Falta uno o más campos requeridos'}), 400
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
                    INSERT INTO billetes (numero, fraccion, precio)
                    VALUES(?,?,?) """,
                    (data['numero'], data['fraccion'], data['precio']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'mensaje': 'Alta efectuada correctamente'}), 201
    except:
        return jsonify({'error': 'Error al dar de alta el producto'}), 500
    
@app.route('/billetes/<int:numero>', methods=['GET'])
def consultar_producto(numero):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM billetes 
                            WHERE numero=?""", (numero,))
        producto = cursor.fetchone()
        if producto is None:
            return jsonify({'error': 'Producto no encontrado'}), 404
        else:
            return jsonify({
                'numero': producto['numero'],
                'fraccion': producto['fraccion'],
                'precio': producto['precio']
            })
    except:
        return jsonify({'error': 'Error al consultar el producto'}), 500

    #----------------------------------------------
# Modifica los datos de un producto a partir
# de su código.
#----------------------------------------------
@app.route('/billetes/<int:numero>', methods=['PUT'])
def modificar_producto(numero):
    data = request.get_json()
    if 'descripcion' not in data or 'fraccion' not in data or 'precio' not in data:
        return jsonify({'error': 'Falta uno o más campos requeridos'}), 400
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM billetes WHERE numero=?""", (numero,))
        producto = cursor.fetchone()
        if producto is None:
            return jsonify({'error': 'Producto no encontrado'}), 404
        else:
            cursor.execute("""UPDATE billetes SET fraccion=?, precio=?
                                WHERE numero=?""", (data['fraccion'], data['precio'], numero))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'mensaje': 'Producto modificado correctamente'}), 200
    except:
        return jsonify({'error': 'Error al modificar el producto'}), 500
    
    #----------------------------------------------
# Lista todos los productos en la base de datos.
#----------------------------------------------
@app.route('/billetes', methods=['GET'])
def listar_productos():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM billetes")
        productos = cursor.fetchall()
        response = []
        for producto in productos:
            response.append({
                'numero': producto['numero'],
                'fraccion': producto['fraccion'],
                'precio': producto['precio']
            })
        return jsonify(response)
    except:
        return jsonify({'error': 'Error al listar los productos'}), 500


@app.route('/', methods=['GET'])
def inicio():
    return "Hola Codo a Codo"

#----------------------------------------------
# Ejecutamos la app
#----------------------------------------------
if __name__ == '__main__':
    crear_tabla()
    app.run()


