from __future__ import annotations
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

    @staticmethod
    def get_all() -> list[Department]:
        """
        Obtiene todos los departamentos ordenados por nombre.

        Returns:
            list[Department]: Lista de departamentos
        """
        return db.session.query(Department).order_by(Department.display_name).all()

    @staticmethod
    def get_by_id(department_id: int) -> Department | None:
        """
        Obtiene un departamento por su ID.

        Args:
            department_id: ID del departamento

        Returns:
            Department | None: El departamento o None si no existe
        """
        return db.session.get(Department, department_id)

    @staticmethod
    def get_technical_secretariat() -> Department | None:
        """
        Obtiene el departamento de Secretaría Técnica.

        Returns:
            Department | None: La Secretaría Técnica o None si no existe
        """
        return (
            db.session.query(Department)
            .filter_by(is_technical_secretariat=True)
            .first()
        )

    @staticmethod
    def get_by_name(name: str) -> Department | None:
        """
        Obtiene un departamento por su nombre interno.

        Args:
            name: Nombre interno del departamento (ej: 'mantenimiento')

        Returns:
            Department | None: El departamento o None si no existe
        """
        return db.session.query(Department).filter_by(name=name).first()

    @staticmethod
    def get_for_admin(admin_user: "AdminUser") -> list[Department]:
        """Devuelve los departamentos visibles para un AdminUser.

        - Secretaría técnica: todos los departamentos
        - Otros roles: solo su departamento (si está asignado)
        """
        if admin_user.is_technical_secretary:
            return Department.get_all()

        if admin_user.department_id is None:
            return []

        department = Department.get_by_id(admin_user.department_id)
        return [department] if department else []

    @staticmethod
    def get_by_ids(department_ids: list[int]) -> list[Department]:
        """
        Obtiene departamentos por lista de IDs.

        Args:
            department_ids: Lista de IDs de departamentos

        Returns:
            Lista de departamentos ordenados por nombre
        """
        if not department_ids:
            return []
        return (
            db.session.query(Department)
            .filter(Department.id.in_(department_ids))
            .order_by(Department.display_name)
            .all()
        )
