"""
image_loader.py - Utilidad para cargar PNGs de forma robusta.

Los archivos del kit Vintage Obsession pueden tener chunks PNG
no estándar que Qt no maneja bien. Este módulo proporciona
funciones para cargar imágenes de forma más tolerante.
"""

from PyQt6.QtGui import QPixmap, QImage, QImageReader
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
from pathlib import Path


def load_pixmap(path: str) -> QPixmap:
    """
    Carga un PNG de forma robusta.

    Intenta múltiples métodos de carga para manejar
    archivos PNG con chunks no estándar (como APNG).

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

    # Método 1: Intentar carga directa con QPixmap
    pixmap = QPixmap(str(path))
    if not pixmap.isNull():
        return pixmap

    # Método 2: Usar QImageReader con formato explícito
    reader = QImageReader(str(path))
    reader.setAutoDetectImageFormat(False)
    reader.setFormat(b"png")

    # Ignorar errores de chunks desconocidos
    reader.setDecideFormatFromContent(True)

    image = reader.read()
    if not image.isNull():
        return QPixmap.fromImage(image)

    # Método 3: Cargar bytes y decodificar
    try:
        with open(path, 'rb') as f:
            data = f.read()

        byte_array = QByteArray(data)
        pixmap = QPixmap()
        if pixmap.loadFromData(byte_array, "PNG"):
            return pixmap
    except Exception:
        pass

    # Método 4: Usar QImage directamente
    image = QImage(str(path))
    if not image.isNull():
        return QPixmap.fromImage(image)

    # Si ningún método funcionó, levantar error
    error_msg = reader.errorString() if reader.error() else "Error desconocido"
    raise FileNotFoundError(
        f"No se pudo cargar la imagen: {path}\n"
        f"Error: {error_msg}\n"
        "Verifica que el archivo PNG no esté corrupto."
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
