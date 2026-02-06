"""Tests básicos para AdminHelper (Fase 10: Gestión de Reclamos Admin)."""

import unittest

from modules.config import db
from modules.models.claim import Claim, ClaimStatus
from modules.models.user.admin_user import AdminRole, AdminUser
from modules.models.user.end_user import Cloister, EndUser
from tests.conftest import BaseTestCase


class TestAdminHelper(BaseTestCase):
    """Tests para AdminHelper"""

    def setUp(self):
        """Configuración antes de cada test"""
        super().setUp()

        # Crear usuario final
        user = EndUser(
            first_name="Usuario",
            last_name="Final",
            email="enduser@test.com",
            username="enduser",
            cloister=Cloister.STUDENT,
        )
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()
        self.end_user_id = user.id

        # Crear reclamos en dos departamentos
        dept1_id = self.sample_departments["dept1_id"]
        dept2_id = self.sample_departments["dept2_id"]

        c1, _ = Claim.create(
            user_id=self.end_user_id, detail="Reclamo dept1", department_id=dept1_id
        )
        c2, _ = Claim.create(
            user_id=self.end_user_id, detail="Reclamo dept2", department_id=dept2_id
        )
        self.assertIsNotNone(c1)
        self.assertIsNotNone(c2)
        self.dept1_claim_id = c1.id
        self.dept2_claim_id = c2.id

        # Crear admin jefe de departamento
        dept1_id = self.sample_departments["dept1_id"]
        user, error = AdminUser.create(
            first_name="Jefe",
            last_name="Depto",
            email="head@test.com",
            username="head",
            admin_role=AdminRole.DEPARTMENT_HEAD,
            password="admin123",
            department_id=dept1_id,
        )
        self.assertIsNone(error)
        self.assertIsNotNone(user)
        self.dept_head_username = user.username

    def login_admin(self, username: str, password: str = "admin123"):
        """Helper para hacer login de admin"""
        return self.client.post(
            "/admin/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_department_head_sees_only_own_department_claims(self):
        """Verifica que jefe de departamento solo ve reclamos de su departamento"""
        login_response = self.login_admin(self.dept_head_username)
        self.assertEqual(login_response.status_code, 200)

        response = self.client.get("/admin/claims")
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Reclamo #{self.dept1_claim_id}".encode(), response.data)
        self.assertNotIn(f"Reclamo #{self.dept2_claim_id}".encode(), response.data)

    def test_department_head_cannot_update_other_department_claim_status(self):
        """Verifica que jefe de departamento no puede actualizar reclamos de otro departamento"""
        login_response = self.login_admin(self.dept_head_username)
        self.assertEqual(login_response.status_code, 200)

        response = self.client.post(
            f"/claims/{self.dept2_claim_id}/status",
            data={"status": "resolved"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("No tienes permiso".encode(), response.data)

        claim = Claim.get_by_id(self.dept2_claim_id)
        self.assertIsNotNone(claim)
        self.assertEqual(claim.status, ClaimStatus.PENDING)


if __name__ == "__main__":
    unittest.main()
