"""
AnimatedLED - LED meter con múltiples frames para animación suave.
Soporta tanto filmstrips como carpetas de frames individuales.
"""

from pathlib import Path
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, QRect
from PyQt6.QtGui import QPainter, QPixmap

from .image_loader import load_pixmap


class AnimatedLED(QWidget):
    """
    LED meter animado que puede usar:
    1. Un filmstrip (imagen vertical con frames apilados)
    2. Una carpeta con frames individuales (LED_off.png, LED_meter_0001.png, etc.)
    """

    def __init__(self, source_path: str, num_frames: int = 62,
                 scale: float = 1.0, parent=None):
        """
        Constructor del AnimatedLED.

        Args:
            source_path: Ruta al filmstrip PNG o carpeta de frames.
            num_frames: Número de frames (usado para filmstrip).
            scale: Factor de escala.
            parent: Widget padre.
        """
        super().__init__(parent)
        self._num_frames = num_frames
        self._brightness = 0.0
        self._is_on = False
        self._pulsing = False
        self._use_folder = False
        self._frames = []

        source = Path(source_path)

        # Detectar si es carpeta o filmstrip
        if source.is_dir():
            # Cargar frames individuales desde carpeta
            self._use_folder = True
            self._load_frames_from_folder(source, scale)
        else:
            # Cargar filmstrip
            self._use_folder = False
            self._filmstrip = load_pixmap(str(source), scale)
            self._frame_width = self._filmstrip.width()
            self._frame_height = self._filmstrip.height() // num_frames

        # Fijar tamaño del widget
        if self._use_folder and self._frames:
            self.setFixedSize(self._frames[0].width(), self._frames[0].height())
        elif not self._use_folder:
            self.setFixedSize(self._frame_width, self._frame_height)

        # Timer para pulsación
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse_step)
        self._pulse_direction = 1
        self._pulse_speed = 0.05

    def _load_frames_from_folder(self, folder: Path, scale: float):
        """Carga frames individuales desde una carpeta."""
        # Buscar LED_off.png como frame 0
        led_off = folder / "LED_off.png"
        if led_off.exists():
            self._frames.append(load_pixmap(str(led_off), scale))

        # Cargar frames numerados LED_meter_0001.png a LED_meter_NNNN.png
        frame_num = 1
        while True:
            frame_path = folder / f"LED_meter_{frame_num:04d}.png"
            if not frame_path.exists():
                break
            self._frames.append(load_pixmap(str(frame_path), scale))
            frame_num += 1

        self._num_frames = len(self._frames)

    def paintEvent(self, event):
        """Dibuja el frame correspondiente al brillo actual."""
        painter = QPainter(self)

        # Calcular qué frame mostrar (0 = apagado, max = lleno)
        frame_index = int(self._brightness * (self._num_frames - 1))
        frame_index = max(0, min(frame_index, self._num_frames - 1))

        if self._use_folder and self._frames:
            # Dibujar frame individual
            painter.drawPixmap(0, 0, self._frames[frame_index])
        elif not self._use_folder:
            # Dibujar desde filmstrip
            source_rect = QRect(
                0,
                frame_index * self._frame_height,
                self._frame_width,
                self._frame_height
            )
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
        """Inicia una animación de pulsación."""
        self._pulsing = True
        self._pulse_speed = speed
        self._pulse_direction = 1
        self._pulse_timer.start(30)

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
        """Establece el brillo del LED (0.0 a 1.0)."""
        self._brightness = max(0.0, min(1.0, brightness))
        self._is_on = brightness > 0
        self._pulsing = False
        self._pulse_timer.stop()
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
