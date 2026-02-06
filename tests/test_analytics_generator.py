"""
Tests para AnalyticsGenerator - Fase 11
"""

import unittest

from modules.config import db
from modules.models.claim import Claim, ClaimStatus
from modules.models.user.end_user import Cloister, EndUser
from modules.analytics_generator import AnalyticsGenerator
from tests.conftest import BaseTestCase


class TestAnalyticsGenerator(BaseTestCase):
    """Tests para el generador de analíticas"""

    def setUp(self):
        """Configuración antes de cada test"""
        super().setUp()

        # Crear usuario de prueba para analytics
        user = EndUser(
            first_name="Analytics",
            last_name="User",
            email="analytics@test.com",
            username="analyticsuser",
            cloister=Cloister.STUDENT,
        )
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()
        self.analytics_user_id = user.id

        # Crear reclamos variados para pruebas de analíticas
        dept1_id = self.sample_departments["dept1_id"]
        dept2_id = self.sample_departments["dept2_id"]

        # Dept1: 3 pendientes, 2 En proceso, 1 Resuelto
        c1, _ = Claim.create(
            user_id=self.analytics_user_id,
            detail="La computadora está rota y no funciona",
            department_id=dept1_id,
        )
        c2, _ = Claim.create(
            user_id=self.analytics_user_id,
            detail="Problema con el agua del baño",
            department_id=dept1_id,
        )
        c3, _ = Claim.create(
            user_id=self.analytics_user_id,
            detail="La luz del aula no enciende",
            department_id=dept1_id,
        )
        c4, _ = Claim.create(
            user_id=self.analytics_user_id,
            detail="El aire acondicionado está roto",
            department_id=dept1_id,
        )
        c5, _ = Claim.create(
            user_id=self.analytics_user_id,
            detail="La puerta del laboratorio está rota",
            department_id=dept1_id,
        )
        c6, _ = Claim.create(
            user_id=self.analytics_user_id,
            detail="Silla del aula rota",
            department_id=dept1_id,
        )

        # Cambiar estados
        c4.status = ClaimStatus.IN_PROGRESS
        c5.status = ClaimStatus.IN_PROGRESS
        c6.status = ClaimStatus.RESOLVED

        # Dept2: 1 Inválido, 1 Pendiente
        c7, _ = Claim.create(
            user_id=self.analytics_user_id,
            detail="Problema con la luz",
            department_id=dept2_id,
        )
        c8, _ = Claim.create(
            user_id=self.analytics_user_id,
            detail="Agua del baño",
            department_id=dept2_id,
        )
        c7.status = ClaimStatus.INVALID

        db.session.commit()

        self.seeded_dept1_id = dept1_id
        self.seeded_dept2_id = dept2_id

    # ============================================================
    # Tests para get_claim_stats
    # ============================================================

    def test_get_claim_stats_global(self):
        """Obtiene estadísticas de todos los departamentos"""
        stats = AnalyticsGenerator.get_claim_stats(department_ids=None)

        self.assertEqual(stats["total_claims"], 8)
        self.assertIn("status_counts", stats)
        self.assertIn("status_percentages", stats)

    def test_get_claim_stats_filtered_by_department(self):
        """Filtra correctamente por departamento"""
        stats = AnalyticsGenerator.get_claim_stats(
            department_ids=[self.seeded_dept1_id]
        )

        self.assertEqual(stats["total_claims"], 6)
        self.assertEqual(stats["status_counts"]["Pendiente"], 3)
        self.assertEqual(stats["status_counts"]["En proceso"], 2)
        self.assertEqual(stats["status_counts"]["Resuelto"], 1)

    def test_get_claim_stats_empty_list(self):
        """Lista vacía retorna stats vacías"""
        stats = AnalyticsGenerator.get_claim_stats(department_ids=[])

        self.assertEqual(stats["total_claims"], 0)
        self.assertEqual(stats["status_counts"], {})
        self.assertEqual(stats["status_percentages"], {})

    def test_get_claim_stats_no_claims(self):
        """Sin reclamos retorna stats vacías (usando BaseTestCase sin datos seeded)"""
        # Crear nueva instancia sin datos seeded
        self.tearDown()
        super(TestAnalyticsGenerator, self).setUp()

        stats = AnalyticsGenerator.get_claim_stats(department_ids=None)

        self.assertEqual(stats["total_claims"], 0)
        self.assertEqual(stats["status_counts"], {})

    # ============================================================
    # Tests para get_keyword_frequencies
    # ============================================================

    def test_get_keyword_frequencies_extracts_words(self):
        """Extrae palabras clave de los reclamos"""
        keywords = AnalyticsGenerator.get_keyword_frequencies(department_ids=None)

        # "rota" aparece varias veces en los claims
        self.assertTrue("rota" in keywords or "roto" in keywords)
        self.assertGreater(len(keywords), 0)

    def test_get_keyword_frequencies_filters_stopwords(self):
        """Filtra stopwords correctamente"""
        keywords = AnalyticsGenerator.get_keyword_frequencies(department_ids=None)

        # Stopwords no deberían aparecer
        self.assertNotIn("la", keywords)
        self.assertNotIn("el", keywords)
        self.assertNotIn("de", keywords)
        self.assertNotIn("del", keywords)
        self.assertNotIn("está", keywords)

    def test_get_keyword_frequencies_respects_top_n(self):
        """Respeta el límite top_n"""
        keywords = AnalyticsGenerator.get_keyword_frequencies(
            department_ids=None, top_n=3
        )

        self.assertLessEqual(len(keywords), 3)

    def test_get_keyword_frequencies_empty_departments(self):
        """Lista vacía de departamentos retorna dict vacío"""
        keywords = AnalyticsGenerator.get_keyword_frequencies(department_ids=[])

        self.assertEqual(keywords, {})

    def test_get_keyword_frequencies_no_claims(self):
        """Sin reclamos retorna dict vacío"""
        # Crear nueva instancia sin datos seeded
        self.tearDown()
        super(TestAnalyticsGenerator, self).setUp()

        keywords = AnalyticsGenerator.get_keyword_frequencies(department_ids=None)

        self.assertEqual(keywords, {})

    # ============================================================
    # Tests para generate_pie_chart
    # ============================================================

    def test_generate_pie_chart_creates_base64(self):
        """Genera gráfico en formato base64"""
        stats = AnalyticsGenerator.get_claim_stats(department_ids=None)
        pie_chart = AnalyticsGenerator.generate_pie_chart(stats["status_counts"])

        self.assertIsNotNone(pie_chart)
        # Verificar que es string base64 válido
        self.assertIsInstance(pie_chart, str)
        self.assertGreater(
            len(pie_chart), 100
        )  # Base64 de imagen tiene muchos caracteres

    def test_generate_pie_chart_empty_data_returns_none(self):
        """Datos vacíos retornan None"""
        pie_chart = AnalyticsGenerator.generate_pie_chart({})

        self.assertIsNone(pie_chart)

    def test_generate_pie_chart_all_zeros_returns_none(self):
        """Todos valores en cero retornan None"""
        pie_chart = AnalyticsGenerator.generate_pie_chart(
            {"Pendiente": 0, "En proceso": 0}
        )

        self.assertIsNone(pie_chart)

    # ============================================================
    # Tests para generate_wordcloud
    # ============================================================

    def test_generate_wordcloud_with_data(self):
        """Genera wordcloud cuando hay datos"""
        keywords = AnalyticsGenerator.get_keyword_frequencies(department_ids=None)
        wordcloud = AnalyticsGenerator.generate_wordcloud(keywords)

        # Puede ser None si wordcloud no está instalado
        if wordcloud is not None:
            self.assertIsInstance(wordcloud, str)
            self.assertGreater(len(wordcloud), 100)

    def test_generate_wordcloud_empty_data(self):
        """Datos vacíos retornan None"""
        wordcloud = AnalyticsGenerator.generate_wordcloud({})

        self.assertIsNone(wordcloud)

    # ============================================================
    # Tests para get_full_analytics
    # ============================================================

    def test_get_full_analytics_returns_all_data(self):
        """Retorna todas las analíticas en una llamada"""
        analytics = AnalyticsGenerator.get_full_analytics(department_ids=None)

        self.assertIn("stats", analytics)
        self.assertIn("pie_chart", analytics)
        self.assertIn("wordcloud", analytics)
        self.assertIn("keywords", analytics)

        self.assertEqual(analytics["stats"]["total_claims"], 8)
        self.assertIsNotNone(analytics["pie_chart"])

    def test_get_full_analytics_filtered(self):
        """Filtra correctamente por departamentos"""
        analytics = AnalyticsGenerator.get_full_analytics(
            department_ids=[self.seeded_dept1_id]
        )

        self.assertEqual(analytics["stats"]["total_claims"], 6)

    def test_get_full_analytics_no_claims(self):
        """Sin reclamos retorna estructura válida pero vacía"""
        # Crear nueva instancia sin datos seeded
        self.tearDown()
        super(TestAnalyticsGenerator, self).setUp()

        analytics = AnalyticsGenerator.get_full_analytics(department_ids=None)

        self.assertEqual(analytics["stats"]["total_claims"], 0)
        self.assertIsNone(analytics["pie_chart"])
        self.assertIsNone(analytics["wordcloud"])
        self.assertEqual(analytics["keywords"], {})

    # ============================================================
    # Tests de integración
    # ============================================================

    def test_percentages_sum_to_100(self):
        """Los porcentajes suman aproximadamente 100%"""
        stats = AnalyticsGenerator.get_claim_stats(department_ids=None)
        percentages = stats["status_percentages"]

        if percentages:
            total = sum(percentages.values())
            # Permitir pequeño margen por redondeo
            self.assertGreaterEqual(total, 99.5)
            self.assertLessEqual(total, 100.5)

    def test_status_counts_match_total(self):
        """La suma de conteos por estado igual al total"""
        stats = AnalyticsGenerator.get_claim_stats(department_ids=None)

        status_sum = sum(stats["status_counts"].values())
        self.assertEqual(status_sum, stats["total_claims"])


if __name__ == "__main__":
    unittest.main()
