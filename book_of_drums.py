#!/usr/bin/env python3
"""
Book of Drums - CLI

Generador de pistas de bateria MIDI con humanizacion autentica
basada en perfiles de bateristas jamaicanos.

Uso:
    python book_of_drums.py                      # Menu interactivo
    python book_of_drums.py --quick              # Genera test rapido
    python book_of_drums.py --drummer sly-dunbar # Especifica baterista
    python book_of_drums.py --list               # Lista bateristas y patrones

Ejemplos:
    python book_of_drums.py --drummer carlton-barrett --bpm 72 --bars 16
    python book_of_drums.py --drummer lloyd-knibb --bpm 120 --style ska
    python book_of_drums.py --song --drummer santa-davis --output mi_cancion.mid
"""

import argparse
import sys
import os
from pathlib import Path

# Asegurar que el directorio raiz esta en el path
sys.path.insert(0, str(Path(__file__).parent))

from profiles import (
    list_drummers,
    get_profile,
    get_available_styles,
    list_patterns,
    get_patterns_by_style,
    get_patterns_for_drummer,
    get_pattern,
)
from generators import MidiGenerator


def print_header():
    """Imprime el header del programa."""
    print()
    print("=" * 60)
    print("  BOOK OF DRUMS")
    print("  Generador de Bateria MIDI con Humanizacion Jamaicana")
    print("=" * 60)
    print()


def list_available():
    """Lista bateristas y patrones disponibles."""
    print_header()

    print("BATERISTAS DISPONIBLES:")
    print("-" * 40)
    for slug in list_drummers():
        profile = get_profile(slug)
        bpm_min, bpm_max = profile.get("bpm_range", (70, 85))
        print(f"  {slug}")
        print(f"    Nombre: {profile['name']}")
        print(f"    Estilo: {profile['style']}")
        print(f"    Era: {profile['era']}")
        print(f"    BPM: {bpm_min}-{bpm_max}")
        print()

    print("\nESTILOS DISPONIBLES:")
    print("-" * 40)
    for style in get_available_styles():
        patterns = get_patterns_by_style(style)
        print(f"  {style}: {len(patterns)} patrones")

    print("\nPATRONES POR TIPO:")
    print("-" * 40)
    from profiles import get_patterns_by_type
    for ptype in ["rhythm", "fill", "intro", "outro", "break"]:
        patterns = get_patterns_by_type(ptype)
        if patterns:
            print(f"  {ptype}: {', '.join(patterns[:3])}{'...' if len(patterns) > 3 else ''}")

    print()


