from __future__ import annotations

from datetime import datetime as Datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.config import db

if TYPE_CHECKING:
    from modules.claim_status_history import ClaimStatusHistory
    from modules.claim_supporter import ClaimSupporter
    from modules.claim_transfer import ClaimTransfer
    from modules.department import Department
    from modules.end_user import EndUser


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

    # ── Helpers privados ─────────────────────────────────────────────

    @staticmethod
    def _get_technical_secretariat_id() -> int | None:
        """
        Obtiene el ID de la Secretaría Técnica.

        Returns:
            ID de la Secretaría Técnica o None si no existe
        """
        from modules.department import Department

        technical_secretariat = Department.get_technical_secretariat()
        return technical_secretariat.id if technical_secretariat else None

    @staticmethod
    def _classify_department(detail: str) -> int | None:
        """
        Clasifica automáticamente un reclamo y retorna el ID del departamento.

        Args:
            detail: Texto del reclamo

        Returns:
            ID del departamento predicho o None si falla la clasificación
        """
        from modules.classifier import classifier
        from modules.department import Department

        if not classifier.is_model_available():
            return None

        try:
            predicted_name = classifier.classify(detail)
            predicted_department = Department.get_by_name(predicted_name)
            return predicted_department.id if predicted_department else None
        except Exception:
            return None

    @staticmethod
    def _resolve_department_id(
        detail: str, department_id: int | None
    ) -> tuple[int | None, str | None]:
        """
        Resuelve el departamento para un reclamo.

        Args:
            detail: Texto del reclamo
            department_id: ID del departamento especificado manualmente (o None)

        Returns:
            tuple[int | None, str | None]: (department_id, error_message)
        """
        from modules.department import Department

        # Si se especificó departamento manualmente, validarlo
        if department_id is not None:
            department = Department.get_by_id(department_id)
            if not department:
                return None, "Departamento no válido"
            return department_id, None

        # Intentar clasificación automática
        classified_id = Claim._classify_department(detail)
        if classified_id is not None:
            return classified_id, None

        # Fallback a Secretaría Técnica
        technical_id = Claim._get_technical_secretariat_id()
        if technical_id is None:
            return None, "No se encontró la Secretaría Técnica"

        return technical_id, None

    # ── Métodos estáticos de creación / actualización ────────────────

    @staticmethod
    def create(
        user_id: int,
        detail: str,
        department_id: int | None = None,
        image_path: str | None = None,
    ) -> tuple["Claim | None", str | None]:
        """
        Crea un nuevo reclamo.

        Args:
            user_id: ID del usuario que crea el reclamo
            detail: Detalle del problema
            department_id: ID del departamento (opcional, se clasifica automáticamente si no se proporciona)
            image_path: Path de la imagen adjunta (opcional)

        Returns:
            tuple[Claim | None, str | None]: (reclamo, None) si exitoso, (None, error_message) si falla
        """
        if not detail or detail.strip() == "":
            return None, "El detalle del reclamo no puede estar vacío"

        # Resolver departamento (manual, clasificado, o fallback)
        resolved_department_id, error = Claim._resolve_department_id(
            detail, department_id
        )
        if error or not resolved_department_id:
            return None, error

        claim = Claim(
            detail=detail.strip(),
            department_id=resolved_department_id,
            creator_id=user_id,
            image_path=image_path,
        )

        db.session.add(claim)
        db.session.commit()

        return claim, None

    @staticmethod
    def update_status(
        claim_id: int, new_status: ClaimStatus, admin_user_id: int
    ) -> tuple[bool, str | None]:
        """
        Actualiza el estado de un reclamo y crea un registro en el historial.
        Esto genera notificaciones individuales para el creador y cada adherente.

        Args:
            claim_id: ID del reclamo
            new_status: Nuevo estado del reclamo
            admin_user_id: ID del usuario administrador que realiza el cambio

        Returns:
            tuple[bool, str | None]: (success, error_message)
        """
        from modules.claim_status_history import ClaimStatusHistory
        from modules.claim_supporter import ClaimSupporter
        from modules.user_notification import UserNotification

        claim = db.session.get(Claim, claim_id)

        if not claim:
            return False, "Reclamo no encontrado"

        old_status = claim.status

        # No crear historial si el estado no cambió
        if old_status == new_status:
            return False, "El estado no ha cambiado"

        # Actualizar el estado del reclamo
        claim.status = new_status

        # Crear entrada en el historial
        history_entry = ClaimStatusHistory(
            claim_id=claim_id,
            old_status=old_status,
            new_status=new_status,
            changed_by_id=admin_user_id,
        )

        db.session.add(history_entry)
        db.session.flush()  # Para obtener el ID de history_entry

        # Crear notificaciones individuales para cada usuario afectado
        # 1. Notificación para el creador del reclamo
        creator_notification = UserNotification(
            user_id=claim.creator_id, claim_status_history_id=history_entry.id
        )
        db.session.add(creator_notification)

        # 2. Notificaciones para cada adherente
        supporters = db.session.query(ClaimSupporter).filter_by(claim_id=claim_id).all()
        for supporter in supporters:
            supporter_notification = UserNotification(
                user_id=supporter.user_id, claim_status_history_id=history_entry.id
            )
            db.session.add(supporter_notification)

        db.session.commit()

        return True, None

    # ── Queries estáticas ────────────────────────────────────────────

    @staticmethod
    def get_by_id(claim_id: int) -> "Claim | None":
        """
        Obtiene un reclamo por su ID.

        Args:
            claim_id: ID del reclamo

        Returns:
            Claim | None: El reclamo o None si no existe
        """
        return db.session.get(Claim, claim_id)

    @staticmethod
    def get_pending(department_id_filter: int | None = None) -> list["Claim"]:
        """
        Obtiene todos los reclamos pendientes.

        Args:
            department_id_filter: ID del departamento para filtrar (opcional)

        Returns:
            list[Claim]: Lista de reclamos pendientes
        """
        query = db.session.query(Claim).filter_by(status=ClaimStatus.PENDING)

        if department_id_filter is not None:
            query = query.filter_by(department_id=department_id_filter)

        return query.order_by(Claim.created_at.desc()).all()

    @staticmethod
    def get_all_with_filters(
        department_filter: int | None = None, status_filter: ClaimStatus | None = None
    ) -> list["Claim"]:
        """
        Obtiene todos los reclamos con filtros opcionales.

        Args:
            department_filter: ID del departamento para filtrar (opcional)
            status_filter: Estado para filtrar (opcional)

        Returns:
            list[Claim]: Lista de reclamos
        """
        query = db.session.query(Claim)

        if department_filter is not None:
            query = query.filter_by(department_id=department_filter)

        if status_filter is not None:
            query = query.filter_by(status=status_filter)

        return query.order_by(Claim.created_at.desc()).all()

    @staticmethod
    def get_status_counts(
        department_ids: list[int] | None = None,
    ) -> dict[ClaimStatus, int]:
        """Obtiene conteos de reclamos por estado.

        Args:
            department_ids: lista de IDs de departamentos a considerar.
                - None: sin filtro (todos los departamentos)
                - []: devuelve 0 para todos los estados

        Returns:
            dict[ClaimStatus, int]: conteos por estado (incluye estados con 0)
        """
        counts: dict[ClaimStatus, int] = {status: 0 for status in ClaimStatus}

        if department_ids is not None and len(department_ids) == 0:
            return counts

        query = db.session.query(Claim.status, func.count(Claim.id))
        if department_ids is not None:
            query = query.filter(Claim.department_id.in_(department_ids))

        for status, count in query.group_by(Claim.status).all():
            counts[status] = int(count)

        return counts

    @staticmethod
    def get_dashboard_counts(
        department_ids: list[int] | None = None,
    ) -> dict[str, int]:
        """Obtiene conteos para el dashboard (total + estados principales).

        Args:
            department_ids: lista de IDs de departamentos a considerar.
                - None: sin filtro (todos los departamentos)
                - []: devuelve 0 en todas las métricas

        Returns:
            dict[str, int]: total_claims, pending_claims, in_progress_claims, resolved_claims
        """
        if department_ids is not None and len(department_ids) == 0:
            return {
                "total_claims": 0,
                "pending_claims": 0,
                "in_progress_claims": 0,
                "resolved_claims": 0,
                "invalid_claims": 0,
            }

        status_counts = Claim.get_status_counts(department_ids=department_ids)

        total_query = db.session.query(Claim)
        if department_ids is not None:
            total_query = total_query.filter(Claim.department_id.in_(department_ids))

        total_claims = int(total_query.count() or 0)

        return {
            "total_claims": total_claims,
            "pending_claims": status_counts[ClaimStatus.PENDING],
            "in_progress_claims": status_counts[ClaimStatus.IN_PROGRESS],
            "resolved_claims": status_counts[ClaimStatus.RESOLVED],
            "invalid_claims": status_counts[ClaimStatus.INVALID],
        }

    @staticmethod
    def get_department_dashboard_counts(
        department_ids: list[int],
    ) -> dict[int, dict[str, int]]:
        """Obtiene conteos por departamento para el dashboard.

        Args:
            department_ids: IDs de departamentos a incluir.

        Returns:
            dict[int, dict[str, int]]: por department_id -> total/pending/in_progress/resolved
        """
        if len(department_ids) == 0:
            return {}

        per_dept: dict[int, dict[str, int]] = {
            dept_id: {
                "total": 0,
                "pending": 0,
                "in_progress": 0,
                "resolved": 0,
                "invalid": 0,
            }
            for dept_id in department_ids
        }

        rows = (
            db.session.query(Claim.department_id, Claim.status, func.count(Claim.id))
            .filter(Claim.department_id.in_(department_ids))
            .group_by(Claim.department_id, Claim.status)
            .all()
        )

        for dept_id, status, count in rows:
            dept_id_int = int(dept_id)
            count_int = int(count)
            per_dept[dept_id_int]["total"] += count_int

            if status == ClaimStatus.PENDING:
                per_dept[dept_id_int]["pending"] = count_int
            elif status == ClaimStatus.IN_PROGRESS:
                per_dept[dept_id_int]["in_progress"] = count_int
            elif status == ClaimStatus.RESOLVED:
                per_dept[dept_id_int]["resolved"] = count_int
            elif status == ClaimStatus.INVALID:
                per_dept[dept_id_int]["invalid"] = count_int

        return per_dept

    # ── Supporters ───────────────────────────────────────────────────

    @staticmethod
    def add_supporter(claim_id: int, user_id: int) -> tuple[bool, str | None]:
        """
        Agrega un adherente a un reclamo.

        Args:
            claim_id: ID del reclamo
            user_id: ID del usuario que se adhiere

        Returns:
            tuple[bool, str | None]: (True, None) si exitoso, (False, error_message) si falla
        """
        from modules.claim_supporter import ClaimSupporter

        # Verificar que el reclamo existe
        claim = Claim.get_by_id(claim_id)
        if not claim:
            return False, "Reclamo no encontrado"

        # Verificar que el usuario no es el creador
        if claim.creator_id == user_id:
            return False, "No puedes adherirte a tu propio reclamo"

        # Verificar si ya está adherido
        if Claim.is_user_supporter(claim_id, user_id):
            return False, "Ya estás adherido a este reclamo"

        # Crear el adherente
        supporter = ClaimSupporter(claim_id=claim_id, user_id=user_id)

        try:
            db.session.add(supporter)
            db.session.commit()
            return True, None
        except IntegrityError:
            db.session.rollback()
            return False, "Error al adherirse al reclamo"

    @staticmethod
    def remove_supporter(claim_id: int, user_id: int) -> tuple[bool, str | None]:
        """
        Remueve un adherente de un reclamo.

        Args:
            claim_id: ID del reclamo
            user_id: ID del usuario que se desadhiere

        Returns:
            tuple[bool, str | None]: (True, None) si exitoso, (False, error_message) si falla
        """
        from modules.claim_supporter import ClaimSupporter

        # Buscar el adherente
        supporter = (
            db.session.query(ClaimSupporter)
            .filter_by(claim_id=claim_id, user_id=user_id)
            .first()
        )

        if not supporter:
            return False, "No estás adherido a este reclamo"

        db.session.delete(supporter)
        db.session.commit()
        return True, None

    @staticmethod
    def is_user_supporter(claim_id: int, user_id: int) -> bool:
        """
        Verifica si un usuario está adherido a un reclamo.

        Args:
            claim_id: ID del reclamo
            user_id: ID del usuario

        Returns:
            bool: True si está adherido, False en caso contrario
        """
        from modules.claim_supporter import ClaimSupporter

        supporter = (
            db.session.query(ClaimSupporter)
            .filter_by(claim_id=claim_id, user_id=user_id)
            .first()
        )
        return supporter is not None

    @staticmethod
    def get_by_user(user_id: int) -> list["Claim"]:
        """
        Obtiene todos los reclamos creados por un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de reclamos ordenados por fecha de creación (más recientes primero)
        """
        claims = (
            db.session.query(Claim)
            .filter_by(creator_id=user_id)
            .order_by(Claim.created_at.desc())
            .all()
        )
        return claims

    @staticmethod
    def get_supported_by_user(user_id: int) -> list["Claim"]:
        """
        Obtiene todos los reclamos a los que un usuario está adherido.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de reclamos ordenados por fecha de adhesión (más recientes primero)
        """
        from modules.claim_supporter import ClaimSupporter

        claims = (
            db.session.query(Claim)
            .join(ClaimSupporter, Claim.id == ClaimSupporter.claim_id)
            .filter(ClaimSupporter.user_id == user_id)
            .order_by(ClaimSupporter.created_at.desc())
            .all()
        )
        return claims

    @staticmethod
    def get_by_departments(department_ids: list[int]) -> list["Claim"]:
        """
        Obtiene reclamos filtrados por lista de departamentos.

        Args:
            department_ids: Lista de IDs de departamentos

        Returns:
            Lista de reclamos ordenados por fecha de creación descendente
        """
        if not department_ids:
            return []
        return (
            db.session.query(Claim)
            .filter(Claim.department_id.in_(department_ids))
            .order_by(Claim.created_at.desc())
            .all()
        )

    @staticmethod
    def get_supporter_ids(claim_id: int) -> list[int]:
        """
        Obtiene IDs de adherentes de un reclamo.

        Args:
            claim_id: ID del reclamo

        Returns:
            Lista de IDs de usuarios adherentes
        """
        from modules.claim_supporter import ClaimSupporter

        rows = (
            db.session.query(ClaimSupporter.user_id)
            .filter_by(claim_id=claim_id)
            .order_by(ClaimSupporter.created_at.asc())
            .all()
        )
        return [int(user_id) for (user_id,) in rows]
