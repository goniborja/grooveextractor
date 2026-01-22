"""
Tests unitarios para Book of Drums.

Ejecutar con: python -m pytest tests/test_book_of_drums.py -v
O simplemente: python tests/test_book_of_drums.py
"""

import sys
import os
from pathlib import Path

# Agregar directorio raiz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
import tempfile
import shutil


class TestDrummerProfiles(unittest.TestCase):
    """Tests para el modulo de perfiles de bateristas."""

    def test_list_drummers(self):
        """Verifica que hay bateristas disponibles."""
        from profiles import list_drummers
        drummers = list_drummers()
        self.assertIsInstance(drummers, list)
        self.assertGreater(len(drummers), 0)
        self.assertIn("carlton-barrett", drummers)
        self.assertIn("sly-dunbar", drummers)

    def test_get_profile(self):
        """Verifica que se puede obtener un perfil."""
        from profiles import get_profile
        profile = get_profile("carlton-barrett")
        self.assertIsInstance(profile, dict)
        self.assertEqual(profile["name"], "Carlton Barrett")
        self.assertEqual(profile["style"], "one-drop")
        self.assertIn("kick", profile)
        self.assertIn("snare", profile)
        self.assertIn("hihat", profile)

    def test_get_profile_invalid(self):
        """Verifica que un perfil invalido lanza error."""
        from profiles import get_profile
        with self.assertRaises(ValueError):
            get_profile("baterista-inexistente")

    def test_get_available_styles(self):
        """Verifica los estilos disponibles."""
        from profiles import get_available_styles
        styles = get_available_styles()
        self.assertIsInstance(styles, list)
        self.assertIn("one-drop", styles)
        self.assertIn("steppers", styles)
        self.assertIn("ska", styles)

    def test_get_drummers_by_style(self):
        """Verifica filtrado por estilo."""
        from profiles import get_drummers_by_style
        one_drop = get_drummers_by_style("one-drop")
        self.assertIn("carlton-barrett", one_drop)

    def test_profile_structure(self):
        """Verifica la estructura completa de un perfil."""
        from profiles import get_profile
        profile = get_profile("sly-dunbar")

        # Campos requeridos
        required_fields = ["name", "slug", "style", "kick", "snare", "hihat", "global"]
        for field in required_fields:
            self.assertIn(field, profile, f"Falta campo: {field}")

        # Estructura de kick
        kick = profile["kick"]
        self.assertIn("beats", kick)
        self.assertIn("offset_ticks", kick)
        self.assertIn("velocity_base", kick)

        # Estructura de hihat
        hihat = profile["hihat"]
        self.assertIn("pattern", hihat)
        self.assertIn("swing_percent", hihat)


class TestPatternLibrary(unittest.TestCase):
    """Tests para la biblioteca de patrones."""

    def test_list_patterns(self):
        """Verifica que hay patrones disponibles."""
        from profiles import list_patterns
        patterns = list_patterns()
        self.assertIsInstance(patterns, list)
        self.assertGreater(len(patterns), 10)  # Al menos 10 patrones

    def test_get_pattern(self):
        """Verifica que se puede obtener un patron."""
        from profiles import get_pattern
        pattern = get_pattern("one-drop-basic")
        self.assertIsInstance(pattern, dict)
        self.assertEqual(pattern["style"], "one-drop")
        self.assertEqual(pattern["type"], "rhythm")
        self.assertIn("events", pattern)
        self.assertGreater(len(pattern["events"]), 0)

    def test_get_pattern_invalid(self):
        """Verifica que un patron invalido lanza error."""
        from profiles import get_pattern
        with self.assertRaises(ValueError):
            get_pattern("patron-inexistente")

    def test_get_patterns_by_style(self):
        """Verifica filtrado por estilo."""
        from profiles import get_patterns_by_style
        ska_patterns = get_patterns_by_style("ska")
        self.assertGreater(len(ska_patterns), 0)
        self.assertIn("ska-basic", ska_patterns)

    def test_get_patterns_by_type(self):
        """Verifica filtrado por tipo."""
        from profiles import get_patterns_by_type
        fills = get_patterns_by_type("fill")
        self.assertGreater(len(fills), 0)
        self.assertIn("fill-1bar-simple", fills)

    def test_get_patterns_for_drummer(self):
        """Verifica patrones compatibles con baterista."""
        from profiles import get_patterns_for_drummer
        patterns = get_patterns_for_drummer("carlton-barrett")
        self.assertGreater(len(patterns), 0)
        self.assertIn("one-drop-basic", patterns)

    def test_pattern_event_structure(self):
        """Verifica la estructura de eventos de patron."""
        from profiles import get_pattern
        pattern = get_pattern("steppers-basic")
        events = pattern["events"]

        for event in events:
            self.assertEqual(len(event), 4)  # (instrumento, beat, subdivision, is_accent)
            instrument, beat, subdivision, is_accent = event
            self.assertIsInstance(instrument, str)
            self.assertIsInstance(beat, int)
            self.assertIn(subdivision, [0, 0.5])
            self.assertIsInstance(is_accent, bool)