def interactive_mode():
    """Modo interactivo para seleccionar opciones."""
    print_header()

    # Seleccionar baterista
    drummers = list_drummers()
    print("Selecciona un baterista:")
    for i, slug in enumerate(drummers, 1):
        profile = get_profile(slug)
        print(f"  {i}. {profile['name']} ({profile['style']})")

    while True:
        try:
            choice = input("\nNumero [1]: ").strip() or "1"
            idx = int(choice) - 1
            if 0 <= idx < len(drummers):
                drummer = drummers[idx]
                break
            print("Opcion invalida")
        except ValueError:
            print("Introduce un numero")

    profile = get_profile(drummer)
    print(f"\n-> Seleccionado: {profile['name']}")

    # BPM
    bpm_min, bpm_max = profile.get("bpm_range", (70, 85))
    default_bpm = (bpm_min + bpm_max) // 2
    bpm_input = input(f"\nBPM [{default_bpm}]: ").strip()
    bpm = int(bpm_input) if bpm_input else default_bpm
    print(f"-> BPM: {bpm}")

    # Tipo de generacion
    print("\nTipo de generacion:")
    print("  1. Test rapido (9 compases)")
    print("  2. Cancion completa (intro + versos + coros)")
    print("  3. Patron personalizado")

    gen_type = input("\nNumero [1]: ").strip() or "1"

    # Nombre de salida
    output = input(f"\nArchivo de salida [output_{drummer}.mid]: ").strip()
    if not output:
        output = f"output_{drummer}.mid"
    if not output.endswith(".mid"):
        output += ".mid"

    # Crear directorio de salida
    output_dir = Path("midi_output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / output

    # Generar
    print(f"\nGenerando MIDI...")
    gen = MidiGenerator(drummer, bpm=bpm)

    if gen_type == "1":
        gen.generate_quick_test(str(output_path))
    elif gen_type == "2":
        intro = int(input("Compases de intro [2]: ").strip() or "2")
        verse = int(input("Compases de verso [8]: ").strip() or "8")
        chorus = int(input("Compases de coro [8]: ").strip() or "8")
        sections = int(input("Secciones (verso+coro) [2]: ").strip() or "2")
        gen.generate_song_structure(
            str(output_path),
            intro_bars=intro,
            verse_bars=verse,
            chorus_bars=chorus,
            sections=sections
        )
    else:
        # Patron personalizado
        patterns = get_patterns_for_drummer(drummer)
        print("\nPatrones disponibles:")
        for i, pid in enumerate(patterns[:10], 1):
            p = get_pattern(pid)
            print(f"  {i}. {p['name']} ({pid})")

        pattern_choice = input("\nNumero [1]: ").strip() or "1"
        try:
            pattern_id = patterns[int(pattern_choice) - 1]
        except (ValueError, IndexError):
            pattern_id = patterns[0]

        bars = int(input("Compases [8]: ").strip() or "8")
        intensity = float(input("Intensidad 0.0-1.0 [0.8]: ").strip() or "0.8")

        blocks = [
            {"pattern_id": pattern_id, "bars": bars, "intensity": intensity}
        ]
        gen.create_midi_file(blocks, str(output_path))

    print(f"\n{'=' * 60}")
    print(f"MIDI generado: {output_path}")
    print(f"{'=' * 60}")
    print(f"\nAbre el archivo en Cubase, Logic, Ableton o cualquier DAW")
    print(f"para escuchar el groove de {profile['name']}!")
    print()


def quick_generate(drummer: str, bpm: int, output: str):
    """Genera un test rapido."""
    print_header()

    profile = get_profile(drummer)
    print(f"Baterista: {profile['name']}")
    print(f"Estilo: {profile['style']}")
    print(f"BPM: {bpm}")

    output_dir = Path("midi_output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / output

    gen = MidiGenerator(drummer, bpm=bpm)
    gen.generate_quick_test(str(output_path))

    print(f"\nGenerado: {output_path}")


def generate_song(drummer: str, bpm: int, output: str,
                  intro: int = 2, verse: int = 8, chorus: int = 8, sections: int = 2):
    """Genera una cancion completa."""
    print_header()

    profile = get_profile(drummer)
    print(f"Baterista: {profile['name']}")
    print(f"Estilo: {profile['style']}")
    print(f"BPM: {bpm}")
    print(f"Estructura: {intro} intro + {sections}x({verse} verso + {chorus} coro)")

    output_dir = Path("midi_output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / output

    gen = MidiGenerator(drummer, bpm=bpm)
    gen.generate_song_structure(
        str(output_path),
        intro_bars=intro,
        verse_bars=verse,
        chorus_bars=chorus,
        sections=sections
    )

    print(f"\nGenerado: {output_path}")


def generate_all_drummers(bpm: int = None, output_dir: str = "midi_output"):
    """Genera un test para cada baterista."""
    print_header()
    print("Generando tests para todos los bateristas...")
    print()

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for slug in list_drummers():
        profile = get_profile(slug)
        drummer_bpm = bpm or (profile["bpm_range"][0] + profile["bpm_range"][1]) // 2

        filename = f"test_{slug}.mid"
        filepath = output_path / filename

        gen = MidiGenerator(slug, bpm=drummer_bpm)
        gen.generate_quick_test(str(filepath))

        print(f"  {profile['name']:25} -> {filename} ({drummer_bpm} BPM)")

    print(f"\nTodos los archivos generados en: {output_path}/")


def main():
    parser = argparse.ArgumentParser(
        description="Book of Drums - Generador de Bateria MIDI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python book_of_drums.py                                    # Modo interactivo
  python book_of_drums.py --list                             # Lista bateristas
  python book_of_drums.py --quick --drummer carlton-barrett  # Test rapido
  python book_of_drums.py --song --drummer sly-dunbar        # Cancion completa
  python book_of_drums.py --all                              # Genera todos
        """
    )

    parser.add_argument("--list", "-l", action="store_true",
                        help="Lista bateristas y patrones disponibles")
    parser.add_argument("--quick", "-q", action="store_true",
                        help="Genera un test rapido (9 compases)")
    parser.add_argument("--song", "-s", action="store_true",
                        help="Genera una cancion completa")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Genera test para todos los bateristas")

    parser.add_argument("--drummer", "-d", type=str, default="carlton-barrett",
                        help="Baterista a usar (default: carlton-barrett)")
    parser.add_argument("--bpm", "-b", type=int, default=None,
                        help="BPM (default: segun baterista)")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Archivo de salida")

    # Opciones de cancion
    parser.add_argument("--intro", type=int, default=2,
                        help="Compases de intro (default: 2)")
    parser.add_argument("--verse", type=int, default=8,
                        help="Compases de verso (default: 8)")
    parser.add_argument("--chorus", type=int, default=8,
                        help="Compases de coro (default: 8)")
    parser.add_argument("--sections", type=int, default=2,
                        help="Numero de secciones verso+coro (default: 2)")

    args = parser.parse_args()

    # Verificar baterista valido
    if args.drummer not in list_drummers():
        print(f"Error: Baterista '{args.drummer}' no encontrado.")
        print(f"Disponibles: {', '.join(list_drummers())}")
        sys.exit(1)

    # Determinar BPM
    if args.bpm is None:
        profile = get_profile(args.drummer)
        args.bpm = (profile["bpm_range"][0] + profile["bpm_range"][1]) // 2

    # Determinar output
    if args.output is None:
        if args.song:
            args.output = f"song_{args.drummer}.mid"
        else:
            args.output = f"test_{args.drummer}.mid"

    # Ejecutar accion
    if args.list:
        list_available()
    elif args.all:
        generate_all_drummers(args.bpm)
    elif args.quick:
        quick_generate(args.drummer, args.bpm, args.output)
    elif args.song:
        generate_song(
            args.drummer, args.bpm, args.output,
            args.intro, args.verse, args.chorus, args.sections
        )
    else:
        # Modo interactivo
        interactive_mode()


if __name__ == "__main__":
    main()
