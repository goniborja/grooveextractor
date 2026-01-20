"""
FileLoaderWidget - Widget para cargar archivos de audio.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QGroupBox, QHBoxLayout, QLabel, QPushButton, QFileDialog
)
from PyQt6.QtCore import pyqtSignal


class FileLoaderWidget(QGroupBox):
    """Widget para seleccionar y cargar archivos de audio WAV."""

    # Signal emitido cuando se carga un archivo
    file_loaded = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__("1. Cargar Audio", parent)
        self._audio_file = None
        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz del widget."""
        layout = QHBoxLayout()

        # Label para mostrar el archivo cargado
        self.file_label = QLabel("No se ha cargado ningún archivo")
        self.file_label.setStyleSheet(
            "padding: 5px; "
            "background-color: #f0f0f0; "
            "border-radius: 3px;"
        )
        layout.addWidget(self.file_label, stretch=1)

        # Botón para cargar archivo
        self.load_button = QPushButton("Cargar WAV")
        self.load_button.setStyleSheet(
            "QPushButton {"
            "  padding: 8px 16px;"
            "  background-color: #007AFF;"
            "  color: white;"
            "  border: none;"
            "  border-radius: 4px;"
            "  font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "  background-color: #0056b3;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #004094;"
            "}"
        )
        self.load_button.clicked.connect(self._open_file_dialog)
        layout.addWidget(self.load_button)

        self.setLayout(layout)

    def _open_file_dialog(self):
        """Abre diálogo para seleccionar archivo de audio."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de audio",
            "",
            "Audio Files (*.wav *.WAV);;All Files (*)"
        )

        if file_name:
            self._audio_file = file_name
            self.file_label.setText(f"📁 {Path(file_name).name}")
            self.file_loaded.emit(file_name)

    @property
    def audio_file(self) -> str | None:
        """Retorna la ruta del archivo cargado."""
        return self._audio_file

    def get_file_name(self) -> str | None:
        """Retorna solo el nombre del archivo (sin ruta)."""
        if self._audio_file:
            return Path(self._audio_file).name
        return None

    def reset(self):
        """Resetea el widget a su estado inicial."""
        self._audio_file = None
        self.file_label.setText("No se ha cargado ningún archivo")
