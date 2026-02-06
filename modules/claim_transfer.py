from __future__ import annotations

from datetime import datetime as Datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.config import db

if TYPE_CHECKING:
    from modules.claim import Claim
    from modules.department import Department
    from modules.admin_user import AdminUser


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

    @staticmethod
    def transfer(
        claim_id: int,
        to_department_id: int,
        transferred_by_id: int,
        reason: str | None = None,
    ) -> tuple["ClaimTransfer | None", str | None]:
        """
        Deriva un reclamo a otro departamento.

        Args:
            claim_id: ID del reclamo a derivar
            to_department_id: ID del departamento destino
            transferred_by_id: ID del admin que realiza la derivación
            reason: Motivo de la derivación (opcional)

        Returns:
            tuple[ClaimTransfer | None, str | None]: (transfer, None) si exitoso,
                (None, error_message) si falla
        """
        from modules.claim import Claim
        from modules.department import Department

        # Obtener el reclamo
        claim = db.session.get(Claim, claim_id)
        if not claim:
            return None, "Reclamo no encontrado"

        # Validar que el departamento destino existe
        to_department = Department.get_by_id(to_department_id)
        if not to_department:
            return None, "Departamento destino no válido"

        # Validar que no se derive al mismo departamento
        if claim.department_id == to_department_id:
            return None, "El reclamo ya pertenece a ese departamento"

        # Guardar el departamento origen
        from_department_id = claim.department_id

        # Crear registro de transferencia
        transfer = ClaimTransfer(
            claim_id=claim_id,
            from_department_id=from_department_id,
            to_department_id=to_department_id,
            transferred_by_id=transferred_by_id,
            reason=reason.strip() if reason else None,
        )

        # Actualizar el departamento del reclamo
        claim.department_id = to_department_id

        db.session.add(transfer)
        db.session.commit()

        return transfer, None

    @staticmethod
    def get_history_for_claim(claim_id: int) -> list["ClaimTransfer"]:
        """
        Obtiene el historial de derivaciones de un reclamo.

        Args:
            claim_id: ID del reclamo

        Returns:
            Lista de transferencias ordenadas por fecha descendente
        """
        return (
            db.session.query(ClaimTransfer)
            .filter(ClaimTransfer.claim_id == claim_id)
            .order_by(ClaimTransfer.transferred_at.desc())
            .all()
        )

    @staticmethod
    def get_available_departments(
        current_department_id: int,
    ) -> list["Department"]:
        """
        Obtiene los departamentos disponibles para derivar un reclamo.
        Excluye el departamento actual.

        Args:
            current_department_id: ID del departamento actual del reclamo

        Returns:
            Lista de departamentos (excluyendo el actual)
        """
        from modules.department import Department

        all_departments = Department.get_all()
        return [d for d in all_departments if d.id != current_department_id]

    @staticmethod
    def can_transfer(admin_user) -> bool:
        """
        Verifica si un admin puede derivar un reclamo específico.
        Solo el secretario técnico puede derivar reclamos.

        Args:
            admin_user: El usuario admin

        Returns:
            True si puede derivar, False en caso contrario
        """
        return admin_user.is_technical_secretary
