"""
Book of Drums - Generators Module

Modulos de generacion MIDI y humanizacion.

Uso:
    from generators import MidiGenerator, Humanizer

    # Generar MIDI con Carlton Barrett
    gen = MidiGenerator("carlton-barrett", bpm=72)
    gen.generate_quick_test("output.mid")

    # Usar humanizador directamente
    from profiles import get_profile
    profile = get_profile("sly-dunbar")
    humanizer = Humanizer(profile, bpm=80)
"""

from .humanizer import Humanizer
from .midi_generator import MidiGenerator

__all__ = [
    "Humanizer",
    "MidiGenerator",
]
