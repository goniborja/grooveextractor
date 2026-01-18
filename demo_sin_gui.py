#!/usr/bin/env python3
"""
DEMO DE GROOVE EXTRACTOR - Sin GUI
===================================
Script de demostración que muestra el análisis DSP sin interfaz gráfica.
"""

import numpy as np
from groove_analyzer import GrooveAnalyzer
import json

def create_test_audio():
    """Crea un archivo de audio de prueba con pulsos simulados."""
    print("📁 Creando archivo de audio de prueba...")

    # Parámetros
    sr = 44100
    duration = 4.0  # 4 segundos
    tempo_bpm = 120

    # Crear audio con pulsos simulados (kick drums cada beat)
    t = np.linspace(0, duration, int(sr * duration))
    audio = np.zeros_like(t)

    # Añadir pulsos cada 0.5 segundos (120 BPM)
    beat_interval = 60.0 / tempo_bpm
    for beat in range(int(duration / beat_interval)):
        beat_time = beat * beat_interval
        beat_sample = int(beat_time * sr)

        # Crear un pulso (kick drum sintético)
        pulse_duration = 0.05  # 50ms
        pulse_samples = int(pulse_duration * sr)

        if beat_sample + pulse_samples < len(audio):
            # Señal de kick: oscilador descendente
            freq_start = 150
            freq_end = 50
            freq_sweep = np.linspace(freq_start, freq_end, pulse_samples)
            phase = np.cumsum(2 * np.pi * freq_sweep / sr)

            # Envelope
            envelope = np.exp(-np.linspace(0, 10, pulse_samples))

            # Aplicar variación de velocidad
            amplitude = 0.5 + np.random.uniform(-0.2, 0.3)

            pulse = amplitude * np.sin(phase) * envelope
            audio[beat_sample:beat_sample + pulse_samples] = pulse

        # Añadir hihat en offbeats
        if beat % 2 == 1:
            hihat_time = beat_time + 0.25
            hihat_sample = int(hihat_time * sr)
            hihat_duration = 0.02
            hihat_samples = int(hihat_duration * sr)

            if hihat_sample + hihat_samples < len(audio):
                # Hihat: ruido filtrado
                noise = np.random.randn(hihat_samples)
                hihat_envelope = np.exp(-np.linspace(0, 20, hihat_samples))
                hihat = 0.2 * noise * hihat_envelope
                audio[hihat_sample:hihat_sample + hihat_samples] += hihat

    # Guardar archivo
    import soundfile as sf
    test_file = "/tmp/test_groove.wav"
    sf.write(test_file, audio, sr)

    print(f"✅ Audio de prueba creado: {test_file}")
    print(f"   - Duración: {duration}s")
    print(f"   - Sample rate: {sr} Hz")
    print(f"   - Tempo: {tempo_bpm} BPM")

    return test_file, tempo_bpm


