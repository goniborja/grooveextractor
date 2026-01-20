"""
AnimatedVUMeter - VU Meter con aguja animada.
"""

import os
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, QRect
from PyQt6.QtGui import QPainter, QPixmap


class AnimatedVUMeter(QWidget):
    """
    VU Meter con aguja animada usando múltiples frames.
    Carga frames desde una carpeta de imágenes individuales.
    """

    def __init__(self, frames_folder: str, num_frames: int = 256, parent=None):
        """
        Constructor del AnimatedVUMeter.

        Args:
            frames_folder: Carpeta con los frames (VU_meter_0000.png, etc.)
            num_frames: Número de frames disponibles.
            parent: Widget padre.
        """
        super().__init__(parent)
        self._num_frames = num_frames
        self._level = 0.0  # Nivel actual (0.0 a 1.0)
        self._display_level = 0.0  # Nivel mostrado (con suavizado)
        self._frames = []

        # Cargar todos los frames
        for i in range(num_frames):
            frame_path = os.path.join(frames_folder, f"VU_meter_{i:04d}.png")
            pixmap = QPixmap(frame_path)
            if pixmap.isNull():
                raise FileNotFoundError(f"No se pudo cargar: {frame_path}")
            self._frames.append(pixmap)

        # Fijar tamaño al tamaño del primer frame
        self.setFixedSize(self._frames[0].size())

        # Timer para animación suave de la aguja
        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._update_display)
        self._animation_timer.start(16)  # ~60fps

        # Timer para decay automático (como un VU real)
        self._decay_timer = QTimer(self)
        self._decay_timer.timeout.connect(self._decay)

    def paintEvent(self, event):
        """Dibuja el frame correspondiente al nivel actual."""
        painter = QPainter(self)

        # Calcular qué frame mostrar
        frame_index = int(self._display_level * (self._num_frames - 1))
        frame_index = max(0, min(frame_index, self._num_frames - 1))

        # Dibujar el frame
        painter.drawPixmap(0, 0, self._frames[frame_index])

    def _update_display(self):
        """Actualiza el nivel mostrado con suavizado."""
        # Suavizado exponencial hacia el nivel objetivo
        diff = self._level - self._display_level
        if abs(diff) > 0.001:
            # Subida rápida, bajada lenta (como VU real)
            if diff > 0:
                self._display_level += diff * 0.3  # Subida rápida
            else:
                self._display_level += diff * 0.1  # Bajada lenta
            self.update()

    def _decay(self):
        """Aplica decay al nivel (bajada automática)."""
        if self._level > 0:
            self._level = max(0, self._level - 0.02)

    def set_level(self, level: float):
        """
        Establece el nivel del VU meter.

        Args:
            level: Nivel entre 0.0 y 1.0.
        """
        self._level = max(0.0, min(1.0, level))

    def get_level(self) -> float:
        """Retorna el nivel actual."""
        return self._level

    def reset(self):
        """Resetea el VU meter a 0."""
        self._level = 0.0
        self._display_level = 0.0
        self.update()

    def animate_needle(self, active: bool):
        """
        Activa o desactiva la animación de decay.

        Args:
            active: True para activar decay automático.
        """
        if active:
            self._decay_timer.start(50)
        else:
            self._decay_timer.stop()

    def set_immediate(self, level: float):
        """
        Establece el nivel inmediatamente sin animación.

        Args:
            level: Nivel entre 0.0 y 1.0.
        """
        self._level = max(0.0, min(1.0, level))
        self._display_level = self._level
        self.update()
