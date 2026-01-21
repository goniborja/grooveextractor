"""
FilmstripKnob - Knob rotatorio con filmstrip.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QPixmap

from .image_loader import load_pixmap


class FilmstripKnob(QWidget):
    """
    Knob rotatorio que usa un filmstrip para mostrar la rotación.
    Puede tener posiciones discretas o continuas.
    """

    value_changed = pyqtSignal(int)  # Para discreto
    value_changed_float = pyqtSignal(float)  # Para continuo

    def __init__(self, strip_path: str, num_frames: int = 256,
                 num_positions: int = None, parent=None):
        """
        Constructor del FilmstripKnob.

        Args:
            strip_path: Ruta al filmstrip.
            num_frames: Número de frames en el filmstrip.
            num_positions: Si se especifica, el knob tiene paradas discretas.
            parent: Widget padre.
        """
        super().__init__(parent)
        self._num_frames = num_frames
        self._num_positions = num_positions
        self._value = 0.0  # Valor entre 0.0 y 1.0
        self._discrete_value = 0  # Valor discreto (0 a num_positions-1)
        self._labels = []
        self._dragging = False
        self._last_y = 0

        # Cargar filmstrip (usando carga robusta para PNGs no estándar)
        self._filmstrip = load_pixmap(strip_path)

        # Calcular tamaño de cada frame
        self._frame_width = self._filmstrip.width()
        self._frame_height = self._filmstrip.height() // num_frames

        # Fijar tamaño del widget
        self.setFixedSize(self._frame_width, self._frame_height)

    def paintEvent(self, event):
        """Dibuja el frame correspondiente al valor actual."""
        painter = QPainter(self)

        # Calcular qué frame mostrar
        if self._num_positions:
            # Modo discreto: mapear posición a frame
            frame_index = int(self._discrete_value * (self._num_frames - 1) / (self._num_positions - 1))
        else:
            # Modo continuo
            frame_index = int(self._value * (self._num_frames - 1))

        frame_index = max(0, min(frame_index, self._num_frames - 1))

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

    def mousePressEvent(self, event):
        """Inicia el arrastre."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._last_y = event.pos().y()

    def mouseMoveEvent(self, event):
        """Actualiza el valor durante el arrastre."""
        if self._dragging:
            delta = self._last_y - event.pos().y()
            self._last_y = event.pos().y()

            # Sensibilidad del knob
            sensitivity = 0.005

            if self._num_positions:
                # Modo discreto
                self._value += delta * sensitivity
                self._value = max(0.0, min(1.0, self._value))
                new_discrete = int(self._value * (self._num_positions - 1) + 0.5)
                new_discrete = max(0, min(new_discrete, self._num_positions - 1))

                if new_discrete != self._discrete_value:
                    self._discrete_value = new_discrete
                    self.update()
                    self.value_changed.emit(self._discrete_value)
            else:
                # Modo continuo
                self._value += delta * sensitivity
                self._value = max(0.0, min(1.0, self._value))
                self.update()
                self.value_changed_float.emit(self._value)

    def mouseReleaseEvent(self, event):
        """Finaliza el arrastre."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def wheelEvent(self, event):
        """Permite ajustar con la rueda del mouse."""
        delta = event.angleDelta().y()

        if self._num_positions:
            # Modo discreto: un paso por notch
            if delta > 0:
                self.set_value(min(self._discrete_value + 1, self._num_positions - 1))
            elif delta < 0:
                self.set_value(max(self._discrete_value - 1, 0))
        else:
            # Modo continuo
            change = 0.05 if delta > 0 else -0.05
            self.set_value(self._value + change)

    def set_value(self, value):
        """
        Establece el valor del knob.

        Args:
            value: int para discreto, float para continuo.
        """
        if self._num_positions:
            # Modo discreto
            value = int(value)
            value = max(0, min(value, self._num_positions - 1))
            if value != self._discrete_value:
                self._discrete_value = value
                self._value = value / (self._num_positions - 1)
                self.update()
                self.value_changed.emit(self._discrete_value)
        else:
            # Modo continuo
            value = float(value)
            value = max(0.0, min(1.0, value))
            if abs(value - self._value) > 0.001:
                self._value = value
                self.update()
                self.value_changed_float.emit(self._value)

    def get_value(self):
        """Retorna el valor actual."""
        if self._num_positions:
            return self._discrete_value
        return self._value

    def set_labels(self, labels: list):
        """
        Establece etiquetas para las posiciones discretas.

        Args:
            labels: Lista de strings para cada posición.
        """
        self._labels = labels
        if self._num_positions is None:
            self._num_positions = len(labels)

    def get_label(self) -> str:
        """Retorna la etiqueta de la posición actual."""
        if self._labels and self._discrete_value < len(self._labels):
            return self._labels[self._discrete_value]
        return str(self._discrete_value)
