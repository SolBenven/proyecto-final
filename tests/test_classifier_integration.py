"""
Test de integración para verificar que Phase 6 funciona correctamente.
"""

import unittest
from tests.conftest import BaseTestCase

from modules.config import db
from modules.models import Department, EndUser, Cloister
from modules.models.claim import Claim
from modules.classifier import classifier


class TestClassifierIntegration(BaseTestCase):
    """Tests de integración para el clasificador"""

    def setUp(self):
        """Configura el entorno de prueba"""
        super().setUp()
        # Crear departamentos específicos para clasificación (solo si no existen)
        dept_configs = [
            ("mantenimiento", "Mantenimiento", False),
            ("infraestructura", "Infraestructura", False),
            ("sistemas", "Sistemas", False),
        ]

        for name, display_name, is_ts in dept_configs:
            existing = db.session.query(Department).filter_by(name=name).first()
            if not existing:
                dept = Department(
                    name=name,
                    display_name=display_name,
                    is_technical_secretariat=is_ts,
                )
                db.session.add(dept)
        db.session.commit()

        self.classifier_departments = {
            "mantenimiento": db.session.query(Department)
            .filter_by(name="mantenimiento")
            .first()
            .id,
            "infraestructura": db.session.query(Department)
            .filter_by(name="infraestructura")
            .first()
            .id,
            "sistemas": db.session.query(Department)
            .filter_by(name="sistemas")
            .first()
            .id,
            "secretaria_tecnica": db.session.query(Department)
            .filter_by(name="secretaria_tecnica")
            .first()
            .id,
        }

        # Crear usuario de prueba
        user = EndUser(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            cloister=Cloister.STUDENT,
        )
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

    def test_claim_classification_with_trained_model(self):
        """Test que un reclamo se clasifica automáticamente con modelo entrenado"""
        # Verificar que el modelo está disponible
        if not classifier.is_model_available():
            self.skipTest("Modelo no entrenado. Ejecutar train_classifier.py primero")

        # Crear reclamo sin especificar departamento (clasificación automática)
        claim, error = Claim.create(
            user_id=self.user_id,
            detail="El proyector del aula 301 no funciona correctamente",
            department_id=None,  # Sin especificar → clasificación automática
        )

        self.assertIsNotNone(claim)
        self.assertIsNone(error)

        # El reclamo debería tener un departamento asignado
        self.assertIsNotNone(claim.department)
        # El clasificador debería asignar a un departamento (puede ser cualquiera,
        # incluyendo secretaria_tecnica si el departamento predicho no existe)
        self.assertIsNotNone(claim.department.name)

    def test_claim_fallback_to_secretaria_without_model(self):
        """Test que sin modelo se asigna a Secretaría Técnica"""
        # Simular que no hay modelo disponible
        original_available = classifier.is_model_available

        def mock_not_available():
            return False

        classifier.is_model_available = mock_not_available

        try:
            # Crear reclamo sin departamento
            claim, error = Claim.create(
                user_id=self.user_id,
                detail="Algún problema que no se puede clasificar",
                department_id=None,
            )

            self.assertIsNotNone(claim)
            self.assertIsNone(error)

            # Debería asignarse a Secretaría Técnica
            self.assertTrue(claim.department.is_technical_secretariat)

        finally:
            # Restaurar método original
            classifier.is_model_available = original_available

    def test_claim_with_manual_department_selection(self):
        """Test que la selección manual de departamento funciona"""
        mantenimiento_id = self.classifier_departments["mantenimiento"]

        # Crear reclamo especificando departamento manualmente
        claim, error = Claim.create(
            user_id=self.user_id,
            detail="Este texto sugeriría sistemas pero seleccionamos mantenimiento",
            department_id=mantenimiento_id,  # Selección manual
        )

        self.assertIsNotNone(claim)
        self.assertIsNone(error)

        # Debería respetar la selección manual
        self.assertEqual(claim.department.name, "mantenimiento")

    def test_classifier_predictions_are_reasonable(self):
        """Test que las predicciones del clasificador retornan valores válidos"""
        if not classifier.is_model_available():
            self.skipTest("Modelo no entrenado. Ejecutar train_classifier.py primero")

        # Textos de prueba representativos
        test_texts = [
            "El aire acondicionado no funciona",
            "Hay grietas en la pared",
            "No funciona el WiFi",
            "Las luces están apagadas",
            "Necesito más bancos",
            "La computadora no enciende",
        ]

        # Verificar que el clasificador retorna predicciones válidas (no None, no vacías)
        for text in test_texts:
            predicted = classifier.classify(text)
            self.assertIsNotNone(predicted, f"'{text}' retornó None")
            self.assertIsInstance(predicted, str, f"'{text}' no retornó string")
            self.assertGreater(len(predicted), 0, f"'{text}' retornó string vacío")

    def test_classifier_confidence_is_valid(self):
        """Test que la confianza del clasificador está en rango válido"""
        if not classifier.is_model_available():
            self.skipTest("Modelo no entrenado. Ejecutar train_classifier.py primero")

        texts = [
            "El aire acondicionado no funciona",
            "Hay grietas en la pared",
            "No funciona el WiFi",
        ]

        for text in texts:
            confidence = classifier.get_confidence(text)
            self.assertGreaterEqual(
                confidence, 0.0, f"Confianza fuera de rango: {confidence}"
            )
            self.assertLessEqual(
                confidence, 1.0, f"Confianza fuera de rango: {confidence}"
            )
            self.assertGreater(
                confidence,
                0.0,
                "La confianza debería ser mayor a 0 para textos válidos",
            )


if __name__ == "__main__":
    unittest.main()
