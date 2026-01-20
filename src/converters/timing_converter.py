"""Conversor de tiempo a ticks MIDI y posiciones en grid."""
from typing import List, Tuple, Optional
from ..models import (
    OnsetData, OnsetList,
    GridPosition, TickData, BarData,
    HumanizationStats,
    time_to_tick, tick_to_time,
    PPQ, STEPS_PER_BAR
)


class TimingConverter:
    """
    Convierte tiempos a ticks MIDI y posiciones en grid.

    PPQ = 480 (Pulses Per Quarter Note)
    Grid = 16 steps por compas (semicorcheas)
    """

    def __init__(self, bpm: float, ppq: int = PPQ):
        self.bpm = bpm
        self.ppq = ppq
        # Ticks por step (semicorchea = 1/4 de negra)
        self.ticks_per_step = ppq // 4  # 120 ticks por step
        # Ticks por compas (4 negras)
        self.ticks_per_bar = ppq * 4  # 1920 ticks por compas

    def time_to_tick(self, time_seconds: float) -> int:
        """Convierte tiempo en segundos a ticks MIDI."""
        return time_to_tick(time_seconds, self.bpm, self.ppq)

    def tick_to_time(self, tick: int) -> float:
        """Convierte ticks MIDI a tiempo en segundos."""
        return tick_to_time(tick, self.bpm, self.ppq)

    def quantize_tick(self, tick: int) -> Tuple[int, int]:
        """
        Cuantiza tick al step mas cercano.

        Args:
            tick: Tick absoluto

        Returns:
            Tuple de (tick_cuantizado, desviacion_en_ticks)
        """
        # Encontrar step mas cercano
        step_index = round(tick / self.ticks_per_step)
        quantized_tick = step_index * self.ticks_per_step
        deviation = tick - quantized_tick

        return quantized_tick, deviation

    def tick_to_grid_position(self, tick: int) -> GridPosition:
        """
        Convierte tick a posicion en grid (bar, step).

        Args:
            tick: Tick absoluto

        Returns:
            GridPosition con bar (1-indexed) y step (1-16)
        """
        # Calcular bar (1-indexed)
        bar = tick // self.ticks_per_bar + 1

        # Calcular step dentro del bar (1-16)
        tick_in_bar = tick % self.ticks_per_bar
        step = tick_in_bar // self.ticks_per_step + 1

        # Asegurar step en rango valido
        step = max(1, min(STEPS_PER_BAR, step))

        return GridPosition(bar=bar, step=step)

    def onset_to_tick_data(self, onset: OnsetData) -> TickData:
        """
        Convierte OnsetData a TickData con grid position.

        Args:
            onset: Datos del onset

        Returns:
            TickData con timing completo
        """
        tick = self.time_to_tick(onset.time)
        quantized_tick, deviation_ticks = self.quantize_tick(tick)
        grid_position = self.tick_to_grid_position(quantized_tick)

        # Convertir desviacion a milisegundos
        deviation_ms = self.tick_to_time(abs(deviation_ticks)) * 1000
        if deviation_ticks < 0:
            deviation_ms = -deviation_ms

        return TickData(
            tick=tick,
            quantized_tick=quantized_tick,
            deviation_ticks=deviation_ticks,
            deviation_ms=deviation_ms,
            grid_position=grid_position
        )

    def onsets_to_tick_data(self, onsets: OnsetList) -> List[TickData]:
        """Convierte lista de onsets a lista de TickData."""
        return [self.onset_to_tick_data(onset) for onset in onsets]

    def onsets_to_bar_data(self, onsets: OnsetList, num_bars: Optional[int] = None) -> List[BarData]:
        """
        Genera BarData por compas a partir de onsets.

        Args:
            onsets: Lista de onsets
            num_bars: Numero de compases (None = calcular automaticamente)

        Returns:
            Lista de BarData, uno por compas
        """
        if len(onsets) == 0:
            return []

        # Convertir todos los onsets
        tick_data_list = self.onsets_to_tick_data(onsets)

        # Determinar numero de compases
        if num_bars is None:
            max_bar = max(td.grid_position.bar for td in tick_data_list)
            num_bars = max_bar

        # Crear BarData para cada compas
        bar_data_list = []

        for bar_num in range(1, num_bars + 1):
            # Filtrar tick_data de este compas
            bar_ticks = [td for td in tick_data_list if td.grid_position.bar == bar_num]

            # Inicializar pattern y velocities
            pattern = [0] * STEPS_PER_BAR
            velocities = [0] * STEPS_PER_BAR

            # Llenar con datos de onsets
            for td in bar_ticks:
                step_idx = td.grid_position.step - 1  # 0-indexed
                if 0 <= step_idx < STEPS_PER_BAR:
                    pattern[step_idx] = 1
                    # Obtener velocity del onset correspondiente
                    onset_idx = tick_data_list.index(td)
                    if onset_idx < len(onsets.onsets):
                        velocities[step_idx] = onsets.onsets[onset_idx].velocity

            bar_data = BarData(
                bar_number=bar_num,
                ticks=bar_ticks,
                pattern=pattern,
                velocities=velocities
            )
            bar_data_list.append(bar_data)

        return bar_data_list

    def get_humanization_stats(self, tick_data_list: List[TickData],
                               tolerance_ms: float = 5.0) -> HumanizationStats:
        """
        Calcula estadisticas de humanizacion.

        Args:
            tick_data_list: Lista de TickData
            tolerance_ms: Tolerancia para considerar "on grid" en ms

        Returns:
            HumanizationStats con porcentajes y desviaciones
        """
        if len(tick_data_list) == 0:
            return HumanizationStats(
                rushing_percent=0.0,
                dragging_percent=0.0,
                on_grid_percent=0.0,
                avg_deviation_ms=0.0,
                max_deviation_ms=0.0
            )

        deviations = [td.deviation_ms for td in tick_data_list]

        # Contar rushing (adelantado), dragging (atrasado), on_grid
        rushing = sum(1 for d in deviations if d < -tolerance_ms)
        dragging = sum(1 for d in deviations if d > tolerance_ms)
        on_grid = sum(1 for d in deviations if abs(d) <= tolerance_ms)

        total = len(deviations)

        return HumanizationStats(
            rushing_percent=rushing / total * 100,
            dragging_percent=dragging / total * 100,
            on_grid_percent=on_grid / total * 100,
            avg_deviation_ms=sum(abs(d) for d in deviations) / total,
            max_deviation_ms=max(abs(d) for d in deviations)
        )
