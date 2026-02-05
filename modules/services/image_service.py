"""Servicio para gestión de imágenes de reclamos"""

import os
import uuid
from pathlib import Path
from typing import Tuple
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

# Configuración
UPLOAD_FOLDER = "static/uploads/claims"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class ImageService:
    """Gestión de imágenes para reclamos"""

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """
        Verifica si el archivo tiene una extensión permitida.

        Args:
            filename: Nombre del archivo

        Returns:
            True si la extensión es válida
        """
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    @staticmethod
    def validate_image(file: FileStorage) -> Tuple[bool, str | None]:
        """
        Valida que el archivo sea una imagen válida.

        Args:
            file: Archivo a validar

        Returns:
            Tuple (is_valid, error_message)
        """
        if not file or not file.filename:
            return False, "No se proporcionó ningún archivo"

        if file.filename == "":
            return False, "El archivo no tiene nombre"

        if not ImageService.allowed_file(file.filename):
            return (
                False,
                f"Tipo de archivo no permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Validar tamaño leyendo el contenido
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Volver al inicio

        if file_size > MAX_FILE_SIZE:
            return False, f"El archivo excede el tamaño máximo de 5MB"

        return True, None

    @staticmethod
    def save_claim_image(file: FileStorage) -> Tuple[str | None, str | None]:
        """
        Guarda una imagen de reclamo y retorna su path relativo.

        Args:
            file: Archivo de imagen

        Returns:
            Tuple (relative_path, error_message)
        """
        # Validar el archivo
        is_valid, error = ImageService.validate_image(file)
        if not is_valid:
            return None, error

        # Crear directorio si no existe
        upload_dir = Path(UPLOAD_FOLDER)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generar nombre único
        original_filename = secure_filename(file.filename or "")
        extension = original_filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{extension}"

        # Guardar archivo
        file_path = upload_dir.joinpath(unique_filename)
        try:
            file.save(str(file_path))
        except Exception as e:
            return None, f"Error al guardar el archivo: {str(e)}"

        # Retornar path relativo
        relative_path = f"{UPLOAD_FOLDER}/{unique_filename}"
        return relative_path, None

    @staticmethod
    def delete_claim_image(image_path: str) -> bool:
        """
        Elimina una imagen de reclamo del sistema de archivos.

        Args:
            image_path: Path relativo de la imagen

        Returns:
            True si se eliminó correctamente
        """
        if not image_path:
            return False

        try:
            file_path = Path(image_path)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
