"""
Groove Extractor - Herramienta DSP para analisis de grooves de bateria.

Modulos:
- models: Modelos de datos (OnsetData, GrooveData, JamaicanStyle, etc.)
- detectors: Detectores de onsets (OnsetDetector)
- classifiers: Clasificadores (HiHatClassifier)
- converters: Conversores de timing (TimingConverter)
- analyzers: Analizadores (JamaicanBPMAnalyzer, SwingCalculator)
- exporters: Exportadores (ExcelExporter)
- separators: Separadores de audio (DrumSeparator)

Uso rapido:
    from src import GrooveExtractor, extract_groove

    # Opcion 1: Clase completa
    extractor = GrooveExtractor()
    groove = extractor.extract("audio.wav")

    # Opcion 2: Funcion de conveniencia
    groove = extract_groove("audio.wav")
"""

from .groove_extractor import GrooveExtractor, ExtractorConfig, extract_groove
from .models import (
    OnsetData, OnsetList,
    HiHatType, HiHatFeatures, HiHatClassification,
    GridPosition, TickData, BarData, time_to_tick, tick_to_time,
    JamaicanStyle, STYLE_BPM_RANGES, suggest_style_from_bpm,
    SwingAnalysis, SWING_RANGES_BY_STYLE,
    GrooveData, InstrumentData, GridMapping, HumanizationStats
)

__version__ = "2.0.0"

__all__ = [
    # Main
    'GrooveExtractor', 'ExtractorConfig', 'extract_groove',
    # Models
    'OnsetData', 'OnsetList',
    'HiHatType', 'HiHatFeatures', 'HiHatClassification',
    'GridPosition', 'TickData', 'BarData', 'time_to_tick', 'tick_to_time',
    'JamaicanStyle', 'STYLE_BPM_RANGES', 'suggest_style_from_bpm',
    'SwingAnalysis', 'SWING_RANGES_BY_STYLE',
    'GrooveData', 'InstrumentData', 'GridMapping', 'HumanizationStats',
]
