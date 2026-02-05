# Guion de Presentación Oral - Sistema de Gestión de Reclamos
## Defensa del Trabajo Práctico

---

## 1. Introducción y Descripción del Problema

El proyecto que desarrollamos es un **sistema de atención y seguimiento de reclamos para la Facultad de Ingeniería de la UNER**.

El propósito principal es permitir a los usuarios finales —estudiantes, docentes y personal administrativo— **registrar reclamos fácilmente** sobre problemas, faltantes o desperfectos en las áreas comunes del edificio.

Además, brinda a los jefes de departamento y a la secretaría técnica una **herramienta para gestionar y resolver** estos reclamos de manera eficiente.

La idea central es **mejorar la trazabilidad, la transparencia y la participación** en el seguimiento de reclamos, facilitando la comunicación entre quienes detectan un problema y quienes pueden resolverlo.

---

## 2. Funcionamiento General del Programa

El sistema es una **aplicación web desarrollada con Flask**.

Los usuarios pueden **registrarse, iniciar sesión, crear nuevos reclamos o adherirse** a reclamos similares ya existentes.

Cuando un usuario crea un reclamo, la aplicación **lo clasifica automáticamente** usando procesamiento de lenguaje natural (TF-IDF y Naive Bayes Multinomial) y lo dirige al departamento correspondiente.

Los responsables de cada área acceden a un **panel de administración** donde pueden visualizar los reclamos de su departamento, modificar su estado, derivarlos a otros departamentos si es necesario, y generar reportes con estadísticas.

Además, el sistema permite **detectar reclamos similares** utilizando análisis de similitud TF-IDF, **enviar notificaciones** automáticas cuando cambia el estado de un reclamo, y **exportar reportes en formato PDF** con estadísticas por departamento.

---

## 3. Explicación del Diseño y Diagrama de Clases

Ahora voy a pasar a explicar el diseño del sistema, que se refleja en el diagrama de clases que está en pantalla (`docs/class.puml`).

El sistema está organizado siguiendo una **arquitectura en capas** y principios de **diseño orientado a objetos**.

### Clases de Dominio

En la base del sistema tenemos las **clases de dominio** que representan los conceptos principales de la aplicación:

- **`User`** (clase base abstracta): Representa un usuario del sistema, encapsulando datos comunes como email, username y contraseña encriptada.
  - **`EndUser`**: Usuario final (estudiantes, docentes, no docentes). Hereda de `User` y agrega atributos como `cloister` (claustro).
  - **`AdminUser`**: Usuario administrador (jefes de departamento, secretaría técnica). Hereda de `User` y agrega `admin_role` y relación con `Department`.

Aquí aplicamos **herencia con Single Table Inheritance**: todas las clases `User` se almacenan en una tabla con un discriminador `user_type` para diferenciar el tipo.

- **`Claim`**: Representa un reclamo, con atributos como `detail`, `status` (PENDING, IN_PROGRESS, RESOLVED, CLOSED), `department_id`, y relaciones a su creador y departamento.

- **`Department`**: Representa un departamento de la facultad (Infraestructura, Servicios Generales, etc.).

### Relaciones Entre Entidades

**Composición (Claim → ClaimStatusHistory, ClaimSupporter, ClaimTransfer):**

La clase `Claim` tiene relaciones de **composición** con:
- **`ClaimStatusHistory`**: Almacena el historial de cambios de estado. Si elimino un reclamo, su historial también se elimina (`cascade="all, delete-orphan"`).
- **`ClaimSupporter`**: Tabla intermedia que modela la relación muchos a muchos entre usuarios y reclamos (cuando un usuario se adhiere a un reclamo). Si elimino el reclamo, se eliminan todas sus adhesiones.
- **`ClaimTransfer`**: Registra las transferencias entre departamentos. Si elimino el reclamo, su historial de transferencias también desaparece.

Esto nos permite aplicar el **principio de composición**: estas entidades no tienen sentido sin un reclamo padre.

**Relación Muchos a Muchos (EndUser ↔ Claim):**

Un punto importante en el diseño es la **relación muchos a muchos** entre usuarios y reclamos, que se da cuando un usuario se adhiere a un reclamo creado por otro.

Esta relación se modela con la tabla intermedia **`ClaimSupporter`**, y en SQLAlchemy se representa usando `relationship()` en el modelo `Claim`, con navegación bidireccional hacia `EndUser`.

### Capa de Servicios

Para mantener la separación de responsabilidades, implementamos una **capa de servicios** que encapsula la lógica de negocio:

