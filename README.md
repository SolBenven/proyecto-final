# Proyecto Flask SQLAlchemy

Esta es una configuración básica de una aplicación Flask con SQLAlchemy y plantillas Jinja, estructurada siguiendo buenas prácticas.

## Configuración

1.  **Crear un entorno virtual:**
    ```bash
    python -m venv venv
    ```

2.  **Activar el entorno virtual:**
    *   Windows (PowerShell):
        ```powershell
        .\venv\Scripts\Activate
        ```
    *   macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Inicializar la base de datos:**
    Ejecuta el script para crear las tablas en la base de datos.
    ```bash
    python init_db.py
    ```

## Ejecutar la Aplicación

1.  Ejecuta la aplicación:
    ```bash
    python run.py
    ```

2.  Abre tu navegador y ve a `http://127.0.0.1:5000`.

## Estructura del Proyecto

*   `app/`: Paquete principal de la aplicación.
    *   `__init__.py`: Fábrica de la aplicación (`create_app`).
    *   `extensions.py`: Inicialización de extensiones (ej. `db`).
    *   `models/`: Modelos de la base de datos.
        *   `user.py`: Modelo `User`.
    *   `routes/`: Blueprints y rutas.
        *   `main.py`: Rutas principales.
    *   `templates/`: Plantillas Jinja2 (en español).
*   `run.py`: Punto de entrada para ejecutar la aplicación.
*   `init_db.py`: Script para inicializar la base de datos.
*   `requirements.txt`: Dependencias de Python.
