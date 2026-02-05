# Sistema de Gestión de Reclamos - Universidad

Sistema web para gestionar reclamos universitarios con clasificación automática, búsqueda por similitud, y reportes estadísticos.

## Características

- 🔐 Autenticación de usuarios (usuarios finales y administradores)
- 📝 Creación y seguimiento de reclamos con imágenes
- 🤖 Clasificación automática de reclamos por departamento (ML)
- 🔍 Búsqueda de reclamos similares (TF-IDF)
- 👥 Sistema de soporte entre usuarios
- 🔔 Notificaciones en tiempo real
- 📊 Analytics y estadísticas (gráficos, wordclouds)
- 📋 Generación de reportes (HTML/PDF)
- 👔 Panel administrativo con roles y permisos

## Requisitos del Sistema

### Python
- Python 3.8 o superior

### Dependencias
Todas las dependencias son puras Python y funcionan en Windows, Linux y macOS sin requerir instalación de bibliotecas del sistema.

## Instalación y Configuración

1.  **Extraer el archivo ZIP** en la ubicación deseada y abrir una terminal en esa carpeta.

2.  **Crear un entorno virtual:**
    ```bash
    python -m venv venv
    ```

3.  **Activar el entorno virtual:**
    *   Windows (PowerShell):
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    *   Windows (CMD):
        ```cmd
        venv\Scripts\activate.bat
        ```
    *   macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Inicializar la base de datos:**
    ```bash
    python init_db.py
    ```
    Esto crea la estructura de la base de datos y los departamentos iniciales.

6.  **Cargar datos de prueba:**
    ```bash
    python seed_db.py
    ```
    Crea usuarios de prueba y reclamos de ejemplo para explorar el sistema.

7.  **Entrenar el clasificador ML:**
    ```bash
    python train_classifier.py
    ```
    Entrena el modelo de clasificación automática de reclamos. Sin este paso, los reclamos se asignarán a Secretaría Técnica por defecto.

## Ejecutar la Aplicación

1.  **Ejecutar el servidor:**
    ```bash
    python run.py
    ```

2.  **Abrir en el navegador:**
    ```
    http://127.0.0.1:5000
    ```

## Usuarios de Prueba (después de `seed_db.py`)

### Usuarios Finales
- **Username:** `user1` / **Password:** `user123`
- **Username:** `user2` / **Password:** `user123`
- **Username:** `user3` / **Password:** `user123`
- **Username:** `user4` / **Password:** `user123`

### Administradores (en /admin/login)
- **Secretario Técnico:**
  - **Username:** `secretario_tecnico` / **Password:** `admin123`
- **Jefes de Departamento:**
  - **Username:** `jefe_mantenimiento` / **Password:** `admin123`
  - **Username:** `jefe_infraestructura` / **Password:** `admin123`
  - **Username:** `jefe_sistemas` / **Password:** `admin123`

## Estructura del Proyecto

```
TP_FINAL_SOL/
├── modules/
│   ├── __init__.py              # Package init
│   ├── config.py                # Fábrica de la aplicación y extensiones
│   ├── routes.py                # Rutas consolidadas (sin blueprints)
│   ├── models/                  # Modelos de base de datos
│   │   ├── claim.py            # Modelo de reclamos
│   │   ├── department.py       # Modelo de departamentos
│   │   ├── user/               # Modelos de usuarios (ABC + STI)
│   │   │   ├── base.py        # Clase base abstracta
│   │   │   ├── end_user.py    # Usuario final
│   │   │   └── admin_user.py  # Usuario administrador
│   │   ├── claim_supporter.py  # Adherentes a reclamos
│   │   ├── claim_status_history.py  # Historial de estados
│   │   ├── claim_transfer.py   # Transferencias entre departamentos
│   │   └── user_notification.py # Notificaciones
│   ├── services/                # Lógica de negocio
│   │   ├── claim_service.py
│   │   ├── classifier_service.py
│   │   ├── similarity_service.py
│   │   ├── analytics_service.py
│   │   ├── report_service.py   # Reportes (ABC: HTMLReport, PDFReport)
│   │   ├── department_service.py
│   │   ├── notification_service.py
│   │   ├── image_service.py
│   │   ├── transfer_service.py
│   │   ├── admin_claim_service.py
│   │   └── user_service.py
│   └── utils/                   # Utilidades compartidas
│       ├── constants.py        # Constantes (stopwords, PDF_CSS)
│       ├── text.py             # Procesamiento de texto
│       └── decorators.py       # Decoradores de permisos
├── templates/                   # Plantillas Jinja2
│   ├── base.html
│   ├── index.html
│   ├── claims/
│   ├── users/
│   ├── admin/
│   ├── auth/
│   └── reports/
├── tests/                       # Tests unitarios
├── docs/                        # Documentación
├── data/                        # Modelos ML entrenados
├── static/
│   └── uploads/                 # Archivos subidos
│       └── claims/
├── instance/                    # Base de datos SQLite
├── run.py                       # Punto de entrada
├── server.py                    # Punto de entrada alternativo
├── init_db.py                   # Inicializar DB
├── seed_db.py                   # Datos de prueba
├── train_classifier.py          # Entrenar clasificador
├── requirements.txt             # Dependencias
└── README.md
```

## Testing

Ejecutar todos los tests:
```bash
pytest tests/ -v
```

Ejecutar tests específicos:
```bash
pytest tests/test_claims.py -v
pytest tests/test_analytics.py -v
pytest tests/test_reports.py -v
```

## Tecnologías

- **Backend:** Flask, SQLAlchemy, Flask-Login
- **Frontend:** Jinja2, Bootstrap, CSS
- **ML:** scikit-learn (TF-IDF, clasificación)
- **Visualización:** matplotlib, wordcloud
- **PDF:** xhtml2pdf (multiplataforma, puro Python)
- **Testing:** pytest

## Funcionalidades Principales

### Para Usuarios Finales
- Crear reclamos con descripción e imagen
- Ver reclamos propios y su historial de estados
- Buscar reclamos similares antes de crear uno nuevo
- Apoyar reclamos de otros usuarios
- Recibir notificaciones de cambios de estado

### Para Administradores
- Dashboard con estadísticas y gráficos
- Gestión de reclamos por departamento
- Cambio de estados y transferencias
- Analytics con wordclouds y gráficos circulares
- Generación de reportes HTML/PDF
- Vista global (Secretaría Técnica) o por departamento (Jefes)

## Notas Importantes

### Clasificador ML
- El clasificador requiere entrenamiento inicial con `train_classifier.py`
- Sin modelo entrenado, los reclamos se asignan a Secretaría Técnica por defecto
- El clasificador mejora con más datos de entrenamiento

### Generación de Reportes
- Soporta formatos HTML y PDF
- xhtml2pdf funciona en todas las plataformas (Windows, Linux, macOS)
- Los reportes HTML pueden imprimirse a PDF desde el navegador si lo prefiere
