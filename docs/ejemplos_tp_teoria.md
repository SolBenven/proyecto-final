# Defensa Escrita del TP - Sistema de Gestión de Reclamos
## Respuestas a Preguntas Teóricas con Ejemplos de Código

---

## PREGUNTA 1: Problema que resuelve el programa y uso de OO

### ¿Qué problema resuelve el programa desarrollado?

El sistema de gestión de reclamos desarrollado resuelve el problema de **gestionar y dar seguimiento a los reclamos universitarios** de forma organizada y eficiente. 

**Problemas específicos que aborda:**

1. **Desorganización en la recepción de reclamos:** Los reclamos llegan por múltiples canales sin un sistema centralizado
2. **Asignación manual a departamentos:** Se requiere personal para clasificar cada reclamo
3. **Falta de seguimiento:** Los usuarios no saben el estado de sus reclamos
4. **Duplicación de esfuerzos:** No se detectan reclamos similares
5. **Falta de métricas:** No hay datos sobre tipos de problemas, tiempos de resolución, etc.

**Soluciones implementadas:**

- **Centralización:** Un único sistema web para crear y consultar reclamos
- **Clasificación automática:** Machine Learning (TF-IDF + Naive Bayes) clasifica reclamos por departamento
- **Seguimiento en tiempo real:** Sistema de notificaciones cuando cambia el estado
- **Detección de similitud:** Algoritmo TF-IDF para encontrar reclamos relacionados
- **Analytics:** Dashboards con estadísticas y reportes PDF

---

### Importancia del uso de la Orientación a Objetos

La orientación a objetos es fundamental en este proyecto por las siguientes razones:

#### 1. **Modelado Natural del Dominio**

El sistema modela entidades del mundo real de forma natural:

```python
# app/models/claim.py
class Claim(db.Model):
    """Un reclamo es una entidad del mundo real"""
    detail: Mapped[str]
    status: Mapped[ClaimStatus]
    department: Mapped["Department"]
    creator: Mapped["EndUser"]
```

Esto permite **pensar en el problema en términos del dominio** (reclamos, usuarios, departamentos) en lugar de estructuras de datos complejas.

#### 2. **Encapsulamiento de Responsabilidades**

Cada clase tiene responsabilidades claras y oculta su implementación:

```python
# app/models/user/base.py
class User(UserMixin, db.Model):
    password_hash: Mapped[str]  # Encapsulado - no se accede directamente
    
    def set_password(self, password: str):
        """Interfaz pública para establecer contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Interfaz pública para verificar contraseña"""
        return check_password_hash(self.password_hash, password)
```

**Ventaja:** Si cambio el algoritmo de hash (bcrypt → argon2), solo modifico esta clase, no todo el sistema.

#### 3. **Herencia para Reutilización de Código**

```python
# app/models/user/base.py, end_user.py, admin_user.py
class User(UserMixin, db.Model):
    """Clase base con funcionalidad común"""
    email: Mapped[str]
    username: Mapped[str]
    def set_password(self, password: str): ...
    def check_password(self, password: str) -> bool: ...

class EndUser(User):
    """Hereda funcionalidad de User + agrega específica"""
    cloister: Mapped[Cloister]
    created_claims: Mapped[list["Claim"]]

class AdminUser(User):
    """Hereda funcionalidad de User + agrega específica"""
    admin_role: Mapped[AdminRole]
    department: Mapped["Department"]
```

**Ventaja:** No duplico código de autenticación en cada tipo de usuario.

#### 4. **Polimorfismo para Flexibilidad**

```python
# app/models/user/*.py
class User:
    @property
    def full_name(self) -> str:
        return ""

class EndUser(User):
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

class AdminUser(User):
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name} [{self.admin_role.value}]"

# Uso polimórfico:
users: list[User] = [EndUser(...), AdminUser(...)]
for user in users:
    print(user.full_name)  # Diferentes implementaciones, misma interfaz
```

**Ventaja:** Puedo tratar diferentes tipos de usuarios uniformemente sin conocer su tipo específico.

#### 5. **Modularidad y Mantenibilidad**

