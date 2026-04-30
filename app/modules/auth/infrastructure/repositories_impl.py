from typing import Optional
from sqlalchemy.orm import Session
from app.modules.users.domain.entities import Usuario
from app.modules.auth.domain.interfaces import IUsuarioRepository
from app.modules.users.infrastructure.orm_models import UsuarioORM

class UsuarioRepositoryImpl(IUsuarioRepository):
    """
    Implementación del repositorio de usuarios orientada a la autenticación.
    
    Provee métodos para la búsqueda, creación y actualización de perfiles 
    de usuario utilizando SQLAlchemy como motor de persistencia.
    """
    
    def __init__(self, db: Session):
        """
        :param db: Sesión de base de datos activa.
        """
        self.db = db

    def _to_entity(self, orm_model: UsuarioORM) -> Usuario:
        """
        Mapea el modelo ORM de base de datos a la entidad de dominio.
        
        :param orm_model: Objeto UsuarioORM recuperado por SQLAlchemy.
        :return: Entidad de dominio Usuario.
        """
        return Usuario(
            id_usuario=orm_model.id_usuario,
            nombre_usuario=orm_model.nombre_usuario,
            email_usuario=orm_model.email_usuario,
            password_hash=orm_model.password_hash,
            telefono_usuario=orm_model.telefono_usuario,
            url_foto_perfil=orm_model.url_foto_perfil,
            rol_usuario=orm_model.rol_usuario,
            reliability_score=orm_model.reliability_score,
            fecha_creacion_usuario=orm_model.fecha_creacion_usuario
        )

    def get_by_email(self, email: str) -> Optional[Usuario]:
        """
        Busca un usuario en el sistema mediante su dirección de correo electrónico.
        
        :param email: Correo a buscar.
        :return: Entidad Usuario o None si no se encontró.
        """
        orm_user = self.db.query(UsuarioORM).filter(UsuarioORM.email_usuario == email).first()
        if orm_user:
            return self._to_entity(orm_user)
        return None

    def create(self, usuario: Usuario) -> Usuario:
        """
        Registra un nuevo usuario en la persistencia local.
        
        :param usuario: Entidad de dominio con los datos del nuevo usuario.
        :return: Entidad persistida con su ID generado.
        """
        orm_user = UsuarioORM(
            nombre_usuario=usuario.nombre_usuario,
            email_usuario=usuario.email_usuario,
            password_hash=usuario.password_hash,
            telefono_usuario=usuario.telefono_usuario,
            url_foto_perfil=usuario.url_foto_perfil,
            rol_usuario=usuario.rol_usuario,
            reliability_score=usuario.reliability_score
        )
        self.db.add(orm_user)
        self.db.commit()
        self.db.refresh(orm_user)
        return self._to_entity(orm_user)

    def update(self, usuario: Usuario) -> Usuario:
        """
        Sincroniza los cambios de una entidad de usuario con la base de datos.
        
        :param usuario: Entidad de dominio con los cambios aplicados.
        :raises ValueError: Si el ID del usuario no existe en la base de datos.
        :return: Entidad actualizada.
        """
        orm_user = self.db.query(UsuarioORM).filter(UsuarioORM.id_usuario == usuario.id_usuario).first()
        if orm_user:
            orm_user.nombre_usuario = usuario.nombre_usuario
            orm_user.email_usuario = usuario.email_usuario
            orm_user.password_hash = usuario.password_hash
            orm_user.telefono_usuario = usuario.telefono_usuario
            orm_user.url_foto_perfil = usuario.url_foto_perfil
            orm_user.rol_usuario = usuario.rol_usuario
            orm_user.reliability_score = usuario.reliability_score
            self.db.commit()
            self.db.refresh(orm_user)
            return self._to_entity(orm_user)
        raise ValueError("Usuario no encontrado para actualizar")
