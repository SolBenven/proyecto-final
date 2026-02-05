"""Servicio para gestionar notificaciones de cambios de estado en reclamos"""

from sqlalchemy.orm import joinedload

from modules.config import db
from modules.models.claim_status_history import ClaimStatusHistory
from modules.models.user_notification import UserNotification


class NotificationService:
    """Gestión de notificaciones basadas en cambios de estado"""

    @staticmethod
    def get_pending_notifications(user_id: int) -> list[UserNotification]:
        """
        Obtiene notificaciones pendientes (no leídas) para un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de UserNotification no leídas, ordenadas por más recientes
        """
        notifications = (
            db.session.query(UserNotification)
            .filter_by(user_id=user_id, read_at=None)
            .options(
                joinedload(UserNotification.claim_status_history).joinedload(
                    ClaimStatusHistory.claim
                ),
                joinedload(UserNotification.claim_status_history).joinedload(
                    ClaimStatusHistory.changed_by
                ),
            )
            .order_by(UserNotification.created_at.desc())
            .all()
        )

        return notifications

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Obtiene el número de notificaciones no leídas para un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Cantidad de notificaciones pendientes
        """
        count = (
            db.session.query(UserNotification)
            .filter_by(user_id=user_id, read_at=None)
            .count()
        )

        return count

    @staticmethod
    def mark_notification_as_read(
        notification_id: int, user_id: int
    ) -> tuple[bool, str | None]:
        """
        Marca una notificación como leída.
        Verifica que el usuario sea el propietario de la notificación.

        Args:
            notification_id: ID de UserNotification
            user_id: ID del usuario que marca como leída

        Returns:
            Tuple (success, error_message)
        """
        notification = db.session.get(UserNotification, notification_id)

        if not notification:
            return False, "Notificación no encontrada"

        # Verificar que el usuario sea el propietario
        if notification.user_id != user_id:
            return False, "No tienes permiso para marcar esta notificación"

        # Marcar como leída
        notification.mark_as_read()
        db.session.commit()

        return True, None

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        """
        Marca todas las notificaciones de un usuario como leídas.

        Args:
            user_id: ID del usuario

        Returns:
            Cantidad de notificaciones marcadas
        """
        # Obtener las notificaciones pendientes
        notifications = NotificationService.get_pending_notifications(user_id)

        # Marcar cada una como leída
        count = 0
        for notification in notifications:
            notification.mark_as_read()
            count += 1

        db.session.commit()
        return count
