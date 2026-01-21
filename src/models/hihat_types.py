"""Tipos y clasificacion de hi-hat."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class HiHatType(Enum):
    """Tipo de hi-hat."""
    CLOSED = "closed"
    OPEN = "open"
    UNKNOWN = "unknown"

    @property
    def midi_note(self) -> int:
        """Nota MIDI estandar GM."""
        return {
            HiHatType.CLOSED: 42,
            HiHatType.OPEN: 46,
            HiHatType.UNKNOWN: 42
        }[self]


@dataclass
class HiHatFeatures:
    """Caracteristicas acusticas extraidas."""
    decay_time: float  # segundos
    amp_100ms: float  # amplitud a 100ms
    temporal_centroid: float
    spectral_centroid: float
    spectral_bandwidth: float
    spectral_flatness: float


@dataclass
class HiHatClassification:
    """Resultado de clasificacion."""
    hit_type: HiHatType
    confidence: float  # 0-1
    features: Optional[HiHatFeatures] = None


@dataclass
class HiHatThresholds:
    """Umbrales de clasificacion."""
    decay_open: float = 0.200  # > 200ms = abierto
    decay_closed: float = 0.100  # < 100ms = cerrado
    # Ponderacion de features
    weight_decay: float = 0.40
    weight_amp: float = 0.25
    weight_temporal: float = 0.20
    weight_spectral: float = 0.15
