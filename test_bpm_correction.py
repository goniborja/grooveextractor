"""Script de prueba para verificar la corrección de BPM con style_hint."""
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import librosa
import numpy as np

# Importar los modelos directamente
from models import JamaicanStyle, STYLE_BPM_RANGES, suggest_style_from_bpm, suggest_bpm_correction
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class BPMAnalysisResult:
    """Resultado del analisis de BPM."""
    bpm_detected: float
    bpm_corrected: float
    style_suggested: JamaicanStyle
    correction_type: str
    confidence: float
    is_vintage: bool = False
    tempo_drift: float = 0.0
    alternatives: List[Tuple[JamaicanStyle, float]] = field(default_factory=list)


def analyze_bpm(y: np.ndarray, sr: int, style_hint: Optional[str] = None) -> BPMAnalysisResult:
    """Analiza BPM con style_hint opcional."""
    # Detectar BPM con librosa
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    if hasattr(tempo, '__len__'):
        bpm_detected = float(tempo[0])
    else:
        bpm_detected = float(tempo)

    print(f"\n[BPM DEBUG] BPM detectado por librosa: {bpm_detected:.2f}")

    # Si el usuario proporciona style_hint, usarlo para corregir BPM
    if style_hint in ['one_drop', 'rockers', 'steppers'] and bpm_detected > 130:
        bpm_corrected = bpm_detected / 2
        correction_type = "halved"
        print(f"[BPM DEBUG] Usuario indicó '{style_hint}' y BPM > 130")
        print(f"[BPM DEBUG] Aplicando corrección: {bpm_detected:.2f} / 2 = {bpm_corrected:.2f}")

        style_map = {
            'one_drop': JamaicanStyle.ONE_DROP,
            'rockers': JamaicanStyle.ROCKERS,
            'steppers': JamaicanStyle.STEPPERS
        }
        style_suggested = style_map[style_hint]
        confidence = 0.95

        return BPMAnalysisResult(
            bpm_detected=bpm_detected,
            bpm_corrected=bpm_corrected,
            style_suggested=style_suggested,
            correction_type=correction_type,
            confidence=confidence
        )

    # Fallback: detección automática
    print(f"[BPM DEBUG] Usando detección automática")
    style_initial, confidence = suggest_style_from_bpm(bpm_detected)
    bpm_corrected, correction_type = suggest_bpm_correction(bpm_detected, style_initial)

    return BPMAnalysisResult(
        bpm_detected=bpm_detected,
        bpm_corrected=bpm_corrected,
        style_suggested=style_initial if correction_type == "none" else suggest_style_from_bpm(bpm_corrected)[0],
        correction_type=correction_type,
        confidence=confidence
    )


# === EJECUCIÓN PRINCIPAL ===
audio_path = "03 Cascades - master 1 - 16bit_drums.wav"
print(f"\n{'='*60}")
print(f"Analizando: {audio_path}")
print(f"{'='*60}")

y, sr = librosa.load(audio_path, sr=22050)
print(f"Audio cargado: {len(y)/sr:.2f} segundos, sr={sr}")

# Prueba 1: Sin style_hint (detección automática)
print(f"\n{'='*60}")
print("PRUEBA 1: Sin style_hint (detección automática)")
print(f"{'='*60}")
result_auto = analyze_bpm(y, sr)
print(f"\n  Resultado:")
print(f"    BPM detectado: {result_auto.bpm_detected:.2f}")
print(f"    BPM corregido: {result_auto.bpm_corrected:.2f}")
print(f"    Estilo sugerido: {result_auto.style_suggested}")
print(f"    Tipo de corrección: {result_auto.correction_type}")

# Prueba 2: Con style_hint='one_drop' (simulando knob en posición 2)
print(f"\n{'='*60}")
print("PRUEBA 2: Con style_hint='one_drop' (knob posición 2)")
print(f"{'='*60}")
result_one_drop = analyze_bpm(y, sr, style_hint='one_drop')
print(f"\n  Resultado:")
print(f"    BPM detectado: {result_one_drop.bpm_detected:.2f}")
print(f"    BPM corregido: {result_one_drop.bpm_corrected:.2f}")
print(f"    Estilo sugerido: {result_one_drop.style_suggested}")
print(f"    Tipo de corrección: {result_one_drop.correction_type}")

# Verificación final
print(f"\n{'='*60}")
print("VERIFICACIÓN FINAL")
print(f"{'='*60}")
expected_original = 152  # aproximado
expected_corrected = 76  # aproximado

if result_one_drop.bpm_detected > 140 and result_one_drop.bpm_corrected < 90:
    print(f"\n✓ CORRECCIÓN EXITOSA!")
    print(f"  ~{result_one_drop.bpm_detected:.1f} BPM → ~{result_one_drop.bpm_corrected:.1f} BPM")
    print(f"  El knob en posición 2 (one_drop) fuerza la división por 2")
else:
    print(f"\n✗ La corrección no funcionó como se esperaba")
