from modules.config import create_app, db

# Importar todos los modelos para que SQLAlchemy los reconozca
from modules.models import (
    User,
    EndUser,
    AdminUser,
    Department,
    Claim,
    ClaimSupporter,
    ClaimStatusHistory,
    ClaimTransfer,
    UserNotification,
)

app = create_app()

with app.app_context():
    db.create_all()
    print("Base de datos inicializada y tablas creadas correctamente.")
