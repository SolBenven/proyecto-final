from __future__ import annotations

from typing import TYPE_CHECKING

from modules.config import db
from modules.models.department import Department

if TYPE_CHECKING:
    from modules.models.user.admin_user import AdminUser


class DepartmentService:
    """Servicio para gestionar departamentos"""

    @staticmethod
    def get_all_departments() -> list[Department]:
        """
        Obtiene todos los departamentos ordenados por nombre.

        Returns:
            list[Department]: Lista de departamentos
        """
        return db.session.query(Department).order_by(Department.display_name).all()

    @staticmethod
    def get_department_by_id(department_id: int) -> Department | None:
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
    def get_department_by_name(name: str) -> Department | None:
        """
        Obtiene un departamento por su nombre interno.

        Args:
            name: Nombre interno del departamento (ej: 'mantenimiento')

        Returns:
            Department | None: El departamento o None si no existe
        """
        return db.session.query(Department).filter_by(name=name).first()

    @staticmethod
    def get_departments_for_admin(admin_user: "AdminUser") -> list[Department]:
        """Devuelve los departamentos visibles para un AdminUser.

        - Secretaría técnica: todos los departamentos
        - Otros roles: solo su departamento (si está asignado)
        """
        if admin_user.is_technical_secretary:
            return DepartmentService.get_all_departments()

        if admin_user.department_id is None:
            return []

        department = DepartmentService.get_department_by_id(admin_user.department_id)
        return [department] if department else []

    @staticmethod
    def get_departments_by_ids(department_ids: list[int]) -> list[Department]:
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
