from flask import request, jsonify
from app import api
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