"""
MainWindow - Ventana principal de Groove Extractor usando widgets custom.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from groove_analyzer import GrooveAnalyzer
from .widgets import (
    FileLoaderWidget,
    ParametersWidget,
    AnalyzeButton,
    ProgressWidget,
    ResultsWidget,
    ExportButtonsWidget,
)


class AnalysisThread(QThread):
    """Thread para análisis de audio sin bloquear la UI."""

    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, audio_file: str, tempo: float = 120.0):
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


class MainWindow(QMainWindow):
    """Ventana principal de Groove Extractor con widgets custom."""

    def __init__(self):
        super().__init__()
        self.analysis_thread = None
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle("Groove Extractor - Book of Drums Tool")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel("🥁 GROOVE EXTRACTOR")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #000000;")
        main_layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Herramienta de Análisis DSP para Extracción de Grooves")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #333333; font-size: 11pt;")
        main_layout.addWidget(subtitle)

        # Widgets custom
        self.file_loader = FileLoaderWidget()
        main_layout.addWidget(self.file_loader)

        self.parameters = ParametersWidget()
        main_layout.addWidget(self.parameters)

        self.analyze_button = AnalyzeButton()
        main_layout.addWidget(self.analyze_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.progress = ProgressWidget()
        main_layout.addWidget(self.progress)

        self.results = ResultsWidget()
        main_layout.addWidget(self.results)

        self.export_buttons = ExportButtonsWidget()
        main_layout.addWidget(self.export_buttons)

        # Status bar
        self.statusBar().showMessage("Listo para cargar audio")
        self.statusBar().setStyleSheet("color: #333333;")

    def _connect_signals(self):
        """Conecta las señales de los widgets."""
        # File loader
        self.file_loader.file_loaded.connect(self._on_file_loaded)

        # Analyze button
        self.analyze_button.analyze_requested.connect(self._start_analysis)

        # Export buttons
        self.export_buttons.json_exported.connect(
            lambda path: self.statusBar().showMessage(f"JSON exportado: {path}")
        )
        self.export_buttons.csv_exported.connect(
            lambda path: self.statusBar().showMessage(f"CSV exportado: {path}")
        )
        self.export_buttons.export_error.connect(
            lambda msg: self.statusBar().showMessage(f"Error: {msg}")
        )

    def _on_file_loaded(self, file_path: str):
        """Maneja la carga de un archivo de audio."""
        self.analyze_button.enable_analysis()
        self.statusBar().showMessage(f"Audio cargado: {file_path}")

    def _start_analysis(self):
        """Inicia el análisis del audio."""
        # Validar tempo
        is_valid, error_msg = self.parameters.validate_tempo()
        if not is_valid:
            self.statusBar().showMessage(f"Error: {error_msg}")
            return

        audio_file = self.file_loader.audio_file
        if not audio_file:
            self.statusBar().showMessage("Error: No hay archivo cargado")
            return

        tempo = self.parameters.get_tempo()

        # Preparar UI para análisis
        self.analyze_button.set_analyzing(True)
        self.progress.start("Analizando audio...")
        self.results.clear()
        self.export_buttons.disable_export()
        self.statusBar().showMessage("Analizando audio...")

        # Crear y lanzar thread de análisis
        self.analysis_thread = AnalysisThread(audio_file, tempo)
        self.analysis_thread.progress.connect(self._on_progress)
        self.analysis_thread.finished.connect(self._on_analysis_complete)
        self.analysis_thread.error.connect(self._on_analysis_error)
        self.analysis_thread.start()

    def _on_progress(self, value: int):
        """Actualiza la barra de progreso."""
        self.progress.set_value(value)

    def _on_analysis_complete(self, results: dict):
        """Maneja la finalización exitosa del análisis."""
        self.results.display_results(results)
        self.export_buttons.set_results(results)
        self.analyze_button.set_analyzing(False)
        self.progress.finish()
        self.statusBar().showMessage("Análisis completado exitosamente")

    def _on_analysis_error(self, error_msg: str):
        """Maneja errores durante el análisis."""
        self.results.display_error(error_msg)
        self.analyze_button.set_analyzing(False)
        self.progress.finish()
        self.export_buttons.disable_export()
        self.statusBar().showMessage("Error en el análisis")
