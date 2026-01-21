"""
ImageButton - Botón con filmstrip de estados (normal, hover, pressed).
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, Qt, QRect
from PyQt6.QtGui import QPainter, QPixmap, QFont, QColor

from .image_loader import load_pixmap


class ImageButton(QWidget):
    """
    Botón que usa un filmstrip para mostrar diferentes estados.
    Los frames están apilados verticalmente en la imagen.
    """

    clicked = pyqtSignal()

    # Estados del botón
    STATE_NORMAL = 0
    STATE_HOVER = 1
    STATE_PRESSED = 2

    def __init__(self, strip_path: str, num_frames: int = 6, label_text: str = "",
                 scale: float = 1.0, parent=None):
        """
        Constructor del ImageButton.

        Args:
            strip_path: Ruta al filmstrip (imagen vertical con frames apilados).
            num_frames: Número de frames en el filmstrip.
            label_text: Texto a mostrar sobre el botón.
            scale: Factor de escala.
            parent: Widget padre.
        """
        super().__init__(parent)
        self._label_text = label_text
        self._num_frames = num_frames
        self._state = self.STATE_NORMAL
        self._enabled = True

        # Cargar filmstrip (usando carga robusta para PNGs no estándar)
        self._filmstrip = load_pixmap(strip_path, scale)

        # Calcular tamaño de cada frame
        self._frame_width = self._filmstrip.width()
        self._frame_height = self._filmstrip.height() // num_frames

        # Fijar tamaño del widget
        self.setFixedSize(self._frame_width, self._frame_height)

        # Habilitar tracking del mouse para hover
        self.setMouseTracking(True)

    def paintEvent(self, event):
        """Dibuja el frame correspondiente al estado actual."""
        painter = QPainter(self)

        # Determinar qué frame mostrar
        if not self._enabled:
            frame_index = min(self._num_frames - 1, 3)  # Frame deshabilitado
        elif self._state == self.STATE_PRESSED:
            frame_index = 2
        elif self._state == self.STATE_HOVER:
            frame_index = 1
        else:
            frame_index = 0

        # Calcular región del frame en el filmstrip
        source_rect = QRect(
            0,
            frame_index * self._frame_height,
            self._frame_width,
            self._frame_height
        )

        # Dibujar el frame
        painter.drawPixmap(0, 0, self._filmstrip,
                          source_rect.x(), source_rect.y(),
                          source_rect.width(), source_rect.height())

        # Dibujar texto si existe
        if self._label_text:
            painter.setPen(QColor("#FFFFFF"))
            font = QFont("Arial", 10, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._label_text)

    def mousePressEvent(self, event):
        """Maneja el click del mouse."""
        if self._enabled and event.button() == Qt.MouseButton.LeftButton:
            self._state = self.STATE_PRESSED
            self.update()

    def mouseReleaseEvent(self, event):
        """Maneja la liberación del mouse."""
        if self._enabled and event.button() == Qt.MouseButton.LeftButton:
            if self.rect().contains(event.pos()):
                self._state = self.STATE_HOVER
                self.clicked.emit()
            else:
                self._state = self.STATE_NORMAL
            self.update()

    def enterEvent(self, event):
        """Maneja cuando el mouse entra al widget."""
        if self._enabled:
            self._state = self.STATE_HOVER
            self.update()

    def leaveEvent(self, event):
        """Maneja cuando el mouse sale del widget."""
        self._state = self.STATE_NORMAL
        self.update()

    def set_text(self, text: str):
        """Establece el texto del botón."""
        self._label_text = text
        self.update()

    def set_enabled(self, enabled: bool):
        """Habilita o deshabilita el botón."""
        self._enabled = enabled
        self._state = self.STATE_NORMAL
        self.update()

    def is_enabled(self) -> bool:
        """Retorna True si el botón está habilitado."""
        return self._enabled
