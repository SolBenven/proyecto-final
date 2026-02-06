from datetime import datetime as Datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload

from modules.config import db

if TYPE_CHECKING:
    from modules.claim_status_history import ClaimStatusHistory
    from modules.user import User


class UserNotification(db.Model):
    """
    Notificación individual por usuario.
    Cada cambio de estado de un reclamo genera una entrada por cada usuario afectado.
    """

    __tablename__ = "user_notification"

    id: Mapped[int] = mapped_column(primary_key=True)
    read_at: Mapped[Datetime | None] = mapped_column(nullable=True, default=None)
    created_at: Mapped[Datetime] = mapped_column(default=Datetime.now)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    claim_status_history_id: Mapped[int] = mapped_column(
        ForeignKey("claim_status_history.id"), nullable=False
    )

    # Relaciones
    user: Mapped["User"] = relationship("User")
    claim_status_history: Mapped["ClaimStatusHistory"] = relationship(
        "ClaimStatusHistory", back_populates="user_notifications"
    )

    def __init__(self, user_id: int, claim_status_history_id: int):
        self.user_id = user_id
        self.claim_status_history_id = claim_status_history_id

    @property
    def is_read(self) -> bool:
        """Indica si la notificación fue leída"""
        return self.read_at is not None

    def mark_as_read(self) -> None:
        """Marca la notificación como leída"""
        if self.read_at is None:
            self.read_at = Datetime.now()

    def __repr__(self):
        status = "leída" if self.is_read else "Pendiente"
        return f"<UserNotification user_id={self.user_id} {status}>"

    @staticmethod
    def get_pending_for_user(user_id: int) -> list["UserNotification"]:
        """
        Obtiene notificaciones pendientes (no leídas) para un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de UserNotification no leídas, ordenadas por más recientes
        """
        from modules.claim_status_history import ClaimStatusHistory

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
    def mark_all_as_read_for_user(user_id: int) -> int:
        """
        Marca todas las notificaciones de un usuario como leídas.

        Args:
            user_id: ID del usuario

        Returns:
            Cantidad de notificaciones marcadas
        """
        # Obtener las notificaciones pendientes
        notifications = UserNotification.get_pending_for_user(user_id)

        # Marcar cada una como leída
        count = 0
        for notification in notifications:
            notification.mark_as_read()
            count += 1

        db.session.commit()
        return count
