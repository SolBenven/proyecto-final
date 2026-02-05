"""Utilidades para procesamiento de texto."""

from __future__ import annotations

import unicodedata


def normalize_text(text: str) -> str:
    """
    Normaliza el texto removiendo acentos y caracteres especiales.

    Args:
        text: Texto a normalizar

    Returns:
        Texto normalizado sin acentos en minúsculas
    """
    text = text.lower()
    text = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )
    return text
