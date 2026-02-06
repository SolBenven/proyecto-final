"""
Tests para el servicio de clasificación automática de reclamos.
"""

import unittest
import os
import tempfile
from modules.classifier import Classifier


class TestClassifierBase(unittest.TestCase):
    """Clase base para tests del clasificador con fixtures comunes"""

    def setUp(self):
        """Configuración antes de cada test"""
        # Crear instancia temporal con paths únicos para tests
        self.classifier = Classifier()

        # Usar directorio temporal para los modelos de prueba
        self.temp_dir = tempfile.mkdtemp()
        self.classifier.model_path = os.path.join(
            self.temp_dir, "test_classifier.joblib"
        )
        self.classifier.vectorizer_path = os.path.join(
            self.temp_dir, "test_vectorizer.joblib"
        )

        # Datos de entrenamiento de ejemplo
        self.sample_training_data = {
            "texts": [
                "El aire acondicionado no funciona",
                "Se rompió la canilla del baño",
                "Las luces están quemadas",
                "Hay grietas en la pared",
                "El techo tiene filtraciones",
                "Las baldosas están rotas",
                "No hay internet en el aula",
                "La computadora no enciende",
                "El proyector no funciona",
            ],
            "labels": [
                "mantenimiento",
                "mantenimiento",
                "mantenimiento",
                "infraestructura",
                "infraestructura",
                "infraestructura",
                "sistemas",
                "sistemas",
                "sistemas",
            ],
        }

    def tearDown(self):
        """Limpieza después de cada test"""
        # Cleanup: eliminar modelos temporales
        if os.path.exists(self.classifier.model_path):
            os.remove(self.classifier.model_path)
        if os.path.exists(self.classifier.vectorizer_path):
            os.remove(self.classifier.vectorizer_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)


class TestClassifierTraining(TestClassifierBase):
    """Tests para entrenamiento del clasificador"""

    def test_train_with_valid_data(self):
        """Test entrenamiento con datos válidos"""
        self.classifier.train(
            self.sample_training_data["texts"], self.sample_training_data["labels"]
        )

        self.assertTrue(self.classifier.is_trained)
        self.assertTrue(os.path.exists(self.classifier.model_path))
        self.assertTrue(os.path.exists(self.classifier.vectorizer_path))

    def test_train_with_empty_data(self):
        """Test entrenamiento con datos vacíos"""
        with self.assertRaisesRegex(ValueError, "Se requieren textos y etiquetas"):
            self.classifier.train([], [])

    def test_train_with_mismatched_lengths(self):
        """Test entrenamiento con cantidades diferentes de textos y etiquetas"""
        with self.assertRaisesRegex(ValueError, "debe coincidir"):
            self.classifier.train(
                ["texto1", "texto2"],
                ["departamento1"],  # Solo una etiqueta para dos textos
            )

    def test_model_persists_after_training(self):
        """Test que el modelo se guarda correctamente"""
        self.classifier.train(
            self.sample_training_data["texts"], self.sample_training_data["labels"]
        )

        # Crear nueva instancia con los mismos paths
        new_classifier = Classifier()
        new_classifier.model_path = self.classifier.model_path
        new_classifier.vectorizer_path = self.classifier.vectorizer_path

        # Debería poder cargar el modelo
        new_classifier._load_model()
        self.assertTrue(new_classifier.is_trained)


