"""Estilos de musica jamaicana y rangos de BPM."""
from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class JamaicanStyle(Enum):
    """Estilos de musica jamaicana."""
    SKA = "ska"
    ROCKSTEADY = "rocksteady"
    EARLY_REGGAE = "early_reggae"
    ONE_DROP = "one_drop"
    ROCKERS = "rockers"
    STEPPERS = "steppers"
    DUB = "dub"
    ROOTS_REGGAE = "roots_reggae"
    UNKNOWN = "unknown"


@dataclass
class StyleBPMRange:
    """Rango de BPM para un estilo."""
    style: JamaicanStyle
    min_bpm: float
    max_bpm: float
    typical_bpm: float


# Rangos de BPM por estilo (investigados)
STYLE_BPM_RANGES = {
    JamaicanStyle.SKA: StyleBPMRange(JamaicanStyle.SKA, 110, 180, 145),
    JamaicanStyle.ROCKSTEADY: StyleBPMRange(JamaicanStyle.ROCKSTEADY, 70, 95, 82),
    JamaicanStyle.EARLY_REGGAE: StyleBPMRange(JamaicanStyle.EARLY_REGGAE, 72, 100, 85),
    JamaicanStyle.ONE_DROP: StyleBPMRange(JamaicanStyle.ONE_DROP, 65, 90, 76),
    JamaicanStyle.ROCKERS: StyleBPMRange(JamaicanStyle.ROCKERS, 70, 95, 80),
    JamaicanStyle.STEPPERS: StyleBPMRange(JamaicanStyle.STEPPERS, 70, 92, 78),
    JamaicanStyle.ROOTS_REGGAE: StyleBPMRange(JamaicanStyle.ROOTS_REGGAE, 65, 95, 78),
    JamaicanStyle.DUB: StyleBPMRange(JamaicanStyle.DUB, 60, 90, 75),
}


def suggest_style_from_bpm(bpm: float) -> Tuple[JamaicanStyle, float]:
    """Sugiere estilo basado en BPM. Devuelve (estilo, confianza)."""
    best_style = JamaicanStyle.UNKNOWN
    best_confidence = 0.0

    for style, range_info in STYLE_BPM_RANGES.items():
        if range_info.min_bpm <= bpm <= range_info.max_bpm:
            # Mas cerca del tipico = mas confianza
            distance = abs(bpm - range_info.typical_bpm)
            max_distance = (range_info.max_bpm - range_info.min_bpm) / 2
            confidence = 1.0 - (distance / max_distance) if max_distance > 0 else 1.0
            confidence = max(0.5, min(1.0, confidence))

            if confidence > best_confidence:
                best_confidence = confidence
                best_style = style

    return best_style, best_confidence


def suggest_bpm_correction(bpm: float, detected_style: JamaicanStyle) -> Tuple[float, str]:
    """
    Corrige BPM si esta detectado al doble/mitad.

    IMPORTANTE para musica jamaicana:
    - Reggae one-drop a menudo se detecta al DOBLE (150 en vez de 75)
    - Ska rapido puede detectarse como reggae lento si se divide incorrectamente

    Devuelve (bpm_corregido, tipo_correccion).
    """
    correction_type = "none"
    corrected = bpm

    # Si es estilo reggae pero BPM > 130, probablemente esta al doble
    reggae_styles = {
        JamaicanStyle.ONE_DROP, JamaicanStyle.ROCKERS,
        JamaicanStyle.STEPPERS, JamaicanStyle.ROOTS_REGGAE, JamaicanStyle.DUB
    }

    if detected_style in reggae_styles and bpm > 130:
        corrected = bpm / 2
        correction_type = "halved"

    # Si es ska pero BPM < 60, probablemente esta a la mitad
    elif detected_style == JamaicanStyle.SKA and bpm < 60:
        corrected = bpm * 2
        correction_type = "doubled"

    return corrected, correction_type
