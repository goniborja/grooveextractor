"""
AnalyzeButton - Botón estilizado para iniciar análisis.
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal


class AnalyzeButton(QPushButton):
    """Botón estilizado para iniciar el análisis de audio."""

    # Signal emitido al hacer click (además del clicked heredado)
    analyze_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("▶ Analizar Audio", parent)
        self._init_style()
        self._is_analyzing = False
        self.clicked.connect(self._on_clicked)

    def _init_style(self):
        """Aplica estilos al botón."""
        self.setStyleSheet(
            "QPushButton {"
            "  padding: 12px 24px;"
            "  font-size: 14px;"
            "  font-weight: bold;"
            "  background-color: #007AFF;"
            "  color: white;"
            "  border: none;"
            "  border-radius: 6px;"
            "  min-width: 200px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #0056b3;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #004094;"
            "}"
            "QPushButton:disabled {"
            "  background-color: #cccccc;"
            "  color: #666666;"
            "}"
        )
        # Estado inicial: deshabilitado hasta que se cargue un archivo
        self.setEnabled(False)

    def _on_clicked(self):
        """Maneja el click del botón."""
        if not self._is_analyzing:
            self.analyze_requested.emit()

    def set_analyzing(self, analyzing: bool):
        """
        Establece el estado de análisis.

        Args:
            analyzing: True si está analizando, False si no.
        """
        self._is_analyzing = analyzing
        if analyzing:
            self.setText("⏳ Analizando...")
            self.setEnabled(False)
        else:
            self.setText("▶ Analizar Audio")
            self.setEnabled(True)

    def enable_analysis(self):
        """Habilita el botón para análisis."""
        if not self._is_analyzing:
            self.setEnabled(True)

    def disable_analysis(self):
        """Deshabilita el botón."""
        self.setEnabled(False)

    @property
    def is_analyzing(self) -> bool:
        """Retorna True si está en proceso de análisis."""
        return self._is_analyzing
