import os
import random
import string
import yagmail
from app import api
from werkzeug.utils import secure_filename
from database import db
from models.personaModel import Persona
from models.usuarioModel import Usuario

class UsuarioController:

    @staticmethod
    def generarPasswordTemporal(longitud=8):
        caracteres = string.ascii_letters + string.digits + "!@#$*"
        return "".join(random.choice(caracteres) for _ in range(longitud))

    @staticmethod
    def enviarCredencialesAlCorreo(destinatario, username, password):
        try:
            userCorreo = os.getenv('USERNAME_CORREO')
            passwordCorreo = os.getenv('PASSWORD_CORREO')
            
            if not userCorreo or not passwordCorreo:
                print("Advertencia: Credenciales de correo no configuradas en .env")
                return False

            email = yagmail.SMTP(user=userCorreo, password=passwordCorreo)
            asunto = "Credenciales de Acceso - Sistema"
            
            mensaje=f"Hola,<br><br>Se ha registrado exitosamente en el sistema.<br>\
            Para ingresar al sistema tenga en cuenta las siguientes credenciales de acceso: <br> \
            <br><b>Usuario:</b> {username}\
            <br><b>Contraseña temporal:</b> {password}\
            <br><br>Por favor, ingresa a la plataforma y cambia tu contraseña."
            
            email.send(to=destinatario, subject=asunto, contents=mensaje)
            return True
        except Exception as e:
            print(f"Error al enviar correo con yagmail: {str(e)}")
            return False

    @staticmethod
    def registrarUsuario(data, fileFoto=None):
        identificacion = data.get('identificacion')
        nombres = data.get('nombres')
        apellidos = data.get('apellidos')
        correo = data.get('correo')
        username = data.get('username')
        tipo = data.get('tipo')
       

        if not all([identificacion, nombres, apellidos, correo, username,tipo]):
            return {"error": "Faltan campos obligatorios para el registro"}, 400

        # Validar duplicados
        if Persona.query.filter_by(identificacion=identificacion).first():
            return {"error": "La identificación ya se encuentra registrada"}, 400
        #Hacer lo mismo para el correo y el username
        if Persona.query.filter_by(correo=correo).first():
            return {"error": "El correo electrónico ya se encuentra registrado"}, 400
        if Usuario.query.filter_by(username=username).first():
            return {"error": "El nombre de usuario (username) ya existe"}, 400

        
        # Procesar foto opcional
        rutaFoto = None
       
        if fileFoto:
            filename = secure_filename(f"{identificacion}_{fileFoto.filename}")
            carpetaUpload = api.config['UPLOAD_FOLDER']
            rutaFoto = os.path.join(carpetaUpload, filename)
            fileFoto.save(rutaFoto)
            rutaFoto = f"http://{os.getenv('HOSTNAME')}:{os.getenv('APP_PORT')}/static/fotos/{filename}"
        
        try:
            nuevaPersona = Persona(
                identificacion=identificacion,
                nombres=nombres,
                apellidos=apellidos,
                correo=correo,
                foto=rutaFoto
            )
            db.session.add(nuevaPersona)
            db.session.flush()

            passwordTemporal = UsuarioController.generarPasswordTemporal()

            nuevoUsuario = Usuario(
                idPersona=nuevaPersona.idPersona,
                username=username,
                tipo=tipo,
                estado='Activo'              
            )
            nuevoUsuario.setPassword(passwordTemporal)
            db.session.add(nuevoUsuario)
            db.session.commit()

            # Enviar credenciales al correo electrónico
            UsuarioController.enviarCredencialesAlCorreo(correo, username, passwordTemporal)

            return {
                "mensaje": "Usuario registrado exitosamente y credenciales enviadas por correo.",
                "usuario": nuevoUsuario.toDict()
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"error": f"Error interno al registrar usuario: {str(e)}"}, 500
        
        
    @staticmethod
    def validarCredenciales(username, password):
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario or not usuario.verificarPassword(password):
            return {"error": "Credenciales inválidas"}, 401
        
        if usuario.estado != 'Activo':
            return {"error": "El usuario se encuentra inactivo"}, 403

        return usuario

   