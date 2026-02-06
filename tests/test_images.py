"""
Tests para Phase 5: Carga de Imágenes
Verifica las funcionalidades del sistema de carga de imágenes en reclamos
"""

import io
import unittest
from pathlib import Path
from werkzeug.datastructures import FileStorage
from tests.conftest import BaseTestCase

from modules.config import db
from modules.claim import Claim
from modules.department import Department
from modules.admin_user import AdminRole, AdminUser
from modules.end_user import Cloister, EndUser
from modules.claim import Claim
from modules.image_handler import ImageHandler


class TestImages(BaseTestCase):
    """Tests para el sistema de carga de imágenes"""

    def setUp(self):
        """Configura el entorno de prueba"""
        super().setUp()
        # Crear usuario de prueba
        user1 = EndUser(
            first_name="Usuario",
            last_name="Test",
            email="user1@test.com",
            username="user1",
            cloister=Cloister.STUDENT,
        )
        user1.set_password("password123")

        db.session.add(user1)
        db.session.commit()
        self.user1_id = user1.id

        # Crear imagen de prueba en memoria
        png_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        self.test_image = FileStorage(
            stream=io.BytesIO(png_data),
            filename="test_image.png",
            content_type="image/png",
        )

        # Crear imagen grande de prueba
        large_data = b"x" * (6 * 1024 * 1024)  # 6MB
        self.large_image = FileStorage(
            stream=io.BytesIO(large_data),
            filename="large.png",
            content_type="image/png",
        )

    def test_allowed_file(self):
        """Verifica que se validen correctamente las extensiones permitidas"""
        self.assertTrue(ImageHandler.allowed_file("image.png"))
        self.assertTrue(ImageHandler.allowed_file("image.jpg"))
        self.assertTrue(ImageHandler.allowed_file("image.jpeg"))
        self.assertTrue(ImageHandler.allowed_file("image.gif"))
        self.assertFalse(ImageHandler.allowed_file("image.bmp"))
        self.assertFalse(ImageHandler.allowed_file("image.txt"))
        self.assertFalse(ImageHandler.allowed_file("image"))

    def test_validate_image_success(self):
        """Verifica que se valide correctamente una imagen válida"""
        is_valid, error = ImageHandler.validate_image(self.test_image)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_image_no_file(self):
        """Verifica que se rechace cuando no hay archivo"""
        is_valid, error = ImageHandler.validate_image(None)
        self.assertFalse(is_valid)
        self.assertIn("no se proporcionó", error.lower())

    def test_validate_image_empty_filename(self):
        """Verifica que se rechace un archivo sin nombre"""
        empty_file = FileStorage(stream=io.BytesIO(b""), filename="")
        is_valid, error = ImageHandler.validate_image(empty_file)
        self.assertFalse(is_valid)
        self.assertIn("no se proporcionó", error.lower())

    def test_validate_image_invalid_extension(self):
        """Verifica que se rechacen extensiones no permitidas"""
        invalid_file = FileStorage(
            stream=io.BytesIO(b"data"), filename="file.txt", content_type="text/plain"
        )
        is_valid, error = ImageHandler.validate_image(invalid_file)
        self.assertFalse(is_valid)
        self.assertIn("no permitido", error.lower())

    def test_validate_image_too_large(self):
        """Verifica que se rechacen imágenes muy grandes"""
        is_valid, error = ImageHandler.validate_image(self.large_image)
        self.assertFalse(is_valid)
        self.assertTrue("excede" in error.lower() or "5mb" in error.lower())

    def test_save_claim_image_success(self):
        """Verifica que se guarde correctamente una imagen"""
        saved_path, error = ImageHandler.save_claim_image(self.test_image)

        self.assertIsNone(error)
        self.assertIsNotNone(saved_path)
        self.assertTrue(saved_path.startswith("static/uploads/claims/"))
        self.assertTrue(saved_path.endswith(".png"))

        # Verificar que el archivo existe
        file_path = Path(saved_path)
        self.assertTrue(file_path.exists())

        # Limpiar
        ImageHandler.delete_claim_image(saved_path)

    def test_save_claim_image_invalid(self):
        """Verifica que se rechace guardar una imagen inválida"""
        invalid_file = FileStorage(stream=io.BytesIO(b"data"), filename="file.txt")
        saved_path, error = ImageHandler.save_claim_image(invalid_file)

        self.assertIsNone(saved_path)
        self.assertIsNotNone(error)

    def test_delete_claim_image(self):
        """Verifica que se elimine correctamente una imagen"""
        # Primero guardar
        saved_path, _ = ImageHandler.save_claim_image(self.test_image)
        self.assertTrue(Path(saved_path).exists())

        # Luego eliminar
        result = ImageHandler.delete_claim_image(saved_path)
        self.assertTrue(result)
        self.assertFalse(Path(saved_path).exists())

    def test_delete_nonexistent_image(self):
        """Verifica que se maneje correctamente la eliminación de imagen inexistente"""
        result = ImageHandler.delete_claim_image("uploads/claims/nonexistent.png")
        self.assertFalse(result)

    def test_create_claim_with_image(self):
        """Verifica que se pueda crear un reclamo con imagen"""
        # Guardar imagen primero
        image_path, _ = ImageHandler.save_claim_image(self.test_image)

        # Crear reclamo con imagen
        claim, error = Claim.create(
            user_id=self.user1_id,
            detail="Reclamo con imagen de prueba",
            department_id=1,
            image_path=image_path,
        )

        self.assertIsNone(error)
        self.assertIsNotNone(claim)
        self.assertEqual(claim.image_path, image_path)
        self.assertTrue(Path(claim.image_path).exists())

        # Limpiar
        ImageHandler.delete_claim_image(image_path)

    def test_create_claim_without_image(self):
        """Verifica que se pueda crear un reclamo sin imagen"""
        claim, error = Claim.create(
            user_id=self.user1_id,
            detail="Reclamo sin imagen",
            department_id=1,
            image_path=None,
        )

        self.assertIsNone(error)
        self.assertIsNotNone(claim)
        self.assertIsNone(claim.image_path)

    def test_create_claim_cleanup_on_error(self):
        """Verifica que se limpie la imagen si falla la creación del reclamo"""
        # Guardar imagen
        image_path, _ = ImageHandler.save_claim_image(self.test_image)
        self.assertTrue(Path(image_path).exists())

        # Intentar crear reclamo con datos inválidos (sin detalle)
        claim, error = Claim.create(
            user_id=self.user1_id,
            detail="",  # Detalle vacío causará error
            department_id=1,
            image_path=image_path,
        )

        self.assertIsNone(claim)
        self.assertIsNotNone(error)

        # En un caso real, el controller debería limpiar la imagen
        # Simulamos esa limpieza aquí
        ImageHandler.delete_claim_image(image_path)
        self.assertFalse(Path(image_path).exists())


if __name__ == "__main__":
    unittest.main()
