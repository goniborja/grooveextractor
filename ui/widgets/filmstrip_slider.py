"""
FilmstripSlider - Slider que usa filmstrip para animación.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, Qt, QRect, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QPixmap


class FilmstripSlider(QWidget):
    """
    Slider que usa un filmstrip vertical para mostrar diferentes posiciones.
    Los frames están apilados verticalmente en la imagen.
    """

    value_changed = pyqtSignal(float)

    def __init__(self, strip_path: str, num_frames: int = 256,
                 orientation: str = 'vertical', parent=None):
        """
        Constructor del FilmstripSlider.

        Args:
            strip_path: Ruta al filmstrip.
            num_frames: Número de frames en el filmstrip.
            orientation: 'vertical' u 'horizontal'.
            parent: Widget padre.
        """
        super().__init__(parent)
        self._num_frames = num_frames
        self._orientation = orientation
        self._value = 0.0  # Valor entre 0.0 y 1.0
        self._dragging = False

        # Cargar filmstrip
        self._filmstrip = QPixmap(strip_path)
        if self._filmstrip.isNull():
            raise FileNotFoundError(f"No se pudo cargar: {strip_path}")

        # Calcular tamaño de cada frame
        self._frame_width = self._filmstrip.width()
        self._frame_height = self._filmstrip.height() // num_frames

        # Fijar tamaño del widget
        self.setFixedSize(self._frame_width, self._frame_height)

        # Para animaciones
        self._target_value = 0.0
        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._animate_step)

    def paintEvent(self, event):
        """Dibuja el frame correspondiente al valor actual."""
        painter = QPainter(self)

        # Calcular qué frame mostrar
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
            self._update_value_from_pos(event.pos())

    def mouseMoveEvent(self, event):
        """Actualiza el valor durante el arrastre."""
        if self._dragging:
            self._update_value_from_pos(event.pos())

    def mouseReleaseEvent(self, event):
        """Finaliza el arrastre."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def _update_value_from_pos(self, pos):
        """Calcula el valor basado en la posición del mouse."""
        if self._orientation == 'vertical':
            # Invertido: arriba = 1.0, abajo = 0.0
            new_value = 1.0 - (pos.y() / self.height())
        else:
            new_value = pos.x() / self.width()

        new_value = max(0.0, min(1.0, new_value))
        self.set_value(new_value)

    def set_value(self, value: float):
        """
        Establece el valor del slider.

        Args:
            value: Valor entre 0.0 y 1.0.
        """
        value = max(0.0, min(1.0, value))
        if abs(self._value - value) > 0.001:
            self._value = value
            self.update()
            self.value_changed.emit(self._value)

    def get_value(self) -> float:
        """Retorna el valor actual (0.0 a 1.0)."""
        return self._value

    def animate_to(self, target: float, duration_ms: int = 300):
        """
        Anima el slider hacia un valor objetivo.

        Args:
            target: Valor objetivo (0.0 a 1.0).
            duration_ms: Duración de la animación en ms.
        """
        self._target_value = max(0.0, min(1.0, target))
        self._animation_steps = max(1, duration_ms // 16)  # ~60fps
        self._animation_delta = (self._target_value - self._value) / self._animation_steps
        self._animation_timer.start(16)

    def _animate_step(self):
        """Ejecuta un paso de la animación."""
        if abs(self._value - self._target_value) < abs(self._animation_delta):
            self.set_value(self._target_value)
            self._animation_timer.stop()
        else:
            self.set_value(self._value + self._animation_delta)

    def reset(self):
        """Resetea el slider a 0."""
        self.set_value(0.0)
