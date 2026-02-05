"""Decoradores de permisos para control de acceso basado en roles"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from modules.models.user import AdminUser, EndUser, AdminRole


def end_user_required(f):
    """
    Decorador que requiere usuario final (EndUser).
    Redirige a login de usuario final si no está autenticado.
    Redirige a admin dashboard si es usuario administrativo.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión para acceder a esta página", "error")
            return redirect(url_for("auth.end_user.login"))

        if not isinstance(current_user, EndUser):
            flash("Esta sección es solo para usuarios finales.", "error")
            return redirect(url_for("admin.dashboard"))

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorador que requiere usuario administrativo.
    Redirige a login de admin si no está autenticado.
    Redirige a home si es usuario final.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión como administrador", "error")
            return redirect(url_for("auth.admin.login"))

        if not isinstance(current_user, AdminUser):
            flash("Acceso denegado. Solo para administradores.", "error")
            return redirect(url_for("main.index"))

        return f(*args, **kwargs)

    return decorated_function


def admin_role_required(*roles: AdminRole):
    """
    Decorador para restringir acceso por rol administrativo específico.

    Args:
        *roles: Uno o más roles de AdminRole que tienen acceso

    Ejemplo:
        @admin_role_required(AdminRole.DEPARTMENT_HEAD, AdminRole.TECHNICAL_SECRETARY)
        def manage_claims():
            ...
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debes iniciar sesión como administrador", "error")
                return redirect(url_for("auth.admin.login"))

            if not isinstance(current_user, AdminUser):
                flash("Acceso denegado. Solo para administradores.", "error")
                return redirect(url_for("main.index"))

            if current_user.admin_role not in roles:
                flash("No tienes permisos para acceder a esta sección.", "error")
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def department_access_required(f):
    """
    Decorador para rutas que requieren acceso a un departamento específico.
    Verifica que:
    - El usuario sea admin
    - Si es jefe de departamento, solo puede acceder a su propio departamento
    - Si es secretaría técnica, tiene acceso a todos los departamentos

    Espera que la ruta tenga un parámetro 'department_id' en kwargs.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión como administrador", "error")
            return redirect(url_for("auth.admin.login"))

        if not isinstance(current_user, AdminUser):
            flash("Acceso denegado. Solo para administradores.", "error")
            return redirect(url_for("main.index"))

        dept_id = kwargs.get("department_id")

        if dept_id is None:
            # Si no hay department_id en la ruta, no se puede verificar
            abort(400)

        # Secretaría técnica tiene acceso a todo
        if current_user.is_technical_secretary:
            return f(*args, **kwargs)

        # Jefe de departamento solo a su departamento
        if current_user.is_department_head:
            if current_user.department_id != dept_id:
                flash("No tienes permiso para acceder a este departamento.", "error")
                abort(403)
            return f(*args, **kwargs)

        # Empleados no tienen acceso a rutas con department_id
        flash("No tienes permisos para acceder a esta sección.", "error")
        abort(403)

    return decorated_function


def can_manage_claim(claim):
    """
    Verifica si el usuario actual puede gestionar un reclamo específico.
    Útil para verificar permisos antes de mostrar acciones en templates.

    Args:
        claim: Instancia de Claim

    Returns:
        bool: True si puede gestionar el reclamo
    """
    if not isinstance(current_user, AdminUser):
        return False
    print(current_user.is_technical_secretary)
    # Secretaría técnica puede gestionar todos los reclamos
    if current_user.is_technical_secretary:
        return True

    # Jefe de departamento solo puede gestionar reclamos de su departamento
    if current_user.is_department_head:
        return current_user.department_id == claim.department_id

    # Empleados no gestionan reclamos
    return False
