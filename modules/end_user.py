from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from modules.user import User
from modules.config import db

if TYPE_CHECKING:
    from modules.claim import Claim
    from modules.claim_supporter import ClaimSupporter


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

    @staticmethod
    def register(
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        cloister: Cloister,
        password: str,
    ) -> tuple["EndUser | None", str | None]:
        """
        Registra un nuevo usuario final.
        Retorna (user, None) si exitoso, (None, error_message) si falla.
        """
        if User.email_exists(email):
            return None, "El email ya está registrado"

        if User.username_exists(username):
            return None, "El nombre de usuario ya está en uso"

        user = EndUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            cloister=cloister,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user, None

    @staticmethod
    def authenticate(username: str, password: str) -> "EndUser | None":
        """Autentica un usuario final por username y password"""
        user = EndUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None