```
app/
├── models/              # Responsabilidad: Estructura de datos
├── services/            # Responsabilidad: Lógica de negocio
├── routes/              # Responsabilidad: Manejo de HTTP
└── utils/               # Responsabilidad: Funcionalidades auxiliares
```

Cada módulo tiene una responsabilidad única y puede modificarse independientemente.

#### 6. **Composición para Relaciones Complejas**

```python
# app/models/claim.py
class Claim(db.Model):
    """Claim está COMPUESTO por otras entidades"""
    status_history: Mapped[list["ClaimStatusHistory"]] = relationship(
        cascade="all, delete-orphan"  # Si elimino Claim, elimino su historial
    )
    supporters: Mapped[list["ClaimSupporter"]] = relationship(
        cascade="all, delete-orphan"
    )
```

**Ventaja:** Las relaciones entre entidades son explícitas y manejadas automáticamente.

---

## PREGUNTA 2: Relaciones entre objetos en el diagrama de clases

### Fundamente la elección de las relaciones

En el diagrama de clases (`docs/class.puml`) implementé diferentes tipos de relaciones según las necesidades del negocio:

---

#### HERENCIA: User → EndUser, AdminUser

**Ubicación:** `app/models/user/base.py`, `end_user.py`, `admin_user.py`

```python
class User(UserMixin, db.Model):
    """Clase base"""
    __tablename__ = "user"
    user_type: Mapped[str]  # Discriminador
    __mapper_args__ = {"polymorphic_on": user_type}

class EndUser(User):
    """Usuario final - hereda de User"""
    __mapper_args__ = {"polymorphic_identity": "end_user"}

class AdminUser(User):
    """Usuario admin - hereda de User"""
    __mapper_args__ = {"polymorphic_identity": "admin_user"}
```

**Justificación:**
- Relación "es un(a)": EndUser **ES UN** User, AdminUser **ES UN** User
- Comparten atributos comunes (email, username, password)
- Comparten comportamiento común (autenticación)
- Cada uno agrega comportamiento específico
- Single Table Inheritance para eficiencia en consultas

**UML:** `User <|-- EndUser` y `User <|-- AdminUser`

---

#### COMPOSICIÓN: Claim → ClaimStatusHistory, ClaimSupporter, ClaimTransfer

**Ubicación:** `app/models/claim.py`

```python
class Claim(db.Model):
    status_history: Mapped[list["ClaimStatusHistory"]] = relationship(
        "ClaimStatusHistory",
        back_populates="claim",
        cascade="all, delete-orphan"  # ← COMPOSICIÓN
    )
    
    supporters: Mapped[list["ClaimSupporter"]] = relationship(
        "ClaimSupporter",
        back_populates="claim",
        cascade="all, delete-orphan"  # ← COMPOSICIÓN
    )
    
    transfers: Mapped[list["ClaimTransfer"]] = relationship(
        "ClaimTransfer",
        back_populates="claim",
        cascade="all, delete-orphan"  # ← COMPOSICIÓN
    )
```

**Justificación:**
- El historial de cambios **NO EXISTE** sin el reclamo
- Los adherentes de un reclamo **NO TIENEN SENTIDO** sin el reclamo
- Las transferencias **PERTENECEN EXCLUSIVAMENTE** a un reclamo
- Al eliminar un Claim, deben eliminarse sus partes (`cascade="all, delete-orphan"`)
- Relación todo-parte con ciclo de vida dependiente

**UML:** `Claim "1" *--> "*" ClaimStatusHistory` (rombo relleno)

---

#### AGREGACIÓN: AdminUser → Department

**Ubicación:** `app/models/user/admin_user.py`

```python
class AdminUser(User):
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("department.id"), nullable=True
    )
    department: Mapped["Department"] = relationship(
        "Department", back_populates="admin_users"
    )
```

**Justificación:**
- Un AdminUser **PERTENECE A** un Department
- El Department **EXISTE INDEPENDIENTEMENTE** del AdminUser
- Si elimino un admin, el departamento sigue existiendo
- Múltiples admins pueden pertenecer al mismo departamento
- La relación es "tiene un" pero sin dependencia de ciclo de vida

