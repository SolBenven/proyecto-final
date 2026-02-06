from modules.config import create_app, db

# Importar todos los modelos para que SQLAlchemy los reconozca
from modules.admin_user import AdminUser
from modules.claim import Claim
from modules.claim_status_history import ClaimStatusHistory
from modules.claim_supporter import ClaimSupporter
from modules.claim_transfer import ClaimTransfer
from modules.department import Department
from modules.end_user import EndUser
from modules.user import User
from modules.user_notification import UserNotification

app = create_app()

with app.app_context():
    db.create_all()
    print("Base de datos inicializada y tablas creadas correctamente.")
