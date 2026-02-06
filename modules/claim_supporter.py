from datetime import datetime as Datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.config import db

if TYPE_CHECKING:
    from modules.claim import Claim
    from modules.end_user import EndUser


class ClaimSupporter(db.Model):
    """Adherente a un reclamo"""

    __tablename__ = "claim_supporter"
    __table_args__ = (
        UniqueConstraint("claim_id", "user_id", name="uq_claim_supporter"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[Datetime] = mapped_column(default=Datetime.now)

    # Foreign Keys
    claim_id: Mapped[int] = mapped_column(ForeignKey("claim.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Relaciones
    claim: Mapped["Claim"] = relationship(
        "Claim", back_populates="supporters"
    )  # noqa: F821
    user: Mapped["EndUser"] = relationship(  # noqa: F821
        "EndUser", back_populates="supported_claims"
    )

    def __init__(self, claim_id: int, user_id: int):
        self.claim_id = claim_id
        self.user_id = user_id

    def __repr__(self):
        return f"<ClaimSupporter claim={self.claim_id} user={self.user_id}>"