**UML:** `AdminUser "*" --> "0..1" Department` (rombo vacío)

---

#### ASOCIACIÓN (Many-to-Many): User ↔ Claim (a través de ClaimSupporter)

**Ubicación:** `app/models/claim_supporter.py`

```python
class ClaimSupporter(db.Model):
    """Tabla intermedia para relación N:M"""
    claim_id: Mapped[int] = mapped_column(ForeignKey("claim.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    
    claim: Mapped["Claim"] = relationship("Claim")
    user: Mapped["EndUser"] = relationship("EndUser")
```

**Justificación:**
- Un usuario puede apoyar **MUCHOS** reclamos
- Un reclamo puede tener **MUCHOS** adherentes
- Ambos existen **INDEPENDIENTEMENTE**
- Se necesita tabla intermedia para N:M
- Permite agregar atributos a la relación (ej: fecha de adhesión)

**UML:** `User "*" <--> "*" Claim` (a través de ClaimSupporter)

---

#### DEPENDENCIA: ClaimService ..> ClassifierService

**Ubicación:** `app/services/claim_service.py`

```python
class ClaimService:
    @staticmethod
    def _classify_claim_department(detail: str):
        """DEPENDE de ClassifierService pero NO lo almacena"""
        try:
            # Usa classifier_service temporalmente
            predicted = classifier_service.classify(detail)
            dept = DepartmentService.get_department_by_name(predicted)
            return dept.id if dept else None
        except Exception:
            return None
```

**Justificación:**
- ClaimService **USA** ClassifierService para una tarea específica
- No almacena una instancia de ClassifierService
- La relación es temporal (solo durante la ejecución del método)
- Bajo acoplamiento: si cambio ClassifierService, ClaimService cambia poco

**UML:** `ClaimService ..> ClassifierService` (línea punteada)

---

## PREGUNTA 3: Polimorfismo de subtipos

### ¿En qué consiste el polimorfismo de subtipos?

El **polimorfismo de subtipos** (o polimorfismo de inclusión) permite que un objeto de una clase derivada pueda ser tratado como un objeto de su clase base, pero manteniendo su comportamiento específico. 

**Características:**
1. Un subtipo puede sustituir a su supertipo
2. El mismo mensaje a diferentes objetos produce respuestas diferentes
3. Se decide en tiempo de ejecución qué método llamar (dynamic dispatch)
4. Permite escribir código genérico que funciona con múltiples tipos

---

### Ejemplo con código del TP

**Ubicación:** `app/models/user/base.py`, `end_user.py`, `admin_user.py`

```python
# ==================== CLASE BASE ====================
# app/models/user/base.py
class User(UserMixin, db.Model):
    """Clase base - define la interfaz"""
    id: Mapped[int]
    first_name: Mapped[str]
    last_name: Mapped[str]
    
    @property
    def full_name(self) -> str:
        """Método polimórfico - cada subtipo lo redefine"""
        return ""

# ==================== SUBTIPOS ====================
# app/models/user/end_user.py
class EndUser(User):
    """Subtipo 1 - implementación específica"""
    cloister: Mapped[Cloister]
    
    @property
    def full_name(self) -> str:
        """Implementación para usuarios finales"""
        return f"{self.first_name} {self.last_name}"

# app/models/user/admin_user.py
class AdminUser(User):
    """Subtipo 2 - implementación diferente"""
    admin_role: Mapped[AdminRole]
    
    @property
    def full_name(self) -> str:
        """Implementación para administradores"""
        return f"{self.first_name} {self.last_name} [{self.admin_role.value}]"

# ==================== USO POLIMÓRFICO ====================
# app/routes/users.py
@users_bp.route("/profile")
@login_required
def profile():
    # current_user puede ser EndUser o AdminUser en tiempo de ejecución
    # Polimorfismo: se llama al método correcto según el tipo real
    
    return render_template(
        "users/profile.html",
        user=current_user,
        full_name=current_user.full_name,  # ← POLIMORFISMO aquí
        email=current_user.email
    )

# ==================== OTRO EJEMPLO ====================
def enviar_notificacion_a_usuarios(usuarios: list[User]):
    """
    Función genérica que acepta cualquier subtipo de User
    Usa polimorfismo para obtener el nombre completo
    """
    for usuario in usuarios:
        # No necesito saber si es EndUser o AdminUser
        # El método correcto se llama automáticamente
        mensaje = f"Hola {usuario.full_name}, tienes una notificación"
        print(mensaje)
        # Si es EndUser: "Hola Juan Pérez, ..."
        # Si es AdminUser: "Hola Ana López [jefe_departamento], ..."

# Uso:
usuarios: list[User] = [
    EndUser(first_name="Juan", last_name="Pérez", ...),
    AdminUser(first_name="Ana", last_name="López", admin_role=AdminRole.DEPARTMENT_HEAD, ...)
]

enviar_notificacion_a_usuarios(usuarios)  # Funciona con ambos tipos
```

