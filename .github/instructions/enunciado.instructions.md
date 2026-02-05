Siempre que se realice una implementación, se deben tener en cuenta los siguientes puntos:
- La implementación debe seguir el pedido original del usuario, respetando sus indicaciones y requerimientos específicos.
- Se debe utilizar un lenguaje claro y conciso, evitando tecnicismos innecesarios que
  puedan dificultar la comprensión del contenido.
- La estructura del contenido debe ser lógica y coherente, facilitando la lectura y comprensión.
- Siempre se puede volver a preguntar al usuario si hay dudas o si se necesita más información para realizar una implementación adecuada.
- Siempre utilizar la sintaxis moderna de SQLAlchemy (tipos Mapped, mapped_column, etc) con db.session para consultas y transacciones.
- **EVITAR JavaScript siempre que sea posible**: Preferir formularios HTML con POST y renderizado del servidor. Solo usar JavaScript si es absolutamente necesario para la funcionalidad requerida.
- Siempre utilizar fechas con timezone (utcnow con timezone.utc) y almacenar en la base de datos en UTC. Para esto utilizar datetime.now().
- Al importar la clase datetime poner from datetime import datetime para seguir la convención del proyecto.
- Siempre se debe entrar al venv antes de instalar nuevas dependencias o ejecutar scripts. .\venv\Scripts\python.exe
- **IMPORTANTE: Después de implementar una nueva funcionalidad, SIEMPRE crear tests básicos en la carpeta `tests/`** que verifiquen:
  - Casos exitosos con datos válidos
  - Manejo de errores con datos inválidos
  - Validaciones y restricciones
  - Casos límite (edge cases)
  - Ver `tests/README.md` para plantilla y guías

Los puntos descriptos arriba deben servir como guia general a la hora de realizar implementaciones. Pero SIEMPRE se debe priorizar el pedido original.
Los templates y el contenido que ve el usuario debe estar en español.

---

## Arquitectura del Proyecto

### Estructura de Carpetas
```
app/
├── models/
│   └── user/                # Modelos de usuario (herencia)
│       ├── __init__.py      # Exporta User, EndUser, AdminUser, enums
│       ├── base.py          # User base class
│       ├── end_user.py      # EndUser + Cloister enum
│       └── admin_user.py    # AdminUser + AdminRole enum
├── routes/
│   ├── auth/                # Autenticación (nested blueprints)
│   │   ├── __init__.py      # Blueprint padre 'auth'
│   │   ├── end_user.py      # auth.end_user.* (/register, /login, /logout)
│   │   └── admin.py         # auth.admin.* (/admin/login, /admin/)
│   └── main.py              # Rutas principales
├── services/                # Lógica de negocio
│   └── user_service.py      # UserService
├── templates/               # Templates Jinja2
│   ├── auth/                # Templates usuario final
│   └── admin/               # Templates admin
├── utils/                   # Utilidades (decorators.py para permisos)
├── extensions.py            # Extensiones Flask (db, login_manager)
└── __init__.py              # Factory de la aplicación
tests/                       # Tests del proyecto
├── test_*.py                # Tests por módulo/funcionalidad
├── run_all_tests.py         # Ejecutar todos los tests
└── README.md                # Guía de testing
```

### Patrón de Diseño
- **Nested Blueprints**: Blueprints anidados para organizar rutas (`auth.end_user.*`, `auth.admin.*`)
- **Services**: La lógica de negocio va en servicios, NO en las rutas
- **Models**: Usar SQLAlchemy con tipos `Mapped` (estilo moderno Python 3.10+)
- **Single Table Inheritance**: Herencia de modelos User → EndUser/AdminUser
- **Testing**: Tests básicos obligatorios para cada nueva funcionalidad

---

## Modelos de Usuario

### Herencia (Single Table Inheritance)
```
User (base)
├── EndUser (cloister: Cloister)
└── AdminUser (department_id: int, admin_role: AdminRole)
```

### Cloister (Claustro) - Solo EndUser
```python
class Cloister(Enum):
    STUDENT = "estudiante"
    TEACHER = "docente"
    PAYS = "PAyS"  # Personal de Apoyo y Servicios
```

### AdminRole (Roles Admin) - Solo AdminUser
```python
class AdminRole(Enum):
    DEPARTMENT_HEAD = "jefe_departamento"   # Jefe de un departamento
    TECHNICAL_SECRETARY = "secretario_tecnico"  # Secretaría técnica
```

### ClaimStatus (Estados de Reclamo)
```python
class ClaimStatus(Enum):
    INVALID = "Inválido"
    PENDING = "Pendiente"
    IN_PROGRESS = "En proceso"
    RESOLVED = "Resuelto"
```

