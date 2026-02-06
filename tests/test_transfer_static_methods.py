"""
Tests para ClaimTransfer static methods - Fase 13: Derivación de Reclamos
"""

import unittest
import time
from tests.conftest import BaseTestCase

from modules.config import db
from modules.models.claim import Claim, ClaimStatus
from modules.models.claim_transfer import ClaimTransfer
from modules.models.department import Department
from modules.models.user.admin_user import AdminRole, AdminUser
from modules.models.user.end_user import Cloister, EndUser


class TestTransferStaticMethods(BaseTestCase):
    """Tests para los métodos estáticos de ClaimTransfer"""

    def setUp(self):
        """Configura el entorno de prueba"""
        super().setUp()
        # Crear usuario de prueba
        user = EndUser(
            first_name="Transfer",
            last_name="User",
            email="transfer@test.com",
            username="transferuser",
            cloister=Cloister.STUDENT,
        )
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

        # Crear secretario técnico
        st_id = self.sample_departments["st_id"]
        admin = AdminUser(
            first_name="Secretario",
            last_name="Técnico",
            email="secretario@test.com",
            username="secretario",
            admin_role=AdminRole.TECHNICAL_SECRETARY,
            department_id=st_id,
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        self.technical_secretary_id = admin.id

        # Crear jefe de departamento
        dept1_id = self.sample_departments["dept1_id"]
        dept_head = AdminUser(
            first_name="Jefe",
            last_name="Departamento",
            email="jefe@test.com",
            username="jefe",
            admin_role=AdminRole.DEPARTMENT_HEAD,
            department_id=dept1_id,
        )
        dept_head.set_password("admin123")
        db.session.add(dept_head)
        db.session.commit()
        self.department_head_id = dept_head.id

        # Crear reclamo de prueba
        claim, _ = Claim.create(
            user_id=self.user_id,
            detail="Reclamo de prueba para transferencia",
            department_id=dept1_id,
        )
        db.session.commit()
        self.claim_id = claim.id
        self.original_department_id = dept1_id

    # ============================================================
    # Tests para ClaimTransfer.transfer
    # ============================================================

    def test_transfer_claim_success(self):
        """Transfiere exitosamente un reclamo a otro departamento"""
        to_dept_id = self.sample_departments["dept2_id"]

        transfer, error = ClaimTransfer.transfer(
            claim_id=self.claim_id,
            to_department_id=to_dept_id,
            transferred_by_id=self.technical_secretary_id,
            reason="Corresponde a otro departamento",
        )

        self.assertIsNone(error)
        self.assertIsNotNone(transfer)
        self.assertEqual(transfer.to_department_id, to_dept_id)
        self.assertEqual(transfer.reason, "Corresponde a otro departamento")

    def test_transfer_claim_updates_department(self):
        """La transferencia actualiza el departamento del reclamo"""
        to_dept_id = self.sample_departments["dept2_id"]

        transfer, error = ClaimTransfer.transfer(
            claim_id=self.claim_id,
            to_department_id=to_dept_id,
            transferred_by_id=self.technical_secretary_id,
        )

        # Verificar que el departamento del reclamo cambió
        claim = Claim.get_by_id(self.claim_id)
        self.assertEqual(claim.department_id, to_dept_id)
        self.assertNotEqual(claim.department_id, self.original_department_id)

    def test_transfer_claim_creates_history_record(self):
        """La transferencia crea un registro en el historial"""
        to_dept_id = self.sample_departments["dept2_id"]

        ClaimTransfer.transfer(
            claim_id=self.claim_id,
            to_department_id=to_dept_id,
            transferred_by_id=self.technical_secretary_id,
        )

        # Verificar historial de transferencias
        history = ClaimTransfer.get_history_for_claim(self.claim_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].from_department_id, self.original_department_id)
        self.assertEqual(history[0].to_department_id, to_dept_id)

    def test_transfer_claim_invalid_claim(self):
        """Error al transferir reclamo inexistente"""
        to_dept_id = self.sample_departments["dept2_id"]

        transfer, error = ClaimTransfer.transfer(
            claim_id=99999,
            to_department_id=to_dept_id,
            transferred_by_id=self.technical_secretary_id,
        )

        self.assertIsNone(transfer)
        self.assertEqual(error, "Reclamo no encontrado")

    def test_transfer_claim_invalid_department(self):
        """Error al transferir a departamento inexistente"""
        transfer, error = ClaimTransfer.transfer(
            claim_id=self.claim_id,
            to_department_id=99999,
            transferred_by_id=self.technical_secretary_id,
        )

        self.assertIsNone(transfer)
        self.assertEqual(error, "Departamento destino no válido")

    def test_transfer_claim_same_department(self):
        """Error al transferir al mismo departamento"""
        transfer, error = ClaimTransfer.transfer(
            claim_id=self.claim_id,
            to_department_id=self.original_department_id,
            transferred_by_id=self.technical_secretary_id,
        )

        self.assertIsNone(transfer)
        self.assertEqual(error, "El reclamo ya pertenece a ese departamento")

    def test_transfer_claim_without_reason(self):
        """Transferencia sin motivo es válida"""
        to_dept_id = self.sample_departments["dept2_id"]

        transfer, error = ClaimTransfer.transfer(
            claim_id=self.claim_id,
            to_department_id=to_dept_id,
            transferred_by_id=self.technical_secretary_id,
            reason=None,
        )

        self.assertIsNone(error)
        self.assertIsNone(transfer.reason)

    # ============================================================
    # Tests para ClaimTransfer.get_history_for_claim
    # ============================================================

    def test_get_transfer_history_empty(self):
        """Historial vacío para reclamo sin transferencias"""
        history = ClaimTransfer.get_history_for_claim(self.claim_id)

        self.assertEqual(history, [])

    def test_get_transfer_history_multiple(self):
        """Historial con múltiples transferencias"""
        dept2_id = self.sample_departments["dept2_id"]
        st_id = self.sample_departments["st_id"]

        # Primera transferencia
        ClaimTransfer.transfer(
            claim_id=self.claim_id,
            to_department_id=dept2_id,
            transferred_by_id=self.technical_secretary_id,
            reason="Primera derivación",
        )

        # Pequeña pausa para asegurar diferente timestamp
        time.sleep(0.01)

        # Segunda transferencia
        ClaimTransfer.transfer(
            claim_id=self.claim_id,
            to_department_id=st_id,
            transferred_by_id=self.technical_secretary_id,
            reason="Segunda derivación",
        )

        history = ClaimTransfer.get_history_for_claim(self.claim_id)

        self.assertEqual(len(history), 2)
        # Ordenado por fecha descendente (más reciente primero)
        self.assertEqual(history[0].reason, "Segunda derivación")
        self.assertEqual(history[1].reason, "Primera derivación")

    # ============================================================
    # Tests para ClaimTransfer.get_available_departments
    # ============================================================

    def test_get_available_departments_excludes_current(self):
        """Excluye el departamento actual de la lista"""
        current_dept_id = self.sample_departments["dept1_id"]

        available = ClaimTransfer.get_available_departments(current_dept_id)

        # Verificar que el departamento actual no está en la lista
        available_ids = [d.id for d in available]
        self.assertNotIn(current_dept_id, available_ids)

        # Verificar que hay otros departamentos disponibles
        self.assertGreaterEqual(len(available), 2)  # dept2 y st al menos

    # ============================================================
    # Tests para ClaimTransfer.can_transfer
    # ============================================================

    def test_can_transfer_technical_secretary(self):
        """Secretario técnico puede transferir"""
        admin = db.session.get(AdminUser, self.technical_secretary_id)

        can = ClaimTransfer.can_transfer(admin)

        self.assertTrue(can)

    def test_can_transfer_department_head_cannot(self):
        """Jefe de departamento no puede transferir"""
        admin = db.session.get(AdminUser, self.department_head_id)

        can = ClaimTransfer.can_transfer(admin)

        self.assertFalse(can)


if __name__ == "__main__":
    unittest.main()