**Ventajas del polimorfismo en este ejemplo:**
1. **Código genérico:** `profile()` funciona con cualquier tipo de usuario
2. **Extensibilidad:** Si agrego `ModeratorUser`, no cambio el código existente
3. **Mantenibilidad:** Cada clase maneja su propia implementación
4. **Principio Open/Closed:** Abierto a extensión, cerrado a modificación

---

## PREGUNTA 4: Principios SOLID

Selecciono dos principios SOLID y los relaciono con el diseño:

---

### PRINCIPIO 1: Single Responsibility Principle (SRP)

#### Enunciado

> **Una clase debe tener una única razón para cambiar.**

Esto significa que cada clase debe tener **una sola responsabilidad** bien definida. Si una clase hace demasiadas cosas, es difícil de mantener, probar y entender.

#### Relación con el diseño del TP

En el sistema separé claramente las responsabilidades en diferentes servicios:

**Ejemplo 1: Separación de Servicios**

```python
# ==================== SERVICIO 1: Gestión de Reclamos ====================
# app/services/claim_service.py
class ClaimService:
    """
    ÚNICA RESPONSABILIDAD: Gestionar reclamos
    Razón para cambiar: Si cambian las reglas de negocio de reclamos
    """
    @staticmethod
    def create_claim(user_id: int, detail: str, ...) -> tuple[Claim | None, str | None]:
        """Crear reclamos"""
        ...
    
    @staticmethod
    def update_claim_status(claim_id: int, new_status: ClaimStatus, ...) -> tuple[Claim | None, str | None]:
        """Actualizar estado"""
        ...
    
    @staticmethod
    def get_claim_by_id(claim_id: int) -> Claim | None:
        """Consultar reclamos"""
        ...

# ==================== SERVICIO 2: Notificaciones ====================
# app/services/notification_service.py
class NotificationService:
    """
    ÚNICA RESPONSABILIDAD: Gestionar notificaciones
    Razón para cambiar: Si cambia cómo se notifica a los usuarios
    """
    @staticmethod
    def create_notification(user_id: int, history_id: int) -> UserNotification:
        """Crear notificaciones"""
        ...
    
    @staticmethod
    def get_user_notifications(user_id: int) -> list[UserNotification]:
        """Obtener notificaciones"""
        ...

# ==================== SERVICIO 3: Clasificación ====================
# app/services/classifier_service.py
class ClassifierService:
    """
    ÚNICA RESPONSABILIDAD: Clasificar texto con ML
    Razón para cambiar: Si cambio el algoritmo de clasificación
    """
    def train(self, texts: list[str], labels: list[str]) -> None:
        """Entrenar modelo"""
        ...
    
    def classify(self, text: str) -> str:
        """Clasificar texto"""
        ...
```

**Ventaja:** Si necesito cambiar cómo se clasifican los reclamos, solo modifico `ClassifierService`, no todo el sistema.

**Ejemplo 2: Separación en Modelos**

