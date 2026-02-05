# Guía de Teoría - Programación Avanzada
## Explicación Simplificada con Ejemplos del TP de Reclamos

---

## UNIDAD 1: Programación Orientada a Objetos

### 1.1 Conceptos Fundamentales

#### ¿Qué es un OBJETO?
Un objeto tiene **estado** (sus datos), **comportamiento** (sus métodos) e **identidad** (es único).

**Ejemplo en el TP:**
```python
# En app/models/claim.py
claim = Claim(
    detail="Se rompió la puerta del aula 101",
    department_id=1,
    creator_id=5,
    image_path="uploads/puerta.jpg"
)
# Estado: detail, department_id, creator_id, image_path, status, created_at
# Comportamiento: supporters_count()
# Identidad: cada reclamo tiene su propio ID único
```

#### ¿Qué es una CLASE?
Una clase es el "molde" o "plantilla" para crear objetos con estructura y comportamiento similar.

**Ejemplo en el TP:**
```python
# app/models/claim.py
class Claim(db.Model):
    """Esta es la CLASE - el molde para todos los reclamos"""
    id: Mapped[int]
    detail: Mapped[str]
    status: Mapped[ClaimStatus]
    # ... más atributos
    
    def __init__(self, detail: str, department_id: int, creator_id: int, ...):
        # Constructor que crea la instancia
        self.detail = detail
        self.department_id = department_id
        # ...
    
    @property
    def supporters_count(self) -> int:
        """Método que retorna el número de adherentes"""
        return len(self.supporters)
```

#### INSTANCIA vs CLASE
- **Clase**: El concepto general (ej: "Reclamo")
- **Instancia**: Un objeto concreto creado de esa clase (ej: "Reclamo #42 sobre la puerta rota")

**Ejemplo en el TP:**
```python
# Claim es la CLASE
# claim1, claim2, claim3 son INSTANCIAS diferentes

claim1 = Claim(detail="Problema A", department_id=1, creator_id=1)
claim2 = Claim(detail="Problema B", department_id=2, creator_id=2)
# Cada uno tiene su propia identidad (diferente ID) aunque usen la misma clase
```

#### ATRIBUTOS: De Instancia vs De Clase

**Atributos de Instancia**: Cada objeto tiene su propia copia (usan `self`)
**Atributos de Clase**: Compartidos por todas las instancias (sin `self`, subrayados en UML)

**Ejemplo en el TP:**
```python
# app/models/user/base.py
class User(UserMixin, db.Model):
    __tablename__ = "user"  # ← Atributo de CLASE (compartido por todas las instancias)
    
    # Atributos de INSTANCIA (cada usuario tiene los suyos):
    id: Mapped[int]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    username: Mapped[str]
```

---

### 1.2 Relaciones entre Clases y Objetos

#### ASOCIACIÓN
Relación donde un objeto usa a otro, pero no lo "posee". Ambos pueden existir independientemente.

**Características:**
- El objeto asociado NO pertenece exclusivamente a la clase
- Puede pertenecer a múltiples objetos a la vez
- Su ciclo de vida NO está gestionado por el objeto que lo usa
- Puede o no conocer la existencia del objeto

**Ejemplo en el TP:**
```python
# app/models/claim_supporter.py
class ClaimSupporter(db.Model):
    """
    Asociación entre User y Claim
    - Un usuario puede apoyar muchos reclamos
    - Un reclamo puede tener muchos adherentes
    - Ambos existen independientemente
    """
    claim_id: Mapped[int]  # FK a Claim
    user_id: Mapped[int]   # FK a User
    
    claim: Mapped["Claim"] = relationship("Claim", back_populates="supporters")
    user: Mapped["EndUser"] = relationship("EndUser", back_populates="supported_claims")
```

En el diagrama UML, esto se ve como una relación N:M (muchos a muchos) entre User y Claim a través de ClaimSupporter.

#### AGREGACIÓN
"Tiene un" - La parte puede existir sin el todo. La parte puede pertenecer a varios objetos.

**Características:**
- La parte ES PARTE del objeto
- La parte puede pertenecer a más de un objeto a la vez
- La existencia de la parte NO está manejada por el objeto
- La parte no sabe sobre la existencia del objeto

**Ejemplo en el TP:**
```python
# app/models/user/admin_user.py
class AdminUser(User):
    """
    Un AdminUser tiene un Department (agregación)
    - El departamento existe independientemente del admin
    - Si eliminamos un admin, el departamento sigue existiendo
    - Múltiples admins pueden pertenecer al mismo departamento
    """
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("department.id"), nullable=True
    )
    department: Mapped["Department"] = relationship("Department", back_populates="admin_users")
```

En UML: `AdminUser "*" --> "0..1" Department : pertenece a` (rombo vacío)

#### COMPOSICIÓN
"Es parte de" - La parte NO puede existir sin el todo. Cuando se destruye el todo, se destruyen las partes.

**Características:**
- La parte ES PARTE del objeto
- La parte SOLO puede pertenecer a un objeto a la vez
- La existencia de la parte está MANEJADA por el objeto (cuando muere el padre, muere la parte)
- La parte no sabe sobre la existencia del objeto

**Ejemplo en el TP:**
```python
# app/models/claim.py
class Claim(db.Model):
    """
    Un Claim tiene ClaimStatusHistory (composición)
    - El historial de cambios NO existe sin el reclamo
    - Si eliminamos el reclamo, se elimina todo su historial
    - cascade="all, delete-orphan" implementa esto
    """
    status_history: Mapped[list["ClaimStatusHistory"]] = relationship(
        "ClaimStatusHistory", 
        back_populates="claim", 
        cascade="all, delete-orphan"  # ← Esto es COMPOSICIÓN
    )
    
    # También composición:
    supporters: Mapped[list["ClaimSupporter"]] = relationship(
        "ClaimSupporter", 
        back_populates="claim", 
        cascade="all, delete-orphan"
    )
    
    transfers: Mapped[list["ClaimTransfer"]] = relationship(
        "ClaimTransfer", 
        back_populates="claim", 
        cascade="all, delete-orphan"
    )
```

En UML: `Claim "1" *--> "*" ClaimStatusHistory` (rombo relleno)

#### HERENCIA
"Es un(a)" - Una clase hereda propiedades y comportamiento de otra clase más general.

**Ejemplo en el TP:**
```python
# app/models/user/base.py
class User(UserMixin, db.Model):
    """Clase BASE o SUPERCLASE o MADRE"""
    id: Mapped[int]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    username: Mapped[str]
    password_hash: Mapped[str]
    user_type: Mapped[str]  # Discriminador para Single Table Inheritance
    
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

# app/models/user/end_user.py
class EndUser(User):
    """Clase DERIVADA o HIJA - hereda de User"""
    cloister: Mapped[Cloister | None]
    created_claims: Mapped[list["Claim"]]
    supported_claims: Mapped[list["ClaimSupporter"]]
    
    __mapper_args__ = {"polymorphic_identity": "end_user"}
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

# app/models/user/admin_user.py
class AdminUser(User):
    """Otra clase HIJA - también hereda de User"""
    department_id: Mapped[int | None]
    admin_role: Mapped[AdminRole | None]
    department: Mapped["Department"]
    
    __mapper_args__ = {"polymorphic_identity": "admin_user"}
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name} [{self.admin_role.value}]"
```

