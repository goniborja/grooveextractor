"""
MainWindow - Ventana principal de Groove Extractor con UI vintage.
Usa widgets basados en imágenes PNG del kit Vintage Obsession.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPalette, QBrush

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
SCALE_PAD = 0.26              # Pads normales
SCALE_KNOB_SMALL = 0.25       # Knobs pequeños (METADATUAK, BANATU)
SCALE_KNOB_ESTILO = 0.22      # Knob ESTILOA
SCALE_KNOB_AZTERTU = 0.30     # Knob AZTERTU (el más grande)
SCALE_SWITCH = 0.46
SCALE_VU = 0.85               # VU meter muy grande
SCALE_LED_METER = 0.35        # LED meters
SCALE_SCREEN_SMALL = 0.23     # Screens pequeños
SCALE_SCREEN_BIG = 0.65       # Screens grandes (zona D)
SCALE_SCREEN_LOG = 0.40       # Screen de log de proceso
SCALE_BUTTON = 0.46

# Margen izquierdo para zonas A, D, G
LEFT_MARGIN = 30


class AnalysisThread(QThread):
    """Thread para análisis de audio sin bloquear la UI."""

    progress = pyqtSignal(int)
    status = pyqtSignal(str)  # Para mensajes de log
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    bpm_detected = pyqtSignal(float, str)
    drums_separated = pyqtSignal(str)  # Ruta al archivo de batería separada

    def __init__(self, audio_file: str, use_stems: bool = True, save_metadata: bool = True):
        super().__init__()
        self.audio_file = audio_file
        self.use_stems = use_stems
        self.save_metadata = save_metadata
        self.config = ExtractorConfig(
            use_stem_separation=use_stems,
            analyze_hihat_type=True,
            export_excel=save_metadata  # Solo guardar en database.xlsx si metadatos activado
        )
        self.extractor = GrooveExtractor(self.config)
        self.groove_data = None
        self.separated_drums_path = None

    def run(self):
        try:
            self.status.emit("Kargatzen audioa...")
            self.progress.emit(5)

            # Paso 1: Separar batería con Demucs
            self.status.emit("Bateria banatzen (Demucs)...")
            self.progress.emit(15)

            # Paso 2: Separar stems si está activado
            if self.use_stems:
                self.status.emit("Stems banatzen (bombo/caja/hihat)...")
                self.progress.emit(30)

            # Paso 3: Análisis completo
            self.status.emit("Onsetak detektatzen...")
            self.progress.emit(45)

            self.groove_data = self.extractor.extract(self.audio_file)

            self.status.emit("BPM kalkulatzen...")
            self.progress.emit(60)
            self.bpm_detected.emit(self.groove_data.bpm, self.groove_data.style.value)

            self.status.emit("Swing analizatzen...")
            self.progress.emit(75)

            # Paso 4: Guardar en database.xlsx si metadatos activado
            if self.save_metadata:
                self.status.emit("Metadatuak gordetzen...")
                self.progress.emit(85)

            self.status.emit("Emaitzak prestatzen...")
            self.progress.emit(95)

            results = self.extractor.extract_to_dict(self.audio_file)

            self.progress.emit(100)
            self.status.emit("Amaituta!")
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))

    def get_separated_drums_path(self) -> str:
        """Retorna la ruta al archivo de batería separada."""
        return self.separated_drums_path


class MainWindow(QMainWindow):
    """Ventana principal de Groove Extractor con interfaz vintage."""

    # Señales
    import_song_clicked = pyqtSignal()
    export_drums_clicked = pyqtSignal()
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
        self._separated_drums_path = None
        self._init_ui()
        self._connect_signals()
        self._set_default_states()

    def _init_ui(self):
        self.setWindowTitle("Groove Extractor - Vintage Edition")
        self.setFixedSize(1200, 800)
        self._set_background()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Columna izquierda (A, D, G) - con margen izquierdo extra
        left_column = QVBoxLayout()
        left_column.setSpacing(10)
        left_column.setContentsMargins(LEFT_MARGIN, 0, 0, 0)  # Margen izquierdo
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

    def _set_default_states(self):
        """Configura estados por defecto de los switches."""
        # METADATUAK: activado por defecto (sí guardar metadatos)
        self.switch_metadata.set_state(True)
        self.knob_metadata.set_value(1)

        # BANATU: activado por defecto (sí separar stems)
        self.switch_banatu.set_state(True)
        self.knob_banatu.set_value(1)

        # MIDI/WAV: WAV por defecto (switch en estado 2 = WAV)
        self.switch_format.set_state(True)

    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("color: #AAAAAA; font-size: 9px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    # ==================== ZONA A ====================
    def _create_zone_a(self) -> QWidget:
        """Zona A: KARGATU + METADATUAK (knob+switch) + BANATU (knob+switch)."""
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

        # BANATU - knob pequeño + switch
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
        """Zona B: VU meter, screen status, LED meters, AZTERTU (knob), log de proceso."""
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

        # LED Meters
        meters_layout = QHBoxLayout()
        meters_layout.setSpacing(30)

        # Ruta a la carpeta de frames LED
        led_folder = str(ONESHOTS_DIR / "LED_meter")

        for name, attr in [("KICK", "led_kick"), ("SNARE", "led_snare"), ("HI-HAT", "led_hihat")]:
            led_layout = QVBoxLayout()
            led_layout.setSpacing(3)
            led = AnimatedLED(
                led_folder,  # Carpeta con frames individuales
                62, scale=SCALE_LED_METER
            )
            setattr(self, attr, led)
            led_layout.addWidget(led, alignment=Qt.AlignmentFlag.AlignCenter)
            led_layout.addWidget(self._create_label(name))
            meters_layout.addLayout(led_layout)

        layout.addLayout(meters_layout)

        # AZTERTU - KNOB grande (no pad)
        aztertu_layout = QVBoxLayout()
        aztertu_layout.setSpacing(3)
        self.knob_analyze = FilmstripKnob(
            str(STRIPS_DIR / "Knob_big.png"),
            128, num_positions=2, scale=SCALE_KNOB_AZTERTU
        )
        aztertu_layout.addWidget(self.knob_analyze, alignment=Qt.AlignmentFlag.AlignCenter)
        aztertu_layout.addWidget(self._create_label("AZTERTU"))
        layout.addLayout(aztertu_layout)

        # Screen de log de proceso
        self.screen_log = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=False,
            scale=SCALE_SCREEN_LOG
        )
        self.screen_log.set_text("Prest analisatzeko")
        self.screen_log.set_text_color("#66AA66")  # Verde suave
        layout.addWidget(self.screen_log, alignment=Qt.AlignmentFlag.AlignCenter)

        return zone

    # ==================== ZONA C ====================
    def _create_zone_c(self) -> QWidget:
        """Zona C: ESPORTATU (exporta batería WAV/MIDI), switch, IREKI/GORDE (muy abajo)."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)

        layout.addStretch(1)

        # ESPORTATU - exporta batería separada
        self.pad_export = ImagePad(
            str(ONESHOTS_DIR / "pad_off.png"),
            str(ONESHOTS_DIR / "pad_on.png"),
            "ESPORTATU",
            scale=SCALE_PAD
        )
        layout.addWidget(self.pad_export, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._create_label("ESPORTATU"))

        layout.addStretch(1)

        # Switch MIDI/WAV (WAV por defecto)
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
        layout.addStretch(6)

        # IREKI (sin función por ahora)
        self.btn_open = ImageButton(
            str(STRIPS_DIR / "but_small_rectangle.png"),
            6, "IREKI",
            scale=SCALE_BUTTON
        )
        layout.addWidget(self.btn_open, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)

        # GORDE (sin función por ahora)
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
        """Zona D: Solo 1 knob ESTILOA + 3 screens grandes."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(15)
        layout.setContentsMargins(5, 5, 5, 5)

        # Knob ESTILOA - solo 1 knob
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

        layout.addSpacing(20)

        # Screens grandes
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
        """Zona G: BPM ANTZEMAN."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)

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

        # Zona B - AZTERTU ahora es un knob
        self.knob_analyze.value_changed.connect(self._on_analyze_knob_changed)

        # Zona C
        self.pad_export.clicked.connect(self._on_export_clicked)
        self.switch_format.toggled.connect(self._on_format_changed)
        # IREKI/GORDE sin función por ahora
        self.btn_open.clicked.connect(lambda: self.screen_status.set_text("IREKI: etorkizunean"))
        self.btn_save.clicked.connect(lambda: self.screen_status.set_text("GORDE: etorkizunean"))

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
            self.screen_log.set_text(f"Audioa: {Path(file_name).name[:20]}")
            self.import_song_clicked.emit()

    def _on_metadata_knob_changed(self, value: int):
        self.switch_metadata.set_state(value == 1)

    def _on_banatu_knob_changed(self, value: int):
        self.switch_banatu.set_state(value == 1)

    def _on_analyze_knob_changed(self, value: int):
        """Cuando el knob AZTERTU se gira a posición 1, ejecuta análisis."""
        if value == 1:
            # Ejecutar análisis
            if self.audio_file:
                self._start_analysis()
                self.analyze_clicked.emit()
            else:
                self.screen_status.set_text("Kargatu audioa!")
                self.screen_log.set_text("Errorea: ez dago audiorik")
            # No resetear automáticamente - el usuario puede girarlo de vuelta

    def _on_analyze_clicked(self):
        if not self.audio_file:
            self.screen_status.set_text("Kargatu audioa!")
            self.screen_log.set_text("Errorea: ez dago audiorik")
            return
        self._start_analysis()
        self.analyze_clicked.emit()

    def _on_format_changed(self, is_wav: bool):
        fmt = "WAV" if is_wav else "MIDI"
        self.export_format_changed.emit(fmt)
        self.screen_log.set_text(f"Formatua: {fmt}")

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
        """Exporta la batería separada como WAV o MIDI."""
        if not self._separated_drums_path:
            self.screen_status.set_text("Aztertu lehenik!")
            self.screen_log.set_text("Errorea: analisatu audioa lehenik")
            return

        # Determinar formato
        is_wav = self.switch_format.is_on()
        ext = ".wav" if is_wav else ".mid"
        fmt_name = "WAV" if is_wav else "MIDI"

        default_name = Path(self.audio_file).stem + f"_drums{ext}" if self.audio_file else f"drums{ext}"
        file_filter = f"{fmt_name} Files (*{ext});;All Files (*)"

        output_file, _ = QFileDialog.getSaveFileName(
            self, "Esportatu bateria", default_name, file_filter
        )

        if output_file:
            try:
                self.screen_status.set_text("Esportatzen...")
                self.screen_log.set_text(f"Esportatzen: {fmt_name}...")

                if is_wav:
                    # Copiar archivo WAV separado
                    import shutil
                    if self._separated_drums_path and Path(self._separated_drums_path).exists():
                        shutil.copy(self._separated_drums_path, output_file)
                        self.screen_status.set_text("Esportatuta!")
                        self.screen_log.set_text(f"WAV gordeta: {Path(output_file).name[:15]}")
                    else:
                        self.screen_status.set_text("Ez dago WAV")
                        self.screen_log.set_text("Errorea: WAV fitxategia ez dago")
                else:
                    # Exportar como MIDI
                    self.screen_status.set_text("MIDI ez dago prest")
                    self.screen_log.set_text("MIDI esportazioa etorkizunean")

            except Exception as e:
                self.screen_status.set_text(f"Errorea!")
                self.screen_log.set_text(f"Errorea: {str(e)[:20]}")

    # ==================== MÉTODOS PÚBLICOS ====================
    def set_vu_level(self, level: float):
        self.vu_meter.set_level(level)

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

        use_stems = self.switch_banatu.is_on()
        save_metadata = self.switch_metadata.is_on()

        self.analysis_thread = AnalysisThread(
            self.audio_file,
            use_stems=use_stems,
            save_metadata=save_metadata
        )
        self.analysis_thread.progress.connect(self._on_analysis_progress)
        self.analysis_thread.status.connect(self._on_analysis_status)
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
        # Actualizar LEDs progresivamente
        if percent < 33:
            self.led_kick.set_brightness(percent / 33.0)
        elif percent < 66:
            self.led_kick.set_brightness(1.0)
            self.led_snare.set_brightness((percent - 33) / 33.0)
        else:
            self.led_kick.set_brightness(1.0)
            self.led_snare.set_brightness(1.0)
            self.led_hihat.set_brightness((percent - 66) / 34.0)

    def _on_analysis_status(self, message: str):
        """Actualiza el log de proceso."""
        self.screen_log.set_text(message)

    def _on_analysis_finished(self, results: dict):
        self.led_kick.turn_off()
        self.led_snare.turn_off()
        self.led_hihat.turn_off()
        self.screen_status.set_text("Amaituta!")

        # Guardar ruta de batería separada para exportación
        self._separated_drums_path = results.get('separated_drums_path')

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
        self.screen_status.set_text(f"Errorea!")
        self.screen_log.set_text(f"Errorea: {error_msg[:25]}")
        self.set_progress(0)

    def _on_bpm_detected(self, bpm: float, style: str):
        self.screen_bpm.set_text(str(int(bpm)))
        style_lower = style.lower()
        for i, s in enumerate(self.STYLES):
            if s.lower() == style_lower or s.lower().replace(" ", "_") == style_lower:
                self.knob_style.set_value(i)
                self.screen_style.set_text(s)
                break