```python
# ==================== MODELO 1: Usuario ====================
# app/models/user/base.py
class User(db.Model):
    """
    ÚNICA RESPONSABILIDAD: Representar un usuario y gestionar autenticación
    """
    email: Mapped[str]
    username: Mapped[str]
    password_hash: Mapped[str]
    
    def set_password(self, password: str): ...
    def check_password(self, password: str) -> bool: ...

# ==================== MODELO 2: Reclamo ====================
# app/models/claim.py
class Claim(db.Model):
    """
    ÚNICA RESPONSABILIDAD: Representar un reclamo y sus propiedades
    NO maneja lógica de negocio (eso es responsabilidad de ClaimService)
    """
    detail: Mapped[str]
    status: Mapped[ClaimStatus]
    
    @property
    def supporters_count(self) -> int:
        return len(self.supporters)
```

**Ventaja:** Cada clase es fácil de entender, probar y mantener.

---

### PRINCIPIO 2: Dependency Inversion Principle (DIP)

#### Enunciado

> **Los módulos de alto nivel no deben depender de módulos de bajo nivel. Ambos deben depender de abstracciones.**
> **Las abstracciones no deben depender de los detalles. Los detalles deben depender de las abstracciones.**

Esto significa que el código debe depender de interfaces/abstracciones, no de implementaciones concretas.

#### Relación con el diseño del TP

**Ejemplo 1: Abstracción de Base de Datos**

```python
# ==================== ALTO NIVEL: Servicio ====================
# app/services/claim_service.py
class ClaimService:
    @staticmethod
    def create_claim(user_id: int, detail: str, ...) -> tuple[Claim | None, str | None]:
        claim = Claim(detail=detail, ...)
        
        # Depende de la ABSTRACCIÓN 'db', no de una implementación concreta
        db.session.add(claim)  # ← No sabe si es SQLite, PostgreSQL, MySQL
        db.session.commit()
        
        return claim, None

# ==================== ABSTRACCIÓN ====================
# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()  # Abstracción que puede usar cualquier motor SQL

# ==================== CONFIGURACIÓN ====================
# Puedo cambiar la base de datos sin modificar ClaimService:
# SQLite en desarrollo:
SQLALCHEMY_DATABASE_URI = "sqlite:///claims.db"

# PostgreSQL en producción:
SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@localhost/claims"
```

**Ventaja:** `ClaimService` no conoce detalles de implementación de la BD.

**Ejemplo 2: Abstracción del Clasificador**

```python
# ==================== ALTO NIVEL: ClaimService ====================
# app/services/claim_service.py
class ClaimService:
    @staticmethod
    def _classify_claim_department(detail: str) -> int | None:
        try:
            # Depende de la ABSTRACCIÓN (interfaz) de classifier_service
            # No sabe si usa TF-IDF, BERT, o reglas simples
            predicted = classifier_service.classify(detail)
            # ↑ Solo conoce el método .classify(), no la implementación
            
            dept = DepartmentService.get_department_by_name(predicted)
            return dept.id if dept else None
        except Exception:
            return None

# ==================== ABSTRACCIÓN (Interfaz implícita) ====================
# app/services/classifier_service.py
class ClassifierService:
    """
    Abstracción: Define el contrato .classify(text) -> str
    Implementación: TF-IDF + Naive Bayes (pero podría cambiar)
    """
    def classify(self, text: str) -> str:
        # Implementación actual: TF-IDF + Naive Bayes
        X = self.vectorizer.transform([text])
        return self.classifier.predict(X)[0]
    
    # Si cambio a BERT, solo modifico esta clase:
    # def classify(self, text: str) -> str:
    #     embeddings = self.bert_model.encode(text)
    #     return self.classifier.predict(embeddings)[0]
```

**Ventaja:** Puedo cambiar de TF-IDF a BERT sin modificar `ClaimService`.

**Ejemplo 3: Decoradores como Abstracción**

```python
# ==================== ABSTRACCIÓN: Decoradores ====================
# app/utils/decorators.py
def admin_required(f):
    """Abstracción de control de acceso"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, AdminUser):
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function

# ==================== USO (Alto nivel) ====================
# app/routes/admin.py
@admin_bp.route("/dashboard")
@admin_required  # ← No sabe CÓMO se verifica, solo que SE verifica
def dashboard():
    return render_template("admin/dashboard.html")
```

