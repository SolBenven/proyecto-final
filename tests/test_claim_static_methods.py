"""
Tests para Claim static methods (CRUD básico - Fase 2)
Verifica las funcionalidades de creación y consulta de reclamos
"""

import unittest

from modules.config import db
from modules.claim import Claim, ClaimStatus
from modules.department import Department
from modules.end_user import Cloister, EndUser
from tests.conftest import BaseTestCase


class TestClaimStaticMethods(BaseTestCase):
    """Tests para los métodos estáticos de Claim"""

    def setUp(self):
        """Configuración antes de cada test"""
        super().setUp()
        # Crear usuario de prueba
        user = EndUser(
            first_name="Test",
            last_name="User",
            email="testuser@test.com",
            username="testuser",
            cloister=Cloister.STUDENT,
        )
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()
        self.sample_user_id = user.id

    def test_create_claim_without_department(self):
        """Verifica que un reclamo sin departamento se asigna a Secretaría Técnica"""
        claim, error = Claim.create(
            user_id=self.sample_user_id,
            detail="Problema de prueba sin departamento",
            department_id=None,
        )

        self.assertIsNone(error)
        self.assertIsNotNone(claim)
        self.assertTrue(claim.department.is_technical_secretariat)
        self.assertEqual(claim.status, ClaimStatus.PENDING)

    def test_create_claim_with_specific_department(self):
        """Verifica que un reclamo se asigna al departamento especificado"""
        dept_id = self.sample_departments["dept1_id"]

        claim, error = Claim.create(
            user_id=self.sample_user_id,
            detail="Problema específico de departamento",
            department_id=dept_id,
        )

        self.assertIsNone(error)
        self.assertIsNotNone(claim)
        self.assertEqual(claim.department_id, dept_id)

    def test_create_claim_with_empty_detail(self):
        """Verifica que no se puede crear un reclamo con detalle vacío"""
        claim, error = Claim.create(
            user_id=self.sample_user_id, detail="   ", department_id=None
        )

        self.assertIsNone(claim)
        self.assertIsNotNone(error)
        self.assertIn("vacío", error.lower())

    def test_create_claim_with_invalid_department(self):
        """Verifica que no se puede crear un reclamo con departamento Inválido"""
        claim, error = Claim.create(
            user_id=self.sample_user_id,
            detail="Problema con dept Inválido",
            department_id=9999,
        )

        self.assertIsNone(claim)
        self.assertIsNotNone(error)
        self.assertIn("válido", error.lower())

    def test_get_claim_by_id(self):
        """Verifica que se puede obtener un reclamo por su ID"""
        # Crear reclamo
        claim, _ = Claim.create(
            user_id=self.sample_user_id,
            detail="Reclamo para recuperar",
            department_id=None,
        )

        # Obtener reclamo
        retrieved_claim = Claim.get_by_id(claim.id)

        self.assertIsNotNone(retrieved_claim)
        self.assertEqual(retrieved_claim.id, claim.id)
        self.assertEqual(retrieved_claim.detail, "Reclamo para recuperar")

    def test_get_claim_with_invalid_id(self):
        """Verifica que retorna None para ID Inválido"""
        claim = Claim.get_by_id(99999)
        self.assertIsNone(claim)

    def test_get_all_claims(self):
        """Verifica que se pueden obtener todos los reclamos"""
        # Crear varios reclamos
        Claim.create(
            user_id=self.sample_user_id, detail="Reclamo 1", department_id=None
        )
        Claim.create(
            user_id=self.sample_user_id, detail="Reclamo 2", department_id=None
        )

        all_claims = Claim.get_all_with_filters()

        self.assertGreaterEqual(len(all_claims), 2)

    def test_filter_claims_by_department(self):
        """Verifica que se pueden filtrar reclamos por departamento"""
        ts = Department.get_technical_secretariat()
        dept1_id = self.sample_departments["dept1_id"]

        # Crear reclamos en diferentes departamentos
        Claim.create(
            user_id=self.sample_user_id, detail="Reclamo ST", department_id=ts.id
        )
        Claim.create(
            user_id=self.sample_user_id, detail="Reclamo Dept1", department_id=dept1_id
        )

        # Filtrar por ST
        filtered_claims = Claim.get_all_with_filters(department_filter=ts.id)

        self.assertGreaterEqual(len(filtered_claims), 1)
        self.assertTrue(all(c.department_id == ts.id for c in filtered_claims))

    def test_filter_claims_by_status(self):
        """Verifica que se pueden filtrar reclamos por estado"""
        # Crear reclamos
        Claim.create(
            user_id=self.sample_user_id, detail="Reclamo Pendiente", department_id=None
        )

        # Filtrar por estado PENDING
        pending_claims = Claim.get_all_with_filters(status_filter=ClaimStatus.PENDING)

        self.assertGreaterEqual(len(pending_claims), 1)
        self.assertTrue(all(c.status == ClaimStatus.PENDING for c in pending_claims))

    def test_get_pending_claims(self):
        """Verifica que se obtienen solo reclamos pendientes"""
        # Crear reclamo Pendiente
        claim, _ = Claim.create(
            user_id=self.sample_user_id, detail="Reclamo Pendiente", department_id=None
        )

        pending_claims = Claim.get_pending()

        self.assertGreaterEqual(len(pending_claims), 1)
        self.assertIn(claim.id, [c.id for c in pending_claims])
        self.assertTrue(all(c.status == ClaimStatus.PENDING for c in pending_claims))


if __name__ == "__main__":
    unittest.main()
