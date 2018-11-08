#!/home/zeroth/Projects/project_01_server/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, make_response, jsonify, abort, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import timedelta, datetime
import jwt
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'A_N3w_w4y_t0_S33_th1ng5'
CORS(app)
mongo_client = MongoClient('mongodb://admin:P455w0rd@dev-shard-00-00-bn3aa.mongodb.net:27017,dev-shard-00-01-bn3aa.mongodb.net:27017,dev-shard-00-02-bn3aa.mongodb.net:27017/test?ssl=true&replicaSet=Dev-shard-0&authSource=admin&retryWrites=true')
db = mongo_client.testing_site

@app.route('/')
def hello_world():
    return 'Hello World!'

# Error Handling
@app.errorhandler(404)
def error_404_not_found(error):
    return make_response(jsonify({
        "error": 'Not found.'
    }))

@app.errorhandler(400)
def error_400_bad_request(error):
    return make_response(jsonify({
        'error': 'Bad Request.'
    }))

# Login
@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    data = request.get_json(force=True)
    if 'username' not in data or 'password' not in data:
        abort(400)
    username = data['username']
    password = data['password']
    user = db.usuarios.find_one({'username': username})
    if bool(user):
        if check_password_hash(user['password'], password):
            token = jwt.encode({
                'username': username,
                'exp': datetime.utcnow() + timedelta(hours=8)
            }, app.config['SECRET_KEY'])
            return jsonify({
                'token': token,
                'username': username
            })
        else:
            return jsonify({
                'error': 'Password Incorrect.'
            })
    else:
        return jsonify({
            'error': 'Username Incorrect.'
        })

    return jsonify(data)

@app.route('/home_data', methods=['GET', 'OPTIONS'])
def obtener_data_home():
    pass

# Create user [No terminado]
@app.route('/usuarios/crear', methods=['POST', 'OPTIONS'])
def crear_usuario():
    data = request.get_json()
    data['password'] = generate_password_hash(data['password'])
    db.usuarios.insert_one(data)
    return jsonify({
        'message': 'Usuario Creado.'
    })

# Obtener el registro de la base de datos
@app.route('/registros/obtener', methods=['GET', 'OPTIONS'])
def obtener_registros():
    facturas = db.facturas.find({}, {'_id': False})
    return jsonify([factura for factura in facturas])

# Agregar datos al registro.
@app.route('/registros/agregar', methods=['POST', 'OPTIONS'])
def agregar_registros():
    data = request.get_json(force=True)
    db.facturas.insert_one(data)
    return jsonify({
        'message': 'Factura guardada.',
    })

# Borrar dato de la base de datos.
@app.route('/registros/borrar/<string:factura_id>', methods=['GET', 'OPTIONS'])
def borrar_registro(factura_id):
    
    db.facturas.delete_one({'id_factura': factura_id})
    data = db.facturas.find({}, {'_id': False})
    return jsonify({
        'message': 'Factura borrada.',
        'data': [x for x in data],
        'id_factura_borrada': factura_id
    })
    # except Exception as e:
    #     return jsonify({
    #         'error': 'Error borrando factura.',
    #     })

# Editar datos de la base de datos.
@app.route('/registros/editar/<string:factura_id>', methods=['POST', 'UPDATE', 'OPTIONS'])
def editar_factura(factura_id):
    data = request.get_json()
    db.facturas.update_one(
        {'factura_id': factura_id}, 
        jsonify(data),
        upsert=True)
    facturas = db.facturas.find({}, {'_id': False})
    return jsonify({
        'data': facturas,
        'message': 'Factura actualizada.'
    })

if __name__ == "__main__":
    app.run(debug=True)