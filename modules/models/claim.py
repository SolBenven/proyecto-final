from datetime import datetime as Datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.config import db

if TYPE_CHECKING:
    from modules.models.claim_status_history import ClaimStatusHistory
    from modules.models.claim_supporter import ClaimSupporter
    from modules.models.claim_transfer import ClaimTransfer
    from modules.models.department import Department
    from modules.models.user.end_user import EndUser


class ClaimStatus(Enum):
    """Estado de un reclamo"""

    INVALID = "Inválido"
    PENDING = "Pendiente"
    IN_PROGRESS = "En proceso"
    RESOLVED = "Resuelto"


class Claim(db.Model):
    """Reclamo creado por un usuario final"""

    __tablename__ = "claim"

    id: Mapped[int] = mapped_column(primary_key=True)
    detail: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[ClaimStatus] = mapped_column(default=ClaimStatus.PENDING)
    image_path: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[Datetime] = mapped_column(default=Datetime.now)
    updated_at: Mapped[Datetime] = mapped_column(
        default=Datetime.now, onupdate=Datetime.now
    )

    # Foreign Keys
    department_id: Mapped[int] = mapped_column(
        ForeignKey("department.id"), nullable=False
    )
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Relaciones
    department: Mapped["Department"] = relationship(  # noqa: F821
        "Department", back_populates="claims"
    )
    creator: Mapped["EndUser"] = relationship(  # noqa: F821
        "EndUser", back_populates="created_claims"
    )
    supporters: Mapped[list["ClaimSupporter"]] = relationship(  # noqa: F821
        "ClaimSupporter", back_populates="claim", cascade="all, delete-orphan"
    )
    status_history: Mapped[list["ClaimStatusHistory"]] = relationship(  # noqa: F821
        "ClaimStatusHistory", back_populates="claim", cascade="all, delete-orphan"
    )
    transfers: Mapped[list["ClaimTransfer"]] = relationship(  # noqa: F821
        "ClaimTransfer", back_populates="claim", cascade="all, delete-orphan"
    )

    def __init__(
        self,
        detail: str,
        department_id: int,
        creator_id: int,
        image_path: str | None = None,
    ):
        self.detail = detail
        self.department_id = department_id
        self.creator_id = creator_id
        self.image_path = image_path

    @property
    def supporters_count(self) -> int:
        """Retorna el número de adherentes"""
        return len(self.supporters)

    def __repr__(self):
        return f"<Claim {self.id} - {self.status.value}>"