**Ventajas de la herencia en este caso:**
- EndUser y AdminUser comparten código común (email, username, password)
- Cada uno puede tener sus propios atributos específicos
- Ambos pueden usar `set_password()` y `check_password()` heredados
- Cada uno puede redefinir `full_name` a su manera (polimorfismo)

En UML: `User <|-- EndUser` y `User <|-- AdminUser` (flecha con triángulo vacío)

#### DEPENDENCIA
Una clase usa temporalmente a otra para completar una tarea, pero no la almacena como atributo.

**Características:**
- Se da cuando un objeto requiere funcionalidades de otro para completar una tarea
- Los objetos NO están relacionados permanentemente
- NO forma parte de los miembros del objeto

**Ejemplo en el TP:**
```python
# app/services/claim_service.py
class ClaimService:
    """ClaimService DEPENDE de ClassifierService, pero no lo almacena"""
    
    @staticmethod
    def _classify_claim_department(detail: str) -> int | None:
        """Usa ClassifierService temporalmente"""
        try:
            # DEPENDENCIA: usa classifier_service solo para esta operación
            predicted = classifier_service.classify(detail)
            dept = DepartmentService.get_department_by_name(predicted)
            return dept.id if dept else None
        except Exception as e:
            print(f"Error en clasificación: {e}")
            return None
    
    # classifier_service NO es un atributo de ClaimService
    # Solo lo usa cuando lo necesita
```

Otro ejemplo:
```python
# app/routes/claims.py
@claims_bp.route("/create", methods=["GET", "POST"])
@end_user_required
def create():
    if request.method == "POST":
        # DEPENDE de request (Flask) para obtener datos
        detail = request.form.get("detail")
        
        # DEPENDE de ClaimService para crear el reclamo
        claim, error = ClaimService.create_claim(...)
        
        # request y ClaimService no son atributos de esta función
        # Solo se usan temporalmente
```

En UML: línea punteada con flecha `ClaimService ..> ClassifierService`

---

### 1.3 PROPERTY (Propiedades)

Las propiedades permiten acceder a "atributos calculados" como si fueran atributos normales, pero en realidad ejecutan un método.

**En UML se indica con:** `<<get>>` o `<<get/set>>` antes del atributo

**Ejemplo en el TP:**
```python
# app/models/claim.py
class Claim(db.Model):
    # ...
    
    @property  # ← Esto es un GETTER (solo lectura)
    def supporters_count(self) -> int:
        """Retorna el número de adherentes"""
        return len(self.supporters)

# Uso:
claim = Claim(...)
print(claim.supporters_count)  # Se usa como atributo, pero ejecuta un método
# NO necesitas hacer: claim.supporters_count()
```

**En UML se vería así:**
```
Claim
─────────────────
+id : int
+detail : str
+status : ClaimStatus
<<get>> +supporters_count : int  ← Indica que es una property
─────────────────
```

Otro ejemplo:
```python
# app/models/user/admin_user.py
class AdminUser(User):
    @property
    def is_department_head(self) -> bool:
        """Property de solo lectura"""
        return self.admin_role == AdminRole.DEPARTMENT_HEAD
    
    @property
    def is_technical_secretary(self) -> bool:
        """Property de solo lectura"""
        return self.admin_role == AdminRole.TECHNICAL_SECRETARY

# Uso:
admin = AdminUser(...)
if admin.is_department_head:  # Se usa como atributo
    print("Es jefe de departamento")
```

---

## UNIDAD 2: Análisis y Diseño Orientado a Objetos

### 2.1 Modelo de Objetos

El modelo de objetos permite trabajar en un nivel de abstracción más alto, más cercano a cómo pensamos en el mundo real.

**En tu TP:**
- En lugar de pensar en "tablas de base de datos", piensas en "Reclamos", "Usuarios", "Departamentos"
- Cada entidad tiene responsabilidades claras
- Las relaciones son naturales: "Un usuario CREA un reclamo", "Un reclamo PERTENECE a un departamento"

### 2.2 Elementos del Modelo de Objetos

#### ABSTRACCIÓN
Extraer las características esenciales de un objeto, ignorando los detalles irrelevantes para el problema.

**Ejemplo en el TP:**
```python
# app/models/claim.py
class Claim(db.Model):
    """
    ABSTRACCIÓN: Un reclamo en el mundo real tiene muchas características,
    pero solo modelamos las ESENCIALES para nuestro sistema:
    - El problema (detail)
    - Estado actual (status)
    - Quién lo creó (creator_id)
    - A qué departamento pertenece (department_id)
    - Cuándo se creó (created_at)
    
    NO incluimos: color del papel, si tiene café derramado, temperatura
    del salón donde se escribió, etc. (no son esenciales)
    """
    id: Mapped[int]
    detail: Mapped[str]
    status: Mapped[ClaimStatus]
    department_id: Mapped[int]
    creator_id: Mapped[int]
    created_at: Mapped[Datetime]
    updated_at: Mapped[Datetime]
    image_path: Mapped[str | None]
```

Otro ejemplo:
```python
# app/models/user/base.py
class User(UserMixin, db.Model):
    """
    ABSTRACCIÓN de un usuario del sistema
    Solo las características relevantes:
    - Identificación (id, username, email)
    - Nombre (first_name, last_name)
    - Seguridad (password_hash)
    
    NO incluimos: altura, color de ojos, comida favorita
    (no son relevantes para el sistema)
    """
```

#### ENCAPSULAMIENTO
Ocultar los detalles de implementación y exponer solo lo necesario a través de una interfaz.

**Ejemplo en el TP:**
```python
# app/models/user/base.py
class User(UserMixin, db.Model):
    password_hash: Mapped[str]  # ← PRIVADO/ENCAPSULADO (no se accede directamente)
    
    # Interfaz pública para trabajar con la contraseña:
    def set_password(self, password: str):
        """El usuario NO sabe cómo se hashea, solo llama a este método"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """El usuario NO sabe cómo se verifica, solo llama a este método"""
        return check_password_hash(self.password_hash, password)

# Uso correcto (usando la interfaz):
user = User(...)
user.set_password("mi_contraseña_secreta")  # ✓ Encapsulado
if user.check_password("mi_contraseña_secreta"):  # ✓ Encapsulado
    print("Contraseña correcta")

# Uso incorrecto (rompiendo el encapsulamiento):
# user.password_hash = "contraseña_en_texto_plano"  # ✗ NO HACER
```

