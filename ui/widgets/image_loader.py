"""
image_loader.py - Utilidad para cargar PNGs de forma robusta.

Los archivos del kit Vintage Obsession son APNG (Animated PNG)
que Qt no soporta directamente. Este módulo usa Pillow para
cargar las imágenes y convertirlas a formato compatible con Qt.
"""

from io import BytesIO
from pathlib import Path

from PIL import Image
from PyQt6.QtGui import QPixmap, QImage


def load_pixmap(path: str) -> QPixmap:
    """
    Carga un PNG/APNG usando Pillow y lo convierte a QPixmap.

    Pillow soporta APNG y extrae el primer frame, convirtiéndolo
    a PNG estándar que Qt puede manejar.

    Args:
        path: Ruta al archivo PNG.

    Returns:
        QPixmap cargado.

    Raises:
        FileNotFoundError: Si el archivo no existe o no se puede cargar.
    """
    path_obj = Path(path)

    if not path_obj.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    try:
        # Cargar con Pillow (soporta APNG)
        img = Image.open(path)

        # Convertir a RGBA si es necesario
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Convertir a bytes PNG estándar
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Cargar en QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.read())

        if pixmap.isNull():
            raise FileNotFoundError(f"No se pudo cargar: {path}")

        return pixmap

    except Exception as e:
        raise FileNotFoundError(
            f"No se pudo cargar la imagen: {path}\n"
            f"Error: {e}"
        )


def load_image(path: str) -> QImage:
    """
    Carga un PNG como QImage de forma robusta.

    Args:
        path: Ruta al archivo PNG.

    Returns:
        QImage cargado.

    Raises:
        FileNotFoundError: Si el archivo no existe o no se puede cargar.
    """
    pixmap = load_pixmap(path)
    return pixmap.toImage()