---

## Convenciones REST API

### Principios
1. **Sustantivos en plural**: `/claims`, `/supporters`, `/transfers`, `/notifications`
2. **Verbos HTTP correctos**:
   - `GET` - Obtener recursos
   - `POST` - Crear recursos
   - `PATCH` - Actualización parcial
   - `DELETE` - Eliminar recursos
3. **Sub-recursos anidados**: `/claims/<id>/supporters`, `/claims/<id>/transfers`
4. **Query parameters para variantes**: `/reports?format=pdf`
5. **Rutas especiales antes de parámetros**: `/claims/new` antes de `/claims/<id>`
6. **Recurso del usuario actual**: `/users/me/` para recursos propios

### Rutas de Autenticación (Nested Blueprints)
| Ruta | Endpoint | Descripción |
|------|----------|-------------|
| `/register` | `auth.end_user.register` | Registro usuario final |
| `/login` | `auth.end_user.login` | Login usuario final |
| `/logout` | `auth.end_user.logout` | Cerrar sesión |
| `/admin/login` | `auth.admin.login` | Login admin |
| `/admin/` | `auth.admin.dashboard` | Dashboard admin |

### Rutas Principales (Futuras)
| Prefijo | Módulo | Acceso |
|---------|--------|--------|
| `/claims` | Reclamos usuario | Usuario autenticado |
| `/users/me` | Recursos propios | Usuario autenticado |
| `/admin` | Panel admin | DEPARTMENT_HEAD, TECHNICAL_SECRETARY |

---

## Stack Tecnológico

### Base
- **Flask** + **Flask-SQLAlchemy** + **Flask-Login** + **Werkzeug**

### Machine Learning (Clasificación y Similitud)
- **scikit-learn**: TF-IDF Vectorizer + Naive Bayes para clasificación
- **scikit-learn**: Cosine Similarity para detección de reclamos similares
- **joblib**: Persistencia de modelos entrenados

### Visualización (Server-side)
- **matplotlib**: Gráficos circulares (pie charts)
- **wordcloud**: Nubes de palabras
- Salida: imágenes PNG codificadas en base64

### Generación de Reportes
- **WeasyPrint**: Conversión HTML → PDF

### Imágenes
- **Pillow**: Procesamiento de imágenes adjuntas

---

## Reglas de Negocio Críticas

### Permisos por Tipo de Usuario
| Acción | EndUser | AdminUser (HEAD) | AdminUser (SECRETARY) |
|--------|---------|------------------|----------------------|
| Crear reclamo | ✅ | ❌ | ❌ |
| Ver reclamos propios | ✅ | ✅ | ✅ |
| Adherirse a reclamo | ✅ | ❌ | ❌ |
| Cambiar estado | ❌ | ✅ (su depto) | ✅ (todos) |
| Derivar reclamo | ❌ | ❌ | ✅ |
| Ver analíticas | ❌ | ✅ (su depto) | ✅ (todos) |
| Generar reportes | ❌ | ✅ (su depto) | ✅ (todos) |

### Flujo de Creación de Reclamo
1. Usuario llena formulario con detalle
2. Sistema clasifica automáticamente (TF-IDF) → asigna departamento
3. Sistema busca reclamos similares en ese departamento
4. Si hay similares: ofrecer adhesión o crear nuevo
5. Si no hay similares: crear reclamo automáticamente
6. Creador se añade como primer adherente

### Adherentes
- El creador del reclamo es automáticamente el primer adherente
- Un usuario no puede adherirse dos veces al mismo reclamo
- Solo usuarios con rol `END_USER` pueden adherirse

### Derivación
- Solo `TECHNICAL_SECRETARY` puede derivar reclamos
- Se registra historial de derivaciones (ClaimTransfer)
- Se guarda motivo de derivación (opcional)

---

## Modelos de Datos

### Relaciones Principales
```
User (1) ──────> (0..1) Department     # Usuario puede pertenecer a un depto
Department (1) ──────> (*) Claim       # Depto tiene muchos reclamos  
User (1) ──────> (*) Claim             # Usuario crea muchos reclamos
User (*) <────> (*) Claim              # Muchos usuarios adhieren a muchos reclamos
                                       # (via ClaimSupporter)
Claim (1) ──────> (*) ClaimStatusHistory   # Historial de cambios de estado
Claim (1) ──────> (*) ClaimTransfer        # Historial de derivaciones
```

---

## Documentación de Referencia

Para detalles completos de implementación, consultar:
- `docs/IMPLEMENTATION_GUIDE.md` - Guía paso a paso con código de ejemplo