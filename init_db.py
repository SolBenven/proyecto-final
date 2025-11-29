from app import create_app
from app.extensions import db

# Importar modelos para que SQLAlchemy los reconozca
from app.models.user import User

app = create_app()

with app.app_context():
    db.create_all()
    print("Base de datos inicializada y tablas creadas correctamente.")