- **`ClaimService`**: Gestiona la creación de reclamos, actualización de estados, adhesión de usuarios y asignación de departamentos. Utiliza el clasificador de ML para asignar automáticamente el departamento.

- **`ClassifierService`**: Implementa el clasificador de texto usando TF-IDF para vectorización y Naive Bayes Multinomial para clasificación. Se entrena con datos históricos y predice el departamento basándose en el detalle del reclamo.

- **`SimilarityService`**: Calcula la similitud entre reclamos usando TF-IDF y similitud del coseno, permitiendo encontrar reclamos similares y sugerir adhesión en lugar de duplicar.

- **`NotificationService`**: Gestiona la creación y consulta de notificaciones cuando cambia el estado de un reclamo.

- **`ReportService`**: Genera reportes en formato PDF con estadísticas por departamento usando ReportLab.

- **`DepartmentService`**: Gestiona operaciones CRUD sobre departamentos.

- **`UserService`**: Gestiona el registro y autenticación de usuarios.

- **`TransferService`**: Gestiona las transferencias de reclamos entre departamentos.

- **`AdminClaimService`**: Gestiona operaciones administrativas sobre reclamos (cambiar estado, transferir, consultar por departamento).

Esto nos permite aplicar **polimorfismo de subtipo** y el **principio de responsabilidad única (SRP)**: cada servicio tiene una única razón para cambiar.

### Aplicación de Principios SOLID

**Principio de Abierto/Cerrado:**

En lugar de codificar directamente en los servicios cada tipo de operación, utilizamos **abstracciones**. Por ejemplo, el `ClassifierService` puede ser reemplazado por otro algoritmo (BERT, Word2Vec) sin modificar `ClaimService`, ya que solo depende de la interfaz `.classify()`.

**Principio de Inversión de Dependencias:**

Los servicios de alto nivel (como `ClaimService`) no dependen de implementaciones concretas de bajo nivel. Dependen de la **abstracción `db`** (SQLAlchemy), lo que nos permite cambiar de SQLite a PostgreSQL sin modificar el código de negocio.

Por ejemplo, `ClaimService` usa `db.session.add()` y `db.session.commit()`, sin conocer detalles de la base de datos subyacente.

### Modelos de Datos (DTOs)

Las clases de dominio (`User`, `Claim`, `Department`, etc.) actúan también como **DTOs (Data Transfer Objects)** ligados a SQLAlchemy, que mapean directamente a tablas de la base de datos usando `Mapped` y `relationship()`.

Esto permite que SQLAlchemy gestione automáticamente la persistencia y las relaciones entre entidades.

---

## 4. Justificación de Decisiones de Diseño

Elegimos **separar la lógica de negocio** (servicios) **de la persistencia** (modelos) **y la presentación** (rutas/templates) para facilitar el mantenimiento y la escalabilidad.

La **modularidad** hace que el sistema sea más fácil de entender y extender. Por ejemplo:
- Si quiero cambiar el algoritmo de clasificación, solo modifico `ClassifierService`.
- Si quiero agregar un nuevo tipo de reporte, solo modifico `ReportService`.
- Si quiero cambiar la base de datos, solo modifico la configuración de SQLAlchemy.

