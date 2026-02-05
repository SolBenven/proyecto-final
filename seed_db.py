"""
Script para inicializar datos de prueba en la base de datos.
Ejecutar después de init_db.py para crear departamentos y usuarios admin.
"""

from modules.config import create_app, db
from modules.models import (
    Department,
    AdminUser,
    AdminRole,
    EndUser,
    Cloister,
    Claim,
    ClaimStatus,
)
from modules.services.claim_service import ClaimService


def clear_database():
    """Limpia todas las tablas de la base de datos para empezar de cero"""
    print("  Limpiando base de datos...")
    
    # Eliminar en orden inverso de dependencias para evitar problemas de FK
    from modules.models.user_notification import UserNotification
    from modules.models.claim_status_history import ClaimStatusHistory
    from modules.models.claim_supporter import ClaimSupporter
    from modules.models.claim_transfer import ClaimTransfer
    
    try:
        # Primero las tablas dependientes
        UserNotification.query.delete()
        ClaimStatusHistory.query.delete()
        ClaimSupporter.query.delete()
        ClaimTransfer.query.delete()
        
        # Luego los reclamos
        Claim.query.delete()
        
        # Usuarios (EndUser y AdminUser)
        EndUser.query.delete()
        AdminUser.query.delete()
        
        # Finalmente departamentos
        Department.query.delete()
        
        db.session.commit()
        print("  ✓ Base de datos limpiada exitosamente")
    except Exception as e:
        db.session.rollback()
        print(f"  ! Error al limpiar base de datos: {e}")
        raise


def create_departments():
    """Crea los departamentos iniciales del sistema"""
    departments_data = [
        {
            "name": "mantenimiento",
            "display_name": "Mantenimiento",
            "is_technical_secretariat": False,
        },
        {
            "name": "infraestructura",
            "display_name": "Infraestructura",
            "is_technical_secretariat": False,
        },
        {
            "name": "sistemas",
            "display_name": "Sistemas",
            "is_technical_secretariat": False,
        },
        {
            "name": "secretaria_tecnica",
            "display_name": "Secretaría Técnica",
            "is_technical_secretariat": True,
        },
    ]

    created = 0
    for dept_data in departments_data:
        existing = Department.query.filter_by(name=dept_data["name"]).first()
        if not existing:
            dept = Department(**dept_data)
            db.session.add(dept)
            created += 1
            print(f"  ✓ Departamento '{dept_data['display_name']}' creado")
        else:
            print(f"  - Departamento '{dept_data['display_name']}' ya existe")

    db.session.commit()
    return created


def create_admin_users():
    """Crea usuarios administrativos de prueba"""
    print("  2a. Creando secretario técnico...")

    # Crear secretario técnico
    secretaria = Department.query.filter_by(is_technical_secretariat=True).first()

    if secretaria:
        existing = AdminUser.query.filter_by(username="secretario_tecnico").first()
        if not existing:
            user = AdminUser(
                first_name="Secretario",
                last_name="Técnico",
                email="secretario@sistema.local",
                username="secretario_tecnico",
                admin_role=AdminRole.TECHNICAL_SECRETARY,
                department_id=secretaria.id,
            )
            user.set_password("admin123")
            db.session.add(user)
            db.session.commit()
            print(f"     ✓ Usuario 'secretario_tecnico' creado")
        else:
            print(f"     - Usuario 'secretario_tecnico' ya existe")

    print("  2b. Creando jefes de departamento...")

    # Crear jefes para cada departamento (excepto secretaría técnica)
    departments = Department.query.filter_by(is_technical_secretariat=False).all()
    created = 0

    for dept in departments:
        username = f"jefe_{dept.name}"
        email = f"jefe.{dept.name}@sistema.local"

        existing = AdminUser.query.filter_by(username=username).first()
        if not existing:
            user = AdminUser(
                first_name="Jefe",
                last_name=dept.display_name,
                email=email,
                username=username,
                admin_role=AdminRole.DEPARTMENT_HEAD,
                department_id=dept.id,
            )
            user.set_password("admin123")
            db.session.add(user)
            created += 1
            print(f"     ✓ Usuario '{username}' creado")
        else:
            print(f"     - Usuario '{username}' ya existe")

    db.session.commit()
    return created + (1 if secretaria and not existing else 0)


