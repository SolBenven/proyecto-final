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
from modules.admin_user import AdminRole, AdminUser
from modules.claim import Claim, ClaimStatus
from modules.claim_transfer import ClaimTransfer
from modules.department import Department
from modules.end_user import Cloister, EndUser
from modules.user import User
from modules.user_notification import UserNotification
from modules.admin_helper import AdminHelper
from modules.analytics_generator import AnalyticsGenerator
from modules.image_handler import ImageHandler
from modules.similarity import similarity_finder
from modules.utils.decorators import (
    admin_required,
    admin_role_required,
    can_manage_claim,
    end_user_required,
)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        unread_count = UserNotification.get_unread_count(current_user.id)
        return {"unread_notifications_count": unread_count}
    return {"unread_notifications_count": 0}


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    uploads_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "static", "uploads"
    )
    return send_from_directory(uploads_dir, filename)


@app.route("/", endpoint="main.index")
@login_required
def index():
    return render_template("index.html", user=current_user)


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
    try:
        cloister = Cloister(cloister_value)
    except ValueError:
        flash("Claustro Inválido", "error")
        return render_template("auth/register.html")
    user, error = EndUser.register(
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
    user = EndUser.authenticate(username, password)
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


@app.route("/admin/login", methods=["GET"], endpoint="auth.admin.login")
def admin_login():
    if current_user.is_authenticated and isinstance(current_user, AdminUser):
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/login.html")


@app.route("/admin/login", methods=["POST"], endpoint="auth.admin.login_post")
def admin_login_post():
    username = request.form["username"]
    password = request.form["password"]
    user = AdminUser.authenticate(username, password)
    if user:
        login_user(user)
        flash("Has iniciado sesión correctamente", "success")
        return redirect(url_for("admin.dashboard"))

    flash("Usuario o contraseña incorrectos", "error")
    return redirect(url_for("auth.admin.login"))


@app.route("/admin/", endpoint="admin.dashboard")
@admin_required
def admin_dashboard():
    admin_user = cast(AdminUser, current_user)
    departments = Department.get_for_admin(admin_user)
    department_ids = [d.id for d in departments]
    dashboard_counts = Claim.get_dashboard_counts(department_ids=department_ids)
    per_dept_counts = Claim.get_department_dashboard_counts(department_ids)
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
    return render_template("admin/help.html")


@app.route("/admin/claims", endpoint="admin.claims_list")
@admin_required
def admin_claims_list():
    admin_user = cast(AdminUser, current_user)
    claims = AdminHelper.get_claims_for_admin(admin_user)
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
    admin_user = cast(AdminUser, current_user)
    claim = AdminHelper.get_claim_for_admin(admin_user, claim_id)
    if claim is None:
        flash("Reclamo no encontrado o sin permisos para verlo", "error")
        return redirect(url_for("admin.claims_list"))
    supporters_ids = [supporter.user_id for supporter in claim.supporters]
    available_departments = []
    can_transfer = ClaimTransfer.can_transfer(admin_user)
    if can_transfer:
        available_departments = ClaimTransfer.get_available_departments(
            claim.department_id
        )
    transfers = ClaimTransfer.get_history_for_claim(claim.id)
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
    admin_user = cast(AdminUser, current_user)
    departments = Department.get_for_admin(admin_user)
    department_ids = [d.id for d in departments]

    analytics_data = AnalyticsGenerator.get_full_analytics(department_ids)

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
    admin_user = cast(AdminUser, current_user)
    departments = Department.get_for_admin(admin_user)

    return render_template(
        "admin/reports.html",
        departments=departments,
        is_technical_secretary=admin_user.is_technical_secretary,
    )


@app.route("/admin/reports/download", endpoint="admin.download_report")
@admin_role_required(AdminRole.DEPARTMENT_HEAD, AdminRole.TECHNICAL_SECRETARY)
def admin_download_report():
    from modules.report_generator import create_report

    admin_user = cast(AdminUser, current_user)
    departments = Department.get_for_admin(admin_user)
    department_ids = [d.id for d in departments]

    report_format = request.args.get("format", "html")
    report = create_report(
        report_format, department_ids, admin_user.is_technical_secretary
    )
    content = report.generate()
    content_type = "application/pdf" if report_format == "pdf" else "text/html"
    if content is None:
        flash(
            "No se pudo generar el reporte.",
            "error",
        )
        return redirect(url_for("admin.reports"))
    return Response(
        content,
        mimetype=content_type,
        headers={
            f"Content-Disposition": f"attachment; filename=reporte_reclamos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        },
    )


@app.route(
    "/admin/claims/<int:claim_id>/transfers",
    methods=["POST"],
    endpoint="admin.create_transfer",
)
@admin_role_required(AdminRole.TECHNICAL_SECRETARY)
def admin_create_transfer(claim_id: int):
    admin_user = cast(AdminUser, current_user)

    claim = AdminHelper.get_claim_for_admin(admin_user, claim_id)
    if claim is None:
        flash("Reclamo no encontrado", "error")
        return redirect(url_for("admin.claims_list"))

    to_department_id = request.form.get("department_id", type=int)
    reason = request.form.get("reason", "").strip()

    if not to_department_id:
        flash("Debe seleccionar un departamento destino", "error")
        return redirect(url_for("admin.claim_detail", claim_id=claim_id))

    transfer, error = ClaimTransfer.transfer(
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
    admin_user = cast(AdminUser, current_user)

    claim = AdminHelper.get_claim_for_admin(admin_user, claim_id)
    if claim is None:
        flash("Reclamo no encontrado", "error")
        return redirect(url_for("admin.claims_list"))

    transfers = ClaimTransfer.get_history_for_claim(claim_id)

    return render_template(
        "admin/transfers.html",
        claim=claim,
        transfers=transfers,
    )


@app.route("/claims", methods=["GET"], endpoint="claims.list")
def claims_list():
    department_filter = request.args.get("department", type=int)
    status_filter = request.args.get("status", type=str)

    status_enum = None
    if status_filter:
        try:
            status_enum = ClaimStatus[status_filter.upper()]
        except KeyError:
            flash("Estado de reclamo no válido", "error")

    claims = Claim.get_all_with_filters(
        department_filter=department_filter, status_filter=status_enum
    )

    departments = Department.get_all()

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
    departments = Department.get_all()
    return render_template("claims/create.html", departments=departments)


@app.route("/claims/preview", methods=["POST"], endpoint="claims.preview")
@login_required
def claims_preview():
    detail = request.form.get("detail", "").strip()
    department_id = request.form.get("department_id", type=int)

    if not detail:
        flash("Debe proporcionar un detalle del reclamo", "error")
        return redirect(url_for("claims.new"))

    image_path = None
    if "image" in request.files:
        file = request.files["image"]
        if file and file.filename != "":
            saved_path, error = ImageHandler.save_claim_image(file)
            if error:
                flash(f"Error con la imagen: {error}", "warning")
            else:
                image_path = saved_path

    similar_claims = similarity_finder.find_similar_claims(text=detail)

    session["pending_claim"] = {
        "detail": detail,
        "department_id": department_id,
        "image_path": image_path,
    }

    department = Department.get_by_id(department_id) if department_id else None

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
    from_preview = request.form.get("from_preview") == "true"

    if from_preview:
        pending_claim = session.get("pending_claim")
        if not pending_claim:
            flash("Sesión expirada. Por favor, intente nuevamente.", "error")
            return redirect(url_for("claims.new"))

        detail = pending_claim.get("detail")
        department_id = pending_claim.get("department_id")
        image_path = pending_claim.get("image_path")

        session.pop("pending_claim", None)
    else:
        detail = request.form.get("detail", "").strip()
        department_id = request.form.get("department_id", type=int)

        if not detail:
            flash("Debe proporcionar un detalle del reclamo", "error")
            return redirect(url_for("claims.new"))

        image_path = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename != "":
                saved_path, error = ImageHandler.save_claim_image(file)
                if error:
                    flash(f"Error con la imagen: {error}", "warning")
                else:
                    image_path = saved_path

    claim, error = Claim.create(
        user_id=current_user.id,
        detail=detail,
        department_id=department_id,
        image_path=image_path,
    )

    if error or not claim:
        if image_path:
            ImageHandler.delete_claim_image(image_path)

        error = error or "Error al crear el reclamo"
        flash(error, "error")
        return redirect(url_for("claims.new"))

    flash(f"Reclamo #{claim.id} creado exitosamente", "success")
    return redirect(url_for("claims.detail", id=claim.id))


@app.route("/claims/<int:id>", methods=["GET"], endpoint="claims.detail")
def claims_detail(id: int):
    claim = Claim.get_by_id(id)

    if not claim:
        flash("Reclamo no encontrado", "error")
        return redirect(url_for("claims.list"))

    is_supporter = False
    if current_user.is_authenticated:
        is_supporter = Claim.is_user_supporter(id, current_user.id)

    return render_template("claims/detail.html", claim=claim, is_supporter=is_supporter)


@app.route(
    "/claims/<int:id>/supporters", methods=["POST"], endpoint="claims.add_supporter"
)
@login_required
def claims_add_supporter(id: int):
    success, error = Claim.add_supporter(claim_id=id, user_id=current_user.id)

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
    success, error = Claim.remove_supporter(claim_id=id, user_id=current_user.id)

    if error:
        flash(error, "error")
    else:
        flash("Has dejado de adherirte al reclamo", "success")

    return redirect(url_for("claims.detail", id=id))


@app.route("/claims/<int:id>/status", methods=["POST"], endpoint="claims.update_status")
@admin_required
def claims_update_status(id: int):
    claim = Claim.get_by_id(id)
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

    try:
        new_status = ClaimStatus[new_status_str.upper()]
    except KeyError:
        flash("Estado no válido", "error")
        return redirect(url_for("claims.detail", id=id))

    success, error = AdminHelper.update_claim_status(
        current_user, id, new_status  # type: ignore
    )

    if error:
        flash(error, "error")
    else:
        flash("Estado actualizado correctamente", "success")

    return redirect(url_for("admin.claim_detail", claim_id=id))


@app.route("/users/me/claims", methods=["GET"], endpoint="users.my_claims")
@end_user_required
def users_my_claims():
    claims = Claim.get_by_user(current_user.id)
    return render_template("users/my_claims.html", claims=claims)


@app.route(
    "/users/me/supported-claims", methods=["GET"], endpoint="users.my_supported_claims"
)
@end_user_required
def users_my_supported_claims():
    claims = Claim.get_supported_by_user(current_user.id)
    return render_template("users/my_supported_claims.html", claims=claims)


@app.route("/users/me/notifications", methods=["GET"], endpoint="users.notifications")
@end_user_required
def users_notifications():
    pending_notifications = UserNotification.get_pending_for_user(current_user.id)
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
    success, error = UserNotification.mark_notification_as_read(
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
    count = UserNotification.mark_all_as_read_for_user(current_user.id)
    flash(f"Se marcaron {count} notificaciones como leídas", "success")
    return redirect(request.referrer or url_for("users.notifications"))
