"""
Tests para Department static methods (Fase 1)
Verifica las funcionalidades de consulta de departamentos
"""

import unittest
from tests.conftest import BaseTestCase

from modules.config import db
from modules.department import Department
from modules.admin_user import AdminRole, AdminUser


class TestDepartmentStaticMethods(BaseTestCase):
    """Tests para los métodos estáticos de Department"""

    def test_get_departments_for_admin_department_head(self):
        """Un admin no-secretaría ve solo su departamento"""
        dept1_id = self.sample_departments["dept1_id"]
        admin = AdminUser(
            first_name="Jefe",
            last_name="Test",
            email="jefe@test.com",
            username="jefetest",
            admin_role=AdminRole.DEPARTMENT_HEAD,
            department_id=dept1_id,
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

        visible = Department.get_for_admin(admin)
        self.assertEqual([d.id for d in visible], [dept1_id])

    def test_get_departments_for_admin_technical_secretary(self):
        """Secretaría técnica ve todos los departamentos"""
        st_id = self.sample_departments["st_id"]
        admin = AdminUser(
            first_name="Secretario",
            last_name="Test",
            email="st@test.com",
            username="sttest",
            admin_role=AdminRole.TECHNICAL_SECRETARY,
            department_id=st_id,
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

        visible = Department.get_for_admin(admin)
        all_depts = Department.get_all()
        self.assertEqual({d.id for d in visible}, {d.id for d in all_depts})

    def test_get_all_departments(self):
        """Verifica que se obtienen todos los departamentos"""
        departments = Department.get_all()

        self.assertGreaterEqual(len(departments), 3)
        self.assertTrue(any(d.is_technical_secretariat for d in departments))

    def test_get_technical_secretariat(self):
        """Verifica que se obtiene la Secretaría Técnica"""
        ts = Department.get_technical_secretariat()

        self.assertIsNotNone(ts)
        self.assertTrue(ts.is_technical_secretariat)
        self.assertIn("técnica", ts.display_name.lower())

    def test_get_department_by_id(self):
        """Verifica que se obtiene un departamento por su ID"""
        dept_id = self.sample_departments["dept1_id"]

        retrieved = Department.get_by_id(dept_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, dept_id)
        self.assertEqual(retrieved.name, "ciencias")

    def test_get_department_by_invalid_id(self):
        """Verifica que retorna None para ID Inválido"""
        dept = Department.get_by_id(9999)

        self.assertIsNone(dept)

    def test_department_relationships(self):
        """Verifica que los departamentos tienen las propiedades correctas"""
        departments = Department.get_all()

        for dept in departments:
            self.assertTrue(hasattr(dept, "name"))
            self.assertTrue(hasattr(dept, "display_name"))
            self.assertTrue(hasattr(dept, "is_technical_secretariat"))
            self.assertIsInstance(dept.is_technical_secretariat, bool)


if __name__ == "__main__":
    unittest.main()
