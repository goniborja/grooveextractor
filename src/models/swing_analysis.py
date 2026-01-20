"""Analisis de swing."""
from dataclasses import dataclass
from typing import Dict, Tuple
from .jamaican_styles import JamaicanStyle


@dataclass
class SwingConfig:
    """Configuracion para analisis de swing."""
    min_intervals: int = 4  # Minimo de intervalos para calcular
    tolerance_ms: float = 10.0  # Tolerancia para considerar "on grid"


@dataclass
class SwingAnalysis:
    """Resultado de analisis de swing."""
    swing_percentage: float  # 50% = sin swing, 66.7% = shuffle completo
    swing_ratio: float  # 1.0 = sin swing, 2.0 = shuffle
    is_swung: bool
    confidence: float
    description: str = ""

    def __post_init__(self):
        if not self.description:
            if self.swing_percentage < 52:
                self.description = "Straight (sin swing)"
            elif self.swing_percentage < 58:
                self.description = "Swing ligero"
            elif self.swing_percentage < 64:
                self.description = "Swing moderado"
            else:
                self.description = "Shuffle/swing pesado"


# Rangos de swing tipicos por estilo
SWING_RANGES_BY_STYLE: Dict[JamaicanStyle, Tuple[float, float]] = {
    JamaicanStyle.SKA: (50, 55),  # Mayormente straight
    JamaicanStyle.ROCKSTEADY: (52, 60),  # Ligero swing
    JamaicanStyle.ONE_DROP: (55, 65),  # Swing moderado
    JamaicanStyle.ROCKERS: (50, 58),  # Tight, menos swing
    JamaicanStyle.STEPPERS: (50, 55),  # Muy straight
}