**Ventaja:** Si cambio de Flask-Login a JWT, solo modifico el decorador.

---

## PREGUNTA 5: Estructura AAA de las pruebas unitarias

### ¿En qué consiste la estructura AAA?

La estructura **AAA** (Arrange-Act-Assert) es un patrón para organizar pruebas unitarias en **tres secciones claramente definidas**:

1. **Arrange (Arreglar/Preparar):** Configurar el escenario de prueba
   - Crear objetos necesarios
   - Configurar datos de entrada
   - Establecer el estado inicial del sistema

2. **Act (Actuar):** Ejecutar la acción que se está probando
   - Llamar al método bajo prueba
   - Realizar la operación específica
   - Capturar el resultado

3. **Assert (Aseverar/Verificar):** Comprobar que el resultado es el esperado
   - Verificar valores de retorno
   - Comprobar cambios de estado
   - Validar excepciones lanzadas

**Ventajas:**
- **Claridad:** Fácil identificar qué hace cada parte
- **Mantenibilidad:** Pruebas fáciles de modificar
- **Legibilidad:** Cualquiera entiende la prueba
- **Estándar:** Patrón ampliamente reconocido

---

### Ejemplo con código del TP

**Ubicación:** `tests/test_claim_service.py`

```python
import unittest
from app.extensions import db
from app.models.claim import Claim, ClaimStatus
from app.models.user.end_user import Cloister, EndUser
from app.services.claim_service import ClaimService
from tests.conftest import BaseTestCase

class TestClaimService(BaseTestCase):
    """Tests para el servicio de reclamos"""
    
    def setUp(self):
        """Configuración común antes de cada test"""
        super().setUp()
        # Crear usuario de prueba
        self.user = EndUser(
            first_name="Test",
            last_name="User",
            email="testuser@test.com",
            username="testuser",
            cloister=Cloister.STUDENT,
        )
        self.user.set_password("test123")
        db.session.add(self.user)
        db.session.commit()
    
    def test_create_claim_with_specific_department(self):
        """Verifica que un reclamo se asigna al departamento especificado"""
        
        # ==================== ARRANGE ====================
        # Preparar los datos de entrada
        detail = "Se rompió la ventana del aula 102"
        dept_id = self.sample_departments["dept1_id"]
        user_id = self.user.id
        
        # ==================== ACT ====================
        # Ejecutar la acción bajo prueba
        claim, error = ClaimService.create_claim(
            user_id=user_id,
            detail=detail,
            department_id=dept_id
        )
        
        # ==================== ASSERT ====================
        # Verificar que el resultado es el esperado
        self.assertIsNotNone(claim, "Debería crear el reclamo")
        self.assertIsNone(error, "No debería haber error")
        self.assertEqual(claim.detail, detail, "El detalle debe coincidir")
        self.assertEqual(claim.department_id, dept_id, "El departamento debe coincidir")
        self.assertEqual(claim.status, ClaimStatus.PENDING, "Estado inicial debe ser PENDING")
        self.assertEqual(claim.creator_id, user_id, "El creador debe ser el usuario especificado")
```

**Ejemplo más complejo con múltiples assertions:**

```python
def test_create_claim_with_empty_detail(self):
    """Verifica que no se puede crear un reclamo con detalle vacío"""
    
    # ==================== ARRANGE ====================
    # Preparar un detalle inválido (vacío)
    detail_vacio = "   "  # Solo espacios en blanco
    dept_id = self.sample_departments["dept1_id"]
    
    # ==================== ACT ====================
    # Intentar crear el reclamo con detalle vacío
    claim, error = ClaimService.create_claim(
        user_id=self.user.id,
        detail=detail_vacio,
        department_id=dept_id
    )
    
    # ==================== ASSERT ====================
    # Verificar que falla correctamente
    self.assertIsNone(claim, "No debería crear el reclamo")
    self.assertIsNotNone(error, "Debería retornar un mensaje de error")
    self.assertIn("vacío", error.lower(), "El error debe mencionar que está vacío")
```

