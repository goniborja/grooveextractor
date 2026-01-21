"""Script de prueba para DrumSeparator con los primeros 30 segundos."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import librosa
import soundfile as sf
from pathlib import Path

# Importar DrumSeparator
from separators.drum_separator import DrumSeparator, HAS_AUDIO_SEPARATOR

print("="*60)
print("PRUEBA DE DRUM SEPARATOR")
print("="*60)

# Verificar disponibilidad
print(f"\naudio-separator disponible: {HAS_AUDIO_SEPARATOR}")

# Cargar primeros 30 segundos
audio_path = "03 Cascades - master 1 - 16bit_drums.wav"
print(f"\nCargando primeros 30 segundos de: {audio_path}")

y, sr = librosa.load(audio_path, sr=None, duration=30.0)
print(f"  Audio cargado: {len(y)/sr:.2f} segundos, sr={sr}")

# Crear directorio de salida
output_dir = Path("test_stems_output")
output_dir.mkdir(exist_ok=True)
print(f"\nDirectorio de salida: {output_dir.absolute()}")

# Crear separador
print("\n" + "="*60)
print("INICIANDO SEPARACION")
print("="*60)

model_name = "MDX23C-DrumSep-aufr33-jarredou.ckpt"
separator = DrumSeparator(model_name=model_name, output_dir=str(output_dir))
print(f"  Modelo: {model_name}")
print(f"  Directorio temporal: {separator.output_dir}")

# Separar
print("\nSeparando stems (esto puede tomar un momento)...")
stems = separator.separate_array(y, sr)

# Mostrar resultados
print("\n" + "="*60)
print("STEMS GENERADOS")
print("="*60)

print(f"\n  Kick:  {'SI' if stems.kick is not None else 'NO'}", end="")
if stems.kick is not None:
    print(f" - {len(stems.kick)/stems.sr:.2f}s, shape={stems.kick.shape}")
else:
    print()

print(f"  Snare: {'SI' if stems.snare is not None else 'NO'}", end="")
if stems.snare is not None:
    print(f" - {len(stems.snare)/stems.sr:.2f}s, shape={stems.snare.shape}")
else:
    print()

print(f"  HiHat: {'SI' if stems.hihat is not None else 'NO'}", end="")
if stems.hihat is not None:
    print(f" - {len(stems.hihat)/stems.sr:.2f}s, shape={stems.hihat.shape}")
else:
    print()

print(f"  Toms:  {'SI' if stems.toms is not None else 'NO'}", end="")
if stems.toms is not None:
    print(f" - {len(stems.toms)/stems.sr:.2f}s, shape={stems.toms.shape}")
else:
    print()

print(f"  Other: {'SI' if stems.other is not None else 'NO'}", end="")
if stems.other is not None:
    print(f" - {len(stems.other)/stems.sr:.2f}s, shape={stems.other.shape}")
else:
    print()

print(f"\n  Sample rate: {stems.sr}")
print(f"  Todos los stems principales: {stems.has_all_stems()}")

# Guardar stems
print("\n" + "="*60)
print("GUARDANDO STEMS")
print("="*60)

saved_files = separator.save_stems(stems, str(output_dir), prefix="cascades_30s")

print("\nArchivos guardados:")
for stem_name, file_path in saved_files.items():
    file_size = os.path.getsize(file_path) / 1024 / 1024  # MB
    print(f"  {stem_name}: {file_path} ({file_size:.2f} MB)")

# Listar todos los archivos en output_dir
print("\n" + "="*60)
print("CONTENIDO DEL DIRECTORIO DE SALIDA")
print("="*60)
print(f"\n{output_dir.absolute()}:")
for f in sorted(output_dir.iterdir()):
    size = f.stat().st_size / 1024 / 1024
    print(f"  {f.name} ({size:.2f} MB)")
