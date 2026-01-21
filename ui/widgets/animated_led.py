"""
AnimatedLED - LED con múltiples frames para animación suave.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, QRect
from PyQt6.QtGui import QPainter, QPixmap

from .image_loader import load_pixmap


class AnimatedLED(QWidget):
    """
    LED animado que usa un filmstrip para mostrar diferentes niveles de brillo.
    """

    def __init__(self, strip_path: str, num_frames: int = 62,
                 scale: float = 1.0, parent=None):
        """
        Constructor del AnimatedLED.

        Args:
            strip_path: Ruta al filmstrip del LED.
            num_frames: Número de frames en el filmstrip.
            scale: Factor de escala.
            parent: Widget padre.
        """
        super().__init__(parent)
        self._num_frames = num_frames
        self._brightness = 0.0  # Brillo actual (0.0 a 1.0)
        self._is_on = False
        self._pulsing = False

        # Cargar filmstrip (usando carga robusta para PNGs no estándar)
        self._filmstrip = load_pixmap(strip_path, scale)

        # Calcular tamaño de cada frame
        self._frame_width = self._filmstrip.width()
        self._frame_height = self._filmstrip.height() // num_frames

        # Fijar tamaño del widget
        self.setFixedSize(self._frame_width, self._frame_height)

        # Timer para pulsación
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse_step)
        self._pulse_direction = 1
        self._pulse_speed = 0.05

    def paintEvent(self, event):
        """Dibuja el frame correspondiente al brillo actual."""
        painter = QPainter(self)

        # Calcular qué frame mostrar
        frame_index = int(self._brightness * (self._num_frames - 1))
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

    def turn_on(self):
        """Enciende el LED al máximo brillo."""
        self._is_on = True
        self._brightness = 1.0
        self._pulsing = False
        self._pulse_timer.stop()
        self.update()

    def turn_off(self):
        """Apaga el LED."""
        self._is_on = False
        self._brightness = 0.0
        self._pulsing = False
        self._pulse_timer.stop()
        self.update()

    def pulse(self, speed: float = 0.05):
        """
        Inicia una animación de pulsación.

        Args:
            speed: Velocidad de la pulsación (cambio por frame).
        """
        self._pulsing = True
        self._pulse_speed = speed
        self._pulse_direction = 1
        self._pulse_timer.start(30)  # ~33fps

    def stop_pulse(self):
        """Detiene la pulsación."""
        self._pulsing = False
        self._pulse_timer.stop()

    def _pulse_step(self):
        """Ejecuta un paso de la animación de pulsación."""
        self._brightness += self._pulse_speed * self._pulse_direction

        if self._brightness >= 1.0:
            self._brightness = 1.0
            self._pulse_direction = -1
        elif self._brightness <= 0.0:
            self._brightness = 0.0
            self._pulse_direction = 1

        self.update()

    def set_brightness(self, brightness: float):
        """
        Establece el brillo del LED.

        Args:
            brightness: Valor entre 0.0 y 1.0.
        """
        self._brightness = max(0.0, min(1.0, brightness))
        self._is_on = brightness > 0
        self.update()

    def get_brightness(self) -> float:
        """Retorna el brillo actual."""
        return self._brightness

    def is_on(self) -> bool:
        """Retorna True si el LED está encendido."""
        return self._is_on

    def is_pulsing(self) -> bool:
        """Retorna True si el LED está pulsando."""
        return self._pulsing
