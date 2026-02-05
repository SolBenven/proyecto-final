"""
Consolidated routes module.
All routes are registered directly with the app using explicit endpoints to maintain
compatibility with existing url_for calls and templates.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import cast

from flask import (
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from modules.config import app, db, login_manager
from modules.models.claim import Claim, ClaimStatus
from modules.models.user import AdminUser, Cloister, EndUser, User
from modules.models.user.admin_user import AdminRole
from modules.services.admin_claim_service import AdminClaimService
from modules.services.analytics_service import AnalyticsService
from modules.services.claim_service import ClaimService
from modules.services.department_service import DepartmentService
from modules.services.image_service import ImageService
from modules.services.notification_service import NotificationService
from modules.services.similarity_service import similarity_service
from modules.services.transfer_service import TransferService
from modules.services.user_service import UserService
from modules.utils.decorators import (
    admin_required,
    admin_role_required,
    can_manage_claim,
    end_user_required,
)


# ============================================================
# User Loader and Context Processors
# ============================================================


@login_manager.user_loader
def load_user(user_id):
    """Carga cualquier tipo de usuario por ID"""
    return UserService.get_by_id(int(user_id))


@app.context_processor
def inject_notifications():
    """Inyecta el contador de notificaciones no leídas en todos los templates"""
    if current_user.is_authenticated:
        unread_count = NotificationService.get_unread_count(current_user.id)
        return {"unread_notifications_count": unread_count}
    return {"unread_notifications_count": 0}


# ============================================================
# Uploads Route
# ============================================================


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Sirve archivos subidos desde la carpeta static/uploads"""
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
    return send_from_directory(uploads_dir, filename)


# ============================================================
# Main Routes (endpoint: main.*)
# ============================================================


@app.route("/", endpoint="main.index")
@login_required
def index():
    return render_template("index.html", user=current_user)


# ============================================================
# Auth - End User Routes (endpoint: auth.end_user.*)
# ============================================================


@app.route("/register", methods=["GET"], endpoint="auth.end_user.register")
def register():
    return render_template("auth/register.html")


@app.route("/register", methods=["POST"], endpoint="auth.end_user.register_post")
def register_post():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    username = request.form["username"]
    cloister_value = request.form["cloister"]
    password = request.form["password"]
    repeated_password = request.form["repeated_password"]

    if password != repeated_password:
        flash("Las contraseñas no coinciden.", "error")
        return redirect(url_for("auth.end_user.register"))

    # Convertir cloister a enum
    try:
        cloister = Cloister(cloister_value)
    except ValueError:
        flash("Claustro Inválido", "error")
        return render_template("auth/register.html")

    # Registrar usuario final
    user, error = UserService.register_end_user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=username,
        cloister=cloister,
        password=password,
    )

    if error:
        flash(error, "error")
        return render_template("auth/register.html")

    flash("Usuario registrado exitosamente. Por favor inicie sesión.", "success")
    return redirect(url_for("auth.end_user.login"))


@app.route("/login", methods=["GET"], endpoint="auth.end_user.login")
def login():
    return render_template("auth/login.html")


@app.route("/login", methods=["POST"], endpoint="auth.end_user.login_post")
def login_post():
    username = request.form["username"]
    password = request.form["password"]

    user = UserService.authenticate_end_user(username, password)

    if user:
        login_user(user)
        flash("Has iniciado sesión correctamente", "success")
        return redirect(url_for("main.index"))

    flash("Nombre de usuario o contraseña incorrectos.", "error")
    return redirect(url_for("auth.end_user.login"))


@app.route("/logout", methods=["GET", "POST"], endpoint="auth.end_user.logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión", "info")
    return redirect(url_for("main.index"))


# ============================================================
# Auth - Admin Routes (endpoint: auth.admin.*)
# ============================================================


@app.route("/admin/login", methods=["GET"], endpoint="auth.admin.login")
def admin_login():
    if current_user.is_authenticated and isinstance(current_user, AdminUser):
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/login.html")


@app.route("/admin/login", methods=["POST"], endpoint="auth.admin.login_post")
def admin_login_post():
    username = request.form["username"]
    password = request.form["password"]

    user = UserService.authenticate_admin_user(username, password)

    if user:
        login_user(user)
        flash("Has iniciado sesión correctamente", "success")
        return redirect(url_for("admin.dashboard"))

    flash("Usuario o contraseña incorrectos", "error")
    return redirect(url_for("auth.admin.login"))


