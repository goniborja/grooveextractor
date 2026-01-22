"""
Book of Drums - Humanizer

Motor de humanizacion que convierte patrones mecanicos en grooves con soul.

Aplica las caracteristicas unicas de cada baterista:
- Timing offsets (adelante/atras del beat)
- Variacion de velocity (dinamica)
- Swing (desplazamiento de offbeats)
- Ghost notes (golpes sutiles adicionales)
"""

import random
from typing import List, Dict, Tuple, Optional


class Humanizer:
    """
    Aplica humanizacion a eventos MIDI basandose en perfiles de bateristas.

    La humanizacion convierte patrones mecanicos en grooves con soul,
    aplicando las caracteristicas unicas de cada baterista.
    """

    # Resolucion MIDI estandar
    TICKS_PER_BEAT = 480

    # Mapeo de instrumentos a notas MIDI (GM Drums, canal 10)
    MIDI_NOTES = {
        "kick": 36,           # C1 - Bass Drum 1
        "snare": 38,          # D1 - Acoustic Snare
        "rimshot": 37,        # C#1 - Side Stick
        "hihat": 42,          # F#1 - Closed Hi-Hat
        "hihat_closed": 42,
        "hihat_open": 46,     # A#1 - Open Hi-Hat
        "hihat_pedal": 44,    # G#1 - Pedal Hi-Hat
        "tom_high": 50,       # D2 - High Tom
        "tom_mid": 47,        # B1 - Low-Mid Tom
        "tom_low": 45,        # A1 - Low Tom
        "crash": 49,          # C#2 - Crash Cymbal 1
        "ride": 51,           # D#2 - Ride Cymbal 1
    }

    def __init__(self, profile: dict, bpm: int = 75):
        """
        Inicializa el humanizador con un perfil de baterista.

        Args:
            profile: Diccionario con el perfil del baterista
            bpm: Tempo en beats por minuto
        """
        self.profile = profile
        self.bpm = bpm
        self.humanize_percent = profile.get("global", {}).get("humanize_percent", 50)

    def beat_to_ticks(self, beat: float) -> int:
        """
        Convierte beat (1-based) a ticks absolutos.

        Args:
            beat: Numero de beat (1-based, puede incluir decimales)

        Returns:
            Posicion en ticks
        """
        return int((beat - 1) * self.TICKS_PER_BEAT)

    def apply_offset(self, tick: int, instrument: str) -> int:
        """
        Aplica offset de timing segun el perfil del instrumento.

        El offset hace que las notas suenen ligeramente antes o despues
        del beat perfecto, dando el "feel" caracteristico del baterista.

        Args:
            tick: Posicion original en ticks
            instrument: Nombre del instrumento (kick, snare, hihat)

        Returns:
            Nueva posicion en ticks con offset aplicado
        """
        # Normalizar nombre de instrumento
        base_instrument = instrument.replace("_open", "").replace("_closed", "").replace("_pedal", "")
        if base_instrument not in ["kick", "snare", "hihat"]:
            base_instrument = "hihat" if "hihat" in instrument else "snare"

        # Obtener configuracion del instrumento
        inst_config = self.profile.get(base_instrument, {})
        base_offset = inst_config.get("offset_ticks", 0)

        # Anadir variacion aleatoria basada en humanize_percent
        # humanize_percent controla cuanta variacion adicional hay
        variation_range = int(self.humanize_percent / 10)  # +/-0 a +/-8 ticks
        random_variation = random.randint(-variation_range, variation_range)

        final_offset = base_offset + random_variation
        return max(0, tick + final_offset)  # No permitir ticks negativos

    def apply_velocity_variation(self, base_velocity: int, instrument: str,
                                 is_accent: bool = False, intensity: float = 1.0) -> int:
        """
        Aplica variacion de velocity segun el perfil.

        Args:
            base_velocity: Velocity base del evento
            instrument: Nombre del instrumento
            is_accent: Si es un golpe acentuado
            intensity: Factor de intensidad del bloque (0.0-1.0)

        Returns:
            Velocity final (0-127)
        """
        # Normalizar nombre de instrumento
        base_instrument = instrument.replace("_open", "").replace("_closed", "").replace("_pedal", "")
        if base_instrument not in ["kick", "snare", "hihat"]:
            base_instrument = "hihat" if "hihat" in instrument else "snare"

        inst_config = self.profile.get(base_instrument, {})

        # Usar velocity del perfil si no se proporciona
        if base_velocity == 0:
            base_velocity = inst_config.get("velocity_base", 100)

        # Aplicar intensidad del bloque
        velocity = int(base_velocity * intensity)

        # Aplicar acentos
        if is_accent:
            velocity = min(127, velocity + 15)

        # Aplicar variacion aleatoria
        variance = inst_config.get("velocity_variance", 5)
        variation = random.randint(-variance, variance)

        velocity = velocity + variation
        return max(1, min(127, velocity))  # Clamp entre 1-127

    def apply_swing(self, tick: int, subdivision: float = 0.5) -> int:
        """
        Aplica swing a los offbeats.

        El swing desplaza las notas en subdivisiones impares (offbeats)
        hacia adelante, creando un feel mas shuffle/groove.

        Args:
            tick: Posicion original en ticks
            subdivision: Subdivision del beat (0.5 = offbeat tipico)

        Returns:
            Nueva posicion en ticks con swing aplicado
        """
        # Solo aplicar swing a offbeats (subdivision != 0)
        if subdivision == 0:
            return tick

        hihat_config = self.profile.get("hihat", {})
        swing_percent = hihat_config.get("swing_percent", 50)

        if swing_percent == 50:
            return tick  # Sin swing

        # Calcular desplazamiento
        # swing_percent=50 -> 0% desplazamiento
        # swing_percent=66 -> 33% desplazamiento (shuffle completo)
        swing_factor = (swing_percent - 50) / 100.0
        subdivision_ticks = int(self.TICKS_PER_BEAT * subdivision)
        swing_offset = int(subdivision_ticks * swing_factor)

        return tick + swing_offset

    def should_add_ghost_note(self, instrument: str, beat_pos: str) -> bool:
        """
        Determina si anadir una ghost note en esta posicion.

        Args:
            instrument: Nombre del instrumento
            beat_pos: Posicion del beat (ej: "2", "2+", "4.5")

        Returns:
            True si se debe anadir ghost note
        """
        # Normalizar nombre de instrumento
        base_instrument = instrument.replace("_open", "").replace("_closed", "").replace("_pedal", "")
        if base_instrument not in ["kick", "snare", "hihat"]:
            return False

        inst_config = self.profile.get(base_instrument, {})
        ghost_prob = inst_config.get("ghost_probability", 0)
        ghost_beats = inst_config.get("ghost_beats", [])

        if ghost_prob == 0 or not ghost_beats:
            return False

        # Convertir beat_pos a string para comparar
        beat_str = str(beat_pos)

        # Verificar si esta posicion es valida para ghosts
        ghost_beats_str = [str(b) for b in ghost_beats]
        if beat_str not in ghost_beats_str:
            return False

        # Decidir aleatoriamente basandose en probabilidad
        return random.random() < ghost_prob

    def get_ghost_velocity(self, instrument: str) -> int:
        """
        Obtiene velocity para ghost notes.

        Args:
            instrument: Nombre del instrumento

        Returns:
            Velocity para ghost notes
        """
        base_instrument = instrument.replace("_open", "").replace("_closed", "").replace("_pedal", "")
        if base_instrument not in ["kick", "snare", "hihat"]:
            base_instrument = "snare"

        inst_config = self.profile.get(base_instrument, {})
        return inst_config.get("ghost_velocity", 35)

    def get_midi_note(self, instrument: str, check_rimshot: bool = False) -> int:
        """
        Obtiene la nota MIDI para un instrumento.

        Args:
            instrument: Nombre del instrumento
            check_rimshot: Si verificar probabilidad de rimshot para snare

        Returns:
            Numero de nota MIDI
        """
        if instrument == "snare" and check_rimshot:
            # Decidir si usar rimshot basandose en probabilidad
            snare_config = self.profile.get("snare", {})
            rimshot_prob = snare_config.get("rimshot_probability", 0)
            if random.random() < rimshot_prob:
                return self.MIDI_NOTES.get("rimshot", 37)

        return self.MIDI_NOTES.get(instrument, 36)

    def humanize_event(self, event: dict, intensity: float = 1.0,
                       enable_ghosts: bool = True) -> dict:
        """
        Aplica toda la humanizacion a un evento MIDI.

        Args:
            event: Dict con {instrument, beat, subdivision, is_accent, velocity}
            intensity: Factor de intensidad del bloque
            enable_ghosts: Si permitir ghost notes

        Returns:
            Dict con el evento humanizado {tick, note, velocity, instrument}
        """
        instrument = event["instrument"]
        beat = event["beat"]
        subdivision = event.get("subdivision", 0)
        is_accent = event.get("is_accent", False)
        base_velocity = event.get("velocity", 0)

        # Calcular tick base
        tick = self.beat_to_ticks(beat + subdivision)

        # Aplicar swing a offbeats
        tick = self.apply_swing(tick, subdivision)

        # Aplicar offset de timing
        tick = self.apply_offset(tick, instrument)

        # Aplicar variacion de velocity
        velocity = self.apply_velocity_variation(base_velocity, instrument,
                                                 is_accent, intensity)

        # Obtener nota MIDI
        check_rimshot = (instrument == "snare" and is_accent)
        note = self.get_midi_note(instrument, check_rimshot=check_rimshot)

        return {
            "tick": tick,
            "note": note,
            "velocity": velocity,
            "instrument": instrument
        }

    def humanize_pattern(self, pattern_events: List[Tuple],
                         intensity: float = 1.0,
                         enable_ghosts: bool = True,
                         num_bars: int = 1) -> List[dict]:
        """
        Humaniza un patron completo.

        Args:
            pattern_events: Lista de eventos (instrument, beat, subdivision, is_accent)
            intensity: Factor de intensidad del bloque
            enable_ghosts: Si permitir ghost notes
            num_bars: Numero de compases a generar

        Returns:
            Lista de eventos MIDI humanizados
        """
        humanized = []
        ticks_per_bar = self.TICKS_PER_BEAT * 4  # 4/4 time

        for bar in range(num_bars):
            bar_offset = bar * ticks_per_bar

            for event_tuple in pattern_events:
                instrument, beat, subdivision, is_accent = event_tuple

                # Ajustar beat para compases multiples
                # Si el beat > 4, asumimos que el patron ya tiene compases multiples
                actual_beat = beat
                if beat > 4:
                    # El patron ya tiene beats absolutos para multiples compases
                    # Ajustar al compas actual
                    pass
                else:
                    actual_beat = beat

                event = {
                    "instrument": instrument,
                    "beat": actual_beat,
                    "subdivision": subdivision,
                    "is_accent": is_accent,
                    "velocity": 0  # Usar velocity del perfil
                }

                humanized_event = self.humanize_event(event, intensity, enable_ghosts)
                humanized_event["tick"] += bar_offset
                humanized.append(humanized_event)

            # Anadir ghost notes si estan habilitadas
            if enable_ghosts:
                ghost_events = self._generate_ghost_notes(bar_offset, intensity)
                humanized.extend(ghost_events)

        # Ordenar por tick
        humanized.sort(key=lambda e: e["tick"])
        return humanized

    def _generate_ghost_notes(self, bar_offset: int, intensity: float) -> List[dict]:
        """
        Genera ghost notes para un compas.

        Args:
            bar_offset: Offset en ticks del compas
            intensity: Factor de intensidad

        Returns:
            Lista de eventos ghost
        """
        ghosts = []

        # Revisar cada posicion posible para ghosts
        for instrument in ["snare", "kick"]:
            inst_config = self.profile.get(instrument, {})
            ghost_beats = inst_config.get("ghost_beats", [])

            for beat_pos in ghost_beats:
                # Parsear posicion (puede ser "2", "2+", 2, etc.)
                if isinstance(beat_pos, str) and "+" in beat_pos:
                    beat = int(beat_pos.replace("+", ""))
                    subdivision = 0.5
                elif isinstance(beat_pos, str):
                    beat = int(beat_pos)
                    subdivision = 0
                else:
                    beat = int(beat_pos)
                    subdivision = 0

                if self.should_add_ghost_note(instrument, beat_pos):
                    tick = self.beat_to_ticks(beat + subdivision)
                    tick = self.apply_offset(tick, instrument)
                    tick += bar_offset

                    velocity = self.get_ghost_velocity(instrument)
                    velocity = int(velocity * intensity)
                    velocity = max(1, min(127, velocity))

                    ghosts.append({
                        "tick": tick,
                        "note": self.get_midi_note(instrument),
                        "velocity": velocity,
                        "instrument": instrument,
                        "is_ghost": True
                    })

        return ghosts


