"""Generador de Analíticas y Estadísticas para el panel de administración."""

from __future__ import annotations

import base64
import io
import re
from collections import Counter

import matplotlib

matplotlib.use("Agg")  # Backend sin GUI - DEBE estar antes de importar pyplot
import matplotlib.pyplot as plt

from modules.config import db
from modules.models.claim import Claim, ClaimStatus
from modules.utils.constants import SPANISH_STOPWORDS_SET
from modules.utils.text import normalize_text


class AnalyticsGenerator:
    """Generador de métricas y visualizaciones de reclamos."""

    # Colores por estado para el gráfico circular
    STATUS_COLORS = {
        "Pendiente": "#ffc107",
        "En proceso": "#17a2b8",
        "Resuelto": "#28a745",
        "Inválido": "#dc3545",
    }

    # Mapeo de ClaimStatus a nombres legibles
    STATUS_LABELS = {
        ClaimStatus.PENDING: "Pendiente",
        ClaimStatus.IN_PROGRESS: "En proceso",
        ClaimStatus.RESOLVED: "Resuelto",
        ClaimStatus.INVALID: "Inválido",
    }

    @staticmethod
    def get_claim_stats(department_ids: list[int] | None = None) -> dict:
        """
        Obtiene estadísticas de reclamos por estado.

        Args:
            department_ids: Lista de IDs de departamentos a considerar.
                           None = todos los departamentos

        Returns:
            dict con:
            - total_claims: número total de reclamos
            - status_counts: dict[str, int] con conteo por estado legible
            - status_percentages: dict[str, float] con porcentajes por estado
        """
        # Reutilizar Claim.get_status_counts
        raw_counts = Claim.get_status_counts(department_ids=department_ids)

        # Convertir a nombres legibles y filtrar estados con 0
        status_counts: dict[str, int] = {}
        for status, count in raw_counts.items():
            if count > 0:
                label = AnalyticsGenerator.STATUS_LABELS[status]
                status_counts[label] = count

        total = sum(status_counts.values())

        if total == 0:
            return {
                "total_claims": 0,
                "status_counts": {},
                "status_percentages": {},
            }

        # Calcular porcentajes
        status_percentages: dict[str, float] = {
            label: round((count / total) * 100, 1)
            for label, count in status_counts.items()
        }

        return {
            "total_claims": total,
            "status_counts": status_counts,
            "status_percentages": status_percentages,
        }

    @staticmethod
    def get_keyword_frequencies(
        department_ids: list[int] | None = None, top_n: int = 20
    ) -> dict[str, int]:
        """
        Extrae palabras clave más frecuentes de los reclamos.

        Args:
            department_ids: Lista de IDs de departamentos a considerar.
                           None = todos los departamentos
            top_n: Cantidad máxima de palabras a retornar

        Returns:
            dict con palabras y sus frecuencias, ordenado por frecuencia descendente
        """
        query = db.session.query(Claim.detail)

        if department_ids is not None:
            if len(department_ids) == 0:
                return {}
            query = query.filter(Claim.department_id.in_(department_ids))

        details = [row[0] for row in query.all()]

        if not details:
            return {}

        # Extraer y filtrar palabras (normalizando texto para match con stopwords)
        all_words: list[str] = []
        for detail in details:
            normalized = normalize_text(detail)
            words = re.findall(r"\b\w+\b", normalized)
            filtered = [
                w
                for w in words
                if w not in SPANISH_STOPWORDS_SET and len(w) > 2 and not w.isdigit()
            ]
            all_words.extend(filtered)

        if not all_words:
            return {}

        # Obtener las top_n palabras más comunes
        word_counts = Counter(all_words).most_common(top_n)
        return dict(word_counts)

    @staticmethod
    def generate_pie_chart(status_counts: dict[str, int]) -> str | None:
        """
        Genera gráfico circular de distribución de estados.

        Args:
            status_counts: dict con estados y sus conteos
                          ej: {'Pendiente': 10, 'En proceso': 5, 'Resuelto': 3}

        Returns:
            String base64 de la imagen PNG o None si no hay datos
        """
        if not status_counts:
            return None

        # Filtrar estados con valor > 0
        filtered_stats = {k: v for k, v in status_counts.items() if v > 0}

        if not filtered_stats:
            return None

        fig, ax = plt.subplots(figsize=(8, 6))
        colors = [
            AnalyticsGenerator.STATUS_COLORS.get(k, "#6c757d")
            for k in filtered_stats.keys()
        ]

        wedges, texts, autotexts = ax.pie(  # type: ignore
            filtered_stats.values(),  # type: ignore
            labels=filtered_stats.keys(),  # type: ignore
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            textprops={"fontsize": 11},
        )

        # Estilizar los porcentajes
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        ax.set_title(
            "Distribución de Reclamos por Estado", fontsize=14, fontweight="bold"
        )
        plt.tight_layout()

        # Convertir a base64
        buffer = io.BytesIO()
        plt.savefig(
            buffer, format="png", dpi=100, bbox_inches="tight", facecolor="white"
        )
        plt.close(fig)  # Liberar memoria
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @staticmethod
    def generate_wordcloud(word_frequencies: dict[str, int]) -> str | None:
        """
        Genera nube de palabras a partir de frecuencias.

        Args:
            word_frequencies: dict con palabras y sus frecuencias
                             ej: {'roto': 15, 'agua': 10, 'luz': 8}

        Returns:
            String base64 de la imagen PNG o None si no hay datos/wordcloud no disponible
        """
        if not word_frequencies:
            return None

        try:
            from wordcloud import WordCloud
        except ImportError:
            # Si wordcloud no está instalado, retornar None
            return None

        wc = WordCloud(
            width=800,
            height=400,
            background_color="white",
            colormap="viridis",
            max_words=50,
            min_font_size=10,
            prefer_horizontal=0.7,
        ).generate_from_frequencies(word_frequencies)

        buffer = io.BytesIO()
        wc.to_image().save(buffer, format="PNG")
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @staticmethod
    def get_full_analytics(department_ids: list[int] | None = None) -> dict:
        """
        Obtiene todas las analíticas en una sola llamada.

        Args:
            department_ids: Lista de IDs de departamentos a considerar.
                           None = todos los departamentos

        Returns:
            dict con:
            - stats: estadísticas de reclamos
            - pie_chart: gráfico circular en base64
            - wordcloud: nube de palabras en base64
            - keywords: dict de palabras frecuentes
        """
        stats = AnalyticsGenerator.get_claim_stats(department_ids)
        keywords = AnalyticsGenerator.get_keyword_frequencies(department_ids)

        pie_chart = AnalyticsGenerator.generate_pie_chart(
            stats.get("status_counts", {})
        )
        wordcloud = AnalyticsGenerator.generate_wordcloud(keywords)

        return {
            "stats": stats,
            "pie_chart": pie_chart,
            "wordcloud": wordcloud,
            "keywords": keywords,
        }
