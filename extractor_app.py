#!/usr/bin/env python3
"""
GROOVE EXTRACTOR
================
Herramienta de análisis DSP para extracción de grooves de batería.

Autor: DSP Engineer / Data Architect
Fecha: 2026-01-18
Versión: 1.0.0
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar,
    QGroupBox, QGridLayout, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from groove_analyzer import GrooveAnalyzer


class AnalysisThread(QThread):
    """Thread para análisis de audio sin bloquear la UI."""

    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, audio_file, tempo=120.0):
        super().__init__()
        self.audio_file = audio_file
        self.tempo = tempo
        self.analyzer = GrooveAnalyzer()

    def run(self):
        """Ejecuta el análisis en segundo plano."""
        try:
            self.progress.emit(10)

            # Cargar audio
            self.analyzer.load_audio(self.audio_file)
            self.progress.emit(30)

            # Detectar onsets
            self.analyzer.detect_onsets()
            self.progress.emit(60)

            # Analizar dinámica y micro-timing
            self.analyzer.analyze_dynamics()
            self.progress.emit(80)

            # Calcular desviaciones del grid
            self.analyzer.calculate_timing_deviations(self.tempo)
            self.progress.emit(90)

            # Obtener resultados
            results = self.analyzer.get_results()
            self.progress.emit(100)

            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))


class GrooveExtractorApp(QMainWindow):
    """Aplicación principal de Groove Extractor."""

    def __init__(self):
        super().__init__()
        self.audio_file = None
        self.analysis_results = None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle("Groove Extractor - Book of Drums Tool")
        self.setGeometry(100, 100, 900, 700)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Título
        title = QLabel("🥁 GROOVE EXTRACTOR")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        subtitle = QLabel("Herramienta de Análisis DSP para Extracción de Grooves")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        # Sección de carga de archivo
        file_group = QGroupBox("1. Cargar Audio")
        file_layout = QHBoxLayout()

        self.file_label = QLabel("No se ha cargado ningún archivo")
        self.file_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        file_layout.addWidget(self.file_label)

        self.load_button = QPushButton("Cargar WAV")
        self.load_button.clicked.connect(self.load_audio_file)
        file_layout.addWidget(self.load_button)

        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # Sección de parámetros
        params_group = QGroupBox("2. Parámetros de Análisis")
        params_layout = QGridLayout()

        params_layout.addWidget(QLabel("Tempo (BPM):"), 0, 0)
        self.tempo_input = QLineEdit("120.0")
        params_layout.addWidget(self.tempo_input, 0, 1)

        params_layout.addWidget(QLabel("Time Signature:"), 1, 0)
        self.time_sig_input = QLineEdit("4/4")
        params_layout.addWidget(self.time_sig_input, 1, 1)

        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)

        # Botón de análisis
        self.analyze_button = QPushButton("▶ Analizar Audio")
        self.analyze_button.setEnabled(False)
        self.analyze_button.clicked.connect(self.start_analysis)
        self.analyze_button.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold;")
        main_layout.addWidget(self.analyze_button)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Resultados
        results_group = QGroupBox("3. Resultados del Análisis")
        results_layout = QVBoxLayout()

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Los resultados aparecerán aquí después del análisis...")
        results_layout.addWidget(self.results_text)

        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        # Botones de exportación
        export_layout = QHBoxLayout()

        self.export_json_button = QPushButton("💾 Exportar JSON")
        self.export_json_button.setEnabled(False)
        self.export_json_button.clicked.connect(self.export_json)
        export_layout.addWidget(self.export_json_button)

        self.export_csv_button = QPushButton("📊 Exportar CSV")
        self.export_csv_button.setEnabled(False)
        self.export_csv_button.clicked.connect(self.export_csv)
        export_layout.addWidget(self.export_csv_button)

        main_layout.addLayout(export_layout)

        # Status bar
        self.statusBar().showMessage("Listo para cargar audio")

    def load_audio_file(self):
        """Abre diálogo para cargar archivo de audio."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de audio",
            "",
            "Audio Files (*.wav *.WAV);;All Files (*)"
        )

        if file_name:
            self.audio_file = file_name
            self.file_label.setText(f"📁 {Path(file_name).name}")
            self.analyze_button.setEnabled(True)
            self.statusBar().showMessage(f"Audio cargado: {file_name}")

    def start_analysis(self):
        """Inicia el análisis del audio en un thread separado."""
        try:
            tempo = float(self.tempo_input.text())
        except ValueError:
            self.statusBar().showMessage("Error: Tempo debe ser un número")
            return

        self.analyze_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.statusBar().showMessage("Analizando audio...")

        # Crear y lanzar thread de análisis
        self.analysis_thread = AnalysisThread(self.audio_file, tempo)
        self.analysis_thread.progress.connect(self.update_progress)
        self.analysis_thread.finished.connect(self.analysis_complete)
        self.analysis_thread.error.connect(self.analysis_error)
        self.analysis_thread.start()

    def update_progress(self, value):
        """Actualiza la barra de progreso."""
        self.progress_bar.setValue(value)

    def analysis_complete(self, results):
        """Maneja la finalización del análisis."""
        self.analysis_results = results

        # Mostrar resumen de resultados
        metadata = results['metadata']
        groove_data = results['groove_data']
        stats = results['humanization_stats']

        summary = f"""
=== ANÁLISIS COMPLETADO ===

METADATA:
- Archivo: {metadata['audio_file']}
- Sample Rate: {metadata['sample_rate']} Hz
- Duración: {metadata['duration_seconds']:.2f} s
- Tempo: {metadata['tempo_bpm']} BPM
- Time Signature: {metadata['time_signature']}

DETECCIÓN DE ONSETS:
- Total de onsets detectados: {len(groove_data)}

ESTADÍSTICAS DE HUMANIZACIÓN:
- Desviación temporal promedio: {stats['avg_timing_deviation_ms']:.2f} ms
- Desviación estándar: {stats['std_timing_deviation_ms']:.2f} ms
- Variación de velocidad promedio: {stats['avg_velocity_variation']:.3f}
- Factor de swing: {stats['swing_factor']:.3f}

Primeros 5 onsets:
"""

        for i, onset in enumerate(groove_data[:5]):
            summary += f"\n  {i+1}. t={onset['onset_time']:.3f}s, vel={onset['velocity']}, dev={onset['timing_deviation_ms']:.2f}ms"

        self.results_text.setText(summary)

        # Habilitar exportación
        self.export_json_button.setEnabled(True)
        self.export_csv_button.setEnabled(True)
        self.analyze_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Análisis completado exitosamente")

    def analysis_error(self, error_msg):
        """Maneja errores durante el análisis."""
        self.results_text.setText(f"❌ ERROR EN EL ANÁLISIS:\n\n{error_msg}")
        self.analyze_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Error en el análisis")

    def export_json(self):
        """Exporta los resultados a JSON."""
        if not self.analysis_results:
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar JSON",
            "groove_analysis.json",
            "JSON Files (*.json)"
        )

        if file_name:
            import json
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
            self.statusBar().showMessage(f"JSON exportado: {file_name}")

    def export_csv(self):
        """Exporta los resultados a CSV."""
        if not self.analysis_results:
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar CSV",
            "groove_analysis.csv",
            "CSV Files (*.csv)"
        )

        if file_name:
            import pandas as pd
            df = pd.DataFrame(self.analysis_results['groove_data'])
            df.to_csv(file_name, index=False)
            self.statusBar().showMessage(f"CSV exportado: {file_name}")


def main():
    """Función principal."""
    app = QApplication(sys.argv)
    window = GrooveExtractorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