class TestClassifierPrediction(TestClassifierBase):
    """Tests para predicción del clasificador"""

    def setUp(self):
        """Configuración con clasificador ya entrenado"""
        super().setUp()
        self.classifier.train(
            self.sample_training_data["texts"], self.sample_training_data["labels"]
        )

    def test_classify_mantenimiento(self):
        """Test clasificación de reclamo de mantenimiento"""
        result = self.classifier.classify(
            "El aire acondicionado hace ruido y no enfría"
        )
        self.assertEqual(result, "mantenimiento")

    def test_classify_infraestructura(self):
        """Test clasificación de reclamo de infraestructura"""
        result = self.classifier.classify("Las paredes tienen grietas grandes")
        self.assertEqual(result, "infraestructura")

    def test_classify_sistemas(self):
        """Test clasificación de reclamo de sistemas"""
        result = self.classifier.classify("No funciona el WiFi en el laboratorio")
        self.assertEqual(result, "sistemas")

    def test_classify_with_empty_text(self):
        """Test clasificación con texto vacío"""
        with self.assertRaisesRegex(ValueError, "no puede estar vacío"):
            self.classifier.classify("")

    def test_classify_with_whitespace_only(self):
        """Test clasificación con solo espacios"""
        with self.assertRaisesRegex(ValueError, "no puede estar vacío"):
            self.classifier.classify("   ")

    def test_classify_without_training(self):
        """Test clasificación sin modelo entrenado"""
        # Crear nuevo clasificador sin entrenar
        new_classifier = Classifier()
        # Usar paths de temp para evitar cargar modelo existente
        new_classifier.model_path = os.path.join(self.temp_dir, "nonexistent.joblib")
        new_classifier.vectorizer_path = os.path.join(
            self.temp_dir, "nonexistent_vec.joblib"
        )
        with self.assertRaisesRegex(ValueError, "no está entrenado"):
            new_classifier.classify("Algún texto")


class TestClassifierConfidence(TestClassifierBase):
    """Tests para confianza de predicción"""

    def setUp(self):
        """Configuración con clasificador ya entrenado"""
        super().setUp()
        self.classifier.train(
            self.sample_training_data["texts"], self.sample_training_data["labels"]
        )

    def test_get_confidence_returns_valid_probability(self):
        """Test que la confianza está entre 0 y 1"""
        confidence = self.classifier.get_confidence("El aire acondicionado no funciona")
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_get_confidence_with_empty_text(self):
        """Test confianza con texto vacío"""
        confidence = self.classifier.get_confidence("")
        self.assertEqual(confidence, 0.0)

    def test_get_confidence_without_training(self):
        """Test confianza sin modelo entrenado"""
        # Crear nuevo clasificador sin entrenar
        new_classifier = Classifier()
        # Usar paths de temp para evitar cargar modelo existente
        new_classifier.model_path = os.path.join(self.temp_dir, "nonexistent.joblib")
        new_classifier.vectorizer_path = os.path.join(
            self.temp_dir, "nonexistent_vec.joblib"
        )
        confidence = new_classifier.get_confidence("Algún texto")
        self.assertEqual(confidence, 0.0)


class TestClassifierAvailability(TestClassifierBase):
    """Tests para verificación de disponibilidad del modelo"""

    def test_is_model_available_returns_false_initially(self):
        """Test que inicialmente no hay modelo disponible"""
        self.assertFalse(self.classifier.is_model_available())

    def test_is_model_available_returns_true_after_training(self):
        """Test que retorna True después de entrenar"""
        self.classifier.train(
            self.sample_training_data["texts"], self.sample_training_data["labels"]
        )
        self.assertTrue(self.classifier.is_model_available())


class TestClassifierIntegration(TestClassifierBase):
    """Tests de integración del clasificador"""

    def test_train_save_load_predict_workflow(self):
        """Test del flujo completo: entrenar, guardar, cargar y predecir"""
        # Entrenar
        self.classifier.train(
            self.sample_training_data["texts"], self.sample_training_data["labels"]
        )

        # Crear nueva instancia y cargar modelo
        new_classifier = Classifier()
        new_classifier.model_path = self.classifier.model_path
        new_classifier.vectorizer_path = self.classifier.vectorizer_path
        new_classifier._load_model()

        # Predecir con el modelo cargado
        result = new_classifier.classify("El aire acondicionado no funciona")
        self.assertEqual(result, "mantenimiento")

    def test_multiple_predictions_are_consistent(self):
        """Test que predicciones múltiples del mismo texto son consistentes"""
        self.classifier.train(
            self.sample_training_data["texts"], self.sample_training_data["labels"]
        )

        text = "El aire acondicionado hace ruido"
        result1 = self.classifier.classify(text)
        result2 = self.classifier.classify(text)
        result3 = self.classifier.classify(text)

        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)


if __name__ == "__main__":
    unittest.main()
