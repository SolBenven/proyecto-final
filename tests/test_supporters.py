"""
Tests para Sistema de Adherentes (Fase 3)
Verifica las funcionalidades de adhesión a reclamos
"""

import unittest
from tests.conftest import BaseTestCase

from modules.models.claim import Claim
from modules.config import db
from modules.models.user.end_user import Cloister, EndUser


class TestSupporters(BaseTestCase):
    """Tests para el sistema de adherentes"""

    def setUp(self):
        """Configura el entorno de prueba"""
        super().setUp()
        # Crear usuario creador
        creator = EndUser(
            first_name="Creator",
            last_name="User",
            email="creator@test.com",
            username="creator_user",
            cloister=Cloister.TEACHER,
        )
        creator.set_password("test123")

        # Crear usuario adherente
        supporter = EndUser(
            first_name="Supporter",
            last_name="User",
            email="supporter@test.com",
            username="supporter_user",
            cloister=Cloister.STUDENT,
        )
        supporter.set_password("test123")

        db.session.add_all([creator, supporter])
        db.session.commit()

        # Crear reclamo
        claim, _ = Claim.create(
            user_id=creator.id, detail="Reclamo de prueba para adherentes"
        )

        self.creator_id = creator.id
        self.supporter_id = supporter.id
        self.claim_id = claim.id

    def test_add_supporter_successfully(self):
        """Verifica que un usuario puede adherirse a un reclamo"""
        success, error = Claim.add_supporter(self.claim_id, self.supporter_id)

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_check_is_supporter(self):
        """Verifica que se puede verificar si un usuario es adherente"""
        # Adherirse
        Claim.add_supporter(self.claim_id, self.supporter_id)

        # Verificar
        is_supporter = Claim.is_user_supporter(self.claim_id, self.supporter_id)

        self.assertTrue(is_supporter)

    def test_cannot_add_supporter_twice(self):
        """Verifica que un usuario no puede adherirse dos veces al mismo reclamo"""
        # Primera adhesión
        Claim.add_supporter(self.claim_id, self.supporter_id)

        # Intentar adherirse nuevamente
        success, error = Claim.add_supporter(self.claim_id, self.supporter_id)

        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertIn("adherido", error.lower())

    def test_creator_cannot_be_supporter(self):
        """Verifica que el creador no puede adherirse a su propio reclamo"""
        success, error = Claim.add_supporter(self.claim_id, self.creator_id)

        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertIn("propio reclamo", error.lower())

    def test_remove_supporter_successfully(self):
        """Verifica que un usuario puede quitar su adhesión"""
        # Adherirse primero
        Claim.add_supporter(self.claim_id, self.supporter_id)

        # Quitar adhesión
        success, error = Claim.remove_supporter(self.claim_id, self.supporter_id)

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_verify_supporter_removed(self):
        """Verifica que después de remover ya no está adherido"""
        # Adherirse y luego remover
        Claim.add_supporter(self.claim_id, self.supporter_id)
        Claim.remove_supporter(self.claim_id, self.supporter_id)

        # Verificar que ya no está adherido
        is_supporter = Claim.is_user_supporter(self.claim_id, self.supporter_id)

        self.assertFalse(is_supporter)

    def test_cannot_remove_if_not_supporter(self):
        """Verifica que no se puede quitar adhesión si no está adherido"""
        success, error = Claim.remove_supporter(self.claim_id, self.supporter_id)

        self.assertFalse(success)
        self.assertIsNotNone(error)

    def test_add_supporter_to_nonexistent_claim(self):
        """Verifica que no se puede adherir a un reclamo inexistente"""
        success, error = Claim.add_supporter(99999, self.supporter_id)

        self.assertFalse(success)
        self.assertIsNotNone(error)

    def test_multiple_supporters_on_same_claim(self):
        """Verifica que múltiples usuarios pueden adherirse al mismo reclamo"""
        # Crear otro usuario
        supporter2 = EndUser(
            first_name="Second",
            last_name="Supporter",
            email="supporter2@test.com",
            username="supporter2_user",
            cloister=Cloister.PAYS,
        )
        supporter2.set_password("test123")
        db.session.add(supporter2)
        db.session.commit()

        # Ambos se adhieren
        Claim.add_supporter(self.claim_id, self.supporter_id)
        Claim.add_supporter(self.claim_id, supporter2.id)

        # Verificar que ambos están adheridos
        self.assertTrue(Claim.is_user_supporter(self.claim_id, self.supporter_id))
        self.assertTrue(Claim.is_user_supporter(self.claim_id, supporter2.id))


if __name__ == "__main__":
    unittest.main()
