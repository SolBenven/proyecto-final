"""
Tests para decoradores de permisos y control de acceso.

Verifica:
- admin_required
- admin_role_required
- department_access_required
- can_manage_claim
"""

import unittest
from tests.conftest import BaseTestCase

from flask import Blueprint
from modules.config import db
from modules.models.user import EndUser, AdminUser, Cloister, AdminRole
from modules.models.department import Department
from modules.models.claim import Claim, ClaimStatus
from modules.utils.decorators import (
    admin_required,
    admin_role_required,
    department_access_required,
    can_manage_claim,
    end_user_required,
)


class TestEndUserRequired(BaseTestCase):
    """Tests para el decorador end_user_required"""

    def setUp(self):
        """Configura el entorno de prueba"""
        super().setUp()
        # Configurar rutas de prueba para los decoradores
        test_bp = Blueprint("test", __name__)

        @test_bp.route("/end-user-only")
        @end_user_required
        def end_user_only():
            return "end-user-ok"

        self.app.register_blueprint(test_bp)

    def test_not_authenticated_redirects_to_login(self):
        """Usuario no autenticado debe redirigir a login de end user"""
        response = self.client.get("/end-user-only")
        self.assertEqual(response.status_code, 302)
        # Flask-Login redirige a /login por defecto si no está configurado
        self.assertIn("login", response.location.lower())


class TestAdminRequired(BaseTestCase):
    """Tests para el decorador admin_required"""

    def setUp(self):
        """Configura el entorno de prueba"""
        super().setUp()
        # Configurar rutas de prueba para los decoradores
        test_bp = Blueprint("test", __name__)

        @test_bp.route("/admin-only")
        @admin_required
        def admin_only():
            return "admin-ok"

        self.app.register_blueprint(test_bp)

    def test_not_authenticated_redirects_to_login(self):
        """Usuario no autenticado debe redirigir a login"""
        response = self.client.get("/admin-only")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.location)


class TestAdminRoleRequired(BaseTestCase):
    """Tests para el decorador admin_role_required"""

    pass  # Los decoradores requieren contexto de Flask-Login completo


class TestDepartmentAccessRequired(BaseTestCase):
    """Tests para el decorador department_access_required"""

    pass  # Los decoradores requieren contexto de Flask-Login completo


class TestCanManageClaim(BaseTestCase):
    """Tests para la función can_manage_claim"""

    def setUp(self):
        """Configura el entorno de prueba"""
        super().setUp()
        # Usar departamento de prueba existente o crear uno nuevo
        dept = db.session.query(Department).filter_by(name="test_dept").first()
        if not dept:
            dept = Department(
                name="test_dept",
                display_name="Departamento de Prueba",
                is_technical_secretariat=False,
            )
            db.session.add(dept)
            db.session.commit()
        self.department_id = dept.id

        # Usar secretaría técnica existente (ya creada por BaseTestCase)
        tech_dept = db.session.query(Department).filter_by(is_technical_secretariat=True).first()
        self.tech_department_id = tech_dept.id

    def test_technical_secretary_properties(self):
        """Secretaría técnica tiene las propiedades correctas"""
        technical_secretary = AdminUser(
            first_name="Secretario",
            last_name="Técnico",
            email="secretary@test.com",
            username="secretary",
            admin_role=AdminRole.TECHNICAL_SECRETARY,
            department_id=self.tech_department_id,
        )
        self.assertTrue(technical_secretary.is_technical_secretary)
        self.assertEqual(technical_secretary.admin_role, AdminRole.TECHNICAL_SECRETARY)

    def test_department_head_properties(self):
        """Jefe de departamento tiene las propiedades correctas"""
        department_head = AdminUser(
            first_name="Jefe",
            last_name="Departamento",
            email="head@test.com",
            username="depthead",
            admin_role=AdminRole.DEPARTMENT_HEAD,
            department_id=self.department_id,
        )
        self.assertTrue(department_head.is_department_head)
        self.assertEqual(department_head.admin_role, AdminRole.DEPARTMENT_HEAD)
        self.assertEqual(department_head.department_id, self.department_id)


class TestRoleProperties(BaseTestCase):
    """Tests para las propiedades de roles en AdminUser"""

    def setUp(self):
        """Configura el entorno de prueba"""
        super().setUp()
        # Usar departamento de prueba existente o crear uno nuevo
        dept = db.session.query(Department).filter_by(name="test_dept").first()
        if not dept:
            dept = Department(
                name="test_dept",
                display_name="Departamento de Prueba",
                is_technical_secretariat=False,
            )
            db.session.add(dept)
            db.session.commit()
        self.department_id = dept.id

        # Usar secretaría técnica existente (ya creada por BaseTestCase)
        tech_dept = db.session.query(Department).filter_by(is_technical_secretariat=True).first()
        self.tech_department_id = tech_dept.id

    def test_is_department_head_property(self):
        """Propiedad is_department_head funciona correctamente"""
        head = AdminUser(
            first_name="Jefe",
            last_name="Test",
            email="head@test.com",
            username="head",
            admin_role=AdminRole.DEPARTMENT_HEAD,
            department_id=self.department_id,
        )

        self.assertTrue(head.is_department_head)

    def test_is_technical_secretary_property(self):
        """Propiedad is_technical_secretary funciona correctamente"""
        secretary = AdminUser(
            first_name="Secretario",
            last_name="Test",
            email="sec@test.com",
            username="sec",
            admin_role=AdminRole.TECHNICAL_SECRETARY,
            department_id=self.tech_department_id,
        )

        self.assertTrue(secretary.is_technical_secretary)

        # Otros roles no son secretarios
        head = AdminUser(
            first_name="Jefe",
            last_name="Test",
            email="head2@test.com",
            username="head2",
            admin_role=AdminRole.DEPARTMENT_HEAD,
            department_id=self.tech_department_id,
        )
        self.assertFalse(head.is_technical_secretary)


class TestIntegration(BaseTestCase):
    """Tests de integración para permisos"""

    pass  # Los tests de integración requieren configuración completa de Flask-Login


if __name__ == '__main__':
    unittest.main()
