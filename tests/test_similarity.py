"""
Tests para el servicio de detección de reclamos similares.
"""

import unittest
from tests.conftest import BaseTestCase

from modules.config import db
from modules.models import Department, EndUser, Claim, Cloister, ClaimStatus
from modules.services.similarity_service import similarity_service


class TestFindSimilarClaims(BaseTestCase):
    """Tests para búsqueda de reclamos similares"""

    def setUp(self):
        """Configura el entorno de prueba"""
        super().setUp()
        # Crear departamentos
        mantenimiento = Department(
            name="mantenimiento",
            display_name="Mantenimiento",
            is_technical_secretariat=False,
        )
        infraestructura = Department(
            name="infraestructura",
            display_name="Infraestructura",
            is_technical_secretariat=False,
        )
        db.session.add(mantenimiento)
        db.session.add(infraestructura)

        # Crear usuario de prueba
        user = EndUser(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            cloister=Cloister.STUDENT,
        )
        user.set_password("test123")
        db.session.add(user)

        db.session.commit()

        self.mantenimiento_id = mantenimiento.id
        self.infraestructura_id = infraestructura.id
        self.user_id = user.id

        # Crear reclamos de prueba
        claim1 = Claim(
            detail="El aire acondicionado del aula 301 no funciona correctamente",
            department_id=mantenimiento.id,
            creator_id=user.id,
        )
        claim2 = Claim(
            detail="El aire acondicionado hace mucho ruido en el aula 302",
            department_id=mantenimiento.id,
            creator_id=user.id,
        )
        claim3 = Claim(
            detail="No funciona el WiFi en el laboratorio",
            department_id=mantenimiento.id,
            creator_id=user.id,
        )
        claim4 = Claim(
            detail="El proyector del aula está roto",
            department_id=mantenimiento.id,
            creator_id=user.id,
        )
        claim4.status = ClaimStatus.RESOLVED  # Change status after creation

        db.session.add_all([claim1, claim2, claim3, claim4])
        db.session.commit()

        self.claim_ids = [claim1.id, claim2.id, claim3.id, claim4.id]

    def test_find_similar_claims_with_high_similarity(self):
        """Test encontrar reclamos muy similares"""
        mantenimiento = (
            db.session.query(Department).filter_by(name="mantenimiento").first()
        )

        # Buscar similares a "aire acondicionado"
        similar = similarity_service.find_similar_claims(
            text="El aire acondicionado del aula no funciona bien",
            department_id=mantenimiento.id,
            threshold=0.2,  # Lower threshold to catch similar claims
            limit=5,
        )

        self.assertGreaterEqual(
            len(similar), 2
        )  # Debe encontrar los 2 reclamos de aire acondicionado
        # Verificar que retorna tuplas (claim, score)
        self.assertTrue(all(isinstance(item, tuple) and len(item) == 2 for item in similar))
        # Verificar que los scores están en orden descendente
        scores = [score for _, score in similar]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_find_similar_claims_only_pending(self):
        """Test que solo encuentra reclamos pendientes"""
        mantenimiento = (
            db.session.query(Department).filter_by(name="mantenimiento").first()
        )

        # Buscar similares a "proyector" (hay uno RESOLVED)
        similar = similarity_service.find_similar_claims(
            text="El proyector del aula tiene problemas",
            department_id=mantenimiento.id,
            threshold=0.1,
            limit=5,
        )

        # No debería incluir el reclamo Resuelto
        claim_ids = [claim.id for claim, _ in similar]
        resolved_claim = (
            db.session.query(Claim).filter_by(status=ClaimStatus.RESOLVED).first()
        )
        self.assertNotIn(resolved_claim.id, claim_ids)

    def test_find_similar_claims_different_department(self):
        """Test que solo busca en el departamento especificado"""
        infraestructura = (
            db.session.query(Department).filter_by(name="infraestructura").first()
        )

        # Buscar en departamento vacío
        similar = similarity_service.find_similar_claims(
            text="El aire acondicionado no funciona",
            department_id=infraestructura.id,
            threshold=0.3,
            limit=5,
        )

        self.assertEqual(len(similar), 0)

    def test_find_similar_claims_with_threshold(self):
        """Test que respeta el umbral de similitud"""
        mantenimiento = (
            db.session.query(Department).filter_by(name="mantenimiento").first()
        )

        # Buscar con umbral alto
        similar_high = similarity_service.find_similar_claims(
            text="El aire acondicionado del aula no funciona",
            department_id=mantenimiento.id,
            threshold=0.7,  # Umbral alto
            limit=5,
        )

        # Buscar con umbral bajo
        similar_low = similarity_service.find_similar_claims(
            text="El aire acondicionado del aula no funciona",
            department_id=mantenimiento.id,
            threshold=0.1,  # Umbral bajo
            limit=5,
        )

        # Con umbral bajo debería haber más resultados
        self.assertGreaterEqual(len(similar_low), len(similar_high))

    def test_find_similar_claims_with_limit(self):
        """Test que respeta el límite de resultados"""
        mantenimiento = (
            db.session.query(Department).filter_by(name="mantenimiento").first()
        )

        # Buscar con límite de 1
        similar = similarity_service.find_similar_claims(
            text="El aire acondicionado del aula no funciona",
            department_id=mantenimiento.id,
            threshold=0.1,
            limit=1,
        )

        self.assertLessEqual(len(similar), 1)

    def test_find_similar_claims_with_empty_text(self):
        """Test con texto vacío"""
        mantenimiento = (
            db.session.query(Department).filter_by(name="mantenimiento").first()
        )

        similar = similarity_service.find_similar_claims(
            text="",
            department_id=mantenimiento.id,
            threshold=0.3,
            limit=5,
        )

        self.assertEqual(len(similar), 0)

    def test_find_similar_claims_exclude_specific_claim(self):
        """Test que excluye un reclamo específico"""
        mantenimiento = (
            db.session.query(Department).filter_by(name="mantenimiento").first()
        )
        first_claim_id = self.claim_ids[0]

        similar = similarity_service.find_similar_claims(
            text="El aire acondicionado del aula no funciona",
            department_id=mantenimiento.id,
            threshold=0.3,
            limit=5,
            exclude_claim_id=first_claim_id,
        )

        # Verificar que no incluye el reclamo excluido
        claim_ids = [claim.id for claim, _ in similar]
        self.assertNotIn(first_claim_id, claim_ids)