Otro ejemplo:
```python
# app/services/claim_service.py
class ClaimService:
    @staticmethod
    def _classify_claim_department(detail: str) -> int | None:
        """
        Método PRIVADO (prefijo _) - ENCAPSULADO
        Los usuarios del servicio NO deben llamar esto directamente
        """
        try:
            predicted = classifier_service.classify(detail)
            dept = DepartmentService.get_department_by_name(predicted)
            return dept.id if dept else None
        except Exception:
            return None
    
    @staticmethod
    def create_claim(user_id: int, detail: str, ...) -> tuple[Claim | None, str | None]:
        """
        Método PÚBLICO - Interfaz del servicio
        Internamente usa _classify_claim_department, pero el usuario no lo sabe
        """
        # ... lógica que usa _classify_claim_department ...
        pass
```

#### MODULARIDAD
Dividir el sistema en módulos independientes, cohesivos y débilmente acoplados.

**Ejemplo en el TP:**
```
app/
├── models/              # MÓDULO: Modelos de datos
│   ├── user/           # Sub-módulo: Usuarios
│   ├── claim.py
│   └── department.py
├── services/            # MÓDULO: Lógica de negocio
│   ├── claim_service.py
│   ├── user_service.py
│   └── classifier_service.py
├── routes/              # MÓDULO: Rutas/Controladores
│   ├── claims.py
│   ├── users.py
│   └── admin.py
└── utils/               # MÓDULO: Utilidades
    ├── decorators.py
    └── constants.py
```

**Beneficios en tu TP:**
- Puedes cambiar `classifier_service.py` sin afectar `claim_service.py` (bajo acoplamiento)
- Cada servicio tiene UNA responsabilidad clara (alta cohesión)
- Si encuentras un bug en los reclamos, sabes que está en `models/claim.py` o `services/claim_service.py`

```python
# app/services/claim_service.py - MÓDULO COHESIVO
class ClaimService:
    """
    TODO sobre reclamos en UN solo lugar
    - Crear reclamos
    - Obtener reclamos
    - Actualizar estados
    - Adherir usuarios
    """
    
    @staticmethod
    def create_claim(...): pass
    
    @staticmethod
    def get_claim_by_id(...): pass
    
    @staticmethod
    def update_claim_status(...): pass
    
    @staticmethod
    def add_supporter(...): pass

# app/services/user_service.py - OTRO MÓDULO COHESIVO
class UserService:
    """
    TODO sobre usuarios en OTRO lugar
    Bajo acoplamiento con ClaimService
    """
    
    @staticmethod
    def create_end_user(...): pass
    
    @staticmethod
    def create_admin_user(...): pass
```

#### JERARQUÍA

**Jerarquía de clases (Herencia):**
Ya la vimos en la Unidad 1 con `User` → `EndUser` y `AdminUser`

**Jerarquía de partes (Composición):**
Un objeto está formado por instancias de otros objetos.

**Ejemplo en el TP:**
```python
# app/models/claim.py
class Claim(db.Model):
    """
    Un Claim está COMPUESTO por:
    - Un Department (jerarquía de partes)
    - Un User creador (jerarquía de partes)
    - Lista de ClaimStatusHistory (jerarquía de partes)
    - Lista de ClaimSupporter (jerarquía de partes)
    - Lista de ClaimTransfer (jerarquía de partes)
    """
    department: Mapped["Department"]
    creator: Mapped["EndUser"]
    status_history: Mapped[list["ClaimStatusHistory"]]
    supporters: Mapped[list["ClaimSupporter"]]
    transfers: Mapped[list["ClaimTransfer"]]
```

Visualmente:
```
         Claim
          / | \
         /  |  \
        /   |   \
  Department User ClaimStatusHistory[]
                  ClaimSupporter[]
                  ClaimTransfer[]
```

### 2.3 Elementos Secundarios

#### TIPIFICACIÓN
Los tipos aseguran que los objetos de tipos distintos no se intercambien incorrectamente.

**Ejemplo en el TP:**
```python
# app/models/claim.py
from enum import Enum

class ClaimStatus(Enum):
    """Tipo enumerado - solo puede ser uno de estos valores"""
    INVALID = "Inválido"
    PENDING = "Pendiente"
    IN_PROGRESS = "En proceso"
    RESOLVED = "Resuelto"

class Claim(db.Model):
    status: Mapped[ClaimStatus]  # ← TIPIFICACIÓN: solo puede ser ClaimStatus
    
    # Esto es VÁLIDO:
    # claim.status = ClaimStatus.PENDING
    
    # Esto causaría ERROR:
    # claim.status = "Pendiente"  # String no es ClaimStatus
    # claim.status = 42  # Int no es ClaimStatus

# Otro ejemplo con type hints:
def update_claim_status(
    claim_id: int,  # ← TIPIFICACIÓN: debe ser int
    new_status: ClaimStatus,  # ← TIPIFICACIÓN: debe ser ClaimStatus
    changed_by_id: int  # ← TIPIFICACIÓN: debe ser int
) -> tuple[Claim | None, str | None]:  # ← TIPIFICACIÓN del retorno
    """Type hints indican qué tipo se espera"""
    pass
```

Más ejemplos:
```python
# app/models/user/end_user.py
class Cloister(Enum):
    """Tipificación de claustros"""
    STUDENT = "estudiante"
    TEACHER = "docente"
    PAYS = "PAyS"

class EndUser(User):
    cloister: Mapped[Cloister | None]  # ← Solo puede ser Cloister o None

# app/models/user/admin_user.py
class AdminRole(Enum):
    """Tipificación de roles"""
    DEPARTMENT_HEAD = "jefe_departamento"
    TECHNICAL_SECRETARY = "secretario_tecnico"

class AdminUser(User):
    admin_role: Mapped[AdminRole | None]  # ← Solo puede ser AdminRole o None
```

#### PERSISTENCIA
Un objeto persiste si su existencia continúa después de que su creador deja de existir.

**Ejemplo en el TP:**
```python
# app/services/claim_service.py
class ClaimService:
    @staticmethod
    def create_claim(user_id: int, detail: str, ...) -> tuple[Claim | None, str | None]:
        # Crear el objeto en memoria:
        claim = Claim(
            detail=detail.strip(),
            department_id=resolved_department_id,
            creator_id=user_id,
            image_path=image_path,
        )
        
        # PERSISTENCIA: guardar en base de datos
        db.session.add(claim)
        db.session.commit()  # ← Ahora persiste incluso si el programa se cierra
        
        return claim, None

# Sin persistencia:
# claim = Claim(...)  # Solo en memoria
# Si el programa se cierra, se pierde

# Con persistencia:
# db.session.add(claim)
# db.session.commit()  # Guardado en disco/base de datos
# Aunque el programa se cierre, el reclamo sigue existiendo
```

