"""
ProgressWidget - Widget de barra de progreso con visibilidad condicional.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import Qt


class ProgressWidget(QWidget):
    """Widget que muestra una barra de progreso con etiqueta opcional."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        # Oculto por defecto
        self.setVisible(False)

    def _init_ui(self):
        """Inicializa la interfaz del widget."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)

        # Label de estado
        self.status_label = QLabel("Procesando...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #666666;"
            "font-size: 11px;"
        )
        layout.addWidget(self.status_label)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(
            "QProgressBar {"
            "  border: 1px solid #ccc;"
            "  border-radius: 5px;"
            "  background-color: #f0f0f0;"
            "  height: 20px;"
            "  text-align: center;"
            "}"
            "QProgressBar::chunk {"
            "  background-color: #007AFF;"
            "  border-radius: 4px;"
            "}"
        )
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def set_value(self, value: int):
        """
        Establece el valor del progreso.

        Args:
            value: Valor entre 0 y 100.
        """
        self.progress_bar.setValue(value)

    def set_status(self, status: str):
        """
        Establece el texto de estado.

        Args:
            status: Texto a mostrar.
        """
        self.status_label.setText(status)

    def start(self, status: str = "Analizando audio..."):
        """
        Inicia la visualización del progreso.

        Args:
            status: Texto de estado inicial.
        """
        self.progress_bar.setValue(0)
        self.status_label.setText(status)
        self.setVisible(True)

    def finish(self):
        """Finaliza y oculta el widget de progreso."""
        self.progress_bar.setValue(100)
        self.setVisible(False)

    def reset(self):
        """Resetea el widget a su estado inicial."""
        self.progress_bar.setValue(0)
        self.status_label.setText("Procesando...")
        self.setVisible(False)

    @property
    def value(self) -> int:
        """Retorna el valor actual del progreso."""
        return self.progress_bar.value()
