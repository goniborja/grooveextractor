"""
ResultsWidget - Widget para mostrar resultados del análisis.
"""

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QFont


class ResultsWidget(QGroupBox):
    """Widget que muestra los resultados del análisis en formato de texto."""

    def __init__(self, parent=None):
        super().__init__("3. Resultados del Análisis", parent)
        self._results = None
        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz del widget."""
        layout = QVBoxLayout()

        # Área de texto para resultados
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText(
            "Los resultados aparecerán aquí después del análisis..."
        )

        # Fuente monoespaciada para resultados
        font = QFont("Courier New", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.results_text.setFont(font)

        self.results_text.setStyleSheet(
            "QTextEdit {"
            "  background-color: #f8f8f8;"
            "  border: 1px solid #ddd;"
            "  border-radius: 4px;"
            "  padding: 10px;"
            "}"
        )

        layout.addWidget(self.results_text)
        self.setLayout(layout)

    def display_results(self, results: dict):
        """
        Muestra los resultados del análisis.

        Args:
            results: Diccionario con resultados del análisis.
        """
        self._results = results

        metadata = results.get('metadata', {})
        groove_data = results.get('groove_data', [])
        stats = results.get('humanization_stats', {})

        summary = f"""
=== ANÁLISIS COMPLETADO ===

METADATA:
- Archivo: {metadata.get('audio_file', 'N/A')}
- Sample Rate: {metadata.get('sample_rate', 'N/A')} Hz
- Duración: {metadata.get('duration_seconds', 0):.2f} s
- Tempo: {metadata.get('tempo_bpm', 'N/A')} BPM
- Time Signature: {metadata.get('time_signature', 'N/A')}

DETECCIÓN DE ONSETS:
- Total de onsets detectados: {len(groove_data)}

ESTADÍSTICAS DE HUMANIZACIÓN:
- Desviación temporal promedio: {stats.get('avg_timing_deviation_ms', 0):.2f} ms
- Desviación estándar: {stats.get('std_timing_deviation_ms', 0):.2f} ms
- Variación de velocidad promedio: {stats.get('avg_velocity_variation', 0):.3f}
- Factor de swing: {stats.get('swing_factor', 0):.3f}

Primeros 5 onsets:
"""

        for i, onset in enumerate(groove_data[:5]):
            summary += (
                f"\n  {i+1}. t={onset.get('onset_time', 0):.3f}s, "
                f"vel={onset.get('velocity', 0)}, "
                f"dev={onset.get('timing_deviation_ms', 0):.2f}ms"
            )

        self.results_text.setText(summary)

    def display_error(self, error_msg: str):
        """
        Muestra un mensaje de error.

        Args:
            error_msg: Mensaje de error a mostrar.
        """
        self._results = None
        self.results_text.setText(f"❌ ERROR EN EL ANÁLISIS:\n\n{error_msg}")
        self.results_text.setStyleSheet(
            "QTextEdit {"
            "  background-color: #fff0f0;"
            "  border: 1px solid #ffcccc;"
            "  border-radius: 4px;"
            "  padding: 10px;"
            "  color: #cc0000;"
            "}"
        )

    def clear(self):
        """Limpia los resultados."""
        self._results = None
        self.results_text.clear()
        # Restaurar estilos normales
        self.results_text.setStyleSheet(
            "QTextEdit {"
            "  background-color: #f8f8f8;"
            "  border: 1px solid #ddd;"
            "  border-radius: 4px;"
            "  padding: 10px;"
            "}"
        )

    @property
    def has_results(self) -> bool:
        """Retorna True si hay resultados disponibles."""
        return self._results is not None

    @property
    def results(self) -> dict | None:
        """Retorna los resultados actuales."""
        return self._results
