"""Prueba de modos OLDIE y NEWIE para separacion de stems.

OLDIE (vintage jamaicano):
- Hi-hat: filtro 3500-8500 Hz (open hihat calido)
- Kick/Snare: DrumSep

NEWIE (moderno):
- Hi-hat: filtro 4500-10000 Hz (hi-hat brillante)
- Kick/Snare: DrumSep
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import librosa
from pathlib import Path
from separators.drum_separator import DrumSeparator, HAS_AUDIO_SEPARATOR

print("="*70)
print("PRUEBA DE MODOS OLDIE vs NEWIE")
print("="*70)
print(f"\n  OLDIE: hi-hat 3500-8500 Hz (vintage jamaicano)")
print(f"  NEWIE: hi-hat 4500-10000 Hz (moderno)")

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

# =====================================================================
# MODO OLDIE
# =====================================================================
print("\n" + "="*70)
print("MODO OLDIE (vintage jamaicano)")
print("="*70)

stems_oldie = separator.separate_oldie(y, sr)

print("\n  STEMS OLDIE:")
print(f"    kick:  {len(stems_oldie.kick)/stems_oldie.sr:.2f}s (DrumSep)")
print(f"    snare: {len(stems_oldie.snare)/stems_oldie.sr:.2f}s (DrumSep)")
print(f"    hihat: {len(stems_oldie.hihat)/stems_oldie.sr:.2f}s (filtro 3500-8500 Hz)")

# Guardar stems oldie
saved_oldie = separator.save_stems(stems_oldie, str(output_dir), prefix="cascades_oldie")
print("\n  Archivos guardados:")
for name, path in saved_oldie.items():
    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"    {name}: {os.path.basename(path)} ({size_mb:.2f} MB)")

# =====================================================================
# MODO NEWIE
# =====================================================================
print("\n" + "="*70)
print("MODO NEWIE (moderno)")
print("="*70)

stems_newie = separator.separate_newie(y, sr)

print("\n  STEMS NEWIE:")
print(f"    kick:  {len(stems_newie.kick)/stems_newie.sr:.2f}s (DrumSep)")
print(f"    snare: {len(stems_newie.snare)/stems_newie.sr:.2f}s (DrumSep)")
print(f"    hihat: {len(stems_newie.hihat)/stems_newie.sr:.2f}s (filtro 4500-10000 Hz)")

# Guardar stems newie
saved_newie = separator.save_stems(stems_newie, str(output_dir), prefix="cascades_newie")
print("\n  Archivos guardados:")
for name, path in saved_newie.items():
    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"    {name}: {os.path.basename(path)} ({size_mb:.2f} MB)")

# =====================================================================
# RESUMEN
# =====================================================================
print("\n" + "="*70)
print("RESUMEN")
print("="*70)
print(f"\n  Directorio: {output_dir.absolute()}")
print(f"\n  OLDIE (vintage):")
print(f"    - cascades_oldie_hihat.wav  -> filtro 3500-8500 Hz")
print(f"    - cascades_oldie_kick.wav   -> DrumSep")
print(f"    - cascades_oldie_snare.wav  -> DrumSep")
print(f"\n  NEWIE (moderno):")
print(f"    - cascades_newie_hihat.wav  -> filtro 4500-10000 Hz")
print(f"    - cascades_newie_kick.wav   -> DrumSep")
print(f"    - cascades_newie_snare.wav  -> DrumSep")
print(f"\n  Compara los hi-hats para escuchar la diferencia!")
