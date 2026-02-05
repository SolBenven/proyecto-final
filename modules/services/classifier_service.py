"""
Servicio de clasificación automática de reclamos usando TF-IDF + Naive Bayes.
"""

from __future__ import annotations
from typing import Optional
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


class ClassifierService:
    """Servicio para clasificar automáticamente reclamos a departamentos"""

    def __init__(self):
        self.vectorizer: TfidfVectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),  # Unigramas y bigramas
            min_df=1,  # Mínima frecuencia de documento
        )
        self.classifier: MultinomialNB = MultinomialNB()
        self.is_trained: bool = False
        self.model_path: str = "data/classifier.joblib"
        self.vectorizer_path: str = "data/vectorizer.joblib"

    def train(self, texts: list[str], labels: list[str]) -> None:
        """
        Entrena el clasificador con textos etiquetados.

        Args:
            texts: Lista de textos de reclamos
            labels: Lista de departamentos correspondientes (nombres internos)
        """
        if not texts or not labels:
            raise ValueError("Se requieren textos y etiquetas para entrenar")

        if len(texts) != len(labels):
            raise ValueError("La cantidad de textos debe coincidir con las etiquetas")

        # Vectorizar textos
        X = self.vectorizer.fit_transform(texts)

        # Entrenar clasificador
        self.classifier.fit(X, labels)
        self.is_trained = True

        # Guardar modelo
        self._save_model()

    def classify(self, text: str) -> str:
        """
        Clasifica un texto y retorna el departamento predicho.

        Args:
            text: Texto del reclamo a clasificar

        Returns:
            Nombre interno del departamento (ej: 'mantenimiento')

        Raises:
            ValueError: Si el modelo no está entrenado o el texto está vacío
        """
        if not text or not text.strip():
            raise ValueError("El texto no puede estar vacío")

        # Cargar modelo si no está entrenado
        if not self.is_trained:
            self._load_model()

        # Verificar que el modelo esté disponible
        if not self.is_trained:
            raise ValueError("El modelo no está entrenado. Ejecute train_classifier.py")

        # Vectorizar y predecir
        X = self.vectorizer.transform([text])
        confidence = self.get_confidence(text)
        if confidence < 0.4:
            return "secretaria_tecnica"
        prediction = self.classifier.predict(X)[0]

        return prediction

    def get_confidence(self, text: str) -> float:
        """
        Retorna la probabilidad/confianza de la predicción.

        Args:
            text: Texto del reclamo a clasificar

        Returns:
            Probabilidad de la clase predicha (0.0 - 1.0)
        """
        if not text or not text.strip():
            return 0.0

        if not self.is_trained:
            self._load_model()

        if not self.is_trained:
            return 0.0

        X = self.vectorizer.transform([text])
        probabilities = self.classifier.predict_proba(X)[0]

        return float(max(probabilities))

    def _save_model(self) -> None:
        """Guarda el modelo y el vectorizador en disco"""
        # Crear directorio si no existe
        os.makedirs("models", exist_ok=True)

        # Guardar ambos componentes
        joblib.dump(self.classifier, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)

    def _load_model(self) -> None:
        """Carga el modelo desde disco"""
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            self.classifier = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)
            self.is_trained = True

    def is_model_available(self) -> bool:
        """
        Verifica si existe un modelo entrenado en disco.

        Returns:
            True si el modelo está disponible, False en caso contrario
        """
        return os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path)


# Instancia global del servicio
classifier_service = ClassifierService()
