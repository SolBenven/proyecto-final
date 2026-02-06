"""
Tests para ReportGenerator - Fase 12
"""

import unittest
from tests.conftest import BaseTestCase

from modules.config import db
from modules.claim import Claim, ClaimStatus
from modules.department import Department
from modules.end_user import Cloister, EndUser
from modules.analytics_generator import AnalyticsGenerator


class TestReportGenerator(BaseTestCase):
    """Tests para el generador de reportes"""

    def setUp(self):
        """Configura el entorno de prueba"""
        super().setUp()
        # Crear usuario de prueba
        user = EndUser(
            first_name="Report",
            last_name="User",
            email="report@test.com",
            username="reportuser",
            cloister=Cloister.STUDENT,
        )
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

        # Crear reclamos variados para pruebas de reportes
        dept1_id = self.sample_departments["dept1_id"]
        dept2_id = self.sample_departments["dept2_id"]

        # Dept1: 2 pendientes, 1 En proceso, 1 Resuelto
        c1, _ = Claim.create(
            user_id=self.user_id,
            detail="Reclamo de prueba número uno para departamento de ciencias",
            department_id=dept1_id,
        )
        c2, _ = Claim.create(
            user_id=self.user_id,
            detail="Segundo reclamo Pendiente en ciencias",
            department_id=dept1_id,
        )
        c3, _ = Claim.create(
            user_id=self.user_id,
            detail="Reclamo En proceso en ciencias",
            department_id=dept1_id,
        )
        c4, _ = Claim.create(
            user_id=self.user_id,
            detail="Reclamo Resuelto satisfactoriamente",
            department_id=dept1_id,
        )

        c3.status = ClaimStatus.IN_PROGRESS
        c4.status = ClaimStatus.RESOLVED

        # Dept2: 1 Inválido, 1 Pendiente
        c5, _ = Claim.create(
            user_id=self.user_id,
            detail="Reclamo Inválido en humanidades",
            department_id=dept2_id,
        )
        c6, _ = Claim.create(
            user_id=self.user_id,
            detail="Reclamo Pendiente en humanidades",
            department_id=dept2_id,
        )
        c5.status = ClaimStatus.INVALID

        db.session.commit()

        self.dept1_id = dept1_id
        self.dept2_id = dept2_id

    # ============================================================
    # Tests para Claim.get_by_departments
    # ============================================================

    def test_get_claims_for_report_returns_claims(self):
        """Retorna reclamos de los departamentos especificados"""
        claims = Claim.get_by_departments([self.dept1_id])

        self.assertEqual(len(claims), 4)

    def test_get_claims_for_report_multiple_departments(self):
        """Incluye reclamos de múltiples departamentos"""
        claims = Claim.get_by_departments([self.dept1_id, self.dept2_id])

        self.assertEqual(len(claims), 6)

    def test_get_claims_for_report_empty_list(self):
        """Lista vacía retorna lista vacía"""
        claims = Claim.get_by_departments([])

        self.assertEqual(claims, [])

    def test_get_claims_for_report_ordered_by_date(self):
        """Reclamos ordenados por fecha descendente"""
        claims = Claim.get_by_departments([self.dept1_id])

        # Verificar orden descendente
        for i in range(len(claims) - 1):
            self.assertGreaterEqual(claims[i].created_at, claims[i + 1].created_at)

    # ============================================================
    # Tests para Department.get_by_ids
    # ============================================================

    def test_get_departments_for_report(self):
        """Retorna departamentos especificados"""
        departments = Department.get_by_ids([self.dept1_id])

        self.assertEqual(len(departments), 1)
        self.assertEqual(departments[0].id, self.dept1_id)

    def test_get_departments_for_report_multiple(self):
        """Retorna múltiples departamentos"""
        departments = Department.get_by_ids([self.dept1_id, self.dept2_id])

        self.assertEqual(len(departments), 2)

    def test_get_departments_for_report_empty_list(self):
        """Lista vacía retorna lista vacía"""
        departments = Department.get_by_ids([])

        self.assertEqual(departments, [])

    # ============================================================
    # Tests para get_report_stats (estadísticas del reporte)
    # ============================================================

    def test_get_report_stats_total_claims(self):
        """Verifica que las estadísticas incluyen total de reclamos"""
        stats = AnalyticsGenerator.get_claim_stats([self.dept1_id])

        self.assertEqual(stats["total_claims"], 4)

    def test_get_report_stats_by_status(self):
        """Verifica conteo por estado"""
        stats = AnalyticsGenerator.get_claim_stats([self.dept1_id])

        self.assertEqual(stats["status_counts"]["Pendiente"], 2)
        self.assertEqual(stats["status_counts"]["En proceso"], 1)
        self.assertEqual(stats["status_counts"]["Resuelto"], 1)

    def test_get_report_stats_multiple_departments(self):
        """Verifica estadísticas con múltiples departamentos"""
        stats = AnalyticsGenerator.get_claim_stats([self.dept1_id, self.dept2_id])

        self.assertEqual(stats["total_claims"], 6)
        self.assertEqual(stats["status_counts"]["Inválido"], 1)


if __name__ == "__main__":
    unittest.main()