**Ejemplo con configuración compleja en Arrange:**

```python
def test_add_supporter_prevents_duplicate(self):
    """Verifica que un usuario no puede adherirse dos veces al mismo reclamo"""
    
    # ==================== ARRANGE ====================
    # Paso 1: Crear un reclamo
    claim, _ = ClaimService.create_claim(
        user_id=self.user.id,
        detail="Problema de prueba",
        department_id=self.sample_departments["dept1_id"]
    )
    
    # Paso 2: Crear otro usuario que será el adherente
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
    
    # Paso 3: Primera adhesión (debe funcionar)
    first_result, first_error = ClaimService.add_supporter(claim.id, supporter.id)
    self.assertTrue(first_result)  # Verificación intermedia
    
    # ==================== ACT ====================
    # Intentar adherirse por segunda vez (esto es lo que probamos)
    second_result, second_error = ClaimService.add_supporter(claim.id, supporter.id)
    
    # ==================== ASSERT ====================
    # Verificar que la segunda adhesión falla
    self.assertFalse(second_result, "No debería adherirse dos veces")
    self.assertIsNotNone(second_error, "Debería retornar un error")
    self.assertIn("ya", second_error.lower(), "El error debe indicar que ya está adherido")
    
    # Verificar que el contador no aumentó
    self.assertEqual(claim.supporters_count, 1, "Debe tener solo 1 adherente")
```

---

## PREGUNTA 6: Protocolo de iteradores en Python

### ¿En qué consiste el protocolo de iteradores?

El **protocolo de iteradores** es un mecanismo de Python que permite **recorrer elementos de una colección de forma secuencial** sin exponer su estructura interna. Se basa en dos métodos especiales:

1. **`__iter__()`:** Retorna el objeto iterador (generalmente `self`)
   - Permite que el objeto sea iterable
   - Se llama cuando usas `iter(objeto)` o inicias un `for` loop

2. **`__next__()`:** Retorna el siguiente elemento de la secuencia
   - Se llama cada vez que necesitas el siguiente elemento
   - Debe lanzar `StopIteration` cuando no hay más elementos

**¿Cómo funciona internamente un for loop?**

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
        break  # Termina cuando no hay más elementos
```

---

### Ejemplo con código del TP

**Ejemplo 1: Iterador simple conceptual**

```python
# Ejemplo educativo (aplicable al contexto del TP)
class ClaimIterator:
    """Iterador personalizado para recorrer reclamos"""
    
    def __init__(self, claims: list):
        self.claims = claims
        self.index = 0
    
    def __iter__(self):
        """Retorna el iterador (self)"""
        return self
    
    def __next__(self):
        """Retorna el siguiente reclamo"""
        if self.index < len(self.claims):
            claim = self.claims[self.index]
            self.index += 1
            return claim
        else:
            raise StopIteration  # No hay más reclamos

# Uso:
claims = [claim1, claim2, claim3]
iterator = ClaimIterator(claims)

for claim in iterator:
    print(f"Reclamo #{claim.id}: {claim.detail}")
```

**Ejemplo 2: Iterador lazy con batches (eficiente en memoria)**

```python
# app/iterators/claim_iterator.py (ejemplo aplicable)
class ClaimsByStatusIterator:
    """
    Iterador que carga reclamos de un estado específico en batches
    Ventaja: No carga todos los reclamos en memoria a la vez
    """
    def __init__(self, status: ClaimStatus, batch_size: int = 50):
        self.status = status
        self.batch_size = batch_size
        self.offset = 0
        self.current_batch = []
        self.batch_index = 0
    
    def __iter__(self):
        """Retorna el iterador"""
        return self
    
    def __next__(self) -> Claim:
        """Retorna el siguiente reclamo, cargando batches según necesidad"""
        # Si terminamos el batch actual, cargar el siguiente
        if self.batch_index >= len(self.current_batch):
            # Consultar el siguiente batch de la base de datos
            self.current_batch = (
                Claim.query
                .filter_by(status=self.status)
                .offset(self.offset)
                .limit(self.batch_size)
                .all()
            )
            self.offset += self.batch_size
            self.batch_index = 0
            
            # Si no hay más reclamos, terminar iteración
            if not self.current_batch:
                raise StopIteration
        
        # Retornar el siguiente reclamo del batch actual
        claim = self.current_batch[self.batch_index]
        self.batch_index += 1
        return claim

