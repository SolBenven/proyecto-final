from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from modules.models.user.base import User

if TYPE_CHECKING:
    from modules.models.claim import Claim
    from modules.models.claim_supporter import ClaimSupporter


class Cloister(Enum):
    """Claustro al que pertenece un usuario final"""

    STUDENT = "estudiante"
    TEACHER = "docente"
    PAYS = "PAyS"  # Personal de Apoyo y Servicios


class EndUser(User):
    """Usuario final que crea y adhiere a reclamos"""

    # Campos específicos de EndUser
    cloister: Mapped[Cloister | None] = mapped_column(nullable=True)

    # Relaciones
    created_claims: Mapped[list["Claim"]] = relationship(  # noqa: F821
        "Claim", back_populates="creator"
    )
    supported_claims: Mapped[list["ClaimSupporter"]] = relationship(  # noqa: F821
        "ClaimSupporter", back_populates="user"
    )

    __mapper_args__ = {"polymorphic_identity": "end_user"}

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        cloister: Cloister,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.cloister = cloister

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name} - {self.cloister.value if self.cloister else 'sin claustro'}"