class TestHumanizer(unittest.TestCase):
    """Tests para el motor de humanizacion."""

    def setUp(self):
        """Preparar datos de test."""
        from profiles import get_profile
        from generators import Humanizer
        self.profile = get_profile("carlton-barrett")
        self.humanizer = Humanizer(self.profile, bpm=72)

    def test_beat_to_ticks(self):
        """Verifica conversion de beats a ticks."""
        # Beat 1 = tick 0
        self.assertEqual(self.humanizer.beat_to_ticks(1), 0)
        # Beat 2 = tick 480
        self.assertEqual(self.humanizer.beat_to_ticks(2), 480)
        # Beat 1.5 (offbeat) = tick 240
        self.assertEqual(self.humanizer.beat_to_ticks(1.5), 240)

    def test_apply_velocity_variation(self):
        """Verifica variacion de velocity."""
        velocities = []
        for _ in range(100):
            vel = self.humanizer.apply_velocity_variation(100, "snare")
            velocities.append(vel)
            # Velocity debe estar en rango valido
            self.assertGreaterEqual(vel, 1)
            self.assertLessEqual(vel, 127)

        # Debe haber variacion
        self.assertGreater(max(velocities) - min(velocities), 0)

    def test_apply_swing(self):
        """Verifica aplicacion de swing."""
        # Sin subdivision = sin cambio
        tick = self.humanizer.apply_swing(0, subdivision=0)
        self.assertEqual(tick, 0)

        # Con subdivision y swing > 50 = tick aumenta
        tick_swing = self.humanizer.apply_swing(240, subdivision=0.5)
        # Carlton tiene swing_percent=62, debe aumentar
        self.assertGreater(tick_swing, 240)

    def test_humanize_pattern(self):
        """Verifica humanizacion de patron completo."""
        from profiles import get_pattern
        pattern = get_pattern("one-drop-basic")

        events = self.humanizer.humanize_pattern(
            pattern["events"],
            intensity=0.8,
            enable_ghosts=True,
            num_bars=2
        )

        self.assertIsInstance(events, list)
        self.assertGreater(len(events), 0)

        # Verificar estructura de eventos
        for event in events:
            self.assertIn("tick", event)
            self.assertIn("note", event)
            self.assertIn("velocity", event)
            self.assertIn("instrument", event)

    def test_midi_notes_mapping(self):
        """Verifica mapeo de instrumentos a notas MIDI."""
        from generators.humanizer import Humanizer
        self.assertEqual(Humanizer.MIDI_NOTES["kick"], 36)
        self.assertEqual(Humanizer.MIDI_NOTES["snare"], 38)
        self.assertEqual(Humanizer.MIDI_NOTES["hihat"], 42)
        self.assertEqual(Humanizer.MIDI_NOTES["crash"], 49)


