"""
GROOVE ANALYZER - Módulo de Análisis DSP
=========================================
Implementa detección de onsets, análisis de dinámica y micro-timing.
"""

import numpy as np
import librosa
import soundfile as sf
from datetime import datetime
from pathlib import Path


class GrooveAnalyzer:
    """
    Analizador DSP para extracción de características de grooves de batería.

    Funcionalidades:
    - Detección de onsets (librosa + madmom)
    - Análisis de dinámica (amplitude, velocity)
    - Cálculo de micro-timing (desviación del grid)
    - Estimación de humanización
    """

    def __init__(self):
        """Inicializa el analizador."""
        self.audio = None
        self.sr = None
        self.audio_file = None
        self.onsets = None
        self.onset_strengths = None
        self.groove_data = []
        self.metadata = {}

    def load_audio(self, audio_file):
        """
        Carga un archivo de audio.

        Args:
            audio_file (str): Path al archivo de audio WAV
        """
        self.audio_file = audio_file
        self.audio, self.sr = librosa.load(audio_file, sr=None)

        # Guardar metadata
        self.metadata['audio_file'] = Path(audio_file).name
        self.metadata['sample_rate'] = int(self.sr)
        self.metadata['duration_seconds'] = float(len(self.audio) / self.sr)

    def detect_onsets(self, method='librosa'):
        """
        Detecta onsets en el audio usando librosa.

        Args:
            method (str): Método de detección ('librosa' o 'madmom')
        """
        if self.audio is None:
            raise ValueError("Primero debes cargar un archivo de audio")

        if method == 'librosa':
            # Usar librosa para detección de onsets
            # Configuración optimizada para batería
            hop_length = 512
            onset_env = librosa.onset.onset_strength(
                y=self.audio,
                sr=self.sr,
                hop_length=hop_length,
                aggregate=np.median
            )

            # Detectar onsets con backtracking
            onset_frames = librosa.onset.onset_detect(
                onset_envelope=onset_env,
                sr=self.sr,
                hop_length=hop_length,
                backtrack=True,
                pre_max=3,
                post_max=3,
                pre_avg=3,
                post_avg=5,
                delta=0.2,
                wait=10
            )

            # Convertir frames a tiempo
            self.onsets = librosa.frames_to_time(
                onset_frames,
                sr=self.sr,
                hop_length=hop_length
            )

            # Guardar fuerzas de onset
            self.onset_strengths = onset_env[onset_frames]

        elif method == 'madmom':
            try:
                from madmom.features.onsets import RNNOnsetProcessor, OnsetPeakPickingProcessor

                # Usar red neuronal de madmom (más preciso para percusión)
                proc_rnn = RNNOnsetProcessor()
                proc_peak = OnsetPeakPickingProcessor(
                    threshold=0.5,
                    pre_max=0.03,
                    post_max=0.03
                )

                # Procesar
                activations = proc_rnn(self.audio_file)
                self.onsets = proc_peak(activations)
                self.onset_strengths = np.ones(len(self.onsets))  # Placeholder

            except ImportError:
                print("Warning: madmom no disponible, usando librosa")
                return self.detect_onsets(method='librosa')

    def analyze_dynamics(self):
        """
        Analiza la dinámica de cada onset (amplitude, velocity MIDI estimada).
        """
        if self.onsets is None:
            raise ValueError("Primero debes detectar onsets")

        # Ventana para análisis de amplitud (±25ms alrededor del onset)
        window_size = int(0.025 * self.sr)

        for i, onset_time in enumerate(self.onsets):
            onset_sample = int(onset_time * self.sr)

            # Extraer ventana alrededor del onset
            start = max(0, onset_sample - window_size)
            end = min(len(self.audio), onset_sample + window_size)
            window = self.audio[start:end]

            # Calcular RMS (amplitud)
            rms = np.sqrt(np.mean(window**2))

            # Convertir a dB
            amplitude_db = 20 * np.log10(rms + 1e-10)

            # Estimar velocidad MIDI (0-127)
            # Mapear dB a MIDI velocity (típicamente -60dB a -6dB)
            velocity = self._db_to_velocity(amplitude_db)

            # Crear entrada de groove data
            onset_data = {
                'onset_time': float(onset_time),
                'velocity': int(velocity),
                'amplitude_db': float(amplitude_db),
                'onset_strength': float(self.onset_strengths[i]) if i < len(self.onset_strengths) else 1.0
            }

            self.groove_data.append(onset_data)

    def calculate_timing_deviations(self, tempo_bpm):
        """
        Calcula las desviaciones de timing respecto al grid métrico.

        Args:
            tempo_bpm (float): Tempo en beats por minuto
        """
        if not self.groove_data:
            raise ValueError("Primero debes analizar la dinámica")

        # Calcular intervalo de beat en segundos
        beat_interval = 60.0 / tempo_bpm

        # Subdivisión del grid (16th notes = 4 subdivisiones por beat)
        grid_subdivision = 4
        grid_interval = beat_interval / grid_subdivision

        # Guardar tempo en metadata
        self.metadata['tempo_bpm'] = float(tempo_bpm)
        self.metadata['time_signature'] = "4/4"  # Default

        # Calcular desviaciones para cada onset
        for onset_data in self.groove_data:
            onset_time = onset_data['onset_time']

            # Encontrar la posición más cercana en el grid
            grid_position = round(onset_time / grid_interval)
            expected_time = grid_position * grid_interval

            # Calcular desviación en milisegundos
            timing_deviation_ms = (onset_time - expected_time) * 1000

            # Calcular beat position (1.0, 1.25, 1.5, etc.)
            beat_position = (onset_time / beat_interval) % 4 + 1

            # Calcular bar number
            bar_number = int(onset_time / (beat_interval * 4)) + 1

            # Añadir campos
            onset_data['timing_deviation_ms'] = float(timing_deviation_ms)
            onset_data['beat_position'] = float(beat_position)
            onset_data['bar_number'] = int(bar_number)

            # Clasificación básica de instrumento (placeholder - podría mejorarse con ML)
            onset_data['drum_type'] = self._classify_drum_type(onset_data)

            # Variación de velocidad normalizada
            onset_data['velocity_variation'] = self._calculate_velocity_variation(onset_data)

    def _db_to_velocity(self, db):
        """
        Convierte amplitud en dB a velocidad MIDI (0-127).

        Args:
            db (float): Amplitud en dB

        Returns:
            int: Velocidad MIDI (0-127)
        """
        # Mapeo típico: -60dB = 1, -6dB = 127
        min_db = -60
        max_db = -6

        # Clipping
        db = np.clip(db, min_db, max_db)

        # Mapeo lineal
        velocity = ((db - min_db) / (max_db - min_db)) * 127

        return int(np.clip(velocity, 1, 127))

    def _classify_drum_type(self, onset_data):
        """
        Clasificación básica de tipo de instrumento basada en características.

        Args:
            onset_data (dict): Datos del onset

        Returns:
            str: Tipo de instrumento estimado
        """
        # Clasificación simple basada en velocidad y timing
        # En producción, esto debería usar ML o análisis espectral

        velocity = onset_data['velocity']
        beat_pos = onset_data['beat_position'] % 1

        # Heurística simple
        if beat_pos < 0.1 or abs(beat_pos - 0.5) < 0.1:
            # Onsets en beats fuertes
            if velocity > 90:
                return 'kick'
            else:
                return 'snare'
        else:
            # Subdivisiones
            return 'hihat'

    def _calculate_velocity_variation(self, onset_data):
        """
        Calcula la variación de velocidad normalizada.

        Args:
            onset_data (dict): Datos del onset

        Returns:
            float: Variación normalizada (0.0-1.0)
        """
        # Placeholder: en producción calcular respecto a media local
        # Por ahora, usar una función simple basada en la velocidad
        velocity = onset_data['velocity']
        variation = abs(velocity - 85) / 127.0
        return float(np.clip(variation, 0.0, 1.0))

    def get_results(self):
        """
        Obtiene los resultados del análisis en formato JSON-compatible.

        Returns:
            dict: Diccionario con metadata, groove_data y estadísticas
        """
        if not self.groove_data:
            raise ValueError("No hay datos de groove. Ejecuta el análisis primero.")

        # Calcular estadísticas de humanización
        timing_devs = [d['timing_deviation_ms'] for d in self.groove_data]
        velocity_vars = [d['velocity_variation'] for d in self.groove_data]

        humanization_stats = {
            'avg_timing_deviation_ms': float(np.mean(timing_devs)),
            'std_timing_deviation_ms': float(np.std(timing_devs)),
            'avg_velocity_variation': float(np.mean(velocity_vars)),
            'swing_factor': self._calculate_swing_factor()
        }

        # Añadir timestamp a metadata
        self.metadata['analyzed_date'] = datetime.now().isoformat()
        self.metadata['analyzer_version'] = "1.0.0"

        return {
            'metadata': self.metadata,
            'groove_data': self.groove_data,
            'humanization_stats': humanization_stats
        }

    def _calculate_swing_factor(self):
        """
        Calcula el factor de swing del groove.

        Returns:
            float: Factor de swing (0.0 = straight, >0 = swing)
        """
        # Analizar desviaciones en subdivisiones impares vs pares
        # Placeholder: implementación simplificada
        if len(self.groove_data) < 4:
            return 0.0

        # Calcular diferencia promedio entre subdivisiones pares e impares
        even_devs = []
        odd_devs = []

        for onset in self.groove_data:
            beat_pos = onset['beat_position']
            frac = beat_pos % 0.5

            if frac < 0.25:
                even_devs.append(onset['timing_deviation_ms'])
            else:
                odd_devs.append(onset['timing_deviation_ms'])

        if even_devs and odd_devs:
            swing = abs(np.mean(odd_devs) - np.mean(even_devs)) / 100.0
            return float(np.clip(swing, 0.0, 1.0))

        return 0.0