Además, utilizamos **decoradores personalizados** (`@admin_required`, `@department_head_required`) para aplicar el **principio DRY (Don't Repeat Yourself)** en el control de acceso, evitando repetir código de verificación de permisos en cada ruta.

---

## 5. Seguridad y Robustez

### Seguridad

Implementamos **seguridad mediante Flask-Login** para autenticar usuarios y proteger rutas con el decorador **`@login_required`**.

También usamos **control de acceso por rol**: 
- Los usuarios finales solo pueden crear y consultar sus propios reclamos.
- Los jefes de departamento pueden gestionar reclamos de su departamento.
- La secretaría técnica puede gestionar todos los reclamos del sistema.

Esto se implementa con decoradores como `@admin_required` y verificaciones en los servicios.

Los datos de sesión están protegidos con **sesiones cifradas de Flask** y las contraseñas se almacenan usando **`werkzeug.security.generate_password_hash`** con salting automático.

Además, evitamos inyecciones SQL usando **SQLAlchemy ORM**, que parametriza automáticamente las consultas.

### Robustez

El sistema **maneja errores comunes**, como:
- Intentos de crear reclamos con detalles vacíos o muy cortos.
- Intentos de un usuario de adherirse dos veces al mismo reclamo.
- Intentos de acceder a reclamos de otros departamentos sin permisos.
- Errores en la clasificación automática (fallback a asignación manual).

Todos los errores muestran **mensajes claros al usuario** mediante Flask flash messages, y se registran para su análisis.

---

## 6. Pruebas Realizadas

Realizamos **pruebas unitarias** utilizando el módulo **`unittest`** y organizándolas según el patrón **AAA (Arrange, Act, Assert)**, lo cual facilita la claridad y el mantenimiento del código de pruebas.

### Ejemplos de Pruebas

**Pruebas del Servicio de Reclamos (`tests/test_claim_service.py`):**
- Testeamos la **creación de reclamos** y validamos que se asignen correctamente al departamento especificado.
- Verificamos la **lógica de adherencia**, asegurando que un usuario no pueda adherirse más de una vez al mismo reclamo.
- Probamos que **no se puedan crear reclamos con detalles vacíos**.

**Pruebas del Clasificador (`tests/test_classifier.py`, `tests/test_classifier_integration.py`):**
- Validamos que el **clasificador se entrene correctamente** con datos de ejemplo.
- Probamos la **clasificación de nuevos reclamos** y verificamos que retorne el departamento correcto.
- Testeamos la **persistencia del modelo** (guardado y carga desde disco).

**Pruebas de Similitud (`tests/test_similarity.py`):**
- Verificamos que el **algoritmo de similitud TF-IDF** detecte correctamente reclamos parecidos.
- Probamos el **threshold de similitud** para evitar falsos positivos.

**Pruebas de Notificaciones (`tests/test_notifications.py`):**
- Validamos que se **creen notificaciones automáticamente** cuando cambia el estado de un reclamo.
- Verificamos que los usuarios reciban notificaciones de los reclamos que crearon o a los que se adhirieron.

**Pruebas de Permisos (`tests/test_permissions.py`):**
- Testeamos que los **usuarios finales no puedan acceder a rutas administrativas**.
- Verificamos que los **jefes de departamento solo vean reclamos de su área**.

**Pruebas de Reportes (`tests/test_reports.py`):**
- Probamos la **generación de reportes PDF** con estadísticas correctas.
- Validamos el **filtrado por departamento** y el cálculo de métricas (total, pendientes, resueltos, tiempo promedio).

**Pruebas de Transferencias (`tests/test_transfers.py`):**
- Verificamos que los **reclamos se transfieran correctamente** entre departamentos.
- Validamos que se **registre el historial** de transferencias.

Usamos una **base de datos SQLite en memoria** (`sqlite:///:memory:`) para mantener aisladas las pruebas y no depender del entorno de producción.

Implementamos una clase base **`BaseTestCase`** en `tests/conftest.py` que configura el entorno de pruebas con `setUp()` y limpia con `tearDown()`, siguiendo las mejores prácticas de unittest.

---

## 7. Cumplimiento de Requisitos y Posibles Mejoras

El sistema cumple con **todos los requisitos funcionales**:
- ✅ Creación de reclamos con clasificación automática
- ✅ Adhesión a reclamos existentes
- ✅ Detección de reclamos similares
- ✅ Gestión administrativa por departamento
- ✅ Transferencia entre departamentos
- ✅ Notificaciones en tiempo real
- ✅ Generación de reportes con estadísticas
- ✅ Control de acceso por roles

### Posibles Mejoras Futuras

- **Notificaciones por email**: Enviar emails automáticos cuando cambia el estado de un reclamo.
- **Filtros avanzados**: Permitir búsqueda por rango de fechas, múltiples estados, palabras clave.
- **Dashboard con gráficos interactivos**: Agregar gráficos dinámicos con Chart.js o Plotly.
- **API REST**: Exponer endpoints REST para integración con otras aplicaciones.
- **Carga de imágenes**: Permitir adjuntar fotos de los desperfectos (ya hay una estructura básica en `ImageService`).
- **Autorización más granular**: Implementar permisos más detallados (ej: moderadores que pueden editar pero no eliminar).
- **Internacionalización**: Soporte multiidioma con Flask-Babel.

---

## 8. Demostración

Ahora, si les parece, les muestro el sistema funcionando:

### 8.1. Registro y Login de Usuarios

Voy a registrar un nuevo usuario final como estudiante:
- Navego a `/auth/register`
- Completo el formulario con nombre, apellido, email, username, contraseña y claustro
- El sistema valida los datos y crea la cuenta
- Inicio sesión con las credenciales

### 8.2. Creación de Reclamo

Como usuario final logueado:
- Navego a `/claims/create`
- Escribo el detalle del reclamo: "Se rompió la ventana del aula 102"
- El sistema **clasifica automáticamente** el reclamo y lo asigna al departamento de Infraestructura
- Puedo subir una imagen del problema (opcional)
- El reclamo se crea con estado PENDING

### 8.3. Detección de Similitud y Adhesión

Voy a crear otro reclamo similar:
- Detalle: "La ventana del aula 102 está rota"
- El sistema **detecta que hay un reclamo similar** ya existente
- Me sugiere adherirme en lugar de crear uno duplicado
- Me adhiero al reclamo existente
- El contador de adherentes aumenta

### 8.4. Panel de Administración

Ahora inicio sesión como jefe del departamento de Infraestructura:
- Navego a `/admin/dashboard`
- Veo estadísticas del departamento: total de reclamos, pendientes, en progreso, resueltos
- Veo la lista de reclamos de mi departamento en `/admin/claims`
- Selecciono un reclamo y veo su detalle completo con historial de cambios
- Cambio el estado de PENDING a IN_PROGRESS
- El sistema **crea una notificación automática** para el creador del reclamo

### 8.5. Transferencia de Reclamo

Si determino que el reclamo corresponde a otro departamento:
- Desde el detalle del reclamo, selecciono "Transferir"
- Elijo el departamento destino (ej: Servicios Generales)
- Agrego un motivo: "Este reclamo corresponde a mantenimiento de mobiliario"
- El reclamo se transfiere y se registra en el historial

### 8.6. Notificaciones

Como usuario final:
- Navego a `/users/notifications`
- Veo todas las notificaciones de mis reclamos
- Veo que el reclamo cambió de PENDING a IN_PROGRESS
- Marco las notificaciones como leídas

### 8.7. Exportación de Reportes

Como administrador:
- Navego a `/admin/reports`
- Selecciono el departamento y el rango de fechas
- Genero un reporte en PDF
- El PDF contiene estadísticas, gráficos y listado de reclamos

### 8.8. Control de Acceso y Manejo de Errores

Demuestro la seguridad del sistema:
- Intento acceder a `/admin/dashboard` como usuario final → **Redirige a la página principal**
- Intento adherirme dos veces al mismo reclamo → **Muestra error: "Ya estás adherido a este reclamo"**
- Intento crear un reclamo con detalle vacío → **Muestra error: "El detalle no puede estar vacío"**

---

## Resumen Final

En resumen, el sistema de gestión de reclamos:

- **Resuelve un problema real** de la facultad: gestionar reclamos de forma organizada
- **Aplica principios de OOP**: herencia, polimorfismo, encapsulamiento, composición
- **Sigue principios SOLID**: SRP, DIP, Open/Closed
- **Utiliza Machine Learning**: TF-IDF + Naive Bayes para clasificación automática
- **Implementa seguridad robusta**: autenticación, control de acceso por roles, contraseñas encriptadas
- **Está bien testeado**: pruebas unitarias con unittest siguiendo patrón AAA
- **Es escalable y mantenible**: arquitectura en capas, modularidad, bajo acoplamiento

Gracias por su atención. ¿Tienen alguna pregunta?

---

## Notas de Apoyo (No leer, solo referencia)

### Archivos Clave a Mencionar

- **Diagrama de clases:** `docs/class.puml`
- **Modelos:** `app/models/user/base.py`, `end_user.py`, `admin_user.py`, `claim.py`, `department.py`
- **Servicios:** `app/services/claim_service.py`, `classifier_service.py`, `similarity_service.py`, `notification_service.py`, `report_service.py`
- **Rutas:** `app/routes/claims.py`, `admin.py`, `auth/end_user.py`, `auth/admin.py`
- **Tests:** `tests/test_claim_service.py`, `tests/test_classifier.py`, `tests/test_permissions.py`
- **Configuración:** `run.py` (punto de entrada), `app/__init__.py` (factory pattern)

### Conceptos Clave a Mencionar

- Single Table Inheritance (User → EndUser/AdminUser)
- Composición con cascade="all, delete-orphan"
- Relación muchos a muchos (ClaimSupporter)
- TF-IDF + Naive Bayes Multinomial
- Similitud del coseno
- Patrón AAA en tests
- unittest con setUp/tearDown
- Flask-Login para autenticación
- SQLAlchemy ORM
- Principios SOLID (especialmente SRP y DIP)
