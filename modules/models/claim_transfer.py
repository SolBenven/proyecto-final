from datetime import datetime as Datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.config import db

if TYPE_CHECKING:
    from modules.models.claim import Claim
    from modules.models.department import Department
    from modules.models.user.admin_user import AdminUser


class ClaimTransfer(db.Model):
    """Derivación de un reclamo entre departamentos"""

    __tablename__ = "claim_transfer"

    id: Mapped[int] = mapped_column(primary_key=True)
    reason: Mapped[str | None] = mapped_column(nullable=True)
    transferred_at: Mapped[Datetime] = mapped_column(default=Datetime.now)

    # Foreign Keys
    claim_id: Mapped[int] = mapped_column(ForeignKey("claim.id"), nullable=False)
    from_department_id: Mapped[int] = mapped_column(
        ForeignKey("department.id"), nullable=False
    )
    to_department_id: Mapped[int] = mapped_column(
        ForeignKey("department.id"), nullable=False
    )
    transferred_by_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False
    )

    # Relaciones
    claim: Mapped["Claim"] = relationship(
        "Claim", back_populates="transfers"
    )  # noqa: F821
    from_department: Mapped["Department"] = relationship(  # noqa: F821
        "Department", foreign_keys=[from_department_id]
    )
    to_department: Mapped["Department"] = relationship(  # noqa: F821
        "Department", foreign_keys=[to_department_id]
    )
    transferred_by: Mapped["AdminUser"] = relationship("AdminUser")  # noqa: F821

    def __init__(
        self,
        claim_id: int,
        from_department_id: int,
        to_department_id: int,
        transferred_by_id: int,
        reason: str | None = None,
    ):
        self.claim_id = claim_id
        self.from_department_id = from_department_id
        self.to_department_id = to_department_id
        self.transferred_by_id = transferred_by_id
        self.reason = reason

    def __repr__(self):
        return f"<ClaimTransfer claim={self.claim_id} {self.from_department_id} -> {self.to_department_id}>"
