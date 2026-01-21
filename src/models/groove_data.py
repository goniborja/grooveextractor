"""Contenedor principal de datos de groove."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .jamaican_styles import JamaicanStyle
from .swing_analysis import SwingAnalysis
from .onset_data import OnsetList


@dataclass
class HumanizationStats:
    """Estadisticas de humanizacion."""
    rushing_percent: float  # % de golpes adelantados
    dragging_percent: float  # % de golpes atrasados
    on_grid_percent: float  # % de golpes en el grid
    avg_deviation_ms: float
    max_deviation_ms: float


@dataclass
class GridMapping:
    """Mapeo de un compas a grid de 16 steps."""
    pattern: List[int]  # 16 valores: 0 o 1
    velocities: List[int]  # 16 valores: 0-127
    timing_deviations: List[float]  # 16 valores: ms de desviacion


@dataclass
class InstrumentData:
    """Datos completos de un instrumento."""
    name: str
    onsets: OnsetList
    grids: List[GridMapping] = field(default_factory=list)
    humanization: Optional[HumanizationStats] = None


@dataclass
class GrooveData:
    """Contenedor principal con todos los datos extraidos."""
    song_name: str
    bpm: float
    style: JamaicanStyle = JamaicanStyle.UNKNOWN
    swing: Optional[SwingAnalysis] = None
    instruments: Dict[str, InstrumentData] = field(default_factory=dict)
    is_vintage: bool = False
    tempo_drift: float = 0.0  # Porcentaje de drift
    separated_drums_path: Optional[str] = None  # Ruta al archivo de batería separada

    def add_instrument(self, instrument: InstrumentData):
        """Anade datos de un instrumento."""
        self.instruments[instrument.name] = instrument
