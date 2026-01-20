"""Modelos de datos para Groove Extractor."""
from .onset_data import OnsetData, OnsetList
from .hihat_types import HiHatType, HiHatFeatures, HiHatClassification, HiHatThresholds
from .timing_data import (
    GridPosition, TickData, BarData,
    time_to_tick, tick_to_time,
    PPQ, STEPS_PER_BAR
)
from .jamaican_styles import (
    JamaicanStyle, StyleBPMRange, STYLE_BPM_RANGES,
    suggest_style_from_bpm, suggest_bpm_correction
)
from .swing_analysis import SwingAnalysis, SwingConfig, SWING_RANGES_BY_STYLE
from .groove_data import GrooveData, InstrumentData, GridMapping, HumanizationStats

__all__ = [
    # onset_data
    'OnsetData', 'OnsetList',
    # hihat_types
    'HiHatType', 'HiHatFeatures', 'HiHatClassification', 'HiHatThresholds',
    # timing_data
    'GridPosition', 'TickData', 'BarData', 'time_to_tick', 'tick_to_time', 'PPQ', 'STEPS_PER_BAR',
    # jamaican_styles
    'JamaicanStyle', 'StyleBPMRange', 'STYLE_BPM_RANGES', 'suggest_style_from_bpm', 'suggest_bpm_correction',
    # swing_analysis
    'SwingAnalysis', 'SwingConfig', 'SWING_RANGES_BY_STYLE',
    # groove_data
    'GrooveData', 'InstrumentData', 'GridMapping', 'HumanizationStats',
]
