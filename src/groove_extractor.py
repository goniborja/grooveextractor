"""Groove Extractor - Orquestador principal del pipeline de analisis."""
import numpy as np
import librosa
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict

from .models import (
    GrooveData, InstrumentData, GridMapping, OnsetList,
    JamaicanStyle, SwingAnalysis, HumanizationStats
)
from typing import Optional
from .detectors import OnsetDetector
from .classifiers import HiHatClassifier
from .converters import TimingConverter
from .analyzers import JamaicanBPMAnalyzer, SwingCalculator
from .exporters import ExcelExporter
from .separators import DrumSeparator, SeparatedStems


@dataclass
class ExtractorConfig:
    """Configuracion del extractor."""
    use_stem_separation: bool = False  # Separar stems antes de analizar
    analyze_hihat_type: bool = True  # Clasificar hi-hats abierto/cerrado
    export_excel: bool = True  # Exportar automaticamente a Excel
    num_bars: Optional[int] = None  # Numero de compases a analizar (None=todos)
    tolerance_ms: float = 5.0  # Tolerancia para "on grid"


class GrooveExtractor:
    """
    Pipeline completo para extraccion de grooves de bateria.

    Integra todos los modulos:
    1. DrumSeparator: Separacion de stems (opcional)
    2. JamaicanBPMAnalyzer: Deteccion de BPM y estilo
    3. OnsetDetector: Deteccion de onsets por instrumento
    4. HiHatClassifier: Clasificacion de hi-hats
    5. TimingConverter: Conversion a grid MIDI
    6. SwingCalculator: Analisis de swing
    7. ExcelExporter: Exportacion a Excel

    Uso:
        extractor = GrooveExtractor()
        result = extractor.extract("audio.wav")
        # Exporta automaticamente a audio_groove.xlsx
    """

    def __init__(self, config: Optional[ExtractorConfig] = None):
        self.config = config or ExtractorConfig()

        # Inicializar componentes
        self.separator = DrumSeparator()
        self.bpm_analyzer = JamaicanBPMAnalyzer()
        self.onset_detector = OnsetDetector()
        self.hihat_classifier = HiHatClassifier()
        self.swing_calculator = SwingCalculator()
        self.exporter = ExcelExporter()

        # Timing converter se inicializa despues de detectar BPM
        self.timing_converter = None

    def extract(self, audio_path: str, output_path: Optional[str] = None,
                style_hint: Optional[JamaicanStyle] = None) -> GrooveData:
        """
        Ejecuta el pipeline completo de extraccion.

        Args:
            audio_path: Ruta al archivo de audio
            output_path: Ruta para Excel de salida (opcional)
            style_hint: Estilo sugerido por el usuario (prioridad sobre deteccion)

        Returns:
            GrooveData con todos los datos extraidos
        """
        audio_path = Path(audio_path)

        # 1. Cargar audio
        y, sr = librosa.load(str(audio_path), sr=22050)

        # Actualizar sample rate en componentes
        self.onset_detector.sr = sr
        self.hihat_classifier.sr = sr
        self.bpm_analyzer.sr = sr

        # 2. Separar stems si esta configurado
        separated_drums_path = None
        if self.config.use_stem_separation:
            stems = self.separator.separate_array(y, sr)
            # Guardar batería separada como archivo WAV
            output_dir = audio_path.parent / "separated"
            saved_files = self.separator.save_stems(stems, str(output_dir), audio_path.stem)
            # Combinar kick + snare + hihat como "drums"
            if stems.kick is not None and stems.snare is not None:
                import soundfile as sf
                drums_combined = stems.kick + stems.snare
                if stems.hihat is not None:
                    drums_combined = drums_combined + stems.hihat
                separated_drums_path = str(output_dir / f"{audio_path.stem}_drums.wav")
                sf.write(separated_drums_path, drums_combined, stems.sr)
        else:
            # Sin separacion: usar audio completo para cada analisis
            stems = SeparatedStems(kick=y, snare=y, hihat=y, sr=sr)

        # 3. Detectar BPM y estilo (usando style_hint si se proporciono)
        bpm_result = self._analyze_bpm(y, stems, style_hint)

        # 4. Inicializar timing converter con BPM detectado
        self.timing_converter = TimingConverter(bpm=bpm_result.bpm_corrected)

        # 5. Crear GrooveData base
        groove = GrooveData(
            song_name=audio_path.stem,
            bpm=bpm_result.bpm_corrected,
            style=bpm_result.style_suggested,
            is_vintage=bpm_result.is_vintage,
            tempo_drift=bpm_result.tempo_drift,
            separated_drums_path=separated_drums_path
        )

        # 6. Procesar cada instrumento
        self._process_kick(groove, stems.kick if stems.kick is not None else y)
        self._process_snare(groove, stems.snare if stems.snare is not None else y)
        self._process_hihat(groove, stems.hihat if stems.hihat is not None else y)

        # 7. Calcular swing desde hi-hats
        if 'hihat' in groove.instruments:
            hihat_onsets = groove.instruments['hihat'].onsets
            groove.swing = self.swing_calculator.calculate_from_onsets(hihat_onsets)

        # 8. Exportar a Excel si esta configurado
        if self.config.export_excel:
            if output_path is None:
                output_path = str(audio_path.with_suffix('.xlsx'))
            self.exporter.export(groove, output_path)

        return groove

    def _analyze_bpm(self, y: np.ndarray, stems: SeparatedStems,
                     style_hint: Optional[JamaicanStyle] = None):
        """Analiza BPM usando patron de kick/snare si disponible."""
        # Detectar onsets para analisis de patron
        kick_onsets = self.onset_detector.detect_kick(
            stems.kick if stems.kick is not None else y
        )
        snare_onsets = self.onset_detector.detect_snare(
            stems.snare if stems.snare is not None else y
        )

        # Usar analyze_with_pattern para deteccion inteligente
        return self.bpm_analyzer.analyze_with_pattern(
            y, kick_onsets.times, snare_onsets.times, style_hint
        )

    def _process_kick(self, groove: GrooveData, y: np.ndarray):
        """Procesa onsets de bombo."""
        onsets = self.onset_detector.detect_kick(y)
        self._add_instrument_data(groove, 'kick', onsets)

    def _process_snare(self, groove: GrooveData, y: np.ndarray):
        """Procesa onsets de caja."""
        onsets = self.onset_detector.detect_snare(y)
        self._add_instrument_data(groove, 'snare', onsets)

    def _process_hihat(self, groove: GrooveData, y: np.ndarray):
        """Procesa onsets de hi-hat con clasificacion opcional."""
        onsets = self.onset_detector.detect_hihat(y)

        # Clasificar hi-hats si esta configurado
        if self.config.analyze_hihat_type and len(onsets) > 0:
            classifications = self.hihat_classifier.classify_onsets(y, onsets)

            # Actualizar instrumento en cada onset
            for onset, classification in zip(onsets.onsets, classifications):
                onset.instrument = f"hihat_{classification.hit_type.value}"

        self._add_instrument_data(groove, 'hihat', onsets)

    def _add_instrument_data(self, groove: GrooveData, name: str, onsets: OnsetList):
        """Agrega datos de instrumento al groove."""
        if len(onsets) == 0:
            return

        # Convertir a tick data
        tick_data_list = self.timing_converter.onsets_to_tick_data(onsets)

        # Generar bar data
        bar_data_list = self.timing_converter.onsets_to_bar_data(
            onsets, self.config.num_bars
        )

        # Crear grid mappings
        grids = []
        for bar_data in bar_data_list:
            # Calcular timing deviations para este compas
            timing_devs = [0.0] * 16
            for td in bar_data.ticks:
                step_idx = td.grid_position.step - 1
                if 0 <= step_idx < 16:
                    timing_devs[step_idx] = td.deviation_ms

            grid = GridMapping(
                pattern=bar_data.pattern,
                velocities=bar_data.velocities,
                timing_deviations=timing_devs
            )
            grids.append(grid)

        # Calcular humanization stats
        humanization = self.timing_converter.get_humanization_stats(
            tick_data_list, self.config.tolerance_ms
        )

        # Crear InstrumentData
        inst_data = InstrumentData(
            name=name,
            onsets=onsets,
            grids=grids,
            humanization=humanization
        )

        groove.add_instrument(inst_data)

    def extract_to_dict(self, audio_path: str) -> Dict:
        """
        Extrae groove y devuelve como diccionario.

        Util para integracion con APIs o serializacion JSON.
        """
        groove = self.extract(audio_path)

        return {
            'song_name': groove.song_name,
            'bpm': groove.bpm,
            'style': groove.style.value,
            'is_vintage': groove.is_vintage,
            'tempo_drift': groove.tempo_drift,
            'separated_drums_path': groove.separated_drums_path,
            'swing': {
                'percentage': groove.swing.swing_percentage if groove.swing else None,
                'ratio': groove.swing.swing_ratio if groove.swing else None,
                'description': groove.swing.description if groove.swing else None,
            } if groove.swing else None,
            'instruments': {
                name: {
                    'num_onsets': len(inst.onsets),
                    'num_bars': len(inst.grids),
                    'humanization': {
                        'rushing_percent': inst.humanization.rushing_percent,
                        'dragging_percent': inst.humanization.dragging_percent,
                        'on_grid_percent': inst.humanization.on_grid_percent,
                        'avg_deviation_ms': inst.humanization.avg_deviation_ms,
                    } if inst.humanization else None
                }
                for name, inst in groove.instruments.items()
            }
        }


def extract_groove(audio_path: str, output_path: Optional[str] = None,
                   use_separation: bool = False) -> GrooveData:
    """
    Funcion de conveniencia para extraccion rapida.

    Args:
        audio_path: Ruta al archivo de audio
        output_path: Ruta para Excel (opcional)
        use_separation: Usar separacion de stems

    Returns:
        GrooveData con resultados
    """
    config = ExtractorConfig(use_stem_separation=use_separation)
    extractor = GrooveExtractor(config)
    return extractor.extract(audio_path, output_path)