Otro ejemplo:
```python
# seed_db.py
def create_departments():
    """Crea departamentos que PERSISTEN en la base de datos"""
    
    mant = Department(
        name="mantenimiento",
        display_name="Mantenimiento",
    )
    
    infra = Department(
        name="infraestructura",
        display_name="Infraestructura",
    )
    
    st = Department(
        name="secretaria_tecnica",
        display_name="Secretaría Técnica",
        is_technical_secretariat=True,
    )
    
    # PERSISTENCIA:
    db.session.add_all([mant, infra, st])
    db.session.commit()
    
    # Estos departamentos existen ahora permanentemente
    # Puedes cerrar Python, reiniciar el servidor, y siguen ahí
```

---

### 2.4 Metodología CRC (Class-Responsibility-Collaboration)

CRC ayuda a diseñar clases identificando sus **Responsabilidades** y **Colaboradores**.

**Ejemplo: Tarjeta CRC para Claim**

```
┌─────────────────────────────────────────────────┐
│ Clase: Claim                                    │
├─────────────────────────────────────────────────┤
│ Responsabilidades:          │ Colaboradores:    │
│                            │                   │
│ - Almacenar detalle        │ - Department      │
│   del problema             │ - EndUser         │
│ - Conocer su estado actual │ - ClaimStatus     │
│ - Saber a qué departamento │ - ClaimSupporter  │
│   pertenece                │ - ClaimStatus     │
│ - Contar adherentes        │   History         │
│ - Registrar cambios de     │                   │
│   estado                   │                   │
└─────────────────────────────────────────────────┘
```

**Ejemplo: Tarjeta CRC para ClaimService**

```
┌─────────────────────────────────────────────────┐
│ Clase: ClaimService                             │
├─────────────────────────────────────────────────┤
│ Responsabilidades:          │ Colaboradores:    │
│                            │                   │
│ - Crear nuevos reclamos    │ - Claim           │
│ - Clasificar reclamos      │ - Department      │
│   automáticamente          │ - Classifier      │
│ - Actualizar estados       │   Service         │
│ - Gestionar adherentes     │ - ClaimStatus     │
│ - Validar reglas de        │   History         │
│   negocio                  │ - Notification    │
│                            │   Service         │
└─────────────────────────────────────────────────┘
```

**Escenario de uso: "Usuario crea un reclamo"**

1. **Usuario** → proporciona detail
2. **ClaimService** → recibe la solicitud
3. **ClaimService** → colabora con **ClassifierService** para clasificar
4. **ClassifierService** → retorna department_id
5. **ClaimService** → crea instancia de **Claim**
6. **Claim** → se asocia con **Department** y **User**
7. **ClaimService** → persiste en **Database**

**Código real del escenario:**
```python
# routes/claims.py
@claims_bp.route("/create", methods=["POST"])
@end_user_required
def create():
    detail = request.form.get("detail")
    
    # Paso 2: ClaimService recibe la solicitud
    claim, error = ClaimService.create_claim(
        user_id=current_user.id,
        detail=detail,
        department_id=None,
        image_path=image_path
    )

# services/claim_service.py
class ClaimService:
    @staticmethod
    def create_claim(...):
        # Paso 3-4: Colabora con ClassifierService
        resolved_department_id, error = ClaimService._resolve_department_id(
            detail, department_id
        )
        
        # Paso 5-6: Crea la instancia de Claim
        claim = Claim(
            detail=detail.strip(),
            department_id=resolved_department_id,
            creator_id=user_id,
            image_path=image_path,
        )
        
        # Paso 7: Persiste
        db.session.add(claim)
        db.session.commit()
```

---

### 2.5 Metodología UML

Tu proyecto incluye un diagrama de clases UML en `docs/class.puml`.

**Elementos clave en tu diagrama:**

```plantuml
' HERENCIA
User <|-- EndUser
User <|-- AdminUser

' COMPOSICIÓN (rombo relleno)
Claim "1" *--> "*" ClaimStatusHistory
Claim "1" *--> "*" ClaimSupporter
Claim "1" *--> "*" ClaimTransfer

' AGREGACIÓN/ASOCIACIÓN (rombo vacío)
AdminUser "*" --> "0..1" Department
Department "1" --> "*" Claim

' DEPENDENCIA (línea punteada)
EndUser ..> Cloister
AdminUser ..> AdminRole
Claim ..> ClaimStatus
```

---

## UNIDAD 3: Pruebas Unitarias

### 3.1 ¿Qué son las Pruebas Unitarias?

Una prueba unitaria verifica un **pequeño fragmento** de código de forma **automática**, **rápida** y **aislada**.

**Ejemplo en el TP:**
```python
# tests/test_claim_service.py
import unittest
from tests.conftest import BaseTestCase

class TestClaimService(BaseTestCase):
    """Tests para el servicio de reclamos"""
    
    def setUp(self):
        """Configuración antes de cada test"""
        super().setUp()
        # Crear usuario de prueba
        user = EndUser(
            first_name="Test",
            last_name="User",
            email="testuser@test.com",
            username="testuser",
            cloister=Cloister.STUDENT,
        )
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()
        self.sample_user_id = user.id
    
    def test_create_claim_with_specific_department(self):
        """
        Prueba unitaria que verifica que create_claim funciona correctamente
        SUT (System Under Test): ClaimService.create_claim
        """
        # ARRANGE (Arreglar): Preparar datos de prueba
        detail = "Se rompió la ventana del aula 102"
        dept_id = self.sample_departments["dept1_id"]
        
        # ACT (Actuar): Ejecutar el código a probar
        claim, error = ClaimService.create_claim(
            user_id=self.sample_user_id,
            detail=detail,
            department_id=dept_id
        )
        
        # ASSERT (Aseverar): Verificar resultados con unittest
        self.assertIsNotNone(claim, "Debería crear el reclamo")
        self.assertIsNone(error, "No debería haber error")
        self.assertEqual(claim.detail, detail, "El detalle debe coincidir")
        self.assertEqual(claim.status, ClaimStatus.PENDING)
        self.assertEqual(claim.creator_id, self.sample_user_id)
```

**Características de unittest:**
- Clase base: `unittest.TestCase`
- Métodos especiales: `setUp()` (antes de cada test), `tearDown()` (después de cada test)
- Assertions: `assertEqual()`, `assertIsNone()`, `assertTrue()`, `assertIn()`, etc.
- Herencia: `BaseTestCase` hereda de `unittest.TestCase` para configuración común

### 3.2 Patrón AAA (Arrange-Act-Assert)

