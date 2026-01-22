"""Analizador de BPM para musica jamaicana."""
import numpy as np
import librosa
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from ..models import (
    JamaicanStyle, STYLE_BPM_RANGES,
    suggest_style_from_bpm, suggest_bpm_correction
)


@dataclass
class BPMAnalysisResult:
    """Resultado del analisis de BPM."""
    bpm_detected: float
    bpm_corrected: float
    style_suggested: JamaicanStyle
    correction_type: str  # "none", "halved", "doubled"
    confidence: float
    is_vintage: bool = False
    tempo_drift: float = 0.0  # Porcentaje de drift
    alternatives: List[Tuple[JamaicanStyle, float]] = field(default_factory=list)


class JamaicanBPMAnalyzer:
    """
    Detecta BPM y sugiere estilo jamaicano.

    Correcciones automaticas:
    - BPM > 130 + estilo reggae -> divide por 2 (EXCEPTO si patron es ska)
    - BPM < 60 + estilo ska -> multiplica por 2
    - Tempo drift > 2% + estilo clasico = grabacion vintage

    IMPORTANTE: Distingue ska real (~155 BPM) de reggae detectado al doble
    basandose en el patron de bombo/caja.
    """

    def __init__(self, sr: int = 22050):
        self.sr = sr
        self.vintage_drift_threshold = 0.02  # 2%

    def analyze(self, y: np.ndarray) -> BPMAnalysisResult:
        """
        Analiza BPM del audio.

        Args:
            y: Audio array (mono)

        Returns:
            BPMAnalysisResult con BPM detectado/corregido y estilo
        """
        # Detectar BPM con librosa
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=self.sr)

        # Convertir a float si es array
        if hasattr(tempo, '__len__'):
            bpm_detected = float(tempo[0])
        else:
            bpm_detected = float(tempo)

        # Calcular tempo drift (variabilidad)
        tempo_drift = self._calculate_tempo_drift(y, beat_frames)
        is_vintage = tempo_drift > self.vintage_drift_threshold

        # Sugerir estilo inicial basado en BPM
        style_initial, confidence = suggest_style_from_bpm(bpm_detected)

        # Correccion basada solo en BPM y estilo (sin patron)
        bpm_corrected, correction_type = suggest_bpm_correction(bpm_detected, style_initial)

        # Obtener alternativas
        alternatives = self._get_style_alternatives(bpm_corrected)

        return BPMAnalysisResult(
            bpm_detected=bpm_detected,
            bpm_corrected=bpm_corrected,
            style_suggested=style_initial if correction_type == "none" else suggest_style_from_bpm(bpm_corrected)[0],
            correction_type=correction_type,
            confidence=confidence,
            is_vintage=is_vintage,
            tempo_drift=tempo_drift,
            alternatives=alternatives
        )

    def analyze_with_pattern(self, y: np.ndarray,
                             kick_times: List[float],
                             snare_times: List[float],
                             style_hint: Optional[JamaicanStyle] = None) -> BPMAnalysisResult:
        """
        Analiza BPM usando informacion de patron de bombo/caja.

        CRITICO: Esta funcion resuelve el problema de distinguir
        ska real (~155 BPM) de reggae detectado al doble.

        Args:
            y: Audio array
            kick_times: Tiempos de bombo en segundos
            snare_times: Tiempos de caja en segundos
            style_hint: Estilo sugerido por el usuario (prioridad sobre deteccion)

        Returns:
            BPMAnalysisResult con BPM refinado por patron
        """
        # Debug: mostrar style_hint recibido
        print(f"[STYLE DEBUG] Estilo seleccionado: {style_hint}")

        # Analisis basico primero
        result = self.analyze(y)

        # Si el usuario especifico un estilo, usarlo para corregir BPM
        if style_hint is not None and style_hint != JamaicanStyle.UNKNOWN:
            corrected_result = self._apply_style_hint_correction(result, style_hint)
            return corrected_result

        # Si BPM > 130, analizar patron para decidir si es ska real o reggae al doble
        if result.bpm_detected > 130 and len(kick_times) > 0 and len(snare_times) > 0:
            pattern_style = self.detect_style_from_pattern(
                kick_times, snare_times, result.bpm_detected
            )

            # Refinar BPM basado en patron
            refined_result = self.refine_bpm_with_pattern(
                result.bpm_detected, pattern_style, result
            )
            return refined_result

        return result

    def _apply_style_hint_correction(self, result: BPMAnalysisResult,
                                     style_hint: JamaicanStyle) -> BPMAnalysisResult:
        """
        Aplica correccion de BPM basada en style_hint del usuario.

        LOGICA:
        - SKA: BPM alto es correcto (120-180), no dividir
        - ONE_DROP/ROCKERS/STEPPERS/DUB: Si BPM > 130, dividir por 2
        - ROCKSTEADY: Rango 90-110, dividir si > 130

        Args:
            result: Resultado del analisis basico
            style_hint: Estilo seleccionado por el usuario

        Returns:
            BPMAnalysisResult corregido
        """
        bpm_detected = result.bpm_detected
        bpm_corrected = bpm_detected
        correction_type = "none"

        # Estilos que NUNCA deben tener BPM > 130
        slow_styles = {
            JamaicanStyle.ONE_DROP,
            JamaicanStyle.ROCKERS,
            JamaicanStyle.STEPPERS,
            JamaicanStyle.DUB,
            JamaicanStyle.ROCKSTEADY,
        }

        if style_hint in slow_styles and bpm_detected > 130:
            # Reggae detectado al doble: DIVIDIR
            bpm_corrected = bpm_detected / 2
            correction_type = "halved"
            print(f"[STYLE DEBUG] BPM corregido: {bpm_detected} -> {bpm_corrected} (estilo {style_hint.value})")

        elif style_hint == JamaicanStyle.SKA:
            # SKA: mantener BPM alto
            bpm_corrected = bpm_detected
            correction_type = "none"
            print(f"[STYLE DEBUG] SKA: manteniendo BPM {bpm_detected}")

        # Recalcular alternativas con BPM corregido
        alternatives = self._get_style_alternatives(bpm_corrected)

        return BPMAnalysisResult(
            bpm_detected=bpm_detected,
            bpm_corrected=bpm_corrected,
            style_suggested=style_hint,
            correction_type=correction_type,
            confidence=0.9,  # Alta confianza porque el usuario especifico el estilo
            is_vintage=result.is_vintage,
            tempo_drift=result.tempo_drift,
            alternatives=alternatives
        )

    def detect_style_from_pattern(self, kick_times: List[float],
                                  snare_times: List[float],
                                  bpm: float) -> JamaicanStyle:
        """
        Detecta estilo basado en patron de bombo/caja.

        Patrones caracteristicos:
        - SKA: Bombo en beats 1 y 3, snare en 2 y 4 (afterbeat)
        - ONE-DROP: Bombo SOLO en beat 3, snare en beat 3
        - ROCKERS: Bombo en 1 y 3, snare en 2 y 4 (similar a ska pero mas lento)
        - STEPPERS: Bombo en TODOS los beats (1, 2, 3, 4)

        Args:
            kick_times: Tiempos de bombo
            snare_times: Tiempos de caja
            bpm: BPM detectado

        Returns:
            JamaicanStyle detectado del patron
        """
        beat_duration = 60.0 / bpm
        tolerance = beat_duration * 0.15  # 15% tolerancia

        # Analizar primeros 4-8 compases para patron
        analysis_duration = beat_duration * 16  # 4 compases

        # Filtrar onsets en rango de analisis
        kicks_in_range = [t for t in kick_times if t < analysis_duration]
        snares_in_range = [t for t in snare_times if t < analysis_duration]

        if len(kicks_in_range) < 2:
            return JamaicanStyle.UNKNOWN

        # Calcular posiciones de beat (0-3) para cada onset
        kick_beats = self._get_beat_positions(kicks_in_range, bpm, tolerance)
        snare_beats = self._get_beat_positions(snares_in_range, bpm, tolerance)

        # Contar frecuencia de cada beat
        kick_on_1 = kick_beats.count(0)
        kick_on_2 = kick_beats.count(1)
        kick_on_3 = kick_beats.count(2)
        kick_on_4 = kick_beats.count(3)

        snare_on_2 = snare_beats.count(1)
        snare_on_3 = snare_beats.count(2)
        snare_on_4 = snare_beats.count(3)

        total_kicks = len(kick_beats)
        if total_kicks == 0:
            return JamaicanStyle.UNKNOWN

        # Detectar STEPPERS: bombo en todos los beats
        kicks_per_beat = [kick_on_1, kick_on_2, kick_on_3, kick_on_4]
        if all(k > 0 for k in kicks_per_beat):
            return JamaicanStyle.STEPPERS

        # Detectar ONE-DROP: bombo principalmente en beat 3
        kick_3_ratio = kick_on_3 / total_kicks if total_kicks > 0 else 0
        if kick_3_ratio > 0.6 and kick_on_1 / total_kicks < 0.2:
            return JamaicanStyle.ONE_DROP

        # Detectar SKA/ROCKERS: bombo en 1 y 3, snare en 2 y 4
        kick_1_3_ratio = (kick_on_1 + kick_on_3) / total_kicks if total_kicks > 0 else 0
        if kick_1_3_ratio > 0.7:
            # Distinguir ska de rockers por BPM
            if bpm > 110:
                return JamaicanStyle.SKA
            else:
                return JamaicanStyle.ROCKERS

        return JamaicanStyle.UNKNOWN

    def refine_bpm_with_pattern(self, bpm_detected: float,
                                pattern_style: JamaicanStyle,
                                base_result: BPMAnalysisResult) -> BPMAnalysisResult:
        """
        Refina BPM basado en patron detectado.

        LOGICA CLAVE para resolver la pregunta pendiente:

        1. Si BPM > 130 Y patron es SKA (bombo 1+3, snare 2+4):
           -> Es SKA REAL, NO dividir

        2. Si BPM > 130 Y patron es ONE-DROP (bombo solo beat 3):
           -> Es reggae detectado al doble, DIVIDIR por 2

        3. Si BPM > 130 Y patron es STEPPERS (bombo en todos):
           -> Es reggae detectado al doble, DIVIDIR por 2

        Args:
            bpm_detected: BPM original detectado
            pattern_style: Estilo detectado del patron
            base_result: Resultado base del analisis

        Returns:
            BPMAnalysisResult refinado
        """
        bpm_corrected = bpm_detected
        correction_type = "none"
        style_final = pattern_style

        if bpm_detected > 130:
            if pattern_style == JamaicanStyle.SKA:
                # SKA REAL: NO dividir, mantener BPM alto
                bpm_corrected = bpm_detected
                correction_type = "none"
                style_final = JamaicanStyle.SKA

            elif pattern_style == JamaicanStyle.ONE_DROP:
                # Reggae one-drop detectado al doble: DIVIDIR
                bpm_corrected = bpm_detected / 2
                correction_type = "halved"
                style_final = JamaicanStyle.ONE_DROP

            elif pattern_style == JamaicanStyle.STEPPERS:
                # Steppers detectado al doble: DIVIDIR
                bpm_corrected = bpm_detected / 2
                correction_type = "halved"
                style_final = JamaicanStyle.STEPPERS

            elif pattern_style == JamaicanStyle.ROCKERS:
                # Rockers no deberia estar a >130 BPM, probablemente mal detectado
                # Dividir por seguridad
                bpm_corrected = bpm_detected / 2
                correction_type = "halved"
                style_final = JamaicanStyle.ROCKERS

            else:
                # Estilo desconocido con BPM alto: aplicar correccion por defecto
                bpm_corrected, correction_type = suggest_bpm_correction(
                    bpm_detected, pattern_style
                )

        # Recalcular confidence basado en estilo final
        _, confidence = suggest_style_from_bpm(bpm_corrected)

        # Obtener alternativas
        alternatives = self._get_style_alternatives(bpm_corrected)

        return BPMAnalysisResult(
            bpm_detected=bpm_detected,
            bpm_corrected=bpm_corrected,
            style_suggested=style_final,
            correction_type=correction_type,
            confidence=confidence,
            is_vintage=base_result.is_vintage,
            tempo_drift=base_result.tempo_drift,
            alternatives=alternatives
        )

    def _get_beat_positions(self, times: List[float], bpm: float,
                            tolerance: float) -> List[int]:
        """
        Calcula posicion de beat (0-3) para cada tiempo.

        Args:
            times: Lista de tiempos en segundos
            bpm: BPM
            tolerance: Tolerancia en segundos

        Returns:
            Lista de posiciones de beat (0=beat 1, 1=beat 2, etc.)
        """
        beat_duration = 60.0 / bpm
        positions = []

        for t in times:
            # Posicion dentro del compas (0-3.99...)
            beat_in_bar = (t / beat_duration) % 4

            # Redondear al beat mas cercano
            beat_pos = round(beat_in_bar) % 4
            positions.append(beat_pos)

        return positions

    def _calculate_tempo_drift(self, y: np.ndarray,
                               beat_frames: np.ndarray) -> float:
        """
        Calcula variabilidad del tempo (drift).

        Returns:
            Coeficiente de variacion del tempo (0-1)
        """
        if len(beat_frames) < 3:
            return 0.0

        # Calcular intervalos entre beats
        beat_times = librosa.frames_to_time(beat_frames, sr=self.sr)
        intervals = np.diff(beat_times)

        if len(intervals) == 0:
            return 0.0

        # Coeficiente de variacion: std / mean
        mean_interval = np.mean(intervals)
        if mean_interval == 0:
            return 0.0

        cv = np.std(intervals) / mean_interval
        return float(cv)

    def _get_style_alternatives(self, bpm: float) -> List[Tuple[JamaicanStyle, float]]:
        """
        Obtiene estilos alternativos que coinciden con el BPM.

        Returns:
            Lista de (estilo, confianza) ordenada por confianza
        """
        alternatives = []

        for style, range_info in STYLE_BPM_RANGES.items():
            if range_info.min_bpm <= bpm <= range_info.max_bpm:
                distance = abs(bpm - range_info.typical_bpm)
                max_distance = (range_info.max_bpm - range_info.min_bpm) / 2
                confidence = 1.0 - (distance / max_distance) if max_distance > 0 else 1.0
                confidence = max(0.3, min(1.0, confidence))
                alternatives.append((style, confidence))

        # Ordenar por confianza descendente
        alternatives.sort(key=lambda x: x[1], reverse=True)
        return alternatives