def create_end_users():
    """Crea usuarios finales de prueba"""
    end_users_data = [
        {
            "first_name": "User",
            "last_name": "One",
            "email": "user1@estudiante.local",
            "username": "user1",
            "cloister": Cloister.STUDENT,
            "password": "user123",
        },
        {
            "first_name": "User",
            "last_name": "Two",
            "email": "user2@docente.local",
            "username": "user2",
            "cloister": Cloister.TEACHER,
            "password": "user123",
        },
        {
            "first_name": "User",
            "last_name": "Three",
            "email": "user3@pays.local",
            "username": "user3",
            "cloister": Cloister.PAYS,
            "password": "user123",
        },
        {
            "first_name": "User",
            "last_name": "Four",
            "email": "user4@estudiante.local",
            "username": "user4",
            "cloister": Cloister.STUDENT,
            "password": "user123",
        },
    ]

    created = 0
    for user_data in end_users_data:
        existing = EndUser.query.filter_by(username=user_data["username"]).first()
        if not existing:
            password = user_data.pop("password")
            user = EndUser(**user_data)
            user.set_password(password)
            db.session.add(user)
            created += 1
            print(f"  ✓ Usuario '{user_data['username']}' creado")
        else:
            print(f"  - Usuario '{user_data['username']}' ya existe")

    db.session.commit()
    return created


