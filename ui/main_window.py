"""
MainWindow - Ventana principal de Groove Extractor con UI vintage.
Usa widgets basados en imágenes PNG del kit Vintage Obsession.
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QPalette, QBrush

from groove_analyzer import GrooveAnalyzer
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
ASSETS_BASE = "assets/ui/vintage_obsession"
ASSETS_DIR = os.path.join(ASSETS_BASE, "Assets")
ONESHOTS_DIR = os.path.join(ASSETS_DIR, "Animations/Oneshots")
STRIPS_DIR = os.path.join(ASSETS_DIR, "Animations/Strips")


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
            self.analyzer.load_audio(self.audio_file)
            self.progress.emit(30)
            self.analyzer.detect_onsets()
            self.progress.emit(60)
            self.analyzer.analyze_dynamics()
            self.progress.emit(80)
            self.analyzer.calculate_timing_deviations(self.tempo)
            self.progress.emit(90)
            results = self.analyzer.get_results()
            self.progress.emit(100)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Ventana principal de Groove Extractor con interfaz vintage."""

    # Señales
    import_song_clicked = pyqtSignal()
    export_drums_clicked = pyqtSignal()
    detect_bpm_clicked = pyqtSignal()
    metadata_toggled = pyqtSignal(bool)
    separate_drums_toggled = pyqtSignal(bool)
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
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle("Groove Extractor - Vintage Edition")
        self.setFixedSize(1200, 800)

        # Fondo de la ventana
        self._set_background()

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal de 3 columnas
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Columna izquierda (A, D, G)
        left_column = QVBoxLayout()
        left_column.setSpacing(20)
        left_column.addWidget(self._create_zone_a())
        left_column.addWidget(self._create_zone_d())
        left_column.addWidget(self._create_zone_g())
        left_column.addStretch()

        # Columna central (B, E)
        center_column = QVBoxLayout()
        center_column.setSpacing(20)
        center_column.addWidget(self._create_zone_b(), stretch=3)
        center_column.addWidget(self._create_zone_e(), stretch=1)

        # Columna derecha (C)
        right_column = QVBoxLayout()
        right_column.setSpacing(20)
        right_column.addWidget(self._create_zone_c())
        right_column.addStretch()

        main_layout.addLayout(left_column)
        main_layout.addLayout(center_column, stretch=2)
        main_layout.addLayout(right_column)

    def _set_background(self):
        """Establece el fondo de la ventana."""
        wallpaper_path = os.path.join(ASSETS_BASE, "Vintage_GUI_KIT_wallpaper_a.png")
        if os.path.exists(wallpaper_path):
            palette = self.palette()
            pixmap = QPixmap(wallpaper_path)
            palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
            self.setPalette(palette)

    def _create_zone_a(self) -> QWidget:
        """Crea Zona A: Importar + switches."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(10)

        # Pad importar
        self.pad_import = ImagePad(
            os.path.join(ONESHOTS_DIR, "pad_off.png"),
            os.path.join(ONESHOTS_DIR, "pad_on.png"),
            "KARGATU"
        )
        layout.addWidget(self.pad_import, alignment=Qt.AlignmentFlag.AlignCenter)

        # Label
        label = QLabel("KARGATU")
        label.setStyleSheet("color: #AAAAAA; font-size: 10px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Switch metadatos
        switch_layout1 = QHBoxLayout()
        self.switch_metadata = ImageSwitch(
            os.path.join(ONESHOTS_DIR, "switch_hor_st1.png"),
            os.path.join(ONESHOTS_DIR, "switch_hor_st2.png")
        )
        switch_layout1.addWidget(self.switch_metadata)
        switch_layout1.addWidget(QLabel("METADATUAK"))
        layout.addLayout(switch_layout1)

        # Switch separar batería
        switch_layout2 = QHBoxLayout()
        self.switch_separate = ImageSwitch(
            os.path.join(ONESHOTS_DIR, "switch_hor_st1.png"),
            os.path.join(ONESHOTS_DIR, "switch_hor_st2.png")
        )
        switch_layout2.addWidget(self.switch_separate)
        switch_layout2.addWidget(QLabel("BANATU BD/SN/HH"))
        layout.addLayout(switch_layout2)

        return zone

    def _create_zone_b(self) -> QWidget:
        """Crea Zona B: VU meter, sliders, LED, status."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(15)

        # VU Meter
        vu_folder = os.path.join(ONESHOTS_DIR, "VU_meter")
        self.vu_meter = AnimatedVUMeter(vu_folder, 256)
        layout.addWidget(self.vu_meter, alignment=Qt.AlignmentFlag.AlignCenter)

        # Screen de estado
        self.screen_status = VintageScreen(
            os.path.join(ASSETS_DIR, "screen.png"),
            editable=False
        )
        self.screen_status.set_text("PREST")
        layout.addWidget(self.screen_status, alignment=Qt.AlignmentFlag.AlignCenter)

        # Sliders y LED
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)

        # Slider Kick
        kick_layout = QVBoxLayout()
        self.slider_kick = FilmstripSlider(
            os.path.join(STRIPS_DIR, "Ver_slider.png"),
            256, 'vertical'
        )
        kick_layout.addWidget(self.slider_kick, alignment=Qt.AlignmentFlag.AlignCenter)
        kick_layout.addWidget(QLabel("KICK"))
        controls_layout.addLayout(kick_layout)

        # Slider Snare
        snare_layout = QVBoxLayout()
        self.slider_snare = FilmstripSlider(
            os.path.join(STRIPS_DIR, "Ver_slider.png"),
            256, 'vertical'
        )
        snare_layout.addWidget(self.slider_snare, alignment=Qt.AlignmentFlag.AlignCenter)
        snare_layout.addWidget(QLabel("SNARE"))
        controls_layout.addLayout(snare_layout)

        # Slider HiHat
        hihat_layout = QVBoxLayout()
        self.slider_hihat = FilmstripSlider(
            os.path.join(STRIPS_DIR, "Ver_slider.png"),
            256, 'vertical'
        )
        hihat_layout.addWidget(self.slider_hihat, alignment=Qt.AlignmentFlag.AlignCenter)
        hihat_layout.addWidget(QLabel("HI-HAT"))
        controls_layout.addLayout(hihat_layout)

        # LED
        led_layout = QVBoxLayout()
        self.led_analyzing = AnimatedLED(
            os.path.join(STRIPS_DIR, "LED_meter.png"),
            62
        )
        led_layout.addWidget(self.led_analyzing, alignment=Qt.AlignmentFlag.AlignCenter)
        led_layout.addWidget(QLabel("AKTIBO"))
        controls_layout.addLayout(led_layout)

        layout.addLayout(controls_layout)

        return zone

    def _create_zone_c(self) -> QWidget:
        """Crea Zona C: Exportar, formato, botones proyecto, slider."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(15)

        # Pad exportar
        self.pad_export = ImagePad(
            os.path.join(ONESHOTS_DIR, "pad_off.png"),
            os.path.join(ONESHOTS_DIR, "pad_on.png"),
            "ESPORTATU"
        )
        layout.addWidget(self.pad_export, alignment=Qt.AlignmentFlag.AlignCenter)

        label_export = QLabel("ESPORTATU")
        label_export.setStyleSheet("color: #AAAAAA; font-size: 10px;")
        label_export.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_export)

        # Switch MIDI/WAV
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("MIDI"))
        self.switch_format = ImageSwitch(
            os.path.join(ONESHOTS_DIR, "switch_hor_st1.png"),
            os.path.join(ONESHOTS_DIR, "switch_hor_st2.png")
        )
        format_layout.addWidget(self.switch_format)
        format_layout.addWidget(QLabel("WAV"))
        layout.addLayout(format_layout)

        # Botón abrir proyecto
        self.btn_open = ImageButton(
            os.path.join(STRIPS_DIR, "but_big_rectangle.png"),
            6, "PROIEKTUA IREKI"
        )
        layout.addWidget(self.btn_open, alignment=Qt.AlignmentFlag.AlignCenter)

        # Botón guardar proyecto
        self.btn_save = ImageButton(
            os.path.join(STRIPS_DIR, "but_big_rectangle.png"),
            6, "PROIEKTUA GORDE"
        )
        layout.addWidget(self.btn_save, alignment=Qt.AlignmentFlag.AlignCenter)

        # Slider reservado
        self.slider_reserved = FilmstripSlider(
            os.path.join(STRIPS_DIR, "Ver_slider.png"),
            256, 'vertical'
        )
        layout.addWidget(self.slider_reserved, alignment=Qt.AlignmentFlag.AlignCenter)

        return zone

    def _create_zone_d(self) -> QWidget:
        """Crea Zona D: Knob estilos, screens."""
        zone = QWidget()
        layout = QHBoxLayout(zone)
        layout.setSpacing(15)

        # Knob de estilos
        knob_layout = QVBoxLayout()
        self.knob_style = FilmstripKnob(
            os.path.join(STRIPS_DIR, "Knob_mid.png"),
            256, num_positions=6
        )
        self.knob_style.set_labels(self.STYLES)
        knob_layout.addWidget(self.knob_style, alignment=Qt.AlignmentFlag.AlignCenter)
        knob_layout.addWidget(QLabel("ESTILOA"))
        layout.addLayout(knob_layout)

        # Screens
        screens_layout = QVBoxLayout()

        # Screen estilo seleccionado
        self.screen_style = VintageScreen(
            os.path.join(ASSETS_DIR, "screen.png"),
            editable=False
        )
        self.screen_style.set_text(self.STYLES[0])
        self.screen_style.set_amber_color()
        screens_layout.addWidget(self.screen_style)

        # Screen nombre batería
        self.screen_drummer = VintageScreen(
            os.path.join(ASSETS_DIR, "screen.png"),
            editable=True
        )
        self.screen_drummer.set_text("BATERIA")
        screens_layout.addWidget(self.screen_drummer)

        # Screen BPM
        self.screen_bpm = VintageScreen(
            os.path.join(ASSETS_DIR, "screen.png"),
            editable=True
        )
        self.screen_bpm.set_text("120")
        screens_layout.addWidget(self.screen_bpm)

        layout.addLayout(screens_layout)

        return zone

    def _create_zone_e(self) -> QWidget:
        """Crea Zona E: Screen de porcentaje."""
        zone = QWidget()
        layout = QVBoxLayout(zone)

        self.screen_progress = VintageScreen(
            os.path.join(ASSETS_DIR, "screen.png"),
            editable=False
        )
        self.screen_progress.set_text("0%")
        self.screen_progress.set_font_size(24)
        layout.addWidget(self.screen_progress, alignment=Qt.AlignmentFlag.AlignCenter)

        return zone

    def _create_zone_g(self) -> QWidget:
        """Crea Zona G: Detectar BPM + slider."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(10)

        # Pad detectar BPM
        self.pad_bpm = ImagePad(
            os.path.join(ONESHOTS_DIR, "pad_off.png"),
            os.path.join(ONESHOTS_DIR, "pad_on.png"),
            "BPM ANTZEMAN"
        )
        layout.addWidget(self.pad_bpm, alignment=Qt.AlignmentFlag.AlignCenter)

        label_bpm = QLabel("BPM ANTZEMAN")
        label_bpm.setStyleSheet("color: #AAAAAA; font-size: 10px;")
        label_bpm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_bpm)

        # Slider horizontal para animación
        self.slider_bpm_detect = FilmstripSlider(
            os.path.join(STRIPS_DIR, "Hor_slider.png"),
            256, 'horizontal'
        )
        layout.addWidget(self.slider_bpm_detect, alignment=Qt.AlignmentFlag.AlignCenter)

        return zone

    def _connect_signals(self):
        """Conecta las señales de los widgets."""
        # Zona A
        self.pad_import.clicked.connect(self._on_import_clicked)
        self.switch_metadata.toggled.connect(self.metadata_toggled.emit)
        self.switch_separate.toggled.connect(self.separate_drums_toggled.emit)

        # Zona C
        self.pad_export.clicked.connect(self.export_drums_clicked.emit)
        self.switch_format.toggled.connect(self._on_format_changed)
        self.btn_open.clicked.connect(self.open_project_clicked.emit)
        self.btn_save.clicked.connect(self.save_project_clicked.emit)

        # Zona D
        self.knob_style.value_changed.connect(self._on_style_changed)
        self.screen_drummer.text_changed.connect(self.drummer_name_changed.emit)
        self.screen_bpm.text_changed.connect(self._on_bpm_changed)

        # Zona G
        self.pad_bpm.clicked.connect(self.detect_bpm_clicked.emit)

    def _on_import_clicked(self):
        """Maneja click en pad de importar."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de audio", "",
            "Audio Files (*.wav *.WAV *.mp3 *.MP3);;All Files (*)"
        )
        if file_name:
            self.audio_file = file_name
            self.screen_status.set_text(f"Cargado: {os.path.basename(file_name)}")
            self.import_song_clicked.emit()

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

    # Métodos públicos para control externo
    def set_vu_level(self, level: float):
        """Establece el nivel del VU meter."""
        self.vu_meter.set_level(level)

    def set_status_message(self, message: str):
        """Establece el mensaje de estado."""
        self.screen_status.set_text(message)

    def set_progress(self, percent: int):
        """Establece el porcentaje de progreso."""
        self.screen_progress.set_text(f"{percent}%")

    def set_analyzing(self, active: bool):
        """Activa/desactiva indicador de análisis."""
        if active:
            self.led_analyzing.pulse()
        else:
            self.led_analyzing.turn_off()

    def set_kick_level(self, level: float):
        """Establece nivel del slider Kick."""
        self.slider_kick.set_value(level)

    def set_snare_level(self, level: float):
        """Establece nivel del slider Snare."""
        self.slider_snare.set_value(level)

    def set_hihat_level(self, level: float):
        """Establece nivel del slider HiHat."""
        self.slider_hihat.set_value(level)

    def set_detecting_bpm(self, active: bool):
        """Activa animación de detección de BPM."""
        if active:
            self.slider_bpm_detect.animate_to(1.0, 1000)
        else:
            self.slider_bpm_detect.animate_to(0.0, 500)