class TestMidiGenerator(unittest.TestCase):
    """Tests para el generador MIDI."""

    def setUp(self):
        """Preparar directorio temporal."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Limpiar directorio temporal."""
        shutil.rmtree(self.temp_dir)

    def test_create_generator(self):
        """Verifica creacion del generador."""
        from generators import MidiGenerator
        gen = MidiGenerator("carlton-barrett", bpm=72)
        self.assertEqual(gen.bpm, 72)
        self.assertEqual(gen.drummer_slug, "carlton-barrett")

    def test_generate_quick_test(self):
        """Verifica generacion de test rapido."""
        from generators import MidiGenerator
        gen = MidiGenerator("sly-dunbar", bpm=80)

        output_path = os.path.join(self.temp_dir, "test.mid")
        result = gen.generate_quick_test(output_path)

        self.assertEqual(result, output_path)
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)

    def test_generate_song_structure(self):
        """Verifica generacion de estructura de cancion."""
        from generators import MidiGenerator
        gen = MidiGenerator("lloyd-knibb", bpm=120)

        output_path = os.path.join(self.temp_dir, "song.mid")
        result = gen.generate_song_structure(
            output_path,
            intro_bars=2,
            verse_bars=4,
            chorus_bars=4,
            sections=1
        )

        self.assertTrue(os.path.exists(output_path))

    def test_blocks_to_events(self):
        """Verifica conversion de bloques a eventos."""
        from generators import MidiGenerator
        gen = MidiGenerator("carlton-barrett", bpm=72)

        blocks = [
            {"pattern_id": "one-drop-basic", "bars": 2, "intensity": 0.8}
        ]

        events = gen.blocks_to_events(blocks)
        self.assertIsInstance(events, list)
        self.assertGreater(len(events), 0)

    def test_add_auto_fills(self):
        """Verifica insercion automatica de fills."""
        from generators import MidiGenerator
        gen = MidiGenerator("carlton-barrett", bpm=72)

        blocks = [{"pattern_id": "one-drop-basic", "bars": 12}]
        new_blocks = gen.add_auto_fills(blocks, fill_every=4)

        # Deberia dividir 12 compases en segmentos con fills
        self.assertGreater(len(new_blocks), 1)

        # Contar fills
        fills = [b for b in new_blocks if "fill" in b["pattern_id"]]
        self.assertGreater(len(fills), 0)

    def test_generate_with_auto_fills(self):
        """Verifica generacion con auto-fills."""
        from generators import MidiGenerator
        gen = MidiGenerator("santa-davis", bpm=74)

        output_path = os.path.join(self.temp_dir, "auto_fills.mid")
        result = gen.generate_with_auto_fills(
            "one-drop-basic",
            total_bars=16,
            output_path=output_path,
            fill_every=4
        )

        self.assertTrue(os.path.exists(output_path))

    def test_all_drummers(self):
        """Verifica que se puede generar con todos los bateristas."""
        from generators import MidiGenerator
        from profiles import list_drummers

        for drummer in list_drummers():
            gen = MidiGenerator(drummer, bpm=75)
            output_path = os.path.join(self.temp_dir, f"{drummer}.mid")
            gen.generate_quick_test(output_path)
            self.assertTrue(os.path.exists(output_path))


class TestIntegration(unittest.TestCase):
    """Tests de integracion end-to-end."""

    def setUp(self):
        """Preparar directorio temporal."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Limpiar directorio temporal."""
        shutil.rmtree(self.temp_dir)

    def test_full_workflow(self):
        """Test del flujo completo de generacion."""
        from profiles import get_profile, get_pattern, get_patterns_for_drummer
        from generators import MidiGenerator, Humanizer

        # 1. Seleccionar baterista
        profile = get_profile("carlton-barrett")
        self.assertEqual(profile["style"], "one-drop")

        # 2. Obtener patrones compatibles
        patterns = get_patterns_for_drummer("carlton-barrett")
        self.assertIn("one-drop-basic", patterns)

        # 3. Crear humanizador
        humanizer = Humanizer(profile, bpm=72)

        # 4. Humanizar patron
        pattern = get_pattern("one-drop-basic")
        events = humanizer.humanize_pattern(pattern["events"], num_bars=1)
        self.assertGreater(len(events), 0)

        # 5. Generar MIDI
        gen = MidiGenerator("carlton-barrett", bpm=72)
        output_path = os.path.join(self.temp_dir, "full_test.mid")
        gen.generate_quick_test(output_path)

        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 100)  # Archivo no vacio

    def test_different_styles(self):
        """Verifica generacion con diferentes estilos."""
        from generators import MidiGenerator

        styles_drummers = [
            ("carlton-barrett", "one-drop"),
            ("sly-dunbar", "steppers"),
            ("lloyd-knibb", "ska"),
        ]

        for drummer, expected_style in styles_drummers:
            gen = MidiGenerator(drummer, bpm=75)
            self.assertEqual(gen.profile["style"], expected_style)

            output_path = os.path.join(self.temp_dir, f"{expected_style}.mid")
            gen.generate_quick_test(output_path)
            self.assertTrue(os.path.exists(output_path))


def run_tests():
    """Ejecuta todos los tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestDrummerProfiles))
    suite.addTests(loader.loadTestsFromTestCase(TestPatternLibrary))
    suite.addTests(loader.loadTestsFromTestCase(TestHumanizer))
    suite.addTests(loader.loadTestsFromTestCase(TestMidiGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
