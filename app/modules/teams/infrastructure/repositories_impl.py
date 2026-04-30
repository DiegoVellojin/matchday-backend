from typing import Optional, List
from sqlalchemy.orm import Session
from app.modules.teams.domain.entities import Equipo, EquipoUsuario
from app.modules.teams.domain.interfaces import IEquipoRepository
from app.modules.teams.infrastructure.orm_models import EquipoORM, EquipoUsuarioORM
from app.modules.catalogs.domain.entities import Deporte
from app.modules.catalogs.infrastructure.orm_models import DeporteORM

class EquipoRepositoryImpl(IEquipoRepository):
    """
    Implementación del repositorio de equipos utilizando SQLAlchemy para la persistencia.
    
    Se encarga de traducir entre las entidades de dominio y los modelos ORM, 
    gestionando las transacciones con la base de datos.
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión activa de base de datos.
        
        :param db: Sesión de SQLAlchemy.
        """
        self.db = db

    def _to_entity(self, orm: EquipoORM, deporte: Optional[Deporte] = None) -> Equipo:
        """
        Convierte un objeto ORM de Equipo a su entidad de dominio correspondiente.
        """
        return Equipo(
            id_equipo=orm.id_equipo,
            nombre_equipo=orm.nombre_equipo,
            fk_id_deporte=orm.fk_id_deporte,
            fk_id_usuario_capitan=orm.fk_id_usuario_capitan,
            deporte=deporte,
            url_logo_equipo=orm.url_logo_equipo,
            puntos_acumulados=orm.puntos_acumulados,
            descripcion_equipo=orm.descripcion_equipo,
            esta_reclutando=orm.esta_reclutando,
            max_miembros=orm.max_miembros,
            fecha_creacion_equipo=orm.fecha_creacion_equipo,
            url_chat_equipo=orm.url_chat_equipo
        )

    def _to_membership_entity(self, orm: EquipoUsuarioORM) -> EquipoUsuario:
        """
        Convierte un objeto ORM de membresía a su entidad de dominio.
        """
        return EquipoUsuario(
            fk_id_equipo=orm.fk_id_equipo,
            fk_id_usuario=orm.fk_id_usuario,
            estatus_miembro=orm.estatus_miembro,
            rol_equipo=orm.rol_equipo
        )

    def create(self, equipo: Equipo) -> Equipo:
        """
        Persiste un nuevo equipo en la base de datos.
        
        :param equipo: Entidad de dominio con los datos del nuevo equipo.
        :return: Entidad de dominio persistida (incluyendo ID generado).
        """
        orm_equipo = EquipoORM(
            nombre_equipo=equipo.nombre_equipo,
            fk_id_deporte=equipo.fk_id_deporte,
            fk_id_usuario_capitan=equipo.fk_id_usuario_capitan,
            url_logo_equipo=equipo.url_logo_equipo,
            descripcion_equipo=equipo.descripcion_equipo,
            esta_reclutando=equipo.esta_reclutando,
            max_miembros=equipo.max_miembros,
            url_chat_equipo=equipo.url_chat_equipo
        )
        self.db.add(orm_equipo)
        self.db.commit()
        self.db.refresh(orm_equipo)
        
        # Recuperar información del deporte para la respuesta completa
        deporte_orm = self.db.query(DeporteORM).filter(DeporteORM.id_deporte == equipo.fk_id_deporte).first()
        deporte = Deporte(deporte_orm.id_deporte, deporte_orm.nombre_deporte) if deporte_orm else None
        
        return self._to_entity(orm_equipo, deporte)

    def get_by_id(self, id_equipo: int) -> Optional[Equipo]:
        """
        Busca un equipo por su identificador primario.
        
        Realiza un JOIN con la tabla de deportes para cargar la información relacionada.
        
        :param id_equipo: ID del equipo.
        :return: Entidad Equipo o None si no existe.
        """
        result = self.db.query(EquipoORM, DeporteORM).join(
            DeporteORM, EquipoORM.fk_id_deporte == DeporteORM.id_deporte
        ).filter(EquipoORM.id_equipo == id_equipo).first()
        
        if result:
            equipo_orm, deporte_orm = result
            deporte = Deporte(deporte_orm.id_deporte, deporte_orm.nombre_deporte)
            return self._to_entity(equipo_orm, deporte)
        return None

    def add_member(self, membership: EquipoUsuario) -> EquipoUsuario:
        """
        Registra una nueva relación entre un usuario y un equipo.
        
        :param membership: Entidad de dominio con los datos de membresía.
        :return: Membresía persistida.
        """
        orm = EquipoUsuarioORM(
            fk_id_equipo=membership.fk_id_equipo,
            fk_id_usuario=membership.fk_id_usuario,
            estatus_miembro=membership.estatus_miembro,
            rol_equipo=membership.rol_equipo
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_membership_entity(orm)

    def update_member_status(self, id_equipo: int, id_usuario: int, status: str, role: str) -> bool:
        """
        Actualiza el estatus o rol de un miembro específico.
        
        :param id_equipo: ID del equipo.
        :param id_usuario: ID del usuario.
        :param status: Nuevo estado (p.ej. 'aceptado').
        :param role: Nuevo rol (p.ej. 'Capitán').
        :return: True si se encontró y actualizó el registro.
        """
        orm = self.db.query(EquipoUsuarioORM).filter(
            EquipoUsuarioORM.fk_id_equipo == id_equipo,
            EquipoUsuarioORM.fk_id_usuario == id_usuario
        ).first()
        if orm:
            orm.estatus_miembro = status
            orm.rol_equipo = role
            self.db.commit()
            return True
        return False

    def get_members(self, id_equipo: int) -> List[EquipoUsuario]:
        """
        Obtiene el listado completo de miembros vinculados a un equipo.
        """
        orms = self.db.query(EquipoUsuarioORM).filter(EquipoUsuarioORM.fk_id_equipo == id_equipo).all()
        return [self._to_membership_entity(orm) for orm in orms]

    def get_teams_by_user(self, id_usuario: int) -> List[Equipo]:
        """
        Obtiene los equipos donde el usuario tiene una membresía aceptada.
        """
        results = self.db.query(EquipoORM, DeporteORM).join(
            DeporteORM, EquipoORM.fk_id_deporte == DeporteORM.id_deporte
        ).join(
            EquipoUsuarioORM, EquipoORM.id_equipo == EquipoUsuarioORM.fk_id_equipo
        ).filter(
            EquipoUsuarioORM.fk_id_usuario == id_usuario,
            EquipoUsuarioORM.estatus_miembro == 'aceptado'
        ).all()
        
        return [self._to_entity(orm, Deporte(d.id_deporte, d.nombre_deporte)) for orm, d in results]

    def delete_member(self, id_equipo: int, id_usuario: int) -> bool:
        """
        Elimina el registro de membresía de un usuario en un equipo.
        """
        orm = self.db.query(EquipoUsuarioORM).filter(
            EquipoUsuarioORM.fk_id_equipo == id_equipo,
            EquipoUsuarioORM.fk_id_usuario == id_usuario
        ).first()
        if orm:
            self.db.delete(orm)
            self.db.commit()
            return True
        return False

    def update(self, id_equipo: int, data: dict) -> Optional[Equipo]:
        """
        Actualiza campos específicos de la tabla de equipos.
        """
        orm = self.db.query(EquipoORM).filter(EquipoORM.id_equipo == id_equipo).first()
        if not orm:
            return None
        
        for key, value in data.items():
            if hasattr(orm, key) and value is not None:
                setattr(orm, key, value)
        
        self.db.commit()
        self.db.refresh(orm)
        return self.get_by_id(id_equipo)

    def delete(self, id_equipo: int) -> bool:
        """
        Elimina el equipo y sus dependencias directas (miembros).
        """
        # Limpieza manual de miembros para asegurar integridad
        self.db.query(EquipoUsuarioORM).filter(EquipoUsuarioORM.fk_id_equipo == id_equipo).delete()
        
        orm = self.db.query(EquipoORM).filter(EquipoORM.id_equipo == id_equipo).first()
        if orm:
            self.db.delete(orm)
            self.db.commit()
            return True
        return False

    def transfer_captain(self, id_equipo: int, id_nuevo_capitan: int) -> bool:
        """
        Ejecuta la transferencia de capitanía actualizando la tabla Equipo y roles de membresía.
        """
        equipo_orm = self.db.query(EquipoORM).filter(EquipoORM.id_equipo == id_equipo).first()
        if not equipo_orm:
            return False
        
        viejo_capitan_id = equipo_orm.fk_id_usuario_capitan
        equipo_orm.fk_id_usuario_capitan = id_nuevo_capitan
        
        # Degradar antiguo capitán
        if viejo_capitan_id:
            viejo_miembro = self.db.query(EquipoUsuarioORM).filter(
                EquipoUsuarioORM.fk_id_equipo == id_equipo,
                EquipoUsuarioORM.fk_id_usuario == viejo_capitan_id
            ).first()
            if viejo_miembro:
                viejo_miembro.rol_equipo = "Jugador"
        
        # Ascender nuevo capitán
        nuevo_miembro = self.db.query(EquipoUsuarioORM).filter(
            EquipoUsuarioORM.fk_id_equipo == id_equipo,
            EquipoUsuarioORM.fk_id_usuario == id_nuevo_capitan
        ).first()
        if nuevo_miembro:
            nuevo_miembro.rol_equipo = "Capitán"
            nuevo_miembro.estatus_miembro = "aceptado"
        
        self.db.commit()
        return True

    def get_discoverable_teams(self) -> List[Equipo]:
        """
        Lista todos los equipos que tienen activado el reclutamiento de miembros.
        """
        results = self.db.query(EquipoORM, DeporteORM).join(
            DeporteORM, EquipoORM.fk_id_deporte == DeporteORM.id_deporte
        ).filter(
            EquipoORM.esta_reclutando == True
        ).all()
        
        return [self._to_entity(orm, Deporte(d.id_deporte, d.nombre_deporte)) for orm, d in results]