# Uso:
pending_iterator = ClaimsByStatusIterator(ClaimStatus.PENDING)

for claim in pending_iterator:
    print(f"Procesando reclamo #{claim.id}")
    # Solo carga 50 reclamos a la vez, eficiente con miles de reclamos
```

**Ejemplo 3: Generador con yield (más simple)**

```python
# app/services/claim_service.py (ejemplo aplicable)
class ClaimService:
    @staticmethod
    def iter_claims_by_department(department_id: int):
        """
        Generador que itera sobre reclamos de un departamento
        yield convierte la función en un iterador automáticamente
        """
        offset = 0
        batch_size = 100
        
        while True:
            # Cargar batch
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
            
            # Yield cada reclamo (esto hace la función un generador)
            for claim in claims:
                yield claim  # ← Pausa aquí y retorna claim
            
            offset += batch_size

# Uso:
for claim in ClaimService.iter_claims_by_department(department_id=1):
    # Procesa reclamos uno a uno, eficiente en memoria
    enviar_notificacion(claim.creator, claim)
```

**Ejemplo 4: Objetos iterables existentes en el TP**

```python
# app/models/claim.py
class Claim(db.Model):
    # Estas relaciones son ITERABLES automáticamente
    supporters: Mapped[list["ClaimSupporter"]] = relationship(
        "ClaimSupporter", back_populates="claim"
    )
    status_history: Mapped[list["ClaimStatusHistory"]] = relationship(
        "ClaimStatusHistory", back_populates="claim"
    )

# Uso en el código:
claim = Claim.query.get(1)

# Iterar sobre adherentes (usa __iter__ internamente)
for supporter in claim.supporters:
    print(f"Adherente: {supporter.user.full_name}")

# Iterar sobre historial (usa __iter__ internamente)
for history in claim.status_history:
    print(f"{history.changed_at}: {history.old_status} → {history.new_status}")

# Comprehensions también usan el protocolo de iteradores:
pending_claims = [c for c in Claim.query.all() if c.status == ClaimStatus.PENDING]
# ↑ Esto usa __iter__ de la lista retornada por .all()
```

**Ventajas del protocolo de iteradores:**
1. **Lazy evaluation:** Solo calcula valores cuando se necesitan
2. **Eficiencia en memoria:** No carga todo en memoria
3. **Interfaz uniforme:** Funciona con `for`, comprehensions, etc.
4. **Composición:** Se pueden encadenar iteradores

---

## TABLA RESUMEN - Ubicaciones Rápidas

| Concepto | Archivo Principal | Ejemplo Clave |
|----------|-------------------|---------------|
| **Herencia** | `app/models/user/base.py`, `end_user.py`, `admin_user.py` | User → EndUser, AdminUser |
| **Composición** | `app/models/claim.py` | `cascade="all, delete-orphan"` |
| **Agregación** | `app/models/user/admin_user.py` | AdminUser → Department |
| **Asociación N:M** | `app/models/claim_supporter.py` | User ↔ Claim |
| **Polimorfismo** | `app/models/user/*.py` | `full_name()` diferente por subtipo |
| **SRP** | `app/services/claim_service.py`, `notification_service.py` | Servicios separados |
| **DIP** | `app/services/claim_service.py` | Depende de `db` abstracto |
| **AAA** | `tests/test_claim_service.py` | Arrange-Act-Assert |
| **Iteradores** | Relaciones en `app/models/claim.py` | `for supporter in claim.supporters` |
| **unittest** | `tests/conftest.py`, `test_*.py` | `BaseTestCase`, `setUp()`, `tearDown()` |

---

**Fin del documento de defensa**
