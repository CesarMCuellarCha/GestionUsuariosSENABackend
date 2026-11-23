from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    __tablename__ ='usuarios'
    
    idUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idPersona = db.Column(db.Integer, db.ForeignKey('personas.idPersona'), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.Enum('Aprendiz', 'Instructor', name='tipo_enum'), nullable=False)
    estado = db.Column(db.Enum('Activo', 'Inactivo', name='estado_enum'), nullable=False,  default='Activo')
    
    def setPassword(self, passwordPlano):
        self.password = generate_password_hash(passwordPlano)

    def checkPassword(self, passwordPlano):
        return check_password_hash(self.password, passwordPlano)
    
    def toDict(self):
        return{
            "idUsuario": self.idUsuario,
            "idPersona": self.idPersona,
            "username": self.username,
            "password": self.password,
            "estado": self.estado,
            "tipo": self.tipo,
             "persona": self.persona.toDict() if self.persona else None,
        }