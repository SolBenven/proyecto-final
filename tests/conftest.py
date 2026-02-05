"""
Configuración para tests - Agrega el path del proyecto y define la clase base
"""

import sys
from pathlib import Path
import unittest

# Agregar el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_test_app():
    """Factory para crear una app de testing completamente aislada"""
    from modules.config import create_app

    test_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key-" + str(id(object())),
        }
    )

    # Register routes on the test app
    import modules.routes as routes_module
    
    # Copy all route rules from the module's app to our test app
    for rule in routes_module.app.url_map.iter_rules():
        if rule.endpoint != 'static':
            # Get the view function from the original app
            view_func = routes_module.app.view_functions.get(rule.endpoint)
            if view_func:
                # Check if the rule already exists
                existing = [r for r in test_app.url_map.iter_rules() if r.endpoint == rule.endpoint]
                if not existing:
                    test_app.add_url_rule(
                        rule.rule,
                        endpoint=rule.endpoint,
                        view_func=view_func,
                        methods=rule.methods - {'OPTIONS', 'HEAD'}
                    )
    
    # Copy context processors from the original app
    for func in routes_module.app.template_context_processors[None]:
        test_app.context_processor(func)

    return test_app


class BaseTestCase(unittest.TestCase):
    """Clase base para todos los tests con configuración común"""

    def setUp(self):
        """Crea una instancia de la aplicación para tests con base de datos limpia"""
        from modules.config import db

        self.app = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()
        self._create_sample_departments()

    def tearDown(self):
        """Limpia la base de datos después de cada test"""
        from modules.config import db
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_sample_departments(self):
        """Crea departamentos de prueba y guarda sus IDs"""
        from modules.config import db
        from modules.models.department import Department

        # Crear Secretaría Técnica
        st = Department(
            name="secretaria_tecnica",
            display_name="Secretaría Técnica",
            is_technical_secretariat=True,
        )
        # Crear otros departamentos
        dept1 = Department(
            name="ciencias",
            display_name="Departamento de Ciencias",
            is_technical_secretariat=False,
        )
        dept2 = Department(
            name="humanidades",
            display_name="Departamento de Humanidades",
            is_technical_secretariat=False,
        )

        db.session.add_all([st, dept1, dept2])
        db.session.commit()

        # Guardar los IDs como atributos de instancia
        self.sample_departments = {
            "st_id": st.id,
            "dept1_id": dept1.id,
            "dept2_id": dept2.id
        }
