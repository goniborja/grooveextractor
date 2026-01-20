"""
ExportButtonsWidget - Widget con botones de exportación JSON y CSV.
"""

import json
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog
from PyQt6.QtCore import pyqtSignal


class ExportButtonsWidget(QWidget):
    """Widget con botones para exportar resultados a JSON y CSV."""

    # Signals emitidos al exportar
    json_exported = pyqtSignal(str)  # Emite la ruta del archivo
    csv_exported = pyqtSignal(str)   # Emite la ruta del archivo
    export_error = pyqtSignal(str)   # Emite mensaje de error

    def __init__(self, parent=None):
        super().__init__(parent)
        self._results = None
        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz del widget."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 10)

        # Estilo común para botones de exportación
        button_style = """
            QPushButton {
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """

        # Botón exportar JSON
        self.json_button = QPushButton("💾 Exportar JSON")
        self.json_button.setStyleSheet(button_style)
        self.json_button.setEnabled(False)
        self.json_button.clicked.connect(self._export_json)
        layout.addWidget(self.json_button)

        # Botón exportar CSV
        self.csv_button = QPushButton("📊 Exportar CSV")
        self.csv_button.setStyleSheet(button_style)
        self.csv_button.setEnabled(False)
        self.csv_button.clicked.connect(self._export_csv)
        layout.addWidget(self.csv_button)

        self.setLayout(layout)

    def set_results(self, results: dict):
        """
        Establece los resultados para exportación.

        Args:
            results: Diccionario con resultados del análisis.
        """
        self._results = results
        self.json_button.setEnabled(True)
        self.csv_button.setEnabled(True)

    def _export_json(self):
        """Exporta los resultados a JSON."""
        if not self._results:
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar JSON",
            "groove_analysis.json",
            "JSON Files (*.json)"
        )

        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(self._results, f, indent=2, ensure_ascii=False)
                self.json_exported.emit(file_name)
            except Exception as e:
                self.export_error.emit(f"Error al exportar JSON: {str(e)}")

    def _export_csv(self):
        """Exporta los resultados a CSV."""
        if not self._results:
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar CSV",
            "groove_analysis.csv",
            "CSV Files (*.csv)"
        )

        if file_name:
            try:
                import pandas as pd
                groove_data = self._results.get('groove_data', [])
                df = pd.DataFrame(groove_data)
                df.to_csv(file_name, index=False)
                self.csv_exported.emit(file_name)
            except ImportError:
                self.export_error.emit("pandas no está instalado")
            except Exception as e:
                self.export_error.emit(f"Error al exportar CSV: {str(e)}")

    def enable_export(self):
        """Habilita los botones de exportación."""
        self.json_button.setEnabled(True)
        self.csv_button.setEnabled(True)

    def disable_export(self):
        """Deshabilita los botones de exportación."""
        self.json_button.setEnabled(False)
        self.csv_button.setEnabled(False)

    def reset(self):
        """Resetea el widget a su estado inicial."""
        self._results = None
        self.disable_export()
