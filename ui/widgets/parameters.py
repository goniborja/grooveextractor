"""
ParametersWidget - Widget para configurar parámetros de análisis.
"""

from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QLabel, QLineEdit
)
from PyQt6.QtCore import pyqtSignal


class ParametersWidget(QGroupBox):
    """Widget para configurar parámetros de análisis (tempo, time signature)."""

    # Signal emitido cuando cambian los parámetros
    parameters_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("2. Parámetros de Análisis", parent)
        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz del widget."""
        layout = QGridLayout()
        layout.setSpacing(10)

        # Campo de tempo
        tempo_label = QLabel("Tempo (BPM):")
        tempo_label.setStyleSheet("font-weight: bold; color: #333333;")
        layout.addWidget(tempo_label, 0, 0)

        self.tempo_input = QLineEdit("120.0")
        self.tempo_input.setStyleSheet(
            "QLineEdit {"
            "  padding: 6px;"
            "  border: 1px solid #ccc;"
            "  border-radius: 4px;"
            "  background-color: white;"
            "}"
            "QLineEdit:focus {"
            "  border-color: #007AFF;"
            "}"
        )
        self.tempo_input.setPlaceholderText("Ej: 120.0")
        self.tempo_input.textChanged.connect(self.parameters_changed.emit)
        layout.addWidget(self.tempo_input, 0, 1)

        # Campo de time signature
        time_sig_label = QLabel("Time Signature:")
        time_sig_label.setStyleSheet("font-weight: bold; color: #333333;")
        layout.addWidget(time_sig_label, 1, 0)

        self.time_sig_input = QLineEdit("4/4")
        self.time_sig_input.setStyleSheet(
            "QLineEdit {"
            "  padding: 6px;"
            "  border: 1px solid #ccc;"
            "  border-radius: 4px;"
            "  background-color: white;"
            "}"
            "QLineEdit:focus {"
            "  border-color: #007AFF;"
            "}"
        )
        self.time_sig_input.setPlaceholderText("Ej: 4/4")
        self.time_sig_input.textChanged.connect(self.parameters_changed.emit)
        layout.addWidget(self.time_sig_input, 1, 1)

        # Stretch para mantener campos compactos
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)

    def get_tempo(self) -> float:
        """
        Retorna el tempo como float.

        Raises:
            ValueError: Si el tempo no es un número válido.
        """
        return float(self.tempo_input.text())

    def get_time_signature(self) -> str:
        """Retorna el time signature como string."""
        return self.time_sig_input.text()

    def set_tempo(self, tempo: float):
        """Establece el valor del tempo."""
        self.tempo_input.setText(str(tempo))

    def set_time_signature(self, time_sig: str):
        """Establece el valor del time signature."""
        self.time_sig_input.setText(time_sig)

    def validate_tempo(self) -> tuple[bool, str]:
        """
        Valida que el tempo sea un número válido.

        Returns:
            Tuple (is_valid, error_message)
        """
        try:
            tempo = float(self.tempo_input.text())
            if tempo <= 0:
                return False, "El tempo debe ser mayor que 0"
            if tempo > 400:
                return False, "El tempo parece demasiado alto (máx: 400 BPM)"
            return True, ""
        except ValueError:
            return False, "El tempo debe ser un número válido"

    def reset(self):
        """Resetea los parámetros a valores por defecto."""
        self.tempo_input.setText("120.0")
        self.time_sig_input.setText("4/4")