**Ejemplo más detallado del TP:**
```python
# tests/test_supporters.py
import unittest
from tests.conftest import BaseTestCase

class TestSupporters(BaseTestCase):
    """Tests para funcionalidad de adherentes"""
    
    def setUp(self):
        super().setUp()
        # Crear usuario inicial
        self.user = EndUser(
            first_name="Test",
            last_name="User",
            email="test@test.com",
            username="testuser",
            cloister=Cloister.STUDENT
        )
        self.user.set_password("password")
        db.session.add(self.user)
        db.session.commit()
    
    def test_add_supporter_to_claim(self):
        # ========== ARRANGE ==========
        # Crear el reclamo inicial
        claim, _ = ClaimService.create_claim(
            user_id=self.user.id,
            detail="Problema de prueba",
            department_id=self.sample_departments["dept1_id"]
        )
        
        # Crear otro usuario que será el adherente
        supporter = EndUser(
            first_name="María",
            last_name="García",
            email="maria@example.com",
            username="maria",
            cloister=Cloister.STUDENT
        )
        supporter.set_password("password")
        db.session.add(supporter)
        db.session.commit()
        
        # ========== ACT ==========
        # Ejecutar la acción a probar
        result, error = ClaimService.add_supporter(claim.id, supporter.id)
        
        # ========== ASSERT ==========
        # Verificar que funcionó correctamente con unittest
        self.assertTrue(result, "Debería adherir correctamente")
        self.assertIsNone(error, "No debería haber error")
        self.assertEqual(claim.supporters_count, 1, "Debería tener 1 adherente")
        
        # Verificar que no se puede adherir dos veces
        result2, error2 = ClaimService.add_supporter(claim.id, supporter.id)
        self.assertFalse(result2, "No debería adherir dos veces")
        self.assertIsNotNone(error2, "Debería haber error")
```

### 3.3 Cobertura de Código

**Ejemplo de ejecución en tu TP:**
```bash
# Ejecutar pruebas con cobertura usando unittest:
coverage run -m unittest discover tests/

# Ver reporte:
coverage report -m

# Resultado (ejemplo):
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
app/services/claim_service.py      150     10    93%   45-48, 102
app/services/user_service.py        80      5    94%   67-70
app/models/claim.py                 50      0   100%
---------------------------------------------------------------
TOTAL                              1200     50    96%
```

**Interpretación:**
- `claim_service.py`: 93% de cobertura, líneas 45-48 y 102 no probadas
- `user_service.py`: 94% de cobertura
- `claim.py`: 100% de cobertura (todas las líneas ejecutadas en las pruebas)

### 3.4 Clase Base BaseTestCase

**Ubicación:** `tests/conftest.py`

```python
import unittest

class BaseTestCase(unittest.TestCase):
    """Clase base para todos los tests con configuración común"""
    
    def setUp(self):
        """Crea una instancia de la aplicación para tests con base de datos limpia"""
        from app.extensions import db
        
        self.app = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()
        self._create_sample_departments()
    
    def tearDown(self):
        """Limpia la base de datos después de cada test"""
        from app.extensions import db
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
```

**Ventajas de BaseTestCase:**
- Configuración común para todos los tests
- Base de datos en memoria (SQLite) para cada test
- Limpieza automática después de cada test
- Herencia para reutilización de código

---

## UNIDAD 4: Polimorfismo y SOLID

### 4.1 POLIMORFISMO

El mismo mensaje a objetos diferentes produce respuestas diferentes.

**Ejemplo en el TP:**
```python
# app/models/user/base.py
class User(UserMixin, db.Model):
    @property
    def full_name(self) -> str:
        return ""  # Implementación base vacía

# app/models/user/end_user.py
class EndUser(User):
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

# app/models/user/admin_user.py
class AdminUser(User):
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name} [{self.admin_role.value}]"

# USO - POLIMORFISMO en acción:
users: list[User] = [
    EndUser(first_name="Juan", last_name="Pérez", ...),
    AdminUser(first_name="Ana", last_name="López", admin_role=AdminRole.DEPARTMENT_HEAD, ...)
]

for user in users:
    print(user.full_name)  # ← Mismo mensaje, diferentes respuestas
    # EndUser imprime: "Juan Pérez"
    # AdminUser imprime: "Ana López [jefe_departamento]"
```

### 4.2 Duck Typing

"Si camina como pato y hace cuac como pato, es un pato"

**Ejemplo en el TP:**
```python
# app/utils/decorators.py
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Duck typing: no preguntamos type(current_user) == AdminUser
        # Solo verificamos si "actúa" como AdminUser
        if not isinstance(current_user, AdminUser):
            flash("Acceso denegado. Solo para administradores.", "error")
            return redirect(url_for("main.index"))
        
        return f(*args, **kwargs)
    return decorated_function

# Otro ejemplo - Duck typing con protocolos:
def process_claim_status_change(claim, new_status):
    """
    Acepta cualquier objeto que tenga los atributos necesarios
    No verifica el tipo explícitamente
    """
    # Si claim tiene .status y .id, funciona (duck typing)
    old_status = claim.status
    claim.status = new_status
    claim.updated_at = datetime.now()
    # ...
```

### 4.3 Principios SOLID

#### S - Single Responsibility Principle
Una clase debe tener UNA sola razón para cambiar.

**✓ Buen ejemplo en el TP:**
```python
# app/services/claim_service.py
class ClaimService:
    """
    UNA responsabilidad: Gestionar reclamos
    Solo cambia si cambian las reglas de negocio de reclamos
    """
    @staticmethod
    def create_claim(...): pass
    
    @staticmethod
    def update_claim_status(...): pass
    
    @staticmethod
    def get_claim_by_id(...): pass

# app/services/notification_service.py
class NotificationService:
    """
    OTRA responsabilidad: Gestionar notificaciones
    Solo cambia si cambian las reglas de notificaciones
    """
    @staticmethod
    def create_notification(...): pass
    
    @staticmethod
    def get_user_notifications(...): pass

# Están SEPARADAS - alta cohesión, bajo acoplamiento
```

**✗ Mal ejemplo (violación):**
```python
# ¡NO HACER! - Clase con múltiples responsabilidades
class ClaimManager:
    def create_claim(self): pass  # Gestiona reclamos
    def send_email(self): pass  # Gestiona emails
    def generate_pdf(self): pass  # Genera PDFs
    def classify_text(self): pass  # Clasifica textos
    # ← Demasiadas responsabilidades, muchas razones para cambiar
```

#### O - Open/Closed Principle
Abierto para extensión, cerrado para modificación.

**Ejemplo en el TP:**
```python
# app/models/user/base.py
class User(UserMixin, db.Model):
    """Clase base - CERRADA para modificación"""
    # Estos métodos NO se modifican
    def set_password(self, password: str): ...
    def check_password(self, password: str) -> bool: ...

# ABIERTA para extensión - agregamos nuevos tipos de usuario:

# app/models/user/end_user.py
class EndUser(User):
    """EXTENSIÓN sin modificar User"""
    cloister: Mapped[Cloister | None]

# app/models/user/admin_user.py
class AdminUser(User):
    """OTRA EXTENSIÓN sin modificar User"""
    admin_role: Mapped[AdminRole | None]

# Si necesitamos un nuevo tipo de usuario en el futuro:
class ModeratorUser(User):
    """NUEVA EXTENSIÓN - no modificamos User ni EndUser ni AdminUser"""
    moderation_level: Mapped[int]
```

