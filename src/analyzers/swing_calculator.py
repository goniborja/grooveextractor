"""Calculador de swing a partir de intervalos de hi-hat."""
import numpy as np
from typing import List, Optional
from ..models import (
    SwingAnalysis, SwingConfig, SWING_RANGES_BY_STYLE,
    JamaicanStyle, OnsetList
)


class SwingCalculator:
    """
    Calcula factor de swing a partir de intervalos entre hi-hats.

    El swing se mide como la proporcion entre notas largas y cortas
    en un patron de corcheas swingueadas:
    - 50% = straight (sin swing)
    - 66.7% = shuffle completo (triplet feel)

    Compara con rangos tipicos por estilo jamaicano.
    """

    def __init__(self, config: Optional[SwingConfig] = None):
        self.config = config or SwingConfig()

    def calculate_from_intervals(self, intervals: List[float]) -> SwingAnalysis:
        """
        Calcula swing a partir de intervalos entre onsets.

        Para calcular swing, agrupamos intervalos en pares (largo, corto)
        y calculamos la proporcion: largo / (largo + corto)

        Args:
            intervals: Lista de intervalos en segundos entre onsets consecutivos

        Returns:
            SwingAnalysis con porcentaje y ratio de swing
        """
        if len(intervals) < self.config.min_intervals:
            return SwingAnalysis(
                swing_percentage=50.0,
                swing_ratio=1.0,
                is_swung=False,
                confidence=0.0,
                description="Datos insuficientes"
            )

        # Calcular swing analizando pares de intervalos
        # En un patron swingueado, los intervalos alternan: largo-corto-largo-corto
        swing_ratios = []

        for i in range(0, len(intervals) - 1, 2):
            interval_1 = intervals[i]
            interval_2 = intervals[i + 1]

            # El intervalo largo es el que tiene swing
            long_interval = max(interval_1, interval_2)
            short_interval = min(interval_1, interval_2)

            total = long_interval + short_interval
            if total > 0:
                ratio = long_interval / total
                swing_ratios.append(ratio)

        if len(swing_ratios) == 0:
            return SwingAnalysis(
                swing_percentage=50.0,
                swing_ratio=1.0,
                is_swung=False,
                confidence=0.0,
                description="No se pudieron calcular ratios"
            )

        # Calcular promedio y desviacion
        mean_ratio = np.mean(swing_ratios)
        std_ratio = np.std(swing_ratios)

        # Convertir a porcentaje (0.5 = 50%, 0.667 = 66.7%)
        swing_percentage = mean_ratio * 100

        # Calcular swing_ratio (1.0 = sin swing, 2.0 = shuffle completo)
        # Si ratio = 0.5 -> swing_ratio = 1.0
        # Si ratio = 0.667 -> swing_ratio = 2.0
        if mean_ratio <= 0.5:
            swing_ratio = 1.0
        else:
            swing_ratio = mean_ratio / (1 - mean_ratio)

        # Determinar si hay swing significativo
        is_swung = swing_percentage > 52.0

        # Calcular confianza basada en consistencia
        confidence = 1.0 - min(1.0, std_ratio * 10)
        confidence = max(0.0, confidence)

        return SwingAnalysis(
            swing_percentage=swing_percentage,
            swing_ratio=swing_ratio,
            is_swung=is_swung,
            confidence=confidence
        )

    def calculate_from_onsets(self, onsets: OnsetList) -> SwingAnalysis:
        """
        Calcula swing a partir de lista de onsets.

        Args:
            onsets: Lista de onsets (tipicamente hi-hat)

        Returns:
            SwingAnalysis
        """
        times = onsets.times
        if len(times) < 2:
            return SwingAnalysis(
                swing_percentage=50.0,
                swing_ratio=1.0,
                is_swung=False,
                confidence=0.0,
                description="Datos insuficientes"
            )

        # Calcular intervalos
        intervals = [times[i+1] - times[i] for i in range(len(times) - 1)]

        return self.calculate_from_intervals(intervals)

    def compare_to_style(self, swing: SwingAnalysis,
                         style: JamaicanStyle) -> str:
        """
        Compara swing detectado con rango tipico del estilo.

        Args:
            swing: Analisis de swing
            style: Estilo jamaicano

        Returns:
            Descripcion de la comparacion
        """
        if style not in SWING_RANGES_BY_STYLE:
            return f"Estilo {style.value} sin rango de swing definido"

        min_swing, max_swing = SWING_RANGES_BY_STYLE[style]

        if swing.swing_percentage < min_swing:
            return f"Swing ({swing.swing_percentage:.1f}%) por debajo del rango tipico de {style.value} ({min_swing}-{max_swing}%)"
        elif swing.swing_percentage > max_swing:
            return f"Swing ({swing.swing_percentage:.1f}%) por encima del rango tipico de {style.value} ({min_swing}-{max_swing}%)"
        else:
            return f"Swing ({swing.swing_percentage:.1f}%) dentro del rango tipico de {style.value} ({min_swing}-{max_swing}%)"

    def suggest_style_from_swing(self, swing: SwingAnalysis) -> List[JamaicanStyle]:
        """
        Sugiere estilos compatibles con el swing detectado.

        Args:
            swing: Analisis de swing

        Returns:
            Lista de estilos compatibles ordenados por ajuste
        """
        compatible = []

        for style, (min_swing, max_swing) in SWING_RANGES_BY_STYLE.items():
            if min_swing <= swing.swing_percentage <= max_swing:
                # Calcular que tan centrado esta
                center = (min_swing + max_swing) / 2
                distance = abs(swing.swing_percentage - center)
                compatible.append((style, distance))

        # Ordenar por distancia al centro (menor = mejor ajuste)
        compatible.sort(key=lambda x: x[1])

        return [style for style, _ in compatible]
