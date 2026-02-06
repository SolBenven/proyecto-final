"""
Detector de reclamos similares usando TF-IDF y similitud coseno.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from modules.utils.constants import SPANISH_STOPWORDS
from modules.utils.text import normalize_text

if TYPE_CHECKING:
    from modules.claim import Claim


class SimilarityFinder:
    """Buscador de reclamos similares"""

    def __init__(self):
        """Inicializa el buscador con vectorizador TF-IDF"""
        self.vectorizer = TfidfVectorizer(
            stop_words=SPANISH_STOPWORDS,
            min_df=1,
            ngram_range=(1, 2),  # Unigramas y bigramas
            max_features=1000,
            preprocessor=normalize_text,  # Normalizar texto antes de vectorizar
        )

    def find_similar_claims(
        self,
        text: str,
        department_id: int | None = None,
        threshold: float = 0.25,
        limit: int = 5,
        exclude_claim_id: int | None = None,
    ) -> list[tuple["Claim", float]]:
        """
        Busca reclamos similares. Si no se proporciona department_id, busca en todos los departamentos.

        Args:
            text: Texto del reclamo a comparar
            department_id: ID del departamento donde buscar (opcional, si es None busca en todos)
            threshold: Umbral mínimo de similitud (0.0 - 1.0), default 0.25
            limit: Número máximo de resultados
            exclude_claim_id: ID de reclamo a excluir (opcional)

        Returns:
            Lista de tuplas (claim, similarity_score) ordenadas por similitud descendente
        """
        if not text or not text.strip():
            return []

        from modules.claim import Claim

        claims = Claim.get_pending(department_id_filter=department_id)

        # Excluir reclamo específico si se proporciona
        if exclude_claim_id is not None:
            claims = [c for c in claims if c.id != exclude_claim_id]

        if not claims:
            return []

        # Crear matriz TF-IDF con el texto nuevo + reclamos existentes
        texts = [text] + [c.detail for c in claims]

        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
        except ValueError:
            # Si hay error en la vectorización (ej: vocabulario vacío)
            return []

        # Calcular similitud coseno entre el texto nuevo y todos los existentes
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()  # type: ignore

        # Filtrar por umbral y crear lista de tuplas
        similar = [
            (claims[i], float(sim))
            for i, sim in enumerate(similarities)
            if sim > threshold
        ]

        # Ordenar por similitud descendente
        similar.sort(key=lambda x: x[1], reverse=True)

        return similar[:limit]


# Instancia global del buscador de similitud
similarity_finder = SimilarityFinder()
