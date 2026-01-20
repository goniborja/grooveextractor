"""
ImagePad - Widget tipo pad que usa imágenes on/off.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QPixmap


class ImagePad(QWidget):
    """
    Widget tipo pad que muestra imágenes diferentes para estados on/off.
    Se ilumina brevemente al hacer clic.
    """

    clicked = pyqtSignal()

    def __init__(self, off_image: str, on_image: str, label_text: str = "", parent=None):
        """
        Constructor del ImagePad.

        Args:
            off_image: Ruta a la imagen del estado apagado.
            on_image: Ruta a la imagen del estado encendido.
            label_text: Texto opcional (no se usa visualmente, solo para identificación).
            parent: Widget padre.
        """
        super().__init__(parent)
        self.label_text = label_text
        self._is_pressed = False

        # Cargar imágenes
        self._img_off = QPixmap(off_image)
        self._img_on = QPixmap(on_image)

        # Verificar que las imágenes se cargaron
        if self._img_off.isNull():
            raise FileNotFoundError(f"No se pudo cargar: {off_image}")
        if self._img_on.isNull():
            raise FileNotFoundError(f"No se pudo cargar: {on_image}")

        # Fijar tamaño al tamaño de la imagen
        self.setFixedSize(self._img_off.size())

        # Timer para el efecto de iluminación breve
        self._flash_timer = QTimer(self)
        self._flash_timer.setSingleShot(True)
        self._flash_timer.timeout.connect(self._end_flash)

    def paintEvent(self, event):
        """Dibuja el pad con la imagen correspondiente al estado."""
        painter = QPainter(self)
        img = self._img_on if self._is_pressed else self._img_off
        painter.drawPixmap(0, 0, img)

    def mousePressEvent(self, event):
        """Maneja el click del mouse."""
        self._is_pressed = True
        self.update()
        self.clicked.emit()

    def mouseReleaseEvent(self, event):
        """Maneja la liberación del mouse."""
        # Mantener encendido brevemente para feedback visual
        self._flash_timer.start(100)  # 100ms de flash

    def _end_flash(self):
        """Finaliza el efecto de flash."""
        self._is_pressed = False
        self.update()

    def set_pressed(self, pressed: bool):
        """
        Establece manualmente el estado del pad.

        Args:
            pressed: True para estado encendido, False para apagado.
        """
        self._is_pressed = pressed
        self.update()

    @property
    def is_pressed(self) -> bool:
        """Retorna True si el pad está presionado."""
        return self._is_pressed
