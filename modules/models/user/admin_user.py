from enum import Enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from modules.models.user.base import User
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.models.department import Department


class AdminRole(Enum):
    """Rol de un usuario administrativo"""

    DEPARTMENT_HEAD = "jefe_departamento"  # Jefe de un departamento específico
    TECHNICAL_SECRETARY = "secretario_tecnico"  # Acceso a secretaría técnica


class AdminUser(User):
    """Usuario administrativo que gestiona reclamos"""

    # Campos específicos de AdminUser
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("department.id"), nullable=True
    )
    admin_role: Mapped[AdminRole | None] = mapped_column(nullable=True)

    # Relaciones
    department: Mapped["Department"] = relationship(  # noqa: F821
        "Department", back_populates="admin_users"
    )

    __mapper_args__ = {"polymorphic_identity": "admin_user"}

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        admin_role: AdminRole,
        department_id: int | None = None,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.admin_role = admin_role
        self.department_id = department_id

    @property
    def is_department_head(self) -> bool:
        return self.admin_role == AdminRole.DEPARTMENT_HEAD

    @property
    def is_technical_secretary(self) -> bool:
        return self.admin_role == AdminRole.TECHNICAL_SECRETARY

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name} - {self.admin_role.value if self.admin_role else 'sin rol'}"
