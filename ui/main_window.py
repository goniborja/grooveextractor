"""
MainWindow - Ventana principal de Groove Extractor con UI vintage.
Usa widgets basados en imágenes PNG del kit Vintage Obsession.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
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

# Escalas para que los widgets quepan en 1200x800 (reducido ~17%)
SCALE_PAD = 0.33         # Pads: 208 -> 69px
SCALE_SWITCH = 0.58      # Switches: 102x44 -> 59x26
SCALE_SLIDER_V = 0.25    # Sliders verticales: 104x444 -> 26x111
SCALE_SLIDER_H = 0.29    # Sliders horizontales: 444x104 -> 129x30
SCALE_KNOB = 0.5         # Knob small: 120 -> 60px
SCALE_LED = 0.1          # LED: 96x413 -> 10x41
SCALE_BUTTON = 0.58      # Buttons small: 144x62 -> 84x36
SCALE_SCREEN = 0.29      # Screen: 510x110 -> 148x32
SCALE_VU = 0.5           # VU meter: 325x184 -> 163x92


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
            export_excel=False  # No exportar automáticamente, lo haremos manualmente
        )
        self.extractor = GrooveExtractor(self.config)
        self.groove_data = None

    def run(self):
        """Ejecuta el análisis en segundo plano."""
        try:
            self.progress.emit(10)

            # Extraer groove completo (BPM, onsets, humanización, swing)
            self.progress.emit(30)
            self.groove_data = self.extractor.extract(self.audio_file)

            self.progress.emit(70)

            # Emitir BPM y estilo detectados
            self.bpm_detected.emit(self.groove_data.bpm, self.groove_data.style.value)

            self.progress.emit(90)

            # Convertir a diccionario para la UI
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
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Columna izquierda (A, D, G)
        left_column = QVBoxLayout()
        left_column.setSpacing(15)
        left_column.addWidget(self._create_zone_a())
        left_column.addWidget(self._create_zone_d())
        left_column.addWidget(self._create_zone_g())
        left_column.addStretch()

        # Columna central (B, E)
        center_column = QVBoxLayout()
        center_column.setSpacing(15)
        center_column.addWidget(self._create_zone_b(), stretch=3)
        center_column.addWidget(self._create_zone_e(), stretch=1)

        # Columna derecha (C)
        right_column = QVBoxLayout()
        right_column.setSpacing(15)
        right_column.addWidget(self._create_zone_c())
        right_column.addStretch()

        main_layout.addLayout(left_column, stretch=1)
        main_layout.addLayout(center_column, stretch=2)
        main_layout.addLayout(right_column, stretch=1)

    def _set_background(self):
        """Establece el fondo de la ventana."""
        wallpaper_path = ASSETS_BASE / "Vintage_GUI_KIT_wallpaper_a.png"
        if wallpaper_path.exists():
            palette = self.palette()
            pixmap = load_pixmap(str(wallpaper_path))
            # Escalar al tamaño de la ventana
            scaled = pixmap.scaled(1200, 800, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
            palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled))
            self.setPalette(palette)

    def _create_label(self, text: str) -> QLabel:
        """Crea un label con estilo consistente."""
        label = QLabel(text)
        label.setStyleSheet("color: #AAAAAA; font-size: 9px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _create_zone_a(self) -> QWidget:
        """Crea Zona A: Importar + switches."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)

        # Pad importar
        self.pad_import = ImagePad(
            str(ONESHOTS_DIR / "pad_off.png"),
            str(ONESHOTS_DIR / "pad_on.png"),
            "KARGATU",
            scale=SCALE_PAD
        )
        layout.addWidget(self.pad_import, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._create_label("KARGATU"))

        # Switch metadatos
        switch_layout1 = QHBoxLayout()
        switch_layout1.setSpacing(5)
        self.switch_metadata = ImageSwitch(
            str(ONESHOTS_DIR / "switch_hor_st1.png"),
            str(ONESHOTS_DIR / "switch_hor_st2.png"),
            scale=SCALE_SWITCH
        )
        switch_layout1.addWidget(self.switch_metadata)
        switch_layout1.addWidget(self._create_label("METADATUAK"))
        switch_layout1.addStretch()
        layout.addLayout(switch_layout1)

        # Switch separar batería
        switch_layout2 = QHBoxLayout()
        switch_layout2.setSpacing(5)
        self.switch_separate = ImageSwitch(
            str(ONESHOTS_DIR / "switch_hor_st1.png"),
            str(ONESHOTS_DIR / "switch_hor_st2.png"),
            scale=SCALE_SWITCH
        )
        switch_layout2.addWidget(self.switch_separate)
        switch_layout2.addWidget(self._create_label("BANATU"))
        switch_layout2.addStretch()
        layout.addLayout(switch_layout2)

        return zone

    def _create_zone_b(self) -> QWidget:
        """Crea Zona B: VU meter, sliders, LED, status."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)

        # VU Meter
        vu_folder = str(ONESHOTS_DIR / "VU_meter")
        self.vu_meter = AnimatedVUMeter(vu_folder, 256, scale=SCALE_VU)
        layout.addWidget(self.vu_meter, alignment=Qt.AlignmentFlag.AlignCenter)

        # Screen de estado
        self.screen_status = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=False,
            scale=SCALE_SCREEN
        )
        self.screen_status.set_text("PREST")
        layout.addWidget(self.screen_status, alignment=Qt.AlignmentFlag.AlignCenter)

        # Sliders y LED en fila
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)

        # Slider Kick
        kick_layout = QVBoxLayout()
        kick_layout.setSpacing(3)
        self.slider_kick = FilmstripSlider(
            str(STRIPS_DIR / "Ver_slider.png"),
            256, 'vertical', scale=SCALE_SLIDER_V
        )
        kick_layout.addWidget(self.slider_kick, alignment=Qt.AlignmentFlag.AlignCenter)
        kick_layout.addWidget(self._create_label("KICK"))
        controls_layout.addLayout(kick_layout)

        # Slider Snare
        snare_layout = QVBoxLayout()
        snare_layout.setSpacing(3)
        self.slider_snare = FilmstripSlider(
            str(STRIPS_DIR / "Ver_slider.png"),
            256, 'vertical', scale=SCALE_SLIDER_V
        )
        snare_layout.addWidget(self.slider_snare, alignment=Qt.AlignmentFlag.AlignCenter)
        snare_layout.addWidget(self._create_label("SNARE"))
        controls_layout.addLayout(snare_layout)

        # Slider HiHat
        hihat_layout = QVBoxLayout()
        hihat_layout.setSpacing(3)
        self.slider_hihat = FilmstripSlider(
            str(STRIPS_DIR / "Ver_slider.png"),
            256, 'vertical', scale=SCALE_SLIDER_V
        )
        hihat_layout.addWidget(self.slider_hihat, alignment=Qt.AlignmentFlag.AlignCenter)
        hihat_layout.addWidget(self._create_label("HI-HAT"))
        controls_layout.addLayout(hihat_layout)

        # LED
        led_layout = QVBoxLayout()
        led_layout.setSpacing(3)
        self.led_analyzing = AnimatedLED(
            str(STRIPS_DIR / "LED_meter.png"),
            62, scale=SCALE_LED
        )
        led_layout.addWidget(self.led_analyzing, alignment=Qt.AlignmentFlag.AlignCenter)
        led_layout.addWidget(self._create_label("AKTIBO"))
        controls_layout.addLayout(led_layout)

        layout.addLayout(controls_layout)

        return zone

    def _create_zone_c(self) -> QWidget:
        """Crea Zona C: Exportar, formato, botones proyecto, slider."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)

        # Pad exportar
        self.pad_export = ImagePad(
            str(ONESHOTS_DIR / "pad_off.png"),
            str(ONESHOTS_DIR / "pad_on.png"),
            "ESPORTATU",
            scale=SCALE_PAD
        )
        layout.addWidget(self.pad_export, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._create_label("ESPORTATU"))

        # Switch MIDI/WAV
        format_layout = QHBoxLayout()
        format_layout.setSpacing(5)
        format_layout.addWidget(self._create_label("MIDI"))
        self.switch_format = ImageSwitch(
            str(ONESHOTS_DIR / "switch_hor_st1.png"),
            str(ONESHOTS_DIR / "switch_hor_st2.png"),
            scale=SCALE_SWITCH
        )
        format_layout.addWidget(self.switch_format)
        format_layout.addWidget(self._create_label("WAV"))
        layout.addLayout(format_layout)

        # Botón abrir proyecto (usando but_small_rectangle)
        self.btn_open = ImageButton(
            str(STRIPS_DIR / "but_small_rectangle.png"),
            6, "IREKI",
            scale=SCALE_BUTTON
        )
        layout.addWidget(self.btn_open, alignment=Qt.AlignmentFlag.AlignCenter)

        # Botón guardar proyecto
        self.btn_save = ImageButton(
            str(STRIPS_DIR / "but_small_rectangle.png"),
            6, "GORDE",
            scale=SCALE_BUTTON
        )
        layout.addWidget(self.btn_save, alignment=Qt.AlignmentFlag.AlignCenter)

        # Slider reservado
        self.slider_reserved = FilmstripSlider(
            str(STRIPS_DIR / "Ver_slider.png"),
            256, 'vertical', scale=SCALE_SLIDER_V
        )
        layout.addWidget(self.slider_reserved, alignment=Qt.AlignmentFlag.AlignCenter)

        return zone

    def _create_zone_d(self) -> QWidget:
        """Crea Zona D: Knob estilos, screens."""
        zone = QWidget()
        layout = QHBoxLayout(zone)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)

        # Knob de estilos (usando Knob_small)
        knob_layout = QVBoxLayout()
        knob_layout.setSpacing(3)
        self.knob_style = FilmstripKnob(
            str(STRIPS_DIR / "Knob_small.png"),
            128, num_positions=6, scale=SCALE_KNOB
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

    def _create_zone_e(self) -> QWidget:
        """Crea Zona E: Screen de porcentaje."""
        zone = QWidget()
        layout = QVBoxLayout(zone)
        layout.setContentsMargins(5, 5, 5, 5)

        self.screen_progress = VintageScreen(
            str(ASSETS_DIR / "screen.png"),
            editable=False,
            scale=0.4  # Un poco más grande para el porcentaje
        )
        self.screen_progress.set_text("0%")
        self.screen_progress.set_font_size(14)
        layout.addWidget(self.screen_progress, alignment=Qt.AlignmentFlag.AlignCenter)

        return zone

    def _create_zone_g(self) -> QWidget:
        """Crea Zona G: Detectar BPM + slider."""
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

    def _connect_signals(self):
        """Conecta las señales de los widgets."""
        # Zona A
        self.pad_import.clicked.connect(self._on_import_clicked)
        self.switch_metadata.toggled.connect(self.metadata_toggled.emit)
        self.switch_separate.toggled.connect(self.separate_drums_toggled.emit)

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

    def _on_import_clicked(self):
        """Maneja click en pad de importar."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de audio", "",
            "Audio Files (*.wav *.WAV *.mp3 *.MP3);;All Files (*)"
        )
        if file_name:
            self.audio_file = file_name
            self.screen_status.set_text(f"Kargatzen: {Path(file_name).name[:15]}")
            self.import_song_clicked.emit()
            # Iniciar análisis automáticamente
            self._start_analysis()

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
        self.screen_status.set_text(message[:25])  # Limitar longitud

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

    # ========== Métodos de integración backend ==========

    def _start_analysis(self):
        """Inicia el análisis del archivo de audio."""
        if not self.audio_file:
            self.screen_status.set_text("Ez dago audiorik")
            return

        if self.analysis_thread and self.analysis_thread.isRunning():
            self.screen_status.set_text("Analisatzen...")
            return

        # Obtener configuración desde UI
        use_separation = self.switch_separate.is_on() if hasattr(self.switch_separate, 'is_on') else False

        # Crear y configurar thread
        self.analysis_thread = AnalysisThread(self.audio_file, use_separation)
        self.analysis_thread.progress.connect(self._on_analysis_progress)
        self.analysis_thread.finished.connect(self._on_analysis_finished)
        self.analysis_thread.error.connect(self._on_analysis_error)
        self.analysis_thread.bpm_detected.connect(self._on_bpm_detected)

        # Activar indicadores
        self.set_analyzing(True)
        self.set_detecting_bpm(True)
        self.screen_status.set_text("Analisatzen...")

        # Iniciar
        self.analysis_thread.start()

    def _on_analysis_progress(self, percent: int):
        """Actualiza el progreso del análisis."""
        self.set_progress(percent)
        # Simular nivel VU basado en progreso
        self.set_vu_level(percent / 100.0)

    def _on_analysis_finished(self, results: dict):
        """Maneja la finalización del análisis."""
        self.set_analyzing(False)
        self.set_detecting_bpm(False)
        self.screen_status.set_text("Amaituta!")

        # Actualizar sliders con datos de instrumentos
        instruments = results.get('instruments', {})
        if 'kick' in instruments:
            kick_data = instruments['kick']
            # Usar porcentaje on_grid como nivel
            humanization = kick_data.get('humanization', {})
            on_grid = humanization.get('on_grid_percent', 50) if humanization else 50
            self.set_kick_level(on_grid / 100.0)

        if 'snare' in instruments:
            snare_data = instruments['snare']
            humanization = snare_data.get('humanization', {})
            on_grid = humanization.get('on_grid_percent', 50) if humanization else 50
            self.set_snare_level(on_grid / 100.0)

        if 'hihat' in instruments:
            hihat_data = instruments['hihat']
            humanization = hihat_data.get('humanization', {})
            on_grid = humanization.get('on_grid_percent', 50) if humanization else 50
            self.set_hihat_level(on_grid / 100.0)

        # Guardar resultados para exportación
        self._last_results = results

    def _on_analysis_error(self, error_msg: str):
        """Maneja errores del análisis."""
        self.set_analyzing(False)
        self.set_detecting_bpm(False)
        self.screen_status.set_text(f"Errorea: {error_msg[:15]}")
        self.set_progress(0)

    def _on_bpm_detected(self, bpm: float, style: str):
        """Actualiza la UI con el BPM y estilo detectados."""
        self.screen_bpm.set_text(str(int(bpm)))

        # Buscar el índice del estilo y actualizar knob
        style_lower = style.lower()
        for i, s in enumerate(self.STYLES):
            if s.lower() == style_lower or s.lower().replace(" ", "_") == style_lower:
                self.knob_style.set_value(i)
                self.screen_style.set_text(s)
                break

    def _on_detect_bpm_clicked(self):
        """Detecta BPM del archivo cargado."""
        if not self.audio_file:
            self.screen_status.set_text("Kargatu audioa lehenik")
            return

        # Si ya hay análisis, solo re-emitir los valores
        if hasattr(self, '_last_results') and self._last_results:
            bpm = self._last_results.get('bpm', 120)
            style = self._last_results.get('style', 'ska')
            self._on_bpm_detected(float(bpm), style)
        else:
            # Iniciar análisis completo
            self._start_analysis()

    def _on_export_clicked(self):
        """Exporta los resultados a Excel."""
        if not self.analysis_thread or not self.analysis_thread.groove_data:
            self.screen_status.set_text("Ez dago daturik")
            return

        # Obtener ruta de salida
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
