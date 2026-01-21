"""Conversion de tiempo a ticks MIDI y posiciones en grid."""
from dataclasses import dataclass
from typing import Optional, List

PPQ = 480  # Pulses Per Quarter Note (estandar MIDI)
STEPS_PER_BAR = 16  # Semicorcheas por compas


@dataclass
class GridPosition:
    """Posicion en la rejilla musical."""
    bar: int  # Compas (1-indexed)
    step: int  # Step dentro del compas (1-16)

    @property
    def absolute_step(self) -> int:
        """Step absoluto desde el inicio."""
        return (self.bar - 1) * STEPS_PER_BAR + self.step


@dataclass
class TickData:
    """Datos de timing en ticks MIDI."""
    tick: int  # Tick absoluto
    quantized_tick: int  # Tick cuantizado al step mas cercano
    deviation_ticks: int  # Desviacion en ticks
    deviation_ms: float  # Desviacion en milisegundos
    grid_position: GridPosition

    @property
    def is_rushing(self) -> bool:
        """Esta adelantado?"""
        return self.deviation_ticks < 0

    @property
    def is_dragging(self) -> bool:
        """Esta atrasado?"""
        return self.deviation_ticks > 0


@dataclass
class BarData:
    """Datos de un compas completo."""
    bar_number: int
    ticks: List[TickData]  # Lista de TickData
    pattern: List[int]  # Lista de 16 valores (0/1)
    velocities: List[int]  # Lista de 16 valores (0-127)


def time_to_tick(time_seconds: float, bpm: float, ppq: int = PPQ) -> int:
    """Convierte tiempo en segundos a ticks MIDI."""
    beats = time_seconds * bpm / 60.0
    return int(beats * ppq)


def tick_to_time(tick: int, bpm: float, ppq: int = PPQ) -> float:
    """Convierte ticks MIDI a tiempo en segundos."""
    beats = tick / ppq
    return beats * 60.0 / bpm