#### L - Liskov Substitution Principle
Los subtipos deben ser sustituibles por sus tipos base.

**Ejemplo en el TP:**
```python
# app/routes/users.py
@users_bp.route("/profile")
@login_required
def profile():
    # current_user puede ser EndUser o AdminUser
    # Ambos son sustituibles por User
    # Todos tienen .full_name, .email, .username
    return render_template(
        "users/profile.html",
        user=current_user,  # ← Puede ser cualquier subtipo de User
        full_name=current_user.full_name,  # ← Polimorfismo
        email=current_user.email
    )

# Funciona con EndUser:
end_user = EndUser(...)
print(end_user.full_name)  # "Juan Pérez"

# Funciona con AdminUser:
admin_user = AdminUser(...)
print(admin_user.full_name)  # "Ana López [jefe_departamento]"

# Ambos son SUSTITUIBLES - no rompen el comportamiento esperado
```

#### I - Interface Segregation Principle
No depender de interfaces que no se usan.

**Ejemplo en el TP:**
```python
# En lugar de una interfaz grande:
# ✗ MAL:
class SuperUserInterface:
    def create_claim(self): pass
    def approve_claim(self): pass
    def transfer_claim(self): pass
    def generate_reports(self): pass
    def manage_users(self): pass
    # ← EndUser no necesita approve, transfer, reports, manage_users

# ✓ BIEN - Interfaces segregadas:

# app/models/user/end_user.py
class EndUser(User):
    """Solo tiene lo que necesita un usuario final"""
    created_claims: Mapped[list["Claim"]]
    supported_claims: Mapped[list["ClaimSupporter"]]
    # NO tiene métodos de administración

# app/models/user/admin_user.py
class AdminUser(User):
    """Solo tiene lo que necesita un administrador"""
    department_id: Mapped[int | None]
    admin_role: Mapped[AdminRole | None]
    
    @property
    def is_department_head(self) -> bool: ...
    
    @property
    def is_technical_secretary(self) -> bool: ...
    # NO tiene supported_claims (no adhieren a reclamos)
```

#### D - Dependency Inversion Principle
Depender de abstracciones, no de implementaciones concretas.

**Ejemplo en el TP:**
```python
# app/services/claim_service.py
class ClaimService:
    @staticmethod
    def create_claim(...):
        # DEPENDE de la abstracción (interfaz) de db, no de una implementación concreta
        db.session.add(claim)  # ← db podría ser SQLite, PostgreSQL, MySQL
        db.session.commit()    # ← No nos importa la implementación
        
        # DEPENDE de la abstracción de ClassifierService
        # No sabe si usa TF-IDF, redes neuronales, o reglas simples
        predicted = classifier_service.classify(detail)

# Si cambiamos la base de datos de SQLite a PostgreSQL,
# ClaimService NO cambia (depende de la abstracción db.Model)

# Si cambiamos el algoritmo de clasificación de TF-IDF a BERT,
# ClaimService NO cambia (depende de la interfaz classifier_service.classify())
```

---

## UNIDAD 5: Manejo de Excepciones

### 5.1 Tipos de Errores

**Errores de Sintaxis:**
```python
# Esto no ejecuta:
if x == 5
    print("cinco")  # ✗ Falta :
```

**Excepciones (errores en tiempo de ejecución):**
```python
# Esto ejecuta pero puede fallar:
def dividir(a, b):
    return a / b  # ✗ ZeroDivisionError si b=0
```

### 5.2 Gestión de Excepciones en el TP

**Ejemplo básico:**
```python
# app/services/claim_service.py
class ClaimService:
    @staticmethod
    def _classify_claim_department(detail: str) -> int | None:
        try:
            # INTENTAR clasificar
            predicted = classifier_service.classify(detail)
            dept = DepartmentService.get_department_by_name(predicted)
            return dept.id if dept else None
        
        except Exception as e:
            # CAPTURAR cualquier error
            print(f"Error en clasificación: {e}")
            return None  # Retornar valor por defecto
```

**Ejemplo con múltiples excepciones:**
```python
# app/services/claim_service.py
@staticmethod
def add_supporter(claim_id: int, user_id: int) -> tuple[bool, str | None]:
    try:
        # Verificar que el reclamo existe
        claim = db.session.get(Claim, claim_id)
        if not claim:
            return False, "Reclamo no encontrado"
        
        # Crear adherente
        supporter = ClaimSupporter(claim_id=claim_id, user_id=user_id)
        db.session.add(supporter)
        db.session.commit()
        return True, None
    
    except IntegrityError:
        # Error de integridad (ej: usuario ya adherido)
        db.session.rollback()
        return False, "Ya adheriste a este reclamo"
    
    except Exception as e:
        # Cualquier otro error
        db.session.rollback()
        return False, f"Error inesperado: {str(e)}"
```

**Ejemplo con finally:**
```python
# app/services/image_service.py
class ImageService:
    @staticmethod
    def save_image(file) -> tuple[str | None, str | None]:
        temp_path = None
        try:
            # Guardar archivo temporal
            temp_path = os.path.join(UPLOAD_FOLDER, "temp_" + filename)
            file.save(temp_path)
            
            # Procesar imagen
            img = Image.open(temp_path)
            img = img.resize((800, 600))
            
            # Guardar final
            final_path = os.path.join(UPLOAD_FOLDER, filename)
            img.save(final_path)
            
            return final_path, None
        
        except Exception as e:
            return None, f"Error al guardar imagen: {str(e)}"
        
        finally:
            # SIEMPRE ejecutar limpieza
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)  # Eliminar archivo temporal
```

### 5.3 Lanzamiento de Excepciones

**Ejemplo en el TP:**
```python
# app/services/classifier_service.py
class ClassifierService:
    def classify(self, text: str) -> str:
        if not text or not text.strip():
            raise ValueError("El texto no puede estar vacío")  # ← RAISE
        
        if not self.is_trained:
            raise ValueError("El modelo no está entrenado")  # ← RAISE
        
        X = self.vectorizer.transform([text])
        prediction = self.classifier.predict(X)[0]
        return prediction

# Uso:
try:
    department = classifier_service.classify("")  # ← Texto vacío
except ValueError as e:
    print(f"Error: {e}")  # "El texto no puede estar vacío"
```

### 5.4 Garantías de Seguridad

**Garantía Básica:**
Si hay error, el sistema queda en un estado válido (aunque pueden perderse datos).