def create_sample_claims():
    """Crea reclamos de prueba y actualiza estados usando servicios (genera notificaciones)."""

    # Usuarios finales: 10 reclamos por usuario
    end_users = (
        db.session.query(EndUser)
        .filter(EndUser.username.in_(["user1", "user2", "user3", "user4"]))
        .order_by(EndUser.username.asc())
        .all()
    )

    # Departamentos
    mantenimiento = db.session.query(Department).filter_by(name="mantenimiento").first()
    infraestructura = (
        db.session.query(Department).filter_by(name="infraestructura").first()
    )
    sistemas = db.session.query(Department).filter_by(name="sistemas").first()
    secretaria = (
        db.session.query(Department).filter_by(is_technical_secretariat=True).first()
    )

    if (
        not all([mantenimiento, infraestructura, sistemas, secretaria])
        or len(end_users) < 1
    ):
        print("  ! No se pueden crear reclamos: faltan usuarios o departamentos")
        return 0

    assert mantenimiento is not None
    assert infraestructura is not None
    assert sistemas is not None
    assert secretaria is not None

    # Admins (para registrar cambios de estado)
    secretario_tecnico = (
        db.session.query(AdminUser)
        .filter_by(admin_role=AdminRole.TECHNICAL_SECRETARY)
        .first()
    )
    jefe_mantenimiento = (
        db.session.query(AdminUser)
        .filter_by(admin_role=AdminRole.DEPARTMENT_HEAD, department_id=mantenimiento.id)
        .first()
    )
    jefe_infraestructura = (
        db.session.query(AdminUser)
        .filter_by(
            admin_role=AdminRole.DEPARTMENT_HEAD, department_id=infraestructura.id
        )
        .first()
    )
    jefe_sistemas = (
        db.session.query(AdminUser)
        .filter_by(admin_role=AdminRole.DEPARTMENT_HEAD, department_id=sistemas.id)
        .first()
    )

    if not all(
        [secretario_tecnico, jefe_mantenimiento, jefe_infraestructura, jefe_sistemas]
    ):
        print("  ! No se pueden actualizar estados: faltan usuarios administrativos")
        return 0

    assert secretario_tecnico is not None
    assert jefe_mantenimiento is not None
    assert jefe_infraestructura is not None
    assert jefe_sistemas is not None

    # Textos realistas por departamento (inspirados en train_classifier.py)
    dept_texts: dict[int, list[str]] = {
        mantenimiento.id: [
            "El aire acondicionado no funciona en el aula 301",
            "Se rompió la canilla del baño del segundo piso",
            "Las luces del pasillo están quemadas",
            "El ascensor hace ruidos extraños",
            "No sale agua caliente en los baños",
            "La puerta del salón no cierra correctamente",
            "El ventilador de techo no enciende",
            "Hay una gotera en el techo del laboratorio",
            "El inodoro del baño está tapado",
            "La cerradura de la puerta está rota",
            "No funciona la calefacción en invierno",
            "El agua del bebedero no sale",
            "La persiana del aula está atascada",
            "Hay humedad en las paredes del aula",
            "El extractor del baño no funciona",
        ],
        infraestructura.id: [
            "Hay grietas en la pared del aula 205",
            "El techo tiene filtraciones de agua",
            "Las baldosas del piso están rotas y peligrosas",
            "Se necesita pintar las paredes del edificio",
            "Faltan bancos en el aula magna",
            "La rampa de acceso está deteriorada",
            "El techo del patio tiene goteras",
            "Las escaleras están en mal estado",
            "Se cayó el revoque de la pared",
            "Los pisos necesitan ser reparados",
            "Faltan sillas en el salón de actos",
            "El banco del aula está roto",
            "La pintura de las aulas está descascarada",
            "El muro del patio tiene grietas",
            "Necesitamos más mesas en la biblioteca",
        ],
        sistemas.id: [
            "No hay internet en el laboratorio de informática",
            "La computadora del aula no enciende",
            "El proyector está fallando y se apaga",
            "No funciona el WiFi en el edificio B",
            "La impresora de la sala de profesores no imprime",
            "El sistema de sonido del auditorio no funciona",
            "No puedo acceder al campus virtual",
            "La red de internet está muy lenta",
            "El software de la computadora tiene virus",
            "No funciona el micrófono del salón",
            "La pantalla del proyector tiene líneas",
            "No se puede conectar la notebook al proyector",
            "El sistema de control de asistencia no funciona",
            "La cámara de videoconferencia no enciende",
            "No funciona el cable HDMI del proyector",
        ],
        secretaria.id: [
            "Mi reclamo fue mal derivado y nadie lo atiende desde hace un mes",
            "Necesito hablar con autoridades sobre un problema que no resuelven",
            "Quiero presentar una queja formal sobre el servicio",
            "El departamento de mantenimiento no responde mis reclamos",
            "Este problema afecta a múltiples áreas y necesita coordinación",
            "Necesito que revisen el historial de mi reclamo porque figura como Resuelto y sigue igual",
            "El problema se repite hace semanas y no hay respuesta",
            "Solicito intervención de secretaría técnica por falta de seguimiento",
            "El reclamo quedó en Pendiente demasiado tiempo sin novedades",
            "Nadie se hace cargo del problema y necesito una solución formal",
        ],
    }

    # Distribución de reclamos (total 40 = 4 usuarios * 10)
    # 10 reclamos por departamento (round-robin para mezclar por usuario)
    dept_cycle = [mantenimiento.id, infraestructura.id, sistemas.id, secretaria.id]
    dept_plan: list[int] = []
    for _ in range(10):
        dept_plan.extend(dept_cycle)

    dept_by_id = {
        mantenimiento.id: mantenimiento,
        infraestructura.id: infraestructura,
        sistemas.id: sistemas,
        secretaria.id: secretaria,
    }

    created = 0
    claims_by_dept: dict[int, list[int]] = {dept_id: [] for dept_id in dept_by_id}

    global_idx = 1
    for user in end_users:
        for i in range(1, 11):
            if len(dept_plan) == 0:
                break

            department_id = dept_plan.pop(0)
            dept = dept_by_id[department_id]

            base_texts = dept_texts.get(department_id, [])
            base_text = (
                base_texts[(global_idx - 1) % len(base_texts)]
                if len(base_texts) > 0
                else "Incidente reportado por el usuario"
            )

            detail = f"{base_text}"

            claim, error = ClaimService.create_claim(
                user_id=user.id,
                detail=detail,
                department_id=department_id,
                image_path=None,
            )
            if error or claim is None:
                print(f"  ! Error creando reclamo: {error}")
                continue

            created += 1
            claims_by_dept[department_id].append(claim.id)
            global_idx += 1

    # Actualizar estados por departamento (usando ClaimService para generar notificaciones)
    def _apply_statuses(
        claim_ids: list[int],
        admin_user_id: int,
        invalid_n: int,
        resolved_n: int,
        in_progress_n: int,
    ) -> None:
        if len(claim_ids) == 0:
            return

        idx = 0
        for _ in range(min(invalid_n, len(claim_ids) - idx)):
            ClaimService.update_claim_status(
                claim_id=claim_ids[idx],
                new_status=ClaimStatus.INVALID,
                admin_user_id=admin_user_id,
            )
            idx += 1

        for _ in range(min(resolved_n, len(claim_ids) - idx)):
            ClaimService.update_claim_status(
                claim_id=claim_ids[idx],
                new_status=ClaimStatus.RESOLVED,
                admin_user_id=admin_user_id,
            )
            idx += 1

        for _ in range(min(in_progress_n, len(claim_ids) - idx)):
            ClaimService.update_claim_status(
                claim_id=claim_ids[idx],
                new_status=ClaimStatus.IN_PROGRESS,
                admin_user_id=admin_user_id,
            )
            idx += 1

    _apply_statuses(
        claims_by_dept[mantenimiento.id],
        jefe_mantenimiento.id,
        invalid_n=1,
        resolved_n=3,
        in_progress_n=2,
    )
    _apply_statuses(
        claims_by_dept[infraestructura.id],
        jefe_infraestructura.id,
        invalid_n=1,
        resolved_n=3,
        in_progress_n=2,
    )
    _apply_statuses(
        claims_by_dept[sistemas.id],
        jefe_sistemas.id,
        invalid_n=1,
        resolved_n=3,
        in_progress_n=2,
    )
    _apply_statuses(
        claims_by_dept[secretaria.id],
        secretario_tecnico.id,
        invalid_n=1,
        resolved_n=3,
        in_progress_n=2,
    )

    return created


