"""
Script para entrenar el modelo de clasificación automática de reclamos.
Ejecutar: python train_classifier.py
"""

from modules.config import create_app, db
from modules.classifier import classifier
from modules.department import Department


# Dataset de entrenamiento inicial
TRAINING_DATA = [
    # Mantenimiento (aire acondicionado, electricidad, plomería, limpieza básica)
    ("El aire acondicionado no funciona en el aula 301", "mantenimiento"),
    ("Se rompió la canilla del baño del segundo piso", "mantenimiento"),
    ("Las luces del pasillo están quemadas", "mantenimiento"),
    ("El ascensor hace ruidos extraños", "mantenimiento"),
    ("No sale agua caliente en los baños", "mantenimiento"),
    ("La puerta del salón no cierra correctamente", "mantenimiento"),
    ("El ventilador de techo no enciende", "mantenimiento"),
    ("Hay una gotera en el techo del laboratorio", "mantenimiento"),
    ("El inodoro del baño está tapado", "mantenimiento"),
    ("La cerradura de la puerta está rota", "mantenimiento"),
    ("No funciona la calefacción en invierno", "mantenimiento"),
    ("El agua del bebedero no sale", "mantenimiento"),
    ("La persiana del aula está atascada", "mantenimiento"),
    ("Hay humedad en las paredes del aula", "mantenimiento"),
    ("El extractor del baño no funciona", "mantenimiento"),
    # Infraestructura (obras, pintura, construcción, mobiliario)
    ("Hay grietas en la pared del aula 205", "infraestructura"),
    ("El techo tiene filtraciones de agua", "infraestructura"),
    ("Las baldosas del piso están rotas y peligrosas", "infraestructura"),
    ("Se necesita pintar las paredes del edificio", "infraestructura"),
    ("Faltan bancos en el aula magna", "infraestructura"),
    ("La rampa de acceso está deteriorada", "infraestructura"),
    ("El techo del patio tiene goteras", "infraestructura"),
    ("Las escaleras están en mal estado", "infraestructura"),
    ("Se cayó el revoque de la pared", "infraestructura"),
    ("Los pisos necesitan ser reparados", "infraestructura"),
    ("Faltan sillas en el salón de actos", "infraestructura"),
    ("El banco del aula está roto", "infraestructura"),
    ("La pintura de las aulas está descascarada", "infraestructura"),
    ("El muro del patio tiene grietas", "infraestructura"),
    ("Necesitamos más mesas en la biblioteca", "infraestructura"),
    # Sistemas (computadoras, internet, software, proyectores)
    ("No hay internet en el laboratorio de informática", "sistemas"),
    ("La computadora del aula no enciende", "sistemas"),
    ("El proyector está fallando y se apaga", "sistemas"),
    ("No funciona el WiFi en el edificio B", "sistemas"),
    ("La impresora de la sala de profesores no imprime", "sistemas"),
    ("El sistema de sonido del auditorio no funciona", "sistemas"),
    ("No puedo acceder al campus virtual", "sistemas"),
    ("La red de internet está muy lenta", "sistemas"),
    ("El software de la computadora tiene virus", "sistemas"),
    ("No funciona el micrófono del salón", "sistemas"),
    ("La pantalla del proyector tiene líneas", "sistemas"),
    ("No se puede conectar la notebook al proyector", "sistemas"),
    ("El sistema de control de asistencia no funciona", "sistemas"),
    ("La cámara de videoconferencia no enciende", "sistemas"),
    ("No funciona el cable HDMI del proyector", "sistemas"),
    # Secretaría Técnica (casos complejos, quejas administrativas)
    (
        "Mi reclamo fue mal derivado y nadie lo atiende desde hace un mes",
        "secretaria_tecnica",
    ),
    (
        "Necesito hablar con autoridades sobre un problema que no resuelven",
        "secretaria_tecnica",
    ),
    ("Quiero presentar una queja formal sobre el servicio", "secretaria_tecnica"),
    (
        "El departamento de mantenimiento no responde mis reclamos",
        "secretaria_tecnica",
    ),
    (
        "Este problema afecta a múltiples áreas y necesita coordinación",
        "secretaria_tecnica",
    ),
    (
        "El profesor se comporta de manera inapropiada y nadie hace nada",
        "secretaria_tecnica",
    ),
]


def get_existing_departments() -> dict[str, int]:
    """Obtiene los departamentos existentes en la base de datos"""
    departments = db.session.query(Department).all()
    return {dept.name: dept.id for dept in departments}


def validate_training_data(existing_departments: dict[str, int]) -> bool:
    """
    Valida que todos los departamentos en el dataset existan en la BD.

    Args:
        existing_departments: Diccionario {nombre: id} de departamentos existentes

    Returns:
        True si todos los departamentos existen, False en caso contrario
    """
    missing_departments = set()

    for _, department in TRAINING_DATA:
        if department not in existing_departments:
            missing_departments.add(department)

    if missing_departments:
        print("\n❌ Error: Los siguientes departamentos no existen en la BD:")
        for dept in sorted(missing_departments):
            print(f"   - {dept}")
        print("\nPor favor, ejecute seed_db.py primero para crear los departamentos.\n")
        return False

    return True


def train_model():
    """Entrena el modelo con el dataset inicial"""
    app = create_app()

    with app.app_context():
        # Verificar que existan departamentos
        existing_departments = get_existing_departments()

        if not existing_departments:
            print("\n❌ Error: No hay departamentos en la base de datos.")
            print("Ejecute seed_db.py primero para crear los departamentos.\n")
            return

        print("\n=== Entrenando Clasificador de Reclamos ===\n")
        print(f"Departamentos disponibles: {', '.join(existing_departments.keys())}")

        # Validar dataset
        if not validate_training_data(existing_departments):
            return

        # Extraer textos y etiquetas
        texts, labels = zip(*TRAINING_DATA)

        # Entrenar modelo
        print(f"\nEntrenando con {len(texts)} ejemplos...")
        classifier.train(list(texts), list(labels))

        print("\n✅ Modelo entrenado exitosamente")
        print(f"   Archivos guardados en: models/")

        # Probar clasificación con ejemplos
        print("\n=== Pruebas de Clasificación ===\n")

        test_cases = [
            "El aire acondicionado del aula hace mucho ruido",
            "Necesito más sillas en el salón",
            "No funciona el WiFi",
            "Hay grietas en las paredes",
        ]

        for test_text in test_cases:
            predicted = classifier.classify(test_text)
            confidence = classifier.get_confidence(test_text)
            print(f"Texto: '{test_text}'")
            print(f"Predicción: {predicted} (confianza: {confidence:.2%})")
            print()


if __name__ == "__main__":
    train_model()
