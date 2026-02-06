from __future__ import annotations

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

    @staticmethod
    def get_by_username(username: str) -> User | None:
        return db.session.query(User).filter_by(username=username).first()

    @staticmethod
    def get_by_email(email: str) -> User | None:
        return db.session.query(User).filter_by(email=email).first()

    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        user = db.session.get(User, user_id)
        if user is not None:
            print(f"Se obtuvo al usuario: {user.full_name}")
        return user

    @staticmethod
    def email_exists(email: str) -> bool:
        """Verifica si el email ya está registrado"""
        return User.query.filter_by(email=email).first() is not None

    @staticmethod
    def username_exists(username: str) -> bool:
        """Verifica si el nombre de usuario ya está registrado"""
        return User.query.filter_by(username=username).first() is not None

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.username}>"
