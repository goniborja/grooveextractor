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

# Rutas base de assets
ASSETS_BASE = Path("assets") / "ui" / "vintage_obsession"
ASSETS_DIR = ASSETS_BASE / "Assets"
ONESHOTS_DIR = ASSETS_DIR / "Animations" / "Oneshots"
STRIPS_DIR = ASSETS_DIR / "Animations" / "Strips"

# ==================== ESCALAS ====================
# Pads
SCALE_PAD = 0.26              # Pads normales
SCALE_PAD_AZTERTU = 0.55      # AZTERTU: el más grande de toda la UI

# Knobs
SCALE_KNOB_SMALL = 0.25       # Knobs pequeños (METADATUAK, BANATU)
SCALE_KNOB_ESTILO = 0.22      # Knob ESTILOA (grande)

# Switches
SCALE_SWITCH = 0.46

# VU Meter y LEDs
SCALE_VU = 0.85               # VU meter muy grande
SCALE_LED_METER = 0.35        # LED meters x3 más grandes

# Screens
SCALE_SCREEN_SMALL = 0.23     # Screens pequeños
SCALE_SCREEN_BIG = 0.65       # Screens grandes (zona D) - x3

# Botones
SCALE_BUTTON = 0.46


class AnalysisThread(QThread):
    """Thread para análisis de audio sin bloquear la UI."""

    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    bpm_detected = pyqtSignal(float, str)

    def __init__(self, audio_file: str, use_separation: bool = False, use_full_stems: bool = False):
        super().__init__()
        self.audio_file = audio_file
        self.use_separation = use_separation
        self.use_full_stems = use_full_stems
        self.config = ExtractorConfig(
            use_stem_separation=use_separation,
            analyze_hihat_type=True,
            export_excel=False
        )
        self.extractor = GrooveExtractor(self.config)
        self.groove_data = None

    def run(self):
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
    separation_toggled = pyqtSignal(bool)
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
        self.setWindowTitle("Groove Extractor - Vintage Edition")
        self.setFixedSize(1200, 800)
        self._set_background()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Columna izquierda (A, D, G)
        left_column = QVBoxLayout()
        left_column.setSpacing(10)
        left_column.addWidget(self._create_zone_a())
        left_column.addWidget(self._create_zone_d())
        left_column.addStretch(1)
        left_column.addWidget(self._create_zone_g())

        # Columna central (B, E)
        center_column = QVBoxLayout()
        center_column.setSpacing(10)
        center_column.addWidget(self._create_zone_b(), stretch=4)
        center_column.addWidget(self._create_zone_e(), stretch=1)

        # Columna derecha (C)
        right_column = QVBoxLayout()
        right_column.setSpacing(0)
        right_column.addWidget(self._create_zone_c())

        main_layout.addLayout(left_column, stretch=1)
        main_layout.addLayout(center_column, stretch=3)
        main_layout.addLayout(right_column, stretch=1)

    def _set_background(self):
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
        label = QLabel(text)
        label.setStyleSheet("color: #AAAAAA; font-size: 9px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    # ==================== ZONA A ====================
    def _create_zone_a(self) -> QWidget:
        """Zona A: KARGATU (izquierda) + METADATUAK (knob+switch) + BANATU (knob+switch)."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(12)
        layout.setContentsMargins(5, 5, 5, 5)

        # KARGATU - alineado a la izquierda
        kargatu_layout = QVBoxLayout()
        kargatu_layout.setSpacing(3)
        self.pad_import = ImagePad(
            str(ONESHOTS_DIR / "pad_off.png"),
            str(ONESHOTS_DIR / "pad_on.png"),
            "KARGATU",
            scale=SCALE_PAD
        )
        kargatu_layout.addWidget(self.pad_import, alignment=Qt.AlignmentFlag.AlignLeft)
        kargatu_layout.addWidget(self._create_label("KARGATU"), alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(kargatu_layout)

        # METADATUAK - knob pequeño + switch
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(8)
        self.knob_metadata = FilmstripKnob(
            str(STRIPS_DIR / "Knob_small.png"),
            128, num_positions=2, scale=SCALE_KNOB_SMALL
        )
        self.switch_metadata = ImageSwitch(
            str(ONESHOTS_DIR / "switch_hor_st1.png"),
            str(ONESHOTS_DIR / "switch_hor_st2.png"),
            scale=SCALE_SWITCH
        )
        meta_layout.addWidget(self.knob_metadata)
        meta_layout.addWidget(self.switch_metadata)
        meta_layout.addWidget(self._create_label("METADATUAK"))
        meta_layout.addStretch()
        layout.addLayout(meta_layout)

        # BANATU - knob pequeño + switch (separar batería)
        banatu_layout = QHBoxLayout()
        banatu_layout.setSpacing(8)
        self.knob_banatu = FilmstripKnob(
            str(STRIPS_DIR / "Knob_small.png"),
            128, num_positions=2, scale=SCALE_KNOB_SMALL
        )
        self.switch_banatu = ImageSwitch(
            str(ONESHOTS_DIR / "switch_hor_st1.png"),
            str(ONESHOTS_DIR / "switch_hor_st2.png"),
            scale=SCALE_SWITCH
        )
        banatu_layout.addWidget(self.knob_banatu)
        banatu_layout.addWidget(self.switch_banatu)
        banatu_layout.addWidget(self._create_label("BANATU"))
        banatu_layout.addStretch()
        layout.addLayout(banatu_layout)

        return zone

    # ==================== ZONA B ====================
    def _create_zone_b(self) -> QWidget:
        """Zona B: VU meter (muy grande), LED meters (x3), AZTERTU (el más grande)."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)

        # VU Meter - muy grande
        vu_folder = str(ONESHOTS_DIR / "VU_meter")
        self.vu_meter = AnimatedVUMeter(vu_folder, 256, scale=SCALE_VU)
        layout.addWidget(self.vu_meter, alignment=Qt.AlignmentFlag.AlignCenter)

        # Screen de estado
        self.screen_status = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=False,
            scale=SCALE_SCREEN_SMALL
        )
        self.screen_status.set_text("PREST")
        self.screen_status.set_text_color("#888888")
        layout.addWidget(self.screen_status, alignment=Qt.AlignmentFlag.AlignCenter)

        # LED Meters - x3 más grandes
        meters_layout = QHBoxLayout()
        meters_layout.setSpacing(30)

        for name, attr in [("KICK", "led_kick"), ("SNARE", "led_snare"), ("HI-HAT", "led_hihat")]:
            led_layout = QVBoxLayout()
            led_layout.setSpacing(3)
            led = AnimatedLED(
                str(STRIPS_DIR / "LED_meter.png"),
                62, scale=SCALE_LED_METER
            )
            setattr(self, attr, led)
            led_layout.addWidget(led, alignment=Qt.AlignmentFlag.AlignCenter)
            led_layout.addWidget(self._create_label(name))
            meters_layout.addLayout(led_layout)

        layout.addLayout(meters_layout)

        # AZTERTU - el PAD más grande de toda la UI
        self.pad_analyze = ImagePad(
            str(ONESHOTS_DIR / "pad_off.png"),
            str(ONESHOTS_DIR / "pad_on.png"),
            "AZTERTU",
            scale=SCALE_PAD_AZTERTU
        )
        layout.addWidget(self.pad_analyze, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._create_label("AZTERTU"))

        return zone

    # ==================== ZONA C ====================
    def _create_zone_c(self) -> QWidget:
        """Zona C: ESPORTATU, switch MIDI/WAV, IREKI/GORDE (muy abajo)."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)

        # ESPORTATU arriba
        layout.addStretch(1)
        self.pad_export = ImagePad(
            str(ONESHOTS_DIR / "pad_off.png"),
            str(ONESHOTS_DIR / "pad_on.png"),
            "ESPORTATU",
            scale=SCALE_PAD
        )
        layout.addWidget(self.pad_export, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._create_label("ESPORTATU"))

        # Switch MIDI/WAV
        layout.addStretch(1)
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

        # Espacio grande antes de IREKI/GORDE
        layout.addStretch(4)

        # IREKI
        self.btn_open = ImageButton(
            str(STRIPS_DIR / "but_small_rectangle.png"),
            6, "IREKI",
            scale=SCALE_BUTTON
        )
        layout.addWidget(self.btn_open, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)

        # GORDE
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
        """Zona D: Knob ESTILOA (grande) + 3 screens (grandes, más abajo)."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(15)
        layout.setContentsMargins(5, 5, 5, 5)

        # Knob ESTILOA - grande
        knob_layout = QVBoxLayout()
        knob_layout.setSpacing(3)
        self.knob_style = FilmstripKnob(
            str(STRIPS_DIR / "Knob_big.png"),
            128, num_positions=6, scale=SCALE_KNOB_ESTILO
        )
        self.knob_style.set_labels(self.STYLES)
        knob_layout.addWidget(self.knob_style, alignment=Qt.AlignmentFlag.AlignCenter)
        knob_layout.addWidget(self._create_label("ESTILOA"))
        layout.addLayout(knob_layout)

        # Espacio antes de los screens
        layout.addSpacing(20)

        # Screens grandes (x3)
        screens_layout = QVBoxLayout()
        screens_layout.setSpacing(8)

        # Screen estilo
        self.screen_style = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=False,
            scale=SCALE_SCREEN_BIG
        )
        self.screen_style.set_text(self.STYLES[0])
        self.screen_style.set_amber_color()
        screens_layout.addWidget(self.screen_style)

        # Screen batería
        self.screen_drummer = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=True,
            scale=SCALE_SCREEN_BIG
        )
        self.screen_drummer.set_text("BATERIA")
        screens_layout.addWidget(self.screen_drummer)

        # Screen BPM
        self.screen_bpm = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=True,
            scale=SCALE_SCREEN_BIG
        )
        self.screen_bpm.set_text("120")
        screens_layout.addWidget(self.screen_bpm)

        layout.addLayout(screens_layout)

        return zone

    # ==================== ZONA E ====================
    def _create_zone_e(self) -> QWidget:
        """Zona E: Screen de porcentaje."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setContentsMargins(5, 5, 5, 5)

        self.screen_progress = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=False,
            scale=0.4
        )
        self.screen_progress.set_text("0%")
        self.screen_progress.set_font_size(14)
        layout.addWidget(self.screen_progress, alignment=Qt.AlignmentFlag.AlignCenter)

        return zone

    # ==================== ZONA G ====================
    def _create_zone_g(self) -> QWidget:
        """Zona G: BPM ANTZEMAN (sin slider horizontal - no tiene función clara)."""
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
        layout.addWidget(self.pad_bpm, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._create_label("BPM ANTZEMAN"), alignment=Qt.AlignmentFlag.AlignLeft)

        return zone

    # ==================== CONEXIONES ====================
    def _connect_signals(self):
        # Zona A
        self.pad_import.clicked.connect(self._on_import_clicked)
        self.knob_metadata.value_changed.connect(self._on_metadata_knob_changed)
        self.switch_metadata.toggled.connect(self.metadata_toggled.emit)
        self.knob_banatu.value_changed.connect(self._on_banatu_knob_changed)
        self.switch_banatu.toggled.connect(self.separation_toggled.emit)

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
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de audio", "",
            "Audio Files (*.wav *.WAV *.mp3 *.MP3);;All Files (*)"
        )
        if file_name:
            self.audio_file = file_name
            self.screen_status.set_text(f"Kargatuta: {Path(file_name).name[:12]}")
            self.import_song_clicked.emit()

    def _on_metadata_knob_changed(self, value: int):
        """Knob METADATUAK controla el switch."""
        self.switch_metadata.set_state(value == 1)

    def _on_banatu_knob_changed(self, value: int):
        """Knob BANATU controla el switch."""
        self.switch_banatu.set_state(value == 1)

    def _on_analyze_clicked(self):
        if not self.audio_file:
            self.screen_status.set_text("Kargatu audioa!")
            return
        self._start_analysis()
        self.analyze_clicked.emit()

    def _on_format_changed(self, is_wav: bool):
        self.export_format_changed.emit("WAV" if is_wav else "MIDI")

    def _on_style_changed(self, index: int):
        style = self.STYLES[index] if index < len(self.STYLES) else self.STYLES[0]
        self.screen_style.set_text(style)
        self.style_changed.emit(style)

    def _on_bpm_changed(self, text: str):
        try:
            bpm = int(text)
            self.bpm_changed.emit(bpm)
        except ValueError:
            pass

    def _on_detect_bpm_clicked(self):
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
        self.vu_meter.set_level(level)

    def set_status_message(self, message: str):
        self.screen_status.set_text(message[:25])

    def set_progress(self, percent: int):
        self.screen_progress.set_text(f"{percent}%")

    def set_kick_level(self, level: float):
        self.led_kick.set_brightness(level)

    def set_snare_level(self, level: float):
        self.led_snare.set_brightness(level)

    def set_hihat_level(self, level: float):
        self.led_hihat.set_brightness(level)

    # ==================== BACKEND ====================
    def _start_analysis(self):
        if not self.audio_file:
            self.screen_status.set_text("Ez dago audiorik")
            return
        if self.analysis_thread and self.analysis_thread.isRunning():
            self.screen_status.set_text("Analisatzen...")
            return

        # Configuración basada en knobs
        use_separation = self.switch_banatu.is_on()
        use_full_stems = self.knob_banatu.get_value() == 1

        self.analysis_thread = AnalysisThread(
            self.audio_file,
            use_separation=use_separation,
            use_full_stems=use_full_stems
        )
        self.analysis_thread.progress.connect(self._on_analysis_progress)
        self.analysis_thread.finished.connect(self._on_analysis_finished)
        self.analysis_thread.error.connect(self._on_analysis_error)
        self.analysis_thread.bpm_detected.connect(self._on_bpm_detected)

        self.led_kick.pulse()
        self.led_snare.pulse()
        self.led_hihat.pulse()
        self.screen_status.set_text("Analisatzen...")

        self.analysis_thread.start()

    def _on_analysis_progress(self, percent: int):
        self.set_progress(percent)
        self.set_vu_level(percent / 100.0)

    def _on_analysis_finished(self, results: dict):
        self.led_kick.turn_off()
        self.led_snare.turn_off()
        self.led_hihat.turn_off()
        self.screen_status.set_text("Amaituta!")

        instruments = results.get('instruments', {})
        for name, led_attr in [('kick', 'led_kick'), ('snare', 'led_snare'), ('hihat', 'led_hihat')]:
            if name in instruments:
                humanization = instruments[name].get('humanization', {})
                on_grid = humanization.get('on_grid_percent', 50) if humanization else 50
                getattr(self, led_attr).set_brightness(on_grid / 100.0)

        self._last_results = results

    def _on_analysis_error(self, error_msg: str):
        self.led_kick.turn_off()
        self.led_snare.turn_off()
        self.led_hihat.turn_off()
        self.screen_status.set_text(f"Errorea: {error_msg[:15]}")
        self.set_progress(0)

    def _on_bpm_detected(self, bpm: float, style: str):
        self.screen_bpm.set_text(str(int(bpm)))
        style_lower = style.lower()
        for i, s in enumerate(self.STYLES):
            if s.lower() == style_lower or s.lower().replace(" ", "_") == style_lower:
                self.knob_style.set_value(i)
                self.screen_style.set_text(s)
                break
