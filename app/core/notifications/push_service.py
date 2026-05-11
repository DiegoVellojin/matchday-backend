from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.modules.users.infrastructure.repositories_impl import FCMRepositoryImpl

class PushNotificationService:
    """
    Servicio centralizado para enviar notificaciones Push mediante FCM
    y registrar la notificación en la base de datos para el historial del usuario.
    """
    def __init__(self, db: Session):
        self.db = db
        self.fcm_repo = FCMRepositoryImpl(db)

    def send_notification(self, fk_id_usuario: int, mensaje: str, tipo: str = "General", referencia_id: Optional[int] = None) -> bool:
        """
        Guarda la notificación en BD y simula el envío a FCM.
        """
        # 1. Guardar en Base de Datos
        query = """
        INSERT INTO bd_matchday."Notificacion" (fk_id_usuario, mensaje, tipo, referencia_id)
        VALUES (:fk_id_usuario, :mensaje, :tipo, :referencia_id)
        RETURNING id_notificacion;
        """
        result = self.db.execute(text(query), {
            "fk_id_usuario": fk_id_usuario,
            "mensaje": mensaje,
            "tipo": tipo,
            "referencia_id": referencia_id
        }).fetchone()
        
        self.db.commit()
        
        # 2. Obtener tokens FCM del usuario
        tokens = self.fcm_repo.get_tokens_by_user(fk_id_usuario)
        
        # 3. Simular envío FCM
        # En producción usaríamos: firebase_admin.messaging.send_multicast(...)
        if tokens:
            print(f"[FCM SIMULATOR] Enviando '{mensaje}' a tokens: {tokens}")
            return True
        else:
            print(f"[FCM SIMULATOR] Usuario {fk_id_usuario} no tiene tokens registrados.")
            return False
