"""
Tests para UserNotification static methods (Phase 4)
Verifica las funcionalidades del sistema de notificaciones
"""

import unittest

from modules.config import db
from modules.models.claim import Claim, ClaimStatus
from modules.models.claim_status_history import ClaimStatusHistory
from modules.models.department import Department
from modules.models.user.admin_user import AdminRole, AdminUser
from modules.models.user.end_user import Cloister, EndUser
from modules.models.user_notification import UserNotification
from tests.conftest import BaseTestCase


class TestNotificationStaticMethods(BaseTestCase):
    """Tests para los métodos estáticos de UserNotification"""

    def setUp(self):
        """Configuración antes de cada test"""
        super().setUp()
        # Crear usuarios de prueba
        user1 = EndUser(
            first_name="Usuario",
            last_name="Uno",
            email="user1@test.com",
            username="user1",
            cloister=Cloister.STUDENT,
        )
        user1.set_password("password123")

        user2 = EndUser(
            first_name="Usuario",
            last_name="Dos",
            email="user2@test.com",
            username="user2",
            cloister=Cloister.TEACHER,
        )
        user2.set_password("password123")

        st_id = self.sample_departments["st_id"]
        admin = AdminUser(
            first_name="Admin",
            last_name="Test",
            email="admin@test.com",
            username="admin",
            admin_role=AdminRole.TECHNICAL_SECRETARY,
            department_id=st_id,
        )
        admin.set_password("admin123")

        db.session.add_all([user1, user2, admin])
        db.session.commit()

        self.user1_id = user1.id
        self.user2_id = user2.id
        self.admin_id = admin.id

    def test_get_user_claims(self):
        """Verifica que se obtienen los reclamos de un usuario"""
        # Crear dos reclamos para user1
        claim1, _ = Claim.create(
            user_id=self.user1_id, detail="Reclamo 1 del usuario", department_id=1
        )
        claim2, _ = Claim.create(
            user_id=self.user1_id, detail="Reclamo 2 del usuario", department_id=2
        )

        # Obtener reclamos del usuario
        user_claims = Claim.get_by_user(self.user1_id)

        self.assertEqual(len(user_claims), 2)
        self.assertIn(claim1, user_claims)
        self.assertIn(claim2, user_claims)

    def test_get_user_supported_claims(self):
        """Verifica que se obtienen los reclamos adheridos por un usuario"""
        # user1 crea un reclamo
        claim, _ = Claim.create(
            user_id=self.user1_id, detail="Reclamo para adherir", department_id=1
        )

        # user2 se adhiere
        Claim.add_supporter(claim_id=claim.id, user_id=self.user2_id)

        # Obtener reclamos adheridos por user2
        supported_claims = Claim.get_supported_by_user(self.user2_id)

        self.assertEqual(len(supported_claims), 1)
        self.assertEqual(supported_claims[0].id, claim.id)

    def test_update_claim_status(self):
        """Verifica que un admin puede cambiar el estado de un reclamo"""
        # Crear reclamo
        claim, _ = Claim.create(
            user_id=self.user1_id, detail="Reclamo para cambiar estado", department_id=1
        )

        self.assertEqual(claim.status, ClaimStatus.PENDING)

        # Admin actualiza el estado
        success, error = Claim.update_status(
            claim_id=claim.id,
            new_status=ClaimStatus.IN_PROGRESS,
            admin_user_id=self.admin_id,
        )

        self.assertTrue(success)
        self.assertIsNone(error)

        # Verificar que se actualizó
        db.session.refresh(claim)
        self.assertEqual(claim.status, ClaimStatus.IN_PROGRESS)

        # Verificar que se creó una entrada en el historial
        history = (
            db.session.query(ClaimStatusHistory).filter_by(claim_id=claim.id).first()
        )
        self.assertIsNotNone(history)
        self.assertEqual(history.old_status, ClaimStatus.PENDING)
        self.assertEqual(history.new_status, ClaimStatus.IN_PROGRESS)
        self.assertEqual(history.changed_by_id, self.admin_id)

    def test_update_status_creates_notification(self):
        """Verifica que cambiar el estado crea una notificación para el creador"""
        # Crear reclamo
        claim, _ = Claim.create(
            user_id=self.user1_id, detail="Reclamo con notificación", department_id=1
        )

        # Verificar que no hay notificaciones inicialmente
        notifications_before = UserNotification.get_pending_for_user(self.user1_id)
        self.assertEqual(len(notifications_before), 0)

        # Admin cambia el estado
        Claim.update_status(
            claim_id=claim.id,
            new_status=ClaimStatus.IN_PROGRESS,
            admin_user_id=self.admin_id,
        )

        # Verificar que se creó una UserNotification para el creador
        notifications_after = UserNotification.get_pending_for_user(self.user1_id)
        self.assertEqual(len(notifications_after), 1)

        notification = notifications_after[0]
        self.assertEqual(notification.user_id, self.user1_id)
        self.assertEqual(notification.claim_status_history.claim_id, claim.id)
        self.assertEqual(
            notification.claim_status_history.new_status, ClaimStatus.IN_PROGRESS
        )
        self.assertFalse(notification.is_read)

    def test_supporter_receives_notification(self):
        """Verifica que los adherentes reciben notificaciones independientes"""
        # user1 crea reclamo
        claim, _ = Claim.create(
            user_id=self.user1_id, detail="Reclamo con adherentes", department_id=1
        )

        # user2 se adhiere
        Claim.add_supporter(claim_id=claim.id, user_id=self.user2_id)

        # Admin cambia el estado
        Claim.update_status(
            claim_id=claim.id,
            new_status=ClaimStatus.RESOLVED,
            admin_user_id=self.admin_id,
        )

        # Verificar que ambos usuarios reciben notificación independiente
        user1_notifications = UserNotification.get_pending_for_user(self.user1_id)
        user2_notifications = UserNotification.get_pending_for_user(self.user2_id)

        self.assertEqual(len(user1_notifications), 1)  # creador
        self.assertEqual(len(user2_notifications), 1)  # adherente

        # Verificar que son notificaciones diferentes (UserNotification con diferentes IDs)
        self.assertNotEqual(user1_notifications[0].id, user2_notifications[0].id)
        self.assertEqual(user1_notifications[0].user_id, self.user1_id)
        self.assertEqual(user2_notifications[0].user_id, self.user2_id)

        # Pero apuntan al mismo cambio de estado
        self.assertEqual(
            user1_notifications[0].claim_status_history_id,
            user2_notifications[0].claim_status_history_id,
        )

    def test_get_unread_count(self):
        """Verifica que se obtiene el contador correcto de notificaciones no leídas"""
        # Inicialmente sin notificaciones
        count = UserNotification.get_unread_count(self.user1_id)
        self.assertEqual(count, 0)

        # Crear reclamo y cambiar estado dos veces
        claim, _ = Claim.create(
            user_id=self.user1_id, detail="Reclamo para contar", department_id=1
        )

        Claim.update_status(
            claim_id=claim.id,
            new_status=ClaimStatus.IN_PROGRESS,
            admin_user_id=self.admin_id,
        )
        Claim.update_status(
            claim_id=claim.id,
            new_status=ClaimStatus.RESOLVED,
            admin_user_id=self.admin_id,
        )

        # Verificar que ahora hay 2 notificaciones
        count = UserNotification.get_unread_count(self.user1_id)
        self.assertEqual(count, 2)

    def test_mark_notification_as_read(self):
        """Verifica que se puede marcar una notificación como leída"""
        # Crear reclamo y cambiar estado
        claim, _ = Claim.create(
            user_id=self.user1_id, detail="Reclamo para marcar leído", department_id=1
        )

        Claim.update_status(
            claim_id=claim.id,
            new_status=ClaimStatus.IN_PROGRESS,
            admin_user_id=self.admin_id,
        )

        # Obtener la notificación
        notifications = UserNotification.get_pending_for_user(self.user1_id)
        self.assertEqual(len(notifications), 1)
        notification = notifications[0]

        # Marcar como leída
        success, error = UserNotification.mark_notification_as_read(
            notification.id, self.user1_id
        )

        self.assertTrue(success)
        self.assertIsNone(error)

        # Verificar que ya no aparece en pendientes
        notifications_after = UserNotification.get_pending_for_user(self.user1_id)
        self.assertEqual(len(notifications_after), 0)

    def test_cannot_mark_other_user_notification(self):
        """Verifica que un usuario no puede marcar notificaciones de otro usuario"""
        # user1 crea reclamo, admin cambia estado
        claim, _ = Claim.create(
            user_id=self.user1_id, detail="Reclamo de user1", department_id=1
        )

        Claim.update_status(
            claim_id=claim.id,
            new_status=ClaimStatus.IN_PROGRESS,
            admin_user_id=self.admin_id,
        )

        # Obtener la notificación de user1 (es una UserNotification)
        notifications = UserNotification.get_pending_for_user(self.user1_id)
        notification = notifications[0]

        # Verificar que la notificación pertenece a user1
        self.assertEqual(notification.user_id, self.user1_id)

        # user2 intenta marcarla como leída (usando el ID de la UserNotification)
        success, error = UserNotification.mark_notification_as_read(
            notification.id, self.user2_id
        )

        self.assertFalse(success)
        self.assertIn("permiso", error.lower())

    def test_mark_all_notifications_as_read(self):
        """Verifica que se pueden marcar todas las notificaciones como leídas"""
        # Crear reclamo y cambiar estado varias veces
        claim, _ = Claim.create(
            user_id=self.user1_id, detail="Reclamo múltiples cambios", department_id=1
        )

        Claim.update_status(
            claim_id=claim.id,
            new_status=ClaimStatus.IN_PROGRESS,
            admin_user_id=self.admin_id,
        )
        Claim.update_status(
            claim_id=claim.id,
            new_status=ClaimStatus.RESOLVED,
            admin_user_id=self.admin_id,
        )

        # Verificar que hay 2 notificaciones
        count_before = UserNotification.get_unread_count(self.user1_id)
        self.assertEqual(count_before, 2)

        # Marcar todas como leídas
        marked = UserNotification.mark_all_as_read_for_user(self.user1_id)
        self.assertEqual(marked, 2)

        # Verificar que no quedan notificaciones
        count_after = UserNotification.get_unread_count(self.user1_id)
        self.assertEqual(count_after, 0)

    def test_no_notification_if_status_unchanged(self):
        """Verifica que no se crea notificación si el estado no cambia"""
        # Crear reclamo
        claim, _ = Claim.create(
            user_id=self.user1_id, detail="Reclamo sin cambio", department_id=1
        )

        # Intentar "cambiar" al mismo estado
        success, error = Claim.update_status(
            claim_id=claim.id,
            new_status=ClaimStatus.PENDING,
            admin_user_id=self.admin_id,
        )

        self.assertFalse(success)
        self.assertIn("no ha cambiado", error.lower())

        # Verificar que no se creó notificación
        notifications = UserNotification.get_pending_for_user(self.user1_id)
        self.assertEqual(len(notifications), 0)

    def test_notifications_are_independent_per_user(self):
        """Verifica que cada usuario tiene notificaciones independientes"""
        # user1 crea reclamo, user2 se adhiere
        claim, _ = Claim.create(
            user_id=self.user1_id, detail="Reclamo para independencia", department_id=1
        )
        Claim.add_supporter(claim_id=claim.id, user_id=self.user2_id)

        # Admin cambia el estado
        Claim.update_status(
            claim_id=claim.id,
            new_status=ClaimStatus.IN_PROGRESS,
            admin_user_id=self.admin_id,
        )

        # Ambos tienen 1 notificación
        self.assertEqual(UserNotification.get_unread_count(self.user1_id), 1)
        self.assertEqual(UserNotification.get_unread_count(self.user2_id), 1)

        # user1 marca su notificación como leída
        user1_notifications = UserNotification.get_pending_for_user(self.user1_id)
        UserNotification.mark_notification_as_read(
            user1_notifications[0].id, self.user1_id
        )

        # user1 ya no tiene notificaciones, pero user2 sí
        self.assertEqual(UserNotification.get_unread_count(self.user1_id), 0)
        self.assertEqual(UserNotification.get_unread_count(self.user2_id), 1)

        # user2 marca su notificación
        user2_notifications = UserNotification.get_pending_for_user(self.user2_id)
        UserNotification.mark_notification_as_read(
            user2_notifications[0].id, self.user2_id
        )

        # Ahora ninguno tiene notificaciones
        self.assertEqual(UserNotification.get_unread_count(self.user1_id), 0)
        self.assertEqual(UserNotification.get_unread_count(self.user2_id), 0)


if __name__ == "__main__":
    unittest.main()