**Ejemplo en el TP:**
```python
# app/services/claim_service.py
@staticmethod
def update_claim_status(...) -> tuple[Claim | None, str | None]:
    try:
        claim = db.session.get(Claim, claim_id)
        claim.status = new_status
        claim.updated_at = Datetime.now()
        
        # Crear historial
        history = ClaimStatusHistory(...)
        db.session.add(history)
        
        db.session.commit()  # Si falla, rollback automático
        return claim, None
    
    except Exception as e:
        db.session.rollback()  # ← GARANTÍA BÁSICA: estado válido
        return None, f"Error: {e}"
        # El sistema sigue funcionando, no se corrompió nada
```

**Garantía Fuerte:**
O completa con éxito O deja todo como estaba.

**Ejemplo en el TP:**
```python
# app/services/transfer_service.py
@staticmethod
def transfer_claim(...) -> tuple[bool, str | None]:
    # Estado inicial guardado
    old_department_id = claim.department_id
    
    try:
        # Cambiar departamento
        claim.department_id = to_department_id
        
        # Crear registro de transferencia
        transfer = ClaimTransfer(...)
        db.session.add(transfer)
        
        # Crear historial
        history = ClaimStatusHistory(...)
        db.session.add(history)
        
        db.session.commit()  # ← TODO o NADA
        return True, None
    
    except Exception as e:
        db.session.rollback()  # ← Vuelve al estado inicial
        # claim.department_id sigue siendo old_department_id
        return False, f"Error: {e}"
```

---

## UNIDAD 6: Biblioteca Estándar y Módulos

### 6.1 Uso de Módulos Estándar

**Ejemplo en el TP:**
```python
# Módulo os (sistema operativo)
import os

# app/services/image_service.py
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Módulo datetime
from datetime import datetime as Datetime

# app/models/claim.py
created_at: Mapped[Datetime] = mapped_column(default=Datetime.now)

# Módulo enum
from enum import Enum

class ClaimStatus(Enum):
    INVALID = "Inválido"
    PENDING = "Pendiente"
```

### 6.2 Módulos de PyPI (Python Package Index)

**Ejemplo en el TP:**
```python
# requirements.txt - Módulos instalados desde PyPI
Flask==3.1.0              # Framework web
Flask-Login==0.6.3        # Autenticación
Flask-SQLAlchemy==3.1.1   # ORM
scikit-learn==1.5.2       # Machine Learning
pytest==8.3.4             # Testing
Pillow==11.0.0            # Procesamiento de imágenes

# Uso en el código:
from flask import Flask, request, render_template  # PyPI
from flask_login import login_required, current_user  # PyPI
from sklearn.feature_extraction.text import TfidfVectorizer  # PyPI
from PIL import Image  # PyPI (Pillow)
```

---

## UNIDAD 7: Protocolo de Iteradores en Python

### 7.1 ¿Qué es el Protocolo de Iteradores?

El protocolo de iteradores en Python permite recorrer elementos de una colección secuencialmente sin exponer su estructura interna. Se basa en dos métodos:
- `__iter__()`: Retorna el iterador (debe retornar `self` o un objeto iterador)
- `__next__()`: Retorna el siguiente elemento, o lanza `StopIteration` cuando no hay más

**Ejemplo conceptual:**
```python
class MiIterador:
    def __init__(self, datos):
        self.datos = datos
        self.indice = 0
    
    def __iter__(self):
        """Retorna el iterador (self)"""
        return self
    
    def __next__(self):
        """Retorna el siguiente elemento"""
        if self.indice < len(self.datos):
            resultado = self.datos[self.indice]
            self.indice += 1
            return resultado
        else:
            raise StopIteration  # No hay más elementos

# Uso:
mi_iter = MiIterador([1, 2, 3, 4, 5])
for numero in mi_iter:
    print(numero)  # Imprime 1, 2, 3, 4, 5
```

**¿Cómo funciona el for loop internamente?**
```python
# Este código:
for item in coleccion:
    print(item)

# Es equivalente a:
iterador = iter(coleccion)  # Llama a coleccion.__iter__()
while True:
    try:
        item = next(iterador)  # Llama a iterador.__next__()
        print(item)
    except StopIteration:
        break  # Termina el loop
```

### 7.2 Ejemplo Aplicado al TP - Iterador de Reclamos por Estado

**Escenario:** Queremos iterar solo sobre los reclamos de un estado específico sin cargar todos en memoria.

```python
# app/iterators/claim_iterator.py (ejemplo hipotético aplicable)
class ClaimsByStatusIterator:
    """
    Iterador que recorre reclamos de un estado específico de forma lazy
    (uno a la vez, sin cargar todos en memoria)
    """
    def __init__(self, status: ClaimStatus):
        self.status = status
        self.query = Claim.query.filter_by(status=status)
        self.offset = 0
        self.batch_size = 10  # Cargar de a 10 reclamos
        self.current_batch = []
        self.batch_index = 0
    
    def __iter__(self):
        """Retorna el iterador"""
        return self
    
    def __next__(self) -> Claim:
        """Retorna el siguiente reclamo"""
        # Si ya recorrimos el batch actual, cargar el siguiente
        if self.batch_index >= len(self.current_batch):
            self.current_batch = (
                self.query
                .offset(self.offset)
                .limit(self.batch_size)
                .all()
            )
            self.offset += self.batch_size
            self.batch_index = 0
            
            # Si no hay más reclamos, terminar
            if not self.current_batch:
                raise StopIteration
        
        # Retornar el siguiente reclamo del batch
        claim = self.current_batch[self.batch_index]
        self.batch_index += 1
        return claim

# Uso:
pending_claims = ClaimsByStatusIterator(ClaimStatus.PENDING)
for claim in pending_claims:
    print(f"Reclamo #{claim.id}: {claim.detail}")
    # Procesa de a 10, eficiente en memoria
```

### 7.3 Generadores con yield (Alternativa más simple)

Los generadores son una forma más simple de crear iteradores usando `yield`:

```python
# app/services/claim_service.py (ejemplo hipotético)
class ClaimService:
    @staticmethod
    def iter_claims_by_department(department_id: int):
        """
        Generador que itera sobre reclamos de un departamento
        yield convierte automáticamente la función en un iterador
        """
        offset = 0
        batch_size = 50
        
        while True:
            # Cargar batch de reclamos
            claims = (
                Claim.query
                .filter_by(department_id=department_id)
                .offset(offset)
                .limit(batch_size)
                .all()
            )
            
            # Si no hay más, terminar
            if not claims:
                break
            
            # Yield cada reclamo (hace la función un generador)
            for claim in claims:
                yield claim
            
            offset += batch_size

# Uso:
for claim in ClaimService.iter_claims_by_department(department_id=1):
    print(claim.detail)
    # Eficiente: solo carga 50 reclamos a la vez en memoria
```

**Ventajas de los iteradores:**
- **Eficiencia en memoria:** No cargan todos los datos a la vez
- **Lazy evaluation:** Solo calculan valores cuando se necesitan
- **Soporte for loop:** Funcionan directamente con `for`
- **Composición:** Se pueden encadenar iteradores