def run_demo():
    """Ejecuta una demostración completa del análisis."""

    print("="*70)
    print("🥁 GROOVE EXTRACTOR - DEMOSTRACIÓN DSP")
    print("="*70)
    print()

    # 1. Crear audio de prueba
    audio_file, tempo = create_test_audio()
    print()

    # 2. Inicializar analizador
    print("🔧 Inicializando analizador...")
    analyzer = GrooveAnalyzer()
    print("✅ Analizador inicializado")
    print()

    # 3. Cargar audio
    print("📂 Cargando audio...")
    analyzer.load_audio(audio_file)
    print(f"✅ Audio cargado: {analyzer.metadata['audio_file']}")
    print(f"   - Sample rate: {analyzer.metadata['sample_rate']} Hz")
    print(f"   - Duración: {analyzer.metadata['duration_seconds']:.2f}s")
    print()

    # 4. Detectar onsets
    print("🎯 Detectando onsets...")
    analyzer.detect_onsets(method='librosa')
    print(f"✅ Onsets detectados: {len(analyzer.onsets)}")
    print(f"   - Primeros 5 tiempos: {[f'{t:.3f}s' for t in analyzer.onsets[:5]]}")
    print()

    # 5. Analizar dinámica
    print("📊 Analizando dinámica...")
    analyzer.analyze_dynamics()
    print("✅ Dinámica analizada")
    print()

    # 6. Calcular timing deviations
    print("⏱️  Calculando micro-timing...")
    analyzer.calculate_timing_deviations(tempo)
    print("✅ Micro-timing calculado")
    print()

    # 7. Obtener resultados
    print("📈 Generando resultados...")
    results = analyzer.get_results()
    print("✅ Análisis completado")
    print()

    # 8. Mostrar resultados
    print("="*70)
    print("📋 RESULTADOS DEL ANÁLISIS")
    print("="*70)
    print()

    print("METADATA:")
    for key, value in results['metadata'].items():
        print(f"  - {key}: {value}")
    print()

    print(f"ONSETS DETECTADOS: {len(results['groove_data'])}")
    print()

    print("PRIMEROS 10 ONSETS:")
    print(f"{'#':<4} {'Tiempo':<10} {'Beat Pos':<10} {'Tipo':<8} {'Vel':<5} {'dB':<8} {'Dev (ms)':<10}")
    print("-"*70)

    for i, onset in enumerate(results['groove_data'][:10], 1):
        print(f"{i:<4} "
              f"{onset['onset_time']:<10.3f} "
              f"{onset['beat_position']:<10.2f} "
              f"{onset['drum_type']:<8} "
              f"{onset['velocity']:<5} "
              f"{onset['amplitude_db']:<8.2f} "
              f"{onset['timing_deviation_ms']:<10.2f}")

    print()
    print("ESTADÍSTICAS DE HUMANIZACIÓN:")
    for key, value in results['humanization_stats'].items():
        print(f"  - {key}: {value:.3f}")
    print()

    # 9. Exportar JSON
    output_json = "/tmp/groove_analysis_demo.json"
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)

    print("="*70)
    print(f"✅ Resultados exportados a: {output_json}")
    print("="*70)
    print()

    # 10. Mostrar interpretación
    print("🔍 INTERPRETACIÓN DE RESULTADOS:")
    print()

    stats = results['humanization_stats']

    # Timing
    avg_dev = abs(stats['avg_timing_deviation_ms'])
    std_dev = stats['std_timing_deviation_ms']

    print("TIMING:")
    if std_dev < 5:
        timing_quality = "muy preciso (casi cuantizado)"
    elif std_dev < 15:
        timing_quality = "natural y humano"
    else:
        timing_quality = "suelto/irregular"

    print(f"  - Consistencia: {timing_quality}")
    print(f"  - Desviación promedio: {avg_dev:.2f}ms")
    print(f"  - Desviación estándar: {std_dev:.2f}ms")

    if avg_dev > 5:
        if stats['avg_timing_deviation_ms'] > 0:
            print(f"  - Tendencia: Ligeramente adelantado (rushing)")
        else:
            print(f"  - Tendencia: Ligeramente atrasado (dragging)")
    print()

    # Dinámica
    vel_var = stats['avg_velocity_variation']

    print("DINÁMICA:")
    if vel_var < 0.1:
        dynamic_quality = "uniforme (poco expresiva)"
    elif vel_var < 0.3:
        dynamic_quality = "natural y variada"
    else:
        dynamic_quality = "muy expresiva"

    print(f"  - Variación: {dynamic_quality}")
    print(f"  - Índice de variación: {vel_var:.3f}")
    print()

    # Swing
    swing = stats['swing_factor']

    print("GROOVE:")
    if swing < 0.1:
        groove_type = "Straight (sin swing)"
    elif swing < 0.3:
        groove_type = "Swing ligero"
    else:
        groove_type = "Swing pronunciado"

    print(f"  - Tipo: {groove_type}")
    print(f"  - Factor de swing: {swing:.3f}")
    print()

    print("="*70)
    print("🎵 Demostración completada exitosamente!")
    print("="*70)


if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        print(f"\n❌ Error durante la demostración: {e}")
        import traceback
        traceback.print_exc()
