"""
ImageSwitch - Switch horizontal/vertical con dos estados usando imágenes.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QPainter, QPixmap


class ImageSwitch(QWidget):
    """
    Switch con dos estados que usa imágenes PNG.
    Puede ser horizontal o vertical.
    """

    toggled = pyqtSignal(bool)

    def __init__(self, image_off: str, image_on: str, parent=None):
        """
        Constructor del ImageSwitch.

        Args:
            image_off: Ruta a la imagen del estado apagado (st1).
            image_on: Ruta a la imagen del estado encendido (st2).
            parent: Widget padre.
        """
        super().__init__(parent)
        self._is_on = False

        # Cargar imágenes
        self._img_off = QPixmap(image_off)
        self._img_on = QPixmap(image_on)

        # Verificar que las imágenes se cargaron
        if self._img_off.isNull():
            raise FileNotFoundError(f"No se pudo cargar: {image_off}")
        if self._img_on.isNull():
            raise FileNotFoundError(f"No se pudo cargar: {image_on}")

        # Fijar tamaño al tamaño de la imagen
        self.setFixedSize(self._img_off.size())

    def paintEvent(self, event):
        """Dibuja el switch con la imagen correspondiente al estado."""
        painter = QPainter(self)
        img = self._img_on if self._is_on else self._img_off
        painter.drawPixmap(0, 0, img)

    def mousePressEvent(self, event):
        """Cambia el estado al hacer clic."""
        self._is_on = not self._is_on
        self.update()
        self.toggled.emit(self._is_on)

    def is_on(self) -> bool:
        """Retorna True si el switch está encendido."""
        return self._is_on

    def set_state(self, state: bool):
        """
        Establece el estado del switch.

        Args:
            state: True para encendido, False para apagado.
        """
        if self._is_on != state:
            self._is_on = state
            self.update()
            self.toggled.emit(self._is_on)

    def toggle(self):
        """Alterna el estado del switch."""
        self.set_state(not self._is_on)
