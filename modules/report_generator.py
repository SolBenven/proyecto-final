"""Generador de Reportes para el panel de administración."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

from flask import render_template

from modules.models.claim import Claim
from modules.models.department import Department
from modules.analytics_generator import AnalyticsGenerator
from modules.utils.constants import PDF_CSS

if TYPE_CHECKING:
    pass


class Report(ABC):
    """Clase base abstracta para generación de reportes."""

    def __init__(
        self,
        department_ids: list[int],
        is_technical_secretary: bool = False,
    ):
        self.department_ids = department_ids
        self.is_technical_secretary = is_technical_secretary

    def _get_claims(self) -> list[Claim]:
        """Obtiene los reclamos para el reporte."""
        return Claim.get_by_departments(self.department_ids)

    def _get_departments(self) -> list[Department]:
        """Obtiene los departamentos para el reporte."""
        return Department.get_by_ids(self.department_ids)

    def _get_stats(self) -> dict:
        """Obtiene las estadísticas para el reporte."""
        return AnalyticsGenerator.get_claim_stats(self.department_ids)

    @abstractmethod
    def generate(self) -> str | bytes | None:
        """Genera el reporte en el formato específico."""
        pass


class HTMLReport(Report):
    """Generador de reportes en formato HTML."""

    def generate(self) -> str:
        """
        Genera un reporte HTML completo.

        Returns:
            String con el contenido HTML del reporte
        """
        return render_template(
            "reports/department_report.html",
            departments=self._get_departments(),
            claims=self._get_claims(),
            stats=self._get_stats(),
            is_technical_secretary=self.is_technical_secretary,
            generated_at=datetime.now(),
            pdf_css=PDF_CSS,
        )


class PDFReport(Report):
    """Generador de reportes en formato PDF."""

    def generate(self) -> bytes | None:
        """
        Genera un reporte PDF a partir del HTML usando xhtml2pdf.

        Returns:
            Bytes del PDF o None si xhtml2pdf no está disponible o hay error
        """
        try:
            from io import BytesIO
            from xhtml2pdf import pisa
        except ImportError:
            return None

        try:
            # Usar HTMLReport para generar el contenido base
            html_report = HTMLReport(self.department_ids, self.is_technical_secretary)
            html_content = html_report.generate()

            pdf_buffer = BytesIO()
            pisa_status = pisa.CreatePDF(src=html_content, dest=pdf_buffer)

            if pisa_status.err:  # type: ignore
                return None

            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            return pdf_bytes
        except Exception:
            return None


def create_report(
    report_format: str,
    department_ids: list[int],
    is_technical_secretary: bool = False,
) -> Report:
    """
    Factory function para crear el tipo de reporte apropiado.

    Args:
        report_format: Formato del reporte ('html' o 'pdf')
        department_ids: Lista de IDs de departamentos a incluir
        is_technical_secretary: Si el usuario es secretario técnico

    Returns:
        Instancia de HTMLReport o PDFReport
    """
    if report_format == "pdf":
        return PDFReport(department_ids, is_technical_secretary)
    return HTMLReport(department_ids, is_technical_secretary)
