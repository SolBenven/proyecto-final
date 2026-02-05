from abc import ABC, ABCMeta, abstractmethod
from sqlalchemy.orm import Mapped, mapped_column
from modules.config import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# Combinar metaclases de ABC y SQLAlchemy para evitar conflicto
class ABCModelMeta(ABCMeta, type(db.Model)):
    """Metaclase combinada para permitir ABC con SQLAlchemy Model."""
    pass


class User(UserMixin, db.Model, ABC, metaclass=ABCModelMeta):
    """Clase base abstracta para todos los usuarios (Single Table Inheritance)"""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    # Columna discriminadora para herencia
    user_type: Mapped[str] = mapped_column(nullable=False)

    __mapper_args__ = {"polymorphic_on": user_type, "polymorphic_identity": "user"}

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    @abstractmethod
    def full_name(self) -> str:
        """Retorna el nombre completo con información de rol/claustro.
        
        Debe ser implementado por las subclases EndUser y AdminUser.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.username}>"
