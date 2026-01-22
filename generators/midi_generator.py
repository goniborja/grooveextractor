"""
Book of Drums - MIDI Generator

Generador de archivos MIDI con humanizacion.

Convierte una secuencia de bloques (patrones + configuracion)
en un archivo MIDI con el feel autentico de un baterista.
"""

from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from typing import List, Dict, Optional
import os

from .humanizer import Humanizer
from profiles.drummer_profiles import get_profile
from profiles.pattern_library import get_pattern, PATTERN_LIBRARY


class MidiGenerator:
    """
    Generador de archivos MIDI con humanizacion.

    Combina perfiles de bateristas, patrones y humanizacion
    para producir archivos MIDI con grooves autenticos.
    """

    # Resolucion MIDI estandar
    TICKS_PER_BEAT = 480

    def __init__(self, drummer_slug: str, bpm: int = 75):
        """
        Inicializa el generador.

        Args:
            drummer_slug: ID del baterista (ej: "carlton-barrett")
            bpm: Tempo en beats por minuto
        """
        self.profile = get_profile(drummer_slug)
        self.bpm = bpm
        self.humanizer = Humanizer(self.profile, bpm)
        self.drummer_slug = drummer_slug

    def pattern_to_events(self, pattern_id: str, num_bars: int = 1,
                          intensity: float = 1.0,
                          enable_ghosts: bool = True) -> List[dict]:
        """
        Convierte un patron a eventos MIDI humanizados.

        Args:
            pattern_id: ID del patron en la libreria
            num_bars: Numero de compases a generar
            intensity: Factor de intensidad (0.0-1.0)
            enable_ghosts: Si anadir ghost notes

        Returns:
            Lista de eventos MIDI humanizados
        """
        pattern = get_pattern(pattern_id)
        pattern_bars = pattern.get("length_bars", 1)

        # Calcular cuantas repeticiones del patron necesitamos
        repetitions = (num_bars + pattern_bars - 1) // pattern_bars

        events = self.humanizer.humanize_pattern(
            pattern["events"],
            intensity=intensity,
            enable_ghosts=enable_ghosts,
            num_bars=repetitions
        )

        # Recortar si generamos de mas
        max_tick = num_bars * 4 * self.TICKS_PER_BEAT
        events = [e for e in events if e["tick"] < max_tick]

        return events

    def blocks_to_events(self, blocks: List[dict]) -> List[dict]:
        """
        Convierte una lista de bloques a eventos MIDI.

        Args:
            blocks: Lista de bloques del arranger
                    Cada bloque: {
                        "pattern_id": str,
                        "bars": int,
                        "position_beats": int (opcional),
                        "intensity": float (opcional, default 1.0),
                        "ghost_notes": bool (opcional, default True),
                        "drummer": str (opcional, override del drummer principal)
                    }

        Returns:
            Lista de eventos MIDI con tiempos absolutos
        """
        all_events = []
        current_position = 0  # En ticks

        for block in blocks:
            pattern_id = block["pattern_id"]
            bars = block.get("bars", 1)
            intensity = block.get("intensity", 1.0)
            enable_ghosts = block.get("ghost_notes", True)

            # Posicion explicita o secuencial
            if "position_beats" in block:
                current_position = block["position_beats"] * self.TICKS_PER_BEAT

            # Generar eventos del patron
            events = self.pattern_to_events(
                pattern_id,
                num_bars=bars,
                intensity=intensity,
                enable_ghosts=enable_ghosts
            )

            # Ajustar posiciones a tiempo absoluto
            for event in events:
                event["tick"] += current_position
                all_events.append(event)

            # Avanzar posicion
            current_position += bars * 4 * self.TICKS_PER_BEAT

        # Ordenar por tick
        all_events.sort(key=lambda e: e["tick"])
        return all_events

    def create_midi_file(self, blocks: List[dict], output_path: str,
                         separate_tracks: bool = True) -> str:
        """
        Genera un archivo MIDI desde una lista de bloques.

        Args:
            blocks: Lista de bloques del arranger
            output_path: Ruta donde guardar el archivo .mid
            separate_tracks: Si True, crea tracks separados para kick/snare/hihat

        Returns:
            Ruta del archivo generado
        """
        # Generar eventos
        events = self.blocks_to_events(blocks)

        if not events:
            raise ValueError("No hay eventos para generar")

        # Crear archivo MIDI
        mid = MidiFile(ticks_per_beat=self.TICKS_PER_BEAT)

        # Track de tempo
        tempo_track = MidiTrack()
        mid.tracks.append(tempo_track)
        tempo_track.append(MetaMessage('set_tempo', tempo=bpm2tempo(self.bpm), time=0))
        tempo_track.append(MetaMessage('track_name',
                                       name=f'Book of Drums - {self.profile["name"]}',
                                       time=0))
        tempo_track.append(MetaMessage('end_of_track', time=0))

        if separate_tracks:
            # Tracks separados por instrumento
            self._create_separate_tracks(mid, events)
        else:
            # Track unico
            self._create_single_track(mid, events)

        # Guardar
        dir_path = os.path.dirname(output_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        mid.save(output_path)

        return output_path

    def _create_separate_tracks(self, mid: MidiFile, events: List[dict]):
        """
        Crea tracks separados para cada tipo de instrumento.

        Args:
            mid: Archivo MIDI
            events: Lista de eventos
        """
        # Agrupar eventos por tipo de instrumento
        instrument_groups = {
            "kick": [],
            "snare": [],
            "hihat": []
        }

        for event in events:
            inst = event.get("instrument", "")
            if "kick" in inst:
                instrument_groups["kick"].append(event)
            elif "snare" in inst or "rimshot" in inst:
                instrument_groups["snare"].append(event)
            elif "hihat" in inst:
                instrument_groups["hihat"].append(event)

        # Crear track para cada grupo
        for inst_name, inst_events in instrument_groups.items():
            if not inst_events:
                continue

            track = MidiTrack()
            mid.tracks.append(track)
            track.append(MetaMessage('track_name', name=inst_name.capitalize(), time=0))

            # Convertir a mensajes MIDI con deltas
            self._events_to_track(track, inst_events)

    def _create_single_track(self, mid: MidiFile, events: List[dict]):
        """
        Crea un unico track con todos los instrumentos.

        Args:
            mid: Archivo MIDI
            events: Lista de eventos
        """
        track = MidiTrack()
        mid.tracks.append(track)
        track.append(MetaMessage('track_name', name='Drums', time=0))
        self._events_to_track(track, events)

    def _events_to_track(self, track: MidiTrack, events: List[dict]):
        """
        Convierte eventos a mensajes MIDI en un track.

        Args:
            track: Track MIDI
            events: Lista de eventos
        """
        # Ordenar por tick
        events = sorted(events, key=lambda e: e["tick"])

        note_duration = 120  # Duracion de cada nota en ticks

        # Crear lista de mensajes Note On y Note Off
        messages = []
        for event in events:
            tick = event["tick"]
            note = event["note"]
            velocity = event["velocity"]

            messages.append(("on", tick, note, velocity))
            messages.append(("off", tick + note_duration, note, 0))

        # Ordenar por tiempo
        messages.sort(key=lambda m: (m[1], 0 if m[0] == "on" else 1))

        # Convertir a deltas
        last_tick = 0
        for msg_type, tick, note, velocity in messages:
            delta = tick - last_tick
            if msg_type == "on":
                track.append(Message('note_on', note=note, velocity=velocity,
                                    time=delta, channel=9))  # Canal 10 = drums
            else:
                track.append(Message('note_off', note=note, velocity=0,
                                    time=delta, channel=9))
            last_tick = tick

        track.append(MetaMessage('end_of_track', time=0))

    def generate_quick_test(self, output_path: str = "test_output.mid") -> str:
        """
        Genera un MIDI de prueba rapida.

        Args:
            output_path: Ruta donde guardar el archivo

        Returns:
            Ruta del archivo generado
        """
        # Buscar un patron compatible con el baterista actual
        style = self.profile.get("style", "one-drop")
        patterns = [pid for pid, p in PATTERN_LIBRARY.items()
                   if p.get("style") == style and p.get("type") == "rhythm"]

        if not patterns:
            patterns = ["one-drop-basic"]  # Fallback

        pattern_id = patterns[0]

        blocks = [
            {"pattern_id": pattern_id, "bars": 4, "intensity": 0.8},
            {"pattern_id": "fill-1bar-simple", "bars": 1, "intensity": 0.9},
            {"pattern_id": pattern_id, "bars": 4, "intensity": 1.0},
        ]

        return self.create_midi_file(blocks, output_path, separate_tracks=True)

    def generate_song_structure(self, output_path: str = "song.mid",
                                intro_bars: int = 2,
                                verse_bars: int = 8,
                                chorus_bars: int = 8,
                                sections: int = 2) -> str:
        """
        Genera una estructura de cancion completa.

        Args:
            output_path: Ruta donde guardar el archivo
            intro_bars: Compases de intro
            verse_bars: Compases de verso
            chorus_bars: Compases de coro
            sections: Numero de repeticiones (verso+coro)

        Returns:
            Ruta del archivo generado
        """
        style = self.profile.get("style", "one-drop")

        # Buscar patrones por estilo
        rhythm_patterns = [pid for pid, p in PATTERN_LIBRARY.items()
                         if p.get("style") == style and p.get("type") == "rhythm"]

        if not rhythm_patterns:
            rhythm_patterns = ["one-drop-basic"]

        main_pattern = rhythm_patterns[0]
        alt_pattern = rhythm_patterns[1] if len(rhythm_patterns) > 1 else main_pattern

        blocks = []

        # Intro
        if intro_bars > 0:
            blocks.append({"pattern_id": "intro-count-2bar", "bars": min(intro_bars, 2), "intensity": 0.5})
            if intro_bars > 2:
                blocks.append({"pattern_id": main_pattern, "bars": intro_bars - 2, "intensity": 0.7})

        # Secciones
        for i in range(sections):
            # Verso
            blocks.append({"pattern_id": main_pattern, "bars": verse_bars - 1, "intensity": 0.8})
            blocks.append({"pattern_id": "fill-1bar-simple", "bars": 1, "intensity": 0.9})

            # Coro
            blocks.append({"pattern_id": alt_pattern, "bars": chorus_bars - 1, "intensity": 1.0})
            if i < sections - 1:
                blocks.append({"pattern_id": "fill-1bar-simple", "bars": 1, "intensity": 0.95})
            else:
                blocks.append({"pattern_id": "outro-hit", "bars": 1, "intensity": 1.0})

        return self.create_midi_file(blocks, output_path, separate_tracks=True)


# ==============================================================================
# TEST
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DE MIDI GENERATOR")
    print("=" * 60)

    # Crear directorio de salida
    output_dir = "midi_output"
    os.makedirs(output_dir, exist_ok=True)

    # Probar con Carlton Barrett
    print("\n1. Generando MIDI con Carlton Barrett (one-drop)...")
    gen = MidiGenerator("carlton-barrett", bpm=72)
    path = gen.generate_quick_test(f"{output_dir}/test_carlton.mid")
    print(f"   Generado: {path}")

    # Probar con Sly Dunbar
    print("\n2. Generando MIDI con Sly Dunbar (steppers)...")
    gen = MidiGenerator("sly-dunbar", bpm=80)
    path = gen.generate_quick_test(f"{output_dir}/test_sly.mid")
    print(f"   Generado: {path}")

    # Probar con Lloyd Knibb
    print("\n3. Generando MIDI con Lloyd Knibb (ska)...")
    gen = MidiGenerator("lloyd-knibb", bpm=120)
    path = gen.generate_quick_test(f"{output_dir}/test_lloyd.mid")
    print(f"   Generado: {path}")

    # Probar bloques personalizados
    print("\n4. Generando MIDI con bloques personalizados...")
    gen = MidiGenerator("carlton-barrett", bpm=75)
    blocks = [
        {"pattern_id": "intro-count-2bar", "bars": 2, "intensity": 0.6, "ghost_notes": False},
        {"pattern_id": "one-drop-basic", "bars": 8, "intensity": 0.8, "ghost_notes": True},
        {"pattern_id": "fill-1bar-simple", "bars": 1, "intensity": 0.9},
        {"pattern_id": "one-drop-ghost", "bars": 8, "intensity": 1.0},
        {"pattern_id": "outro-hit", "bars": 1, "intensity": 1.0},
    ]
    path = gen.create_midi_file(blocks, f"{output_dir}/test_song.mid", separate_tracks=True)
    print(f"   Generado: {path}")

    # Probar estructura de cancion
    print("\n5. Generando cancion completa con estructura...")
    gen = MidiGenerator("santa-davis", bpm=74)
    path = gen.generate_song_structure(
        f"{output_dir}/test_full_song.mid",
        intro_bars=2,
        verse_bars=8,
        chorus_bars=8,
        sections=2
    )
    print(f"   Generado: {path}")

    print("\n" + "=" * 60)
    print("TODOS LOS TESTS PASARON")
    print("=" * 60)
    print(f"\nArchivos generados en '{output_dir}/':")
    print("  - test_carlton.mid (one-drop, 72 BPM)")
    print("  - test_sly.mid (steppers, 80 BPM)")
    print("  - test_lloyd.mid (ska, 120 BPM)")
    print("  - test_song.mid (cancion con intro/outro)")
    print("  - test_full_song.mid (estructura completa)")
    print("\nAbrelos en Cubase o un reproductor MIDI para escuchar!")