### 7.4 Objetos Iterables en tu TP

**Ubicación:** Relaciones en modelos

```python
# app/models/claim.py
class Claim(db.Model):
    # Estas relaciones son ITERABLES (tienen __iter__)
    supporters: Mapped[list["ClaimSupporter"]] = relationship(
        "ClaimSupporter", back_populates="claim"
    )
    status_history: Mapped[list["ClaimStatusHistory"]] = relationship(
        "ClaimStatusHistory", back_populates="claim"
    )

# Uso - Se pueden iterar directamente:
claim = Claim.query.get(1)

# Iterar sobre adherentes:
for supporter in claim.supporters:  # ← claim.supporters es iterable
    print(supporter.user.full_name)

# Iterar sobre historial:
for history in claim.status_history:  # ← Implementa __iter__
    print(f"{history.changed_at}: {history.old_status} → {history.new_status}")
```

**Comprehensions (usan el protocolo de iteración):**
```python
# app/services/analytics_service.py
class AnalyticsService:
    @staticmethod
    def get_claims_summary(department_id: int):
        claims = Claim.query.filter_by(department_id=department_id).all()
        
        # List comprehension (usa __iter__ internamente)
        pending_count = len([c for c in claims if c.status == ClaimStatus.PENDING])
        
        # Generator expression (más eficiente en memoria)
        total_supporters = sum(c.supporters_count for c in claims)
        
        return {"pending": pending_count, "supporters": total_supporters}
```

---

## UNIDAD 8: Algoritmos de Machine Learning

### 8.1 Clasificación con Machine Learning

**Ejemplo en el TP:**
```python
# app/services/classifier_service.py
class ClassifierService:
    """
    Clasificador de reclamos usando:
    - TF-IDF (Term Frequency-Inverse Document Frequency)
    - Naive Bayes (algoritmo probabilístico)
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2)  # Unigramas y bigramas
        )
        self.classifier = MultinomialNB()
    
    def train(self, texts: list[str], labels: list[str]):
        """
        Entrena el clasificador
        texts: ["Se rompió la puerta", "No hay luz", ...]
        labels: ["mantenimiento", "infraestructura", ...]
        """
        # Vectorizar: convertir texto a números
        X = self.vectorizer.fit_transform(texts)
        
        # Entrenar modelo
        self.classifier.fit(X, labels)
        self.is_trained = True
    
    def classify(self, text: str) -> str:
        """
        Clasifica un texto nuevo
        Input: "Se cayó el techo del aula 305"
        Output: "mantenimiento"
        """
        X = self.vectorizer.transform([text])
        prediction = self.classifier.predict(X)[0]
        return prediction
```

### 7.2 Persistencia de Modelos

**Ejemplo en el TP:**
```python
# train_classifier.py
import joblib

# Entrenar modelo
classifier_service.train(texts, labels)

# PERSISTENCIA: guardar modelo en disco
joblib.dump(classifier_service.vectorizer, "models/vectorizer.joblib")
joblib.dump(classifier_service.classifier, "models/classifier.joblib")

# Cargar modelo (en otra sesión/programa)
vectorizer = joblib.load("models/vectorizer.joblib")
classifier = joblib.load("models/classifier.joblib")
```

### 7.3 Similitud de Textos (Bonus en tu TP)

**Ejemplo (si implementaste similarity_service):**
```python
# app/services/similarity_service.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SimilarityService:
    @staticmethod
    def find_similar_claims(claim_detail: str, limit: int = 5):
        """
        Encuentra reclamos similares usando TF-IDF y similitud de coseno
        """
        # Obtener todos los reclamos
        all_claims = Claim.query.all()
        
        # Crear corpus de textos
        texts = [claim.detail for claim in all_claims]
        texts.append(claim_detail)  # Agregar el texto a buscar
        
        # Vectorizar
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Calcular similitud
        similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
        
        # Obtener los más similares
        similar_indices = similarities[0].argsort()[-limit:][::-1]
        
        return [all_claims[i] for i in similar_indices]
```

---

## Resumen de Conceptos Clave por Ubicación en el TP

### Herencia (Single Table Inheritance)
- **Ubicación:** `app/models/user/base.py`, `app/models/user/end_user.py`, `app/models/user/admin_user.py`
- **Concepto:** User → EndUser, AdminUser

### Composición
- **Ubicación:** `app/models/claim.py`
- **Concepto:** `cascade="all, delete-orphan"` en relationships

### Agregación
- **Ubicación:** `app/models/user/admin_user.py`, `app/models/claim.py`
- **Concepto:** AdminUser → Department, Claim → Department

### Asociación (Many-to-Many)
- **Ubicación:** `app/models/claim_supporter.py`
- **Concepto:** User ↔ Claim

### Encapsulamiento
- **Ubicación:** `app/models/user/base.py`
- **Concepto:** `password_hash` con `set_password()`, `check_password()`

### Properties
- **Ubicación:** `app/models/claim.py`, `app/models/user/admin_user.py`
- **Concepto:** `@property supporters_count`, `@property is_department_head`

### Polimorfismo
- **Ubicación:** `app/models/user/` (todos)
- **Concepto:** `full_name()` diferente en EndUser y AdminUser

### Decoradores (Aspect-Oriented Programming)
- **Ubicación:** `app/utils/decorators.py`
- **Concepto:** `@admin_required`, `@end_user_required`, `@admin_role_required`

### Excepciones
- **Ubicación:** `app/services/claim_service.py`, `app/services/image_service.py`
- **Concepto:** try-except-finally, raise

### Pruebas Unitarias (AAA)
- **Ubicación:** `tests/`
- **Concepto:** Arrange-Act-Assert en todos los archivos test_*.py

### Principio de Responsabilidad Única
- **Ubicación:** `app/services/`
- **Concepto:** Cada servicio tiene UNA responsabilidad

### Persistencia
- **Ubicación:** Todos los modelos, `db.session.add()`, `db.session.commit()`
- **Concepto:** SQLAlchemy ORM

### Clasificación/ML
- **Ubicación:** `app/services/classifier_service.py`, `train_classifier.py`
- **Concepto:** TF-IDF + Naive Bayes

---

## Consejos para el Examen Teórico

### Para preguntas conceptuales:
1. **Lee teoria.md** (este documento)
2. **Identifica el concepto** en el enunciado
3. **Relaciona con tu código** mental usando los ejemplos de aquí

### Para preguntas de "dé un ejemplo":
1. Usa los ejemplos de este documento
2. Menciona la ubicación en tu código (ej: "En app/models/claim.py...")
3. Explica BREVEMENTE qué hace

### Para la defensa escrita:
1. Usa el documento de referencia rápida (el siguiente que voy a crear)
2. Ten las ubicaciones memorizadas
3. Practica explicar cada concepto en 2-3 oraciones

---

**Fin del documento de teoría explicada**