class TestSimilarityScoring(BaseTestCase):
    """Tests para verificar puntuación de similitud"""

    def setUp(self):
        """Configura el entorno de prueba"""
        super().setUp()
        # Crear departamento
        mantenimiento = Department(
            name="mantenimiento",
            display_name="Mantenimiento",
            is_technical_secretariat=False,
        )
        db.session.add(mantenimiento)

        # Crear usuario de prueba
        user = EndUser(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            cloister=Cloister.STUDENT,
        )
        user.set_password("test123")
        db.session.add(user)

        db.session.commit()

        # Crear reclamos de prueba
        claim1 = Claim(
            detail="El aire acondicionado del aula 301 no funciona correctamente",
            department_id=mantenimiento.id,
            creator_id=user.id,
        )
        claim2 = Claim(
            detail="El aire acondicionado hace mucho ruido en el aula 302",
            department_id=mantenimiento.id,
            creator_id=user.id,
        )
        claim3 = Claim(
            detail="No funciona el WiFi en el laboratorio",
            department_id=mantenimiento.id,
            creator_id=user.id,
        )

        db.session.add_all([claim1, claim2, claim3])
        db.session.commit()

        self.mantenimiento_id = mantenimiento.id

    def test_similarity_scores_are_valid(self):
        """Test que los scores están entre 0 y 1"""
        mantenimiento = (
            db.session.query(Department).filter_by(name="mantenimiento").first()
        )

        similar = similarity_service.find_similar_claims(
            text="El aire acondicionado del aula no funciona",
            department_id=mantenimiento.id,
            threshold=0.0,  # Sin filtro
            limit=10,
        )

        for _, score in similar:
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    def test_more_similar_texts_have_higher_scores(self):
        """Test que textos más similares tienen scores más altos"""
        mantenimiento = (
            db.session.query(Department).filter_by(name="mantenimiento").first()
        )

        # Texto muy similar al primero
        similar = similarity_service.find_similar_claims(
            text="El aire acondicionado del aula 301 no funciona bien",
            department_id=mantenimiento.id,
            threshold=0.0,
            limit=10,
        )

        if len(similar) >= 2:
            # El más similar debería estar primero
            first_score = similar[0][1]
            last_score = similar[-1][1]
            self.assertGreaterEqual(first_score, last_score)


if __name__ == '__main__':
    unittest.main()
