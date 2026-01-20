"""Modelos para representar onsets detectados."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class OnsetData:
    """Un golpe detectado."""
    time: float  # segundos
    velocity: int = 100  # 0-127
    instrument: str = "unknown"

    @property
    def time_ms(self) -> float:
        """Tiempo en milisegundos."""
        return self.time * 1000


@dataclass
class OnsetList:
    """Lista de onsets con metadatos."""
    onsets: List[OnsetData] = field(default_factory=list)
    instrument: str = "unknown"

    def __len__(self) -> int:
        return len(self.onsets)

    def __iter__(self):
        return iter(self.onsets)

    @property
    def times(self) -> List[float]:
        """Lista de tiempos en segundos."""
        return [o.time for o in self.onsets]
