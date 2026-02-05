"""Servicio para gestionar derivaciones (transferencias) de reclamos entre departamentos."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modules.config import db
from modules.models.claim import Claim
from modules.models.claim_transfer import ClaimTransfer
from modules.services.department_service import DepartmentService

if TYPE_CHECKING:
    from modules.models.department import Department


class TransferService:
    """Servicio para derivar reclamos entre departamentos."""

    @staticmethod
    def transfer_claim(
        claim_id: int,
        to_department_id: int,
        transferred_by_id: int,
        reason: str | None = None,
    ) -> tuple[ClaimTransfer | None, str | None]:
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
        # Obtener el reclamo
        claim = db.session.get(Claim, claim_id)
        if not claim:
            return None, "Reclamo no encontrado"

        # Validar que el departamento destino existe
        to_department = DepartmentService.get_department_by_id(to_department_id)
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
    def get_transfer_history(claim_id: int) -> list[ClaimTransfer]:
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
    def get_available_departments_for_transfer(
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
        all_departments = DepartmentService.get_all_departments()
        return [d for d in all_departments if d.id != current_department_id]

    @staticmethod
    def can_transfer(admin_user) -> bool:
        """
        Verifica si un admin puede derivar un reclamo específico.
        Solo el secretario técnico puede derivar reclamos.

        Args:
            claim: El reclamo a verificar
            admin_user: El usuario admin

        Returns:
            True si puede derivar, False en caso contrario
        """
        return admin_user.is_technical_secretary
