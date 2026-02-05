from datetime import datetime as Datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.config import db

if TYPE_CHECKING:
    from modules.models.claim_status_history import ClaimStatusHistory
    from modules.models.user.base import User


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
