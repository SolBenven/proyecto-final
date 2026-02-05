from datetime import datetime as Datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.config import db

if TYPE_CHECKING:
    from modules.models.claim import Claim
    from modules.models.user.admin_user import AdminUser


class Department(db.Model):
    """Departamento que gestiona reclamos"""

    __tablename__ = "department"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)  # Nombre interno
    display_name: Mapped[str] = mapped_column(nullable=False)  # Nombre para mostrar
    is_technical_secretariat: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[Datetime] = mapped_column(default=Datetime.now)

    # Relaciones
    claims: Mapped[list["Claim"]] = relationship(  # noqa: F821
        "Claim", back_populates="department"
    )
    admin_users: Mapped[list["AdminUser"]] = relationship(  # noqa: F821
        "AdminUser", back_populates="department"
    )

    def __init__(
        self,
        name: str,
        display_name: str,
        is_technical_secretariat: bool = False,
    ):
        self.name = name
        self.display_name = display_name
        self.is_technical_secretariat = is_technical_secretariat

    def __repr__(self):
        return f"<Department {self.name}>"
