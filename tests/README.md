# Tests

Esta carpeta contiene los tests del proyecto organizados por módulo/funcionalidad.

## Estructura

- `conftest.py` - Configuración base de tests con BaseTestCase
- `test_department_service.py` - Tests para DepartmentService (Fase 1)
- `test_claim_service.py` - Tests para ClaimService CRUD (Fase 2)
- `test_supporters.py` - Tests para Sistema de Adherentes (Fase 3)
- `test_notifications.py` - Tests para sistema de notificaciones (Fase 4)
- `test_analytics.py` - Tests para servicio de analíticas (Fase 11)
- `test_classifier.py` - Tests para clasificador automático
- Y más...

## Ejecutar Tests

El proyecto usa **unittest** (biblioteca estándar de Python) en lugar de pytest.

### Ejecutar todos los tests:
```bash
python -m unittest discover tests
```

### Ejecutar un test específico:
```bash
python -m unittest tests.test_claim_service
python -m unittest tests.test_notifications
python -m unittest tests.test_analytics
```

### Ejecutar una clase de test específica:
```bash
python -m unittest tests.test_claim_service.TestClaimService
```

### Ejecutar un test individual:
```bash
python -m unittest tests.test_claim_service.TestClaimService.test_create_claim_without_department
```

### Opciones útiles:
```bash
# Con salida detallada (verbose)
python -m unittest discover tests -v

# Detener en el primer fallo
python -m unittest discover tests -f
```

## Guía para Agregar Nuevos Tests

Cuando implementes una nueva funcionalidad, **siempre crea tests básicos** que verifiquen:

1. **Casos exitosos**: La funcionalidad funciona correctamente con datos válidos
2. **Casos de error**: Manejo correcto de errores con datos inválidos
3. **Validaciones**: Todas las restricciones y validaciones funcionan
4. **Edge cases**: Casos límite y situaciones especiales

### Plantilla para nuevos tests:

```python
"""
Tests para [Nombre del Módulo] - [Fase X]
"""
import unittest

from app.extensions import db
from app.services.tu_servicio import TuServicio
from tests.conftest import BaseTestCase


class TestTuFuncionalidad(BaseTestCase):
    """Tests para tu funcionalidad"""

    def setUp(self):
        """Configuración antes de cada test"""
        super().setUp()
        # Agregar configuración adicional si es necesaria
        # Por ejemplo, crear usuarios de prueba, datos, etc.

    def test_caso_exitoso(self):
        """Descripción de qué prueba este test"""
        # Arrange - preparar datos
        # Act - ejecutar la funcionalidad
        # Assert - verificar resultados
        self.assertEqual(resultado_esperado, resultado_actual)
        self.assertIsNotNone(objeto)
        self.assertTrue(condicion)

    def test_caso_de_error(self):
        """Test que verifica manejo de errores"""
        with self.assertRaises(ValueError):
            # Código que debería lanzar ValueError
            pass

    def test_edge_case(self):
        """Test de caso límite o especial"""
        # ...
        self.assertIn(elemento, lista)


if __name__ == '__main__':
    unittest.main()
```

### Assertions comunes en unittest:

- `assertEqual(a, b)` - Verifica que a == b
- `assertNotEqual(a, b)` - Verifica que a != b
- `assertTrue(x)` / `assertFalse(x)` - Verifica booleano
- `assertIsNone(x)` / `assertIsNotNone(x)` - Verifica None
- `assertIn(a, b)` / `assertNotIn(a, b)` - Verifica membresía
- `assertRaises(Exception)` - Verifica que se lanza excepción
- `assertGreater(a, b)` / `assertLess(a, b)` - Comparaciones numéricas
- `assertIsInstance(a, type)` - Verifica tipo

## Convenciones

- Usa nombres descriptivos: `test_nombre_funcionalidad.py`
- Agrupa tests relacionados en el mismo archivo
- Usa asserts para validaciones automáticas
- Imprime mensajes claros de progreso con ✅/❌
- Documenta qué prueba cada test
- Limpia datos de prueba si es necesario