# ============================================================
# Admin Panel Routes (endpoint: admin.*)
# ============================================================


@app.route("/admin/", endpoint="admin.dashboard")
@admin_required
def admin_dashboard():
    """Dashboard de administración."""
    admin_user = cast(AdminUser, current_user)
    departments = DepartmentService.get_departments_for_admin(admin_user)
    department_ids = [d.id for d in departments]

    dashboard_counts = ClaimService.get_dashboard_counts(department_ids=department_ids)

    per_dept_counts = ClaimService.get_department_dashboard_counts(department_ids)
    dept_stats = [
        {
            "department": dept,
            "total": per_dept_counts.get(dept.id, {}).get("total", 0),
            "pending": per_dept_counts.get(dept.id, {}).get("pending", 0),
            "in_progress": per_dept_counts.get(dept.id, {}).get("in_progress", 0),
            "resolved": per_dept_counts.get(dept.id, {}).get("resolved", 0),
            "invalid": per_dept_counts.get(dept.id, {}).get("invalid", 0),
        }
        for dept in departments
    ]

    return render_template(
        "admin/dashboard.html",
        dept_stats=dept_stats,
        is_technical_secretary=admin_user.is_technical_secretary,
        **dashboard_counts,
    )


@app.route("/admin/help", endpoint="admin.help")
@admin_required
def admin_help():
    """Página de ayuda del panel de administración."""
    return render_template("admin/help.html")


@app.route("/admin/claims", endpoint="admin.claims_list")
@admin_required
def admin_claims_list():
    """Lista de reclamos visibles para el usuario admin."""
    admin_user = cast(AdminUser, current_user)
    claims = AdminClaimService.get_claims_for_admin(admin_user)

    supporters_ids_by_claim = {
        claim.id: [supporter.user_id for supporter in claim.supporters]
        for claim in claims
    }

    return render_template(
        "admin/claims_list.html",
        claims=claims,
        supporters_ids_by_claim=supporters_ids_by_claim,
    )


@app.route("/admin/claims/<int:claim_id>", endpoint="admin.claim_detail")
@admin_required
def admin_claim_detail(claim_id: int):
    """Detalle de un reclamo para administración."""
    admin_user = cast(AdminUser, current_user)
    claim = AdminClaimService.get_claim_for_admin(admin_user, claim_id)

    if claim is None:
        flash("Reclamo no encontrado o sin permisos para verlo", "error")
        return redirect(url_for("admin.claims_list"))

    supporters_ids = [supporter.user_id for supporter in claim.supporters]

    # Obtener departamentos disponibles para derivación (si es secretario técnico)
    available_departments = []
    can_transfer = TransferService.can_transfer(admin_user)
    if can_transfer:
        available_departments = TransferService.get_available_departments_for_transfer(
            claim.department_id
        )

    # Obtener historial de transferencias
    transfers = TransferService.get_transfer_history(claim.id)

    return render_template(
        "admin/claim_detail.html",
        claim=claim,
        supporters_ids=supporters_ids,
        can_transfer=can_transfer,
        available_departments=available_departments,
        transfers=transfers,
    )


@app.route("/admin/analytics", endpoint="admin.analytics")
@admin_role_required(AdminRole.DEPARTMENT_HEAD, AdminRole.TECHNICAL_SECRETARY)
def admin_analytics():
    """Página de analíticas y estadísticas de reclamos."""
    admin_user = cast(AdminUser, current_user)
    departments = DepartmentService.get_departments_for_admin(admin_user)
    department_ids = [d.id for d in departments]

    # Obtener todas las analíticas
    analytics_data = AnalyticsService.get_full_analytics(department_ids)

    return render_template(
        "admin/analytics.html",
        stats=analytics_data["stats"],
        pie_chart=analytics_data["pie_chart"],
        wordcloud=analytics_data["wordcloud"],
        keywords=analytics_data["keywords"],
        departments=departments,
        is_technical_secretary=admin_user.is_technical_secretary,
    )


