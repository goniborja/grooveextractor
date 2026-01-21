"""Prueba del flujo de separacion HIBRIDO.

FLUJO HIBRIDO:
==============
- Kick y Snare: del pipeline Demucs + DrumSep (mejor separacion de graves)
- Hihat: de DrumSep directo sobre la mezcla (mejor ataque de hihat)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import librosa
from pathlib import Path
from separators.drum_separator import DrumSeparator, HAS_AUDIO_SEPARATOR

print("="*70)
print("PRUEBA DE SEPARACION HIBRIDA")
print("="*70)

print(f"\naudio-separator disponible: {HAS_AUDIO_SEPARATOR}")

# Cargar primeros 30 segundos
audio_path = "03 Cascades - master 1 - 16bit_drums.wav"
print(f"\nCargando primeros 30 segundos de: {audio_path}")

y, sr = librosa.load(audio_path, sr=None, duration=30.0)
print(f"Audio cargado: {len(y)/sr:.2f} segundos, sr={sr}")

# Crear directorio de salida
output_dir = Path("test_stems_output")
output_dir.mkdir(exist_ok=True)

# Crear separador
separator = DrumSeparator(output_dir=str(output_dir))

print("\n" + "="*70)
print("EJECUTANDO SEPARACION HIBRIDA")
print("="*70)

# Ejecutar separacion hibrida
stems = separator.separate_hybrid(y, sr)

print("\n" + "-"*40)
print("STEMS GENERADOS (HIBRIDO):")
print("-"*40)

print(f"  kick:  {len(stems.kick)/stems.sr:.2f}s (de Demucs+DrumSep)" if stems.kick is not None else "  kick:  NO")
print(f"  snare: {len(stems.snare)/stems.sr:.2f}s (de Demucs+DrumSep)" if stems.snare is not None else "  snare: NO")
print(f"  hihat: {len(stems.hihat)/stems.sr:.2f}s (de DrumSep directo)" if stems.hihat is not None else "  hihat: NO")
print(f"  toms:  {len(stems.toms)/stems.sr:.2f}s (de Demucs+DrumSep)" if stems.toms is not None else "  toms:  NO")

# Guardar stems
print("\n" + "-"*40)
print("GUARDANDO STEMS:")
print("-"*40)

saved = separator.save_stems(stems, str(output_dir), prefix="cascades_hybrid")
for name, path in saved.items():
    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"  {name}: {path} ({size_mb:.2f} MB)")

print("\n" + "="*70)
print("RESUMEN")
print("="*70)
print(f"  Stems principales: {'TODOS OK' if stems.has_all_stems() else 'INCOMPLETO'}")
print(f"  Archivos en: {output_dir.absolute()}")
print("\n  ORIGEN DE CADA STEM:")
print("    - kick:  Demucs + DrumSep (mejor separacion de graves)")
print("    - snare: Demucs + DrumSep (mejor separacion de graves)")
print("    - hihat: DrumSep directo (mejor ataque y definicion)")
