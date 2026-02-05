from __future__ import annotations

from sqlalchemy.orm import joinedload, selectinload

from modules.config import db
from modules.models.claim import Claim, ClaimStatus
from modules.models.claim_supporter import ClaimSupporter
from modules.models.user.admin_user import AdminUser
from modules.services.claim_service import ClaimService
from modules.services.department_service import DepartmentService


class AdminClaimService:
    """Servicio para gestión de reclamos desde el panel de administración."""

    @staticmethod
    def get_claim_supporters_ids(claim_id: int) -> list[int]:
        rows = (
            db.session.query(ClaimSupporter.user_id)
            .filter_by(claim_id=claim_id)
            .order_by(ClaimSupporter.created_at.asc())
            .all()
        )
        return [int(user_id) for (user_id,) in rows]

    @staticmethod
    def get_claims_for_admin(
        admin_user: AdminUser, department_id: int | None = None
    ) -> list[Claim]:
        """Lista reclamos visibles para un admin.

        - Secretaría técnica: todos los departamentos (con filtro opcional department_id)
        - Jefe de departamento: solo su departamento
        """
        visible_departments = DepartmentService.get_departments_for_admin(admin_user)
        visible_department_ids = [d.id for d in visible_departments]

        if not visible_department_ids:
            return []

        if department_id is not None:
            if department_id not in visible_department_ids:
                return []
            department_ids = [department_id]
        else:
            department_ids = visible_department_ids

        return (
            db.session.query(Claim)
            .filter(Claim.department_id.in_(department_ids))
            .order_by(Claim.created_at.desc())
            .all()
        )

    @staticmethod
    def get_claim_for_admin(admin_user: AdminUser, claim_id: int) -> Claim | None:
        claim = db.session.query(Claim).filter_by(id=claim_id).first()
        if not claim:
            return None

        if admin_user.is_technical_secretary:
            return claim

        if (
            admin_user.is_department_head
            and admin_user.department_id == claim.department_id
        ):
            return claim

        return None

    @staticmethod
    def update_claim_status_for_admin(
        admin_user: AdminUser, claim_id: int, new_status: ClaimStatus
    ) -> tuple[bool, str | None]:
        claim = db.session.get(Claim, claim_id)
        if not claim:
            return False, "Reclamo no encontrado"

        if not admin_user.is_technical_secretary and not (
            admin_user.is_department_head
            and admin_user.department_id == claim.department_id
        ):
            return False, "No tienes permiso para gestionar este reclamo"

        return ClaimService.update_claim_status(claim_id, new_status, admin_user.id)
