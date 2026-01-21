"""
MainWindow - Ventana principal de Groove Extractor con UI vintage.
Usa widgets basados en imágenes PNG del kit Vintage Obsession.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QPalette, QBrush

from src import GrooveExtractor, ExtractorConfig
from .widgets.image_loader import load_pixmap
from .widgets import (
    ImagePad,
    ImageSwitch,
    ImageButton,
    FilmstripSlider,
    FilmstripKnob,
    AnimatedVUMeter,
    AnimatedLED,
    VintageScreen,
)

# Rutas base de assets (usando pathlib para compatibilidad Windows/Linux)
ASSETS_BASE = Path("assets") / "ui" / "vintage_obsession"
ASSETS_DIR = ASSETS_BASE / "Assets"
ONESHOTS_DIR = ASSETS_DIR / "Animations" / "Oneshots"
STRIPS_DIR = ASSETS_DIR / "Animations" / "Strips"

# Escalas para que los widgets quepan en 1200x800
SCALE_PAD = 0.26         # Pads: 208 -> 54px
SCALE_PAD_BIG = 0.32     # Pad AZTERTU más grande
SCALE_SWITCH = 0.46      # Switches: 102x44 -> 47x20
SCALE_SLIDER_H = 0.23    # Sliders horizontales: 444x104 -> 102x24
SCALE_KNOB_BIG = 0.15    # Knob big (muy grande, necesita escala pequeña)
SCALE_LED_METER = 0.12   # LED meters para Kick/Snare/HiHat
SCALE_BUTTON = 0.46      # Buttons small: 144x62 -> 66x29
SCALE_SCREEN = 0.23      # Screen: 510x110 -> 117x25
SCALE_VU = 0.45          # VU meter: 325x184 -> 146x83


class AnalysisThread(QThread):
    """Thread para análisis de audio sin bloquear la UI."""

    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    bpm_detected = pyqtSignal(float, str)  # bpm, style

    def __init__(self, audio_file: str, use_separation: bool = False):
        super().__init__()
        self.audio_file = audio_file
        self.use_separation = use_separation
        self.config = ExtractorConfig(
            use_stem_separation=use_separation,
            analyze_hihat_type=True,
            export_excel=False
        )
        self.extractor = GrooveExtractor(self.config)
        self.groove_data = None

    def run(self):
        """Ejecuta el análisis en segundo plano."""
        try:
            self.progress.emit(10)
            self.progress.emit(30)
            self.groove_data = self.extractor.extract(self.audio_file)
            self.progress.emit(70)
            self.bpm_detected.emit(self.groove_data.bpm, self.groove_data.style.value)
            self.progress.emit(90)
            results = self.extractor.extract_to_dict(self.audio_file)
            self.progress.emit(100)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

    def export_to_excel(self, output_path: str):
        """Exporta los resultados a Excel."""
        if self.groove_data:
            from src.exporters import ExcelExporter
            exporter = ExcelExporter()
            exporter.export(self.groove_data, output_path)


class MainWindow(QMainWindow):
    """Ventana principal de Groove Extractor con interfaz vintage."""

    # Señales
    import_song_clicked = pyqtSignal()
    export_drums_clicked = pyqtSignal()
    detect_bpm_clicked = pyqtSignal()
    analyze_clicked = pyqtSignal()
    metadata_toggled = pyqtSignal(bool)
    export_format_changed = pyqtSignal(str)
    style_changed = pyqtSignal(str)
    drummer_name_changed = pyqtSignal(str)
    bpm_changed = pyqtSignal(int)
    open_project_clicked = pyqtSignal()
    save_project_clicked = pyqtSignal()

    STYLES = ["Ska", "Rocksteady", "Early Reggae", "Roots Reggae", "Steppers", "Dub"]

    def __init__(self):
        super().__init__()
        self.audio_file = None
        self.analysis_thread = None
        self._last_results = None
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle("Groove Extractor - Vintage Edition")
        self.setFixedSize(1200, 800)
        self._set_background()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal de 3 columnas
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Columna izquierda (A, D, G)
        left_column = QVBoxLayout()
        left_column.setSpacing(15)
        left_column.addWidget(self._create_zone_a())
        left_column.addWidget(self._create_zone_d())
        left_column.addStretch(1)
        left_column.addWidget(self._create_zone_g())

        # Columna central (B, E)
        center_column = QVBoxLayout()
        center_column.setSpacing(15)
        center_column.addWidget(self._create_zone_b(), stretch=3)
        center_column.addWidget(self._create_zone_e(), stretch=1)

        # Columna derecha (C)
        right_column = QVBoxLayout()
        right_column.setSpacing(0)
        right_column.addWidget(self._create_zone_c())

        main_layout.addLayout(left_column, stretch=1)
        main_layout.addLayout(center_column, stretch=2)
        main_layout.addLayout(right_column, stretch=1)

    def _set_background(self):
        """Establece el fondo de la ventana."""
        bg_path = ASSETS_DIR / "back_a.png"
        if bg_path.exists():
            palette = self.palette()
            pixmap = load_pixmap(str(bg_path))
            scaled = pixmap.scaled(1200, 800, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
            palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled))
            self.setPalette(palette)
        else:
            self.setStyleSheet("background-color: #1a1a1a;")

    def _create_label(self, text: str) -> QLabel:
        """Crea un label con estilo consistente."""
        label = QLabel(text)
        label.setStyleSheet("color: #AAAAAA; font-size: 9px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    # ==================== ZONA A ====================
    def _create_zone_a(self) -> QWidget:
        """Crea Zona A: Importar + switch metadatos (sin BANATU)."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 5, 5, 5)  # Margen izquierdo extra

        # Pad importar
        self.pad_import = ImagePad(
            str(ONESHOTS_DIR / "pad_off.png"),
            str(ONESHOTS_DIR / "pad_on.png"),
            "KARGATU",
            scale=SCALE_PAD
        )
        layout.addWidget(self.pad_import, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._create_label("KARGATU"))

        # Switch metadatos (movido a la derecha con margen)
        switch_layout = QHBoxLayout()
        switch_layout.setContentsMargins(20, 0, 0, 0)  # Margen izquierdo
        switch_layout.setSpacing(5)
        self.switch_metadata = ImageSwitch(
            str(ONESHOTS_DIR / "switch_hor_st1.png"),
            str(ONESHOTS_DIR / "switch_hor_st2.png"),
            scale=SCALE_SWITCH
        )
        switch_layout.addWidget(self.switch_metadata)
        switch_layout.addWidget(self._create_label("METADATUAK"))
        switch_layout.addStretch()
        layout.addLayout(switch_layout)

        return zone

    # ==================== ZONA B ====================
    def _create_zone_b(self) -> QWidget:
        """Crea Zona B: VU meter, screen status, LED meters, pad AZTERTU."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)

        # VU Meter
        vu_folder = str(ONESHOTS_DIR / "VU_meter")
        self.vu_meter = AnimatedVUMeter(vu_folder, 256, scale=SCALE_VU)
        layout.addWidget(self.vu_meter, alignment=Qt.AlignmentFlag.AlignCenter)

        # Screen de estado (color gris apagado)
        self.screen_status = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=False,
            scale=SCALE_SCREEN
        )
        self.screen_status.set_text("PREST")
        self.screen_status.set_text_color("#888888")  # Gris apagado
        layout.addWidget(self.screen_status, alignment=Qt.AlignmentFlag.AlignCenter)

        # LED Meters para Kick/Snare/HiHat (en vez de sliders)
        meters_layout = QHBoxLayout()
        meters_layout.setSpacing(20)

        # LED Kick
        kick_layout = QVBoxLayout()
        kick_layout.setSpacing(3)
        self.led_kick = AnimatedLED(
            str(STRIPS_DIR / "LED_meter.png"),
            62, scale=SCALE_LED_METER
        )
        kick_layout.addWidget(self.led_kick, alignment=Qt.AlignmentFlag.AlignCenter)
        kick_layout.addWidget(self._create_label("KICK"))
        meters_layout.addLayout(kick_layout)

        # LED Snare
        snare_layout = QVBoxLayout()
        snare_layout.setSpacing(3)
        self.led_snare = AnimatedLED(
            str(STRIPS_DIR / "LED_meter.png"),
            62, scale=SCALE_LED_METER
        )
        snare_layout.addWidget(self.led_snare, alignment=Qt.AlignmentFlag.AlignCenter)
        snare_layout.addWidget(self._create_label("SNARE"))
        meters_layout.addLayout(snare_layout)

        # LED HiHat
        hihat_layout = QVBoxLayout()
        hihat_layout.setSpacing(3)
        self.led_hihat = AnimatedLED(
            str(STRIPS_DIR / "LED_meter.png"),
            62, scale=SCALE_LED_METER
        )
        hihat_layout.addWidget(self.led_hihat, alignment=Qt.AlignmentFlag.AlignCenter)
        hihat_layout.addWidget(self._create_label("HI-HAT"))
        meters_layout.addLayout(hihat_layout)

        layout.addLayout(meters_layout)

        # Pad AZTERTU (análisis completo)
        self.pad_analyze = ImagePad(
            str(ONESHOTS_DIR / "pad_off.png"),
            str(ONESHOTS_DIR / "pad_on.png"),
            "AZTERTU",
            scale=SCALE_PAD_BIG
        )
        layout.addWidget(self.pad_analyze, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._create_label("AZTERTU"))

        return zone

    # ==================== ZONA C ====================
    def _create_zone_c(self) -> QWidget:
        """Crea Zona C: Exportar, formato, botones proyecto (distribuidos verticalmente)."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)

        # Espaciador arriba
        layout.addStretch(1)

        # Pad exportar
        self.pad_export = ImagePad(
            str(ONESHOTS_DIR / "pad_off.png"),
            str(ONESHOTS_DIR / "pad_on.png"),
            "ESPORTATU",
            scale=SCALE_PAD
        )
        layout.addWidget(self.pad_export, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._create_label("ESPORTATU"))

        layout.addStretch(1)

        # Switch MIDI/WAV
        format_layout = QHBoxLayout()
        format_layout.setSpacing(5)
        format_layout.addStretch()
        format_layout.addWidget(self._create_label("MIDI"))
        self.switch_format = ImageSwitch(
            str(ONESHOTS_DIR / "switch_hor_st1.png"),
            str(ONESHOTS_DIR / "switch_hor_st2.png"),
            scale=SCALE_SWITCH
        )
        format_layout.addWidget(self.switch_format)
        format_layout.addWidget(self._create_label("WAV"))
        format_layout.addStretch()
        layout.addLayout(format_layout)

        layout.addStretch(1)

        # Botón abrir proyecto
        self.btn_open = ImageButton(
            str(STRIPS_DIR / "but_small_rectangle.png"),
            6, "IREKI",
            scale=SCALE_BUTTON
        )
        layout.addWidget(self.btn_open, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)

        # Botón guardar proyecto
        self.btn_save = ImageButton(
            str(STRIPS_DIR / "but_small_rectangle.png"),
            6, "GORDE",
            scale=SCALE_BUTTON
        )
        layout.addWidget(self.btn_save, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)

        return zone

    # ==================== ZONA D ====================
    def _create_zone_d(self) -> QWidget:
        """Crea Zona D: Knob estilos (grande), screens."""
        zone = QWidget()
        layout = QHBoxLayout(zone)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)

        # Knob de estilos (usando Knob_big)
        knob_layout = QVBoxLayout()
        knob_layout.setSpacing(3)
        self.knob_style = FilmstripKnob(
            str(STRIPS_DIR / "Knob_big.png"),
            128, num_positions=6, scale=SCALE_KNOB_BIG
        )
        self.knob_style.set_labels(self.STYLES)
        knob_layout.addWidget(self.knob_style, alignment=Qt.AlignmentFlag.AlignCenter)
        knob_layout.addWidget(self._create_label("ESTILOA"))
        layout.addLayout(knob_layout)

        # Screens
        screens_layout = QVBoxLayout()
        screens_layout.setSpacing(5)

        # Screen estilo seleccionado
        self.screen_style = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=False,
            scale=SCALE_SCREEN
        )
        self.screen_style.set_text(self.STYLES[0])
        self.screen_style.set_amber_color()
        screens_layout.addWidget(self.screen_style)

        # Screen nombre batería
        self.screen_drummer = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=True,
            scale=SCALE_SCREEN
        )
        self.screen_drummer.set_text("BATERIA")
        screens_layout.addWidget(self.screen_drummer)

        # Screen BPM
        self.screen_bpm = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=True,
            scale=SCALE_SCREEN
        )
        self.screen_bpm.set_text("120")
        screens_layout.addWidget(self.screen_bpm)

        layout.addLayout(screens_layout)

        return zone

    # ==================== ZONA E ====================
    def _create_zone_e(self) -> QWidget:
        """Crea Zona E: Screen de porcentaje."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setContentsMargins(5, 5, 5, 5)

        self.screen_progress = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=False,
            scale=0.32
        )
        self.screen_progress.set_text("0%")
        self.screen_progress.set_font_size(12)
        layout.addWidget(self.screen_progress, alignment=Qt.AlignmentFlag.AlignCenter)

        return zone

    # ==================== ZONA G ====================
    def _create_zone_g(self) -> QWidget:
        """Crea Zona G: Detectar BPM + slider horizontal."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)

        # Pad detectar BPM
        self.pad_bpm = ImagePad(
            str(ONESHOTS_DIR / "pad_off.png"),
            str(ONESHOTS_DIR / "pad_on.png"),
            "BPM ANTZEMAN",
            scale=SCALE_PAD
        )
        layout.addWidget(self.pad_bpm, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._create_label("BPM ANTZEMAN"))

        # Slider horizontal para animación
        self.slider_bpm_detect = FilmstripSlider(
            str(STRIPS_DIR / "Hor_slider.png"),
            256, 'horizontal', scale=SCALE_SLIDER_H
        )
        layout.addWidget(self.slider_bpm_detect, alignment=Qt.AlignmentFlag.AlignCenter)

        return zone

    # ==================== CONEXIONES ====================
    def _connect_signals(self):
        """Conecta las señales de los widgets."""
        # Zona A
        self.pad_import.clicked.connect(self._on_import_clicked)
        self.switch_metadata.toggled.connect(self.metadata_toggled.emit)

        # Zona B
        self.pad_analyze.clicked.connect(self._on_analyze_clicked)

        # Zona C
        self.pad_export.clicked.connect(self._on_export_clicked)
        self.switch_format.toggled.connect(self._on_format_changed)
        self.btn_open.clicked.connect(self.open_project_clicked.emit)
        self.btn_save.clicked.connect(self.save_project_clicked.emit)

        # Zona D
        self.knob_style.value_changed.connect(self._on_style_changed)
        self.screen_drummer.text_changed.connect(self.drummer_name_changed.emit)
        self.screen_bpm.text_changed.connect(self._on_bpm_changed)

        # Zona G
        self.pad_bpm.clicked.connect(self._on_detect_bpm_clicked)

    # ==================== HANDLERS ====================
    def _on_import_clicked(self):
        """Maneja click en pad de importar (solo carga, no analiza)."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de audio", "",
            "Audio Files (*.wav *.WAV *.mp3 *.MP3);;All Files (*)"
        )
        if file_name:
            self.audio_file = file_name
            self.screen_status.set_text(f"Kargatuta: {Path(file_name).name[:12]}")
            self.import_song_clicked.emit()

    def _on_analyze_clicked(self):
        """Maneja click en pad AZTERTU - ejecuta análisis completo."""
        if not self.audio_file:
            self.screen_status.set_text("Kargatu audioa!")
            return
        self._start_analysis()
        self.analyze_clicked.emit()

    def _on_format_changed(self, is_wav: bool):
        """Maneja cambio de formato de exportación."""
        self.export_format_changed.emit("WAV" if is_wav else "MIDI")

    def _on_style_changed(self, index: int):
        """Maneja cambio de estilo."""
        style = self.STYLES[index] if index < len(self.STYLES) else self.STYLES[0]
        self.screen_style.set_text(style)
        self.style_changed.emit(style)

    def _on_bpm_changed(self, text: str):
        """Maneja cambio de BPM."""
        try:
            bpm = int(text)
            self.bpm_changed.emit(bpm)
        except ValueError:
            pass

    def _on_detect_bpm_clicked(self):
        """Detecta BPM del archivo cargado."""
        if not self.audio_file:
            self.screen_status.set_text("Kargatu audioa!")
            return

        if self._last_results:
            bpm = self._last_results.get('bpm', 120)
            style = self._last_results.get('style', 'ska')
            self._on_bpm_detected(float(bpm), style)
        else:
            self._start_analysis()

    def _on_export_clicked(self):
        """Exporta los resultados a Excel."""
        if not self.analysis_thread or not self.analysis_thread.groove_data:
            self.screen_status.set_text("Ez dago daturik")
            return

        default_name = Path(self.audio_file).stem + "_groove.xlsx" if self.audio_file else "groove.xlsx"
        output_file, _ = QFileDialog.getSaveFileName(
            self, "Gorde fitxategia", default_name,
            "Excel Files (*.xlsx);;All Files (*)"
        )

        if output_file:
            try:
                self.screen_status.set_text("Esportatzen...")
                self.analysis_thread.export_to_excel(output_file)
                self.screen_status.set_text("Esportatuta!")
            except Exception as e:
                self.screen_status.set_text(f"Errorea: {str(e)[:12]}")

    # ==================== MÉTODOS PÚBLICOS ====================
    def set_vu_level(self, level: float):
        """Establece el nivel del VU meter."""
        self.vu_meter.set_level(level)

    def set_status_message(self, message: str):
        """Establece el mensaje de estado."""
        self.screen_status.set_text(message[:25])

    def set_progress(self, percent: int):
        """Establece el porcentaje de progreso."""
        self.screen_progress.set_text(f"{percent}%")

    def set_kick_level(self, level: float):
        """Establece nivel del LED Kick."""
        self.led_kick.set_brightness(level)

    def set_snare_level(self, level: float):
        """Establece nivel del LED Snare."""
        self.led_snare.set_brightness(level)

    def set_hihat_level(self, level: float):
        """Establece nivel del LED HiHat."""
        self.led_hihat.set_brightness(level)

    def set_detecting_bpm(self, active: bool):
        """Activa animación de detección de BPM."""
        if active:
            self.slider_bpm_detect.animate_to(1.0, 1000)
        else:
            self.slider_bpm_detect.animate_to(0.0, 500)

    # ==================== BACKEND ====================
    def _start_analysis(self):
        """Inicia el análisis del archivo de audio."""
        if not self.audio_file:
            self.screen_status.set_text("Ez dago audiorik")
            return

        if self.analysis_thread and self.analysis_thread.isRunning():
            self.screen_status.set_text("Analisatzen...")
            return

        self.analysis_thread = AnalysisThread(self.audio_file, use_separation=False)
        self.analysis_thread.progress.connect(self._on_analysis_progress)
        self.analysis_thread.finished.connect(self._on_analysis_finished)
        self.analysis_thread.error.connect(self._on_analysis_error)
        self.analysis_thread.bpm_detected.connect(self._on_bpm_detected)

        # Activar indicadores
        self.led_kick.pulse()
        self.led_snare.pulse()
        self.led_hihat.pulse()
        self.set_detecting_bpm(True)
        self.screen_status.set_text("Analisatzen...")

        self.analysis_thread.start()

    def _on_analysis_progress(self, percent: int):
        """Actualiza el progreso del análisis."""
        self.set_progress(percent)
        self.set_vu_level(percent / 100.0)

    def _on_analysis_finished(self, results: dict):
        """Maneja la finalización del análisis."""
        self.led_kick.turn_off()
        self.led_snare.turn_off()
        self.led_hihat.turn_off()
        self.set_detecting_bpm(False)
        self.screen_status.set_text("Amaituta!")

        # Actualizar LEDs con datos de instrumentos
        instruments = results.get('instruments', {})
        if 'kick' in instruments:
            humanization = instruments['kick'].get('humanization', {})
            on_grid = humanization.get('on_grid_percent', 50) if humanization else 50
            self.set_kick_level(on_grid / 100.0)

        if 'snare' in instruments:
            humanization = instruments['snare'].get('humanization', {})
            on_grid = humanization.get('on_grid_percent', 50) if humanization else 50
            self.set_snare_level(on_grid / 100.0)

        if 'hihat' in instruments:
            humanization = instruments['hihat'].get('humanization', {})
            on_grid = humanization.get('on_grid_percent', 50) if humanization else 50
            self.set_hihat_level(on_grid / 100.0)

        self._last_results = results

    def _on_analysis_error(self, error_msg: str):
        """Maneja errores del análisis."""
        self.led_kick.turn_off()
        self.led_snare.turn_off()
        self.led_hihat.turn_off()
        self.set_detecting_bpm(False)
        self.screen_status.set_text(f"Errorea: {error_msg[:15]}")
        self.set_progress(0)

    def _on_bpm_detected(self, bpm: float, style: str):
        """Actualiza la UI con el BPM y estilo detectados."""
        self.screen_bpm.set_text(str(int(bpm)))

        style_lower = style.lower()
        for i, s in enumerate(self.STYLES):
            if s.lower() == style_lower or s.lower().replace(" ", "_") == style_lower:
                self.knob_style.set_value(i)
                self.screen_style.set_text(s)
                break
