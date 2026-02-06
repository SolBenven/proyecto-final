"""Tests unitarios de estadísticas del Dashboard (Fase 9).

Importante: se testea la lógica de negocio (services), no rutas protegidas.
"""

import unittest
from tests.conftest import BaseTestCase

from modules.config import db
from modules.models.claim import Claim, ClaimStatus
from modules.models.department import Department
from modules.models.user.end_user import Cloister, EndUser


class TestDashboard(BaseTestCase):
    """Tests unitarios para el Dashboard"""

    def setUp(self):
        """Configura el entorno de prueba"""
        super().setUp()
        # Crear usuario de prueba
        user = EndUser(
            first_name="Test",
            last_name="User",
            email="dash@test.com",
            username="dashuser",
            cloister=Cloister.STUDENT,
        )
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

        # Crear reclamos en distintos departamentos y estados
        dept1_id = self.sample_departments["dept1_id"]
        dept2_id = self.sample_departments["dept2_id"]

        # dept1: 2 pendientes, 1 En proceso, 1 Resuelto
        c1, _ = Claim.create(
            user_id=self.user_id, detail="d1 p1", department_id=dept1_id
        )
        c2, _ = Claim.create(
            user_id=self.user_id, detail="d1 p2", department_id=dept1_id
        )
        c3, _ = Claim.create(
            user_id=self.user_id, detail="d1 ip", department_id=dept1_id
        )
        c4, _ = Claim.create(
            user_id=self.user_id, detail="d1 r", department_id=dept1_id
        )

        c3.status = ClaimStatus.IN_PROGRESS
        c4.status = ClaimStatus.RESOLVED

        # dept2: 1 Inválido, 1 Pendiente
        c5, _ = Claim.create(
            user_id=self.user_id, detail="d2 inv", department_id=dept2_id
        )
        c6, _ = Claim.create(
            user_id=self.user_id, detail="d2 p", department_id=dept2_id
        )
        c5.status = ClaimStatus.INVALID

        db.session.commit()

        self.seeded_dept1_id = dept1_id
        self.seeded_dept2_id = dept2_id

    def test_get_status_counts_global(self):
        """Incluye todos los departamentos cuando department_ids=None"""
        counts = Claim.get_status_counts(department_ids=None)

        self.assertGreaterEqual(counts[ClaimStatus.PENDING], 3)
        self.assertGreaterEqual(counts[ClaimStatus.IN_PROGRESS], 1)
        self.assertGreaterEqual(counts[ClaimStatus.RESOLVED], 1)
        self.assertGreaterEqual(counts[ClaimStatus.INVALID], 1)

    def test_get_dashboard_counts_filtered_by_department(self):
        """Filtra correctamente por lista de department_ids"""
        counts = Claim.get_dashboard_counts(department_ids=[self.seeded_dept1_id])

        self.assertEqual(counts["total_claims"], 4)
        self.assertEqual(counts["pending_claims"], 2)
        self.assertEqual(counts["in_progress_claims"], 1)
        self.assertEqual(counts["resolved_claims"], 1)
        self.assertEqual(counts["invalid_claims"], 0)

    def test_get_dashboard_counts_empty_list_returns_zero(self):
        """department_ids=[] no debe significar 'todos', sino 'ninguno'"""
        counts = Claim.get_dashboard_counts(department_ids=[])
        self.assertEqual(
            counts,
            {
                "total_claims": 0,
                "pending_claims": 0,
                "in_progress_claims": 0,
                "resolved_claims": 0,
                "invalid_claims": 0,
            },
        )

    def test_get_department_dashboard_counts(self):
        """Devuelve conteos por departamento sin N+1 queries"""
        per_dept = Claim.get_department_dashboard_counts(
            [self.seeded_dept1_id, self.seeded_dept2_id]
        )

        self.assertEqual(
            per_dept[self.seeded_dept1_id],
            {
                "total": 4,
                "pending": 2,
                "in_progress": 1,
                "resolved": 1,
                "invalid": 0,
            },
        )
        self.assertEqual(
            per_dept[self.seeded_dept2_id],
            {
                "total": 2,
                "pending": 1,
                "in_progress": 0,
                "resolved": 0,
                "invalid": 1,
            },
        )


if __name__ == "__main__":
    unittest.main()
