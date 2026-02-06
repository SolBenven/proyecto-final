from datetime import datetime as Datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.config import db
from modules.claim import ClaimStatus

if TYPE_CHECKING:
    from modules.claim import Claim
    from modules.admin_user import AdminUser
    from modules.user_notification import UserNotification


class ClaimStatusHistory(db.Model):
    """Historial de cambios de estado de un reclamo"""

    __tablename__ = "claim_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    old_status: Mapped[ClaimStatus] = mapped_column(nullable=False)
    new_status: Mapped[ClaimStatus] = mapped_column(nullable=False)
    changed_at: Mapped[Datetime] = mapped_column(default=Datetime.now)

    # Foreign Keys
    claim_id: Mapped[int] = mapped_column(ForeignKey("claim.id"), nullable=False)
    changed_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Relaciones
    claim: Mapped["Claim"] = relationship(  # noqa: F821
        "Claim", back_populates="status_history"
    )
    changed_by: Mapped["AdminUser"] = relationship("AdminUser")  # noqa: F821
    user_notifications: Mapped[list["UserNotification"]] = relationship(
        "UserNotification", back_populates="claim_status_history"
    )

    def __init__(
        self,
        claim_id: int,
        old_status: ClaimStatus,
        new_status: ClaimStatus,
        changed_by_id: int,
    ):
        self.claim_id = claim_id
        self.old_status = old_status
        self.new_status = new_status
        self.changed_by_id = changed_by_id

    def __repr__(self):
        return (
            f"<ClaimStatusHistory {self.old_status.value} -> {self.new_status.value}>"
        )