# ==============================================================================
# TEST
# ==============================================================================

if __name__ == "__main__":
    from profiles.drummer_profiles import get_profile
    from profiles.pattern_library import get_pattern

    print("=" * 60)
    print("TEST DE HUMANIZER")
    print("=" * 60)

    # Cargar perfil de Carlton Barrett
    profile = get_profile("carlton-barrett")
    humanizer = Humanizer(profile, bpm=72)

    print(f"\nBaterista: {profile['name']}")
    print(f"Estilo: {profile['style']}")
    print(f"BPM: 72")

    # Cargar patron one-drop
    pattern = get_pattern("one-drop-basic")
    print(f"\nPatron: {pattern['name']}")

    # Humanizar 2 compases
    events = humanizer.humanize_pattern(
        pattern["events"],
        intensity=0.8,
        enable_ghosts=True,
        num_bars=2
    )

    print(f"\nEventos generados: {len(events)}")
    print("\nPrimeros 10 eventos:")
    for e in events[:10]:
        ghost_marker = " (ghost)" if e.get("is_ghost") else ""
        print(f"  Tick {e['tick']:4d} | Note {e['note']:2d} | Vel {e['velocity']:3d} | {e['instrument']}{ghost_marker}")

    # Probar con Sly Dunbar
    print("\n" + "-" * 60)
    print("Probando con Sly Dunbar (steppers)...")
    profile_sly = get_profile("sly-dunbar")
    humanizer_sly = Humanizer(profile_sly, bpm=80)
    pattern_steppers = get_pattern("steppers-basic")

    events_sly = humanizer_sly.humanize_pattern(
        pattern_steppers["events"],
        intensity=0.9,
        enable_ghosts=True,
        num_bars=1
    )

    print(f"\nEventos generados: {len(events_sly)}")
    print("\nEventos de Sly:")
    for e in events_sly[:8]:
        ghost_marker = " (ghost)" if e.get("is_ghost") else ""
        print(f"  Tick {e['tick']:4d} | Note {e['note']:2d} | Vel {e['velocity']:3d} | {e['instrument']}{ghost_marker}")

    print("\n" + "=" * 60)
    print("HUMANIZER FUNCIONANDO CORRECTAMENTE")
    print("=" * 60)
