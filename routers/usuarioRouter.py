from flask import request, jsonify
from app import api
from flask_jwt_extended import create_access_token, jwt_required
from controllers.usuarioController import UsuarioController

@api.route('/api/usuarios', methods=['POST'])
def registrarUsuario():
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
        fileFoto = request.files.get('fileFoto')
    else:
        data = request.get_json() or {}
        fileFoto = None

    resultado, status_code = UsuarioController.registrarUsuario(data, fileFoto)
    return jsonify(resultado), status_code

@api.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Se requiere username y password"}), 400

    resultado = UsuarioController.validarCredenciales(username, password)
    if isinstance(resultado, tuple):
        return jsonify(resultado[0]), resultado[1]

    usuario = resultado
    #crear el token
    tokenAcceso=create_access_token(identity=str(usuario.idUsuario))

    return jsonify({
        "mensaje": "Inicio de sesión exitoso",
        "tokenAcceso": tokenAcceso,
        "usuario": usuario.toDict()
    }), 200