@app.route("/admin/reports", endpoint="admin.reports")
@admin_role_required(AdminRole.DEPARTMENT_HEAD, AdminRole.TECHNICAL_SECRETARY)
def admin_reports():
    """Página de reportes con opciones de descarga."""
    admin_user = cast(AdminUser, current_user)
    departments = DepartmentService.get_departments_for_admin(admin_user)

    return render_template(
        "admin/reports.html",
        departments=departments,
        is_technical_secretary=admin_user.is_technical_secretary,
    )


@app.route("/admin/reports/download", endpoint="admin.download_report")
@admin_role_required(AdminRole.DEPARTMENT_HEAD, AdminRole.TECHNICAL_SECRETARY)
def admin_download_report():
    """Descarga el reporte en el formato especificado."""
    from modules.services.report_service import create_report

    admin_user = cast(AdminUser, current_user)
    departments = DepartmentService.get_departments_for_admin(admin_user)
    department_ids = [d.id for d in departments]

    report_format = request.args.get("format", "html")
    report = create_report(report_format, department_ids, admin_user.is_technical_secretary)
    content = report.generate()

    if report_format == "pdf":
        if content is None:
            flash(
                "No se pudo generar el PDF. Verifica que xhtml2pdf esté instalado correctamente.",
                "error",
            )
            return redirect(url_for("admin.reports"))

        return Response(
            content,
            mimetype="application/pdf",
            headers={
                f"Content-Disposition": f"attachment; filename=reporte_reclamos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            },
        )
    else:
        return Response(
            content,
            mimetype="text/html",
            headers={
                f"Content-Disposition": f"attachment; filename=reporte_reclamos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            },
        )


@app.route(
    "/admin/claims/<int:claim_id>/transfers",
    methods=["POST"],
    endpoint="admin.create_transfer",
)
@admin_role_required(AdminRole.TECHNICAL_SECRETARY)
def admin_create_transfer(claim_id: int):
    """Crear una nueva derivación (transferencia) del reclamo."""
    admin_user = cast(AdminUser, current_user)

    # Verificar que el reclamo existe y el admin puede verlo
    claim = AdminClaimService.get_claim_for_admin(admin_user, claim_id)
    if claim is None:
        flash("Reclamo no encontrado", "error")
        return redirect(url_for("admin.claims_list"))

    # Obtener datos del formulario
    to_department_id = request.form.get("department_id", type=int)
    reason = request.form.get("reason", "").strip()

    if not to_department_id:
        flash("Debe seleccionar un departamento destino", "error")
        return redirect(url_for("admin.claim_detail", claim_id=claim_id))

    # Realizar la derivación
    transfer, error = TransferService.transfer_claim(
        claim_id=claim_id,
        to_department_id=to_department_id,
        transferred_by_id=admin_user.id,
        reason=reason,
    )

    if error:
        flash(f"Error al derivar reclamo: {error}", "error")
    else:
        flash("Reclamo derivado exitosamente", "success")

    return redirect(url_for("admin.claim_detail", claim_id=claim_id))


@app.route(
    "/admin/claims/<int:claim_id>/transfers",
    methods=["GET"],
    endpoint="admin.get_transfers",
)
@admin_required
def admin_get_transfers(claim_id: int):
    """Ver historial de derivaciones de un reclamo."""
    admin_user = cast(AdminUser, current_user)

    # Verificar que el reclamo existe y el admin puede verlo
    claim = AdminClaimService.get_claim_for_admin(admin_user, claim_id)
    if claim is None:
        flash("Reclamo no encontrado", "error")
        return redirect(url_for("admin.claims_list"))

    transfers = TransferService.get_transfer_history(claim_id)

    return render_template(
        "admin/transfers.html",
        claim=claim,
        transfers=transfers,
    )


# ============================================================
# Claims Routes (endpoint: claims.*)
# ============================================================


@app.route("/claims", methods=["GET"], endpoint="claims.list")
def claims_list():
    """Lista todos los reclamos con filtros opcionales"""
    # Obtener filtros de query params
    department_filter = request.args.get("department", type=int)
    status_filter = request.args.get("status", type=str)

    # Convertir status_filter a enum si existe
    status_enum = None
    if status_filter:
        try:
            status_enum = ClaimStatus[status_filter.upper()]
        except KeyError:
            flash("Estado de reclamo no válido", "error")

    # Obtener reclamos
    claims = ClaimService.get_all_claims(
        department_filter=department_filter, status_filter=status_enum
    )

    # Obtener departamentos para el filtro
    departments = DepartmentService.get_all_departments()

    return render_template(
        "claims/list.html",
        claims=claims,
        departments=departments,
        selected_department=department_filter,
        selected_status=status_filter,
    )


@app.route("/claims/new", methods=["GET"], endpoint="claims.new")
@login_required
def claims_new():
    """Muestra el formulario de creación de reclamo"""
    departments = DepartmentService.get_all_departments()
    return render_template("claims/create.html", departments=departments)


@app.route("/claims/preview", methods=["POST"], endpoint="claims.preview")
@login_required
def claims_preview():
    """
    Analiza un reclamo y detecta similares en TODOS los departamentos.
    La clasificación del departamento se hace durante la creación real.
    """
    detail = request.form.get("detail", "").strip()
    department_id = request.form.get("department_id", type=int)

    if not detail:
        flash("Debe proporcionar un detalle del reclamo", "error")
        return redirect(url_for("claims.new"))

    # Guardar imagen temporalmente si se proporcionó
    image_path = None
    if "image" in request.files:
        file = request.files["image"]
        if file and file.filename != "":
            saved_path, error = ImageService.save_claim_image(file)
            if error:
                flash(f"Error con la imagen: {error}", "warning")
            else:
                image_path = saved_path

    # Buscar reclamos similares en TODOS los departamentos
    similar_claims = similarity_service.find_similar_claims(text=detail)

    # Guardar datos en sesión para creación posterior
    session["pending_claim"] = {
        "detail": detail,
        "department_id": department_id,
        "image_path": image_path,
    }

    # Si el usuario especificó un departamento, obtenerlo para mostrar
    department = (
        DepartmentService.get_department_by_id(department_id) if department_id else None
    )

    return render_template(
        "claims/preview.html",
        detail=detail,
        department=department,
        similar_claims=similar_claims,
        image_path=image_path,
    )


@app.route("/claims", methods=["POST"], endpoint="claims.create")
@login_required
def claims_create():
    """Crea un nuevo reclamo (confirmación después de preview o creación directa)"""
    # Verificar si viene de preview (confirmación)
    from_preview = request.form.get("from_preview") == "true"

    if from_preview:
        # Recuperar datos de la sesión
        pending_claim = session.get("pending_claim")
        if not pending_claim:
            flash("Sesión expirada. Por favor, intente nuevamente.", "error")
            return redirect(url_for("claims.new"))

        detail = pending_claim.get("detail")
        department_id = pending_claim.get("department_id")
        image_path = pending_claim.get("image_path")

        # Limpiar sesión
        session.pop("pending_claim", None)
    else:
        # Creación directa (sin preview)
        detail = request.form.get("detail", "").strip()
        department_id = request.form.get("department_id", type=int)

        if not detail:
            flash("Debe proporcionar un detalle del reclamo", "error")
            return redirect(url_for("claims.new"))

        # Manejar imagen si se proporcionó
        image_path = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename != "":
                saved_path, error = ImageService.save_claim_image(file)
                if error:
                    flash(f"Error con la imagen: {error}", "warning")
                else:
                    image_path = saved_path

    # Crear el reclamo
    claim, error = ClaimService.create_claim(
        user_id=current_user.id,
        detail=detail,
        department_id=department_id,
        image_path=image_path,
    )

    if error or not claim:
        # Si hubo error y ya guardamos una imagen, eliminarla
        if image_path:
            ImageService.delete_claim_image(image_path)

        error = error or "Error al crear el reclamo"
        flash(error, "error")
        return redirect(url_for("claims.new"))

    flash(f"Reclamo #{claim.id} creado exitosamente", "success")
    return redirect(url_for("claims.detail", id=claim.id))


@app.route("/claims/<int:id>", methods=["GET"], endpoint="claims.detail")
def claims_detail(id: int):
    """Muestra el detalle de un reclamo"""
    claim = ClaimService.get_claim_by_id(id)

    if not claim:
        flash("Reclamo no encontrado", "error")
        return redirect(url_for("claims.list"))

    # Verificar si el usuario actual está adherido
    is_supporter = False
    if current_user.is_authenticated:
        is_supporter = ClaimService.is_user_supporter(id, current_user.id)

    return render_template("claims/detail.html", claim=claim, is_supporter=is_supporter)


@app.route("/claims/<int:id>/supporters", methods=["POST"], endpoint="claims.add_supporter")
@login_required
def claims_add_supporter(id: int):
    """Permite a un usuario adherirse a un reclamo"""
    success, error = ClaimService.add_supporter(claim_id=id, user_id=current_user.id)

    if error:
        flash(error, "error")
    else:
        flash("Te has adherido al reclamo exitosamente", "success")

    return redirect(url_for("claims.detail", id=id))


@app.route(
    "/claims/<int:id>/supporters/delete",
    methods=["POST"],
    endpoint="claims.remove_supporter",
)
@login_required
def claims_remove_supporter(id: int):
    """Permite a un usuario quitarse como adherente de un reclamo"""
    success, error = ClaimService.remove_supporter(claim_id=id, user_id=current_user.id)

    if error:
        flash(error, "error")
    else:
        flash("Has dejado de adherirte al reclamo", "success")

    return redirect(url_for("claims.detail", id=id))


@app.route("/claims/<int:id>/status", methods=["POST"], endpoint="claims.update_status")
@admin_required
def claims_update_status(id: int):
    """Actualiza el estado de un reclamo (solo admins)."""
    claim = ClaimService.get_claim_by_id(id)
    if not claim:
        flash("Reclamo no encontrado", "error")
        return redirect(url_for("claims.list"))

    if not can_manage_claim(claim):
        flash("No tienes permiso para gestionar este reclamo", "error")
        return redirect(url_for("claims.detail", id=id))

    new_status_str = request.form.get("status", "")

    if not new_status_str:
        flash("Debe proporcionar un estado", "error")
        return redirect(url_for("claims.detail", id=id))

    # Convertir el string a enum
    try:
        new_status = ClaimStatus[new_status_str.upper()]
    except KeyError:
        flash("Estado no válido", "error")
        return redirect(url_for("claims.detail", id=id))

    # Actualizar el estado
    success, error = AdminClaimService.update_claim_status_for_admin(
        current_user, id, new_status  # type: ignore
    )

    if error:
        flash(error, "error")
    else:
        flash("Estado actualizado correctamente", "success")

    return redirect(url_for("admin.claim_detail", claim_id=id))


# ============================================================
# Users Routes (endpoint: users.*)
# ============================================================


@app.route("/users/me/claims", methods=["GET"], endpoint="users.my_claims")
@end_user_required
def users_my_claims():
    """Muestra los reclamos creados por el usuario actual"""
    claims = ClaimService.get_user_claims(current_user.id)
    return render_template("users/my_claims.html", claims=claims)


@app.route(
    "/users/me/supported-claims", methods=["GET"], endpoint="users.my_supported_claims"
)
@end_user_required
def users_my_supported_claims():
    """Muestra los reclamos a los que el usuario está adherido"""
    claims = ClaimService.get_user_supported_claims(current_user.id)
    return render_template("users/my_supported_claims.html", claims=claims)


@app.route("/users/me/notifications", methods=["GET"], endpoint="users.notifications")
@end_user_required
def users_notifications():
    """Muestra las notificaciones pendientes del usuario"""
    pending_notifications = NotificationService.get_pending_notifications(
        current_user.id
    )
    return render_template(
        "users/notifications.html", notifications=pending_notifications
    )


@app.route(
    "/users/me/notifications/<int:notification_id>",
    methods=["POST"],
    endpoint="users.mark_notification_read",
)
@end_user_required
def users_mark_notification_read(notification_id):
    """Marca una notificación como leída (formulario POST)"""
    success, error = NotificationService.mark_notification_as_read(
        notification_id, current_user.id
    )

    if error:
        flash(error, "error")
    else:
        flash("Notificación marcada como leída", "success")

    return redirect(url_for("users.notifications"))


@app.route(
    "/users/me/notifications/mark-all-read",
    methods=["POST"],
    endpoint="users.mark_all_notifications_read",
)
@end_user_required
def users_mark_all_notifications_read():
    """Marca todas las notificaciones del usuario como leídas"""
    count = NotificationService.mark_all_as_read(current_user.id)
    flash(f"Se marcaron {count} notificaciones como leídas", "success")
    return redirect(request.referrer or url_for("users.notifications"))
