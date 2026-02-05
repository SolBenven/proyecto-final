from modules.models.user import User, EndUser, AdminUser, Cloister, AdminRole
from modules.config import db


class UserService:
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

    @staticmethod
    def register_end_user(
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        cloister: Cloister,
        password: str,
    ) -> tuple[EndUser | None, str | None]:
        """
        Registra un nuevo usuario final.
        Retorna (user, None) si exitoso, (None, error_message) si falla.
        """
        if UserService.email_exists(email):
            return None, "El email ya está registrado"

        if UserService.username_exists(username):
            return None, "El nombre de usuario ya está en uso"

        user = EndUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            cloister=cloister,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user, None

    @staticmethod
    def create_admin_user(
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        admin_role: AdminRole,
        password: str,
        department_id: int | None = None,
    ) -> tuple[AdminUser | None, str | None]:
        """
        Crea un nuevo usuario administrativo (solo por scripts de sistema).
        Retorna (user, None) si exitoso, (None, error_message) si falla.
        """
        if UserService.email_exists(email):
            return None, "El email ya está registrado"

        if UserService.username_exists(username):
            return None, "El nombre de usuario ya está en uso"

        user = AdminUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            admin_role=admin_role,
            department_id=department_id,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user, None

    @staticmethod
    def authenticate_end_user(username: str, password: str) -> EndUser | None:
        """Autentica un usuario final por username y password"""
        user = EndUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def authenticate_admin_user(username: str, password: str) -> AdminUser | None:
        """Autentica un usuario administrativo por username y password"""
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None