def main():
    app = create_app()

    with app.app_context():
        print("\n=== Inicializando datos de prueba ===\n")
        
        print("0. Limpiando base de datos existente...")
        clear_database()
        print()

        print("1. Creando departamentos...")
        dept_count = create_departments()
        print(f"   {dept_count} departamentos nuevos creados\n")

        print("2. Creando usuarios administrativos...")
        admin_count = create_admin_users()
        print(f"   Total: {admin_count} usuarios administrativos\n")

        print("3. Creando usuarios finales...")
        user_count = create_end_users()
        print(f"   {user_count} usuarios finales nuevos creados\n")

        print("4. Creando reclamos de prueba...")
        claim_count = create_sample_claims()
        print(f"   {claim_count} reclamos nuevos creados\n")

        print("=== Inicialización completada ===\n")

        # Mostrar resumen
        print("Departamentos en el sistema:")
        for dept in Department.query.all():
            suffix = " (Secretaría Técnica)" if dept.is_technical_secretariat else ""
            print(f"  - {dept.display_name}{suffix}")

        print("\nUsuarios administrativos:")
        for user in AdminUser.query.all():
            dept_name = (
                user.department.display_name if user.department else "Sin departamento"
            )
            print(f"  - {user.username} ({user.admin_role.value}) - {dept_name}")

        print("\nUsuarios finales:")
        for user in EndUser.query.all():
            print(f"  - {user.username} ({user.cloister.value})")

        print(f"\nReclamos creados: {Claim.query.count()}")
        print(
            "  Se generaron reclamos en varios estados (Pendiente/En proceso/Resuelto/Inválido)"
        )


if __name__ == "__main__":
    main()
