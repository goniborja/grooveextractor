"""Prueba del flujo de separacion en dos fases.

FLUJO:
======
Cascades (bateria pura) -> DrumSep -> kick/snare/hihat

Como el archivo "03 Cascades" ya es bateria pura, solo se usa Fase 2.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import librosa
from pathlib import Path
from separators.drum_separator import DrumSeparator, HAS_AUDIO_SEPARATOR

print("="*70)
print("PRUEBA DE SEPARACION EN DOS FASES")
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
print("CASO 1: Audio es bateria pura (solo Fase 2 - DrumSep)")
print("="*70)

# Como el archivo ya es bateria, solo usamos Fase 2
stems = separator.separate_drums(y, sr)

print("\n" + "-"*40)
print("STEMS GENERADOS:")
print("-"*40)

for stem_name in ['kick', 'snare', 'hihat', 'toms']:
    stem = getattr(stems, stem_name)
    if stem is not None:
        print(f"  {stem_name}: {len(stem)/stems.sr:.2f}s, shape={stem.shape}")
    else:
        print(f"  {stem_name}: NO")

# Guardar stems
print("\n" + "-"*40)
print("GUARDANDO STEMS:")
print("-"*40)

saved = separator.save_stems(stems, str(output_dir), prefix="cascades_fase2")
for name, path in saved.items():
    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"  {name}: {path} ({size_mb:.2f} MB)")

print("\n" + "="*70)
print("RESUMEN")
print("="*70)
print(f"  Stems principales: {'TODOS OK' if stems.has_all_stems() else 'INCOMPLETO'}")
print(f"  Archivos en: {output_dir.absolute()}")
