"""Detector de onsets optimizado por instrumento."""
import numpy as np
import librosa
from typing import List
from ..models import OnsetData, OnsetList


class OnsetDetector:
    """Detecta onsets con parametros optimizados por instrumento."""

    def __init__(self, sr: int = 22050):
        self.sr = sr

        # Parametros optimizados por instrumento
        self.params = {
            'kick': {
                'hop_length': 512,
                'fmin': 20,
                'fmax': 150,
                'delta': 0.07,
                'wait': 30,  # frames entre onsets
            },
            'snare': {
                'hop_length': 256,
                'fmin': 150,
                'fmax': 5000,
                'delta': 0.05,
                'wait': 20,
            },
            'hihat': {
                'hop_length': 256,
                'fmin': 5000,
                'fmax': 16000,
                'delta': 0.03,
                'wait': 10,  # hi-hats pueden estar muy juntos
            }
        }

    def detect(self, y: np.ndarray, instrument: str = 'hihat') -> OnsetList:
        """
        Detecta onsets para un instrumento especifico.

        Args:
            y: Audio array (mono)
            instrument: 'kick', 'snare', o 'hihat'

        Returns:
            OnsetList con los onsets detectados
        """
        params = self.params.get(instrument, self.params['hihat'])

        # Filtrar frecuencias relevantes
        y_filtered = self._bandpass_filter(y, params['fmin'], params['fmax'])

        # Detectar onsets
        onset_env = librosa.onset.onset_strength(
            y=y_filtered,
            sr=self.sr,
            hop_length=params['hop_length']
        )

        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=self.sr,
            hop_length=params['hop_length'],
            delta=params['delta'],
            wait=params['wait']
        )

        # Convertir frames a tiempos
        onset_times = librosa.frames_to_time(
            onset_frames,
            sr=self.sr,
            hop_length=params['hop_length']
        )

        # Extraer velocities (aproximacion basada en amplitud)
        velocities = self._estimate_velocities(y_filtered, onset_times, params['hop_length'])

        # Crear OnsetList
        onsets = [
            OnsetData(time=float(t), velocity=v, instrument=instrument)
            for t, v in zip(onset_times, velocities)
        ]

        return OnsetList(onsets=onsets, instrument=instrument)

    def detect_kick(self, y: np.ndarray) -> OnsetList:
        """Detecta onsets de bombo."""
        return self.detect(y, 'kick')

    def detect_snare(self, y: np.ndarray) -> OnsetList:
        """Detecta onsets de caja."""
        return self.detect(y, 'snare')

    def detect_hihat(self, y: np.ndarray) -> OnsetList:
        """Detecta onsets de hi-hat."""
        return self.detect(y, 'hihat')

    def _bandpass_filter(self, y: np.ndarray, fmin: float, fmax: float) -> np.ndarray:
        """Aplica filtro paso banda."""
        # Usar STFT para filtrar
        D = librosa.stft(y)
        freqs = librosa.fft_frequencies(sr=self.sr)

        # Crear mascara de frecuencias
        mask = (freqs >= fmin) & (freqs <= fmax)
        D_filtered = D * mask[:, np.newaxis]

        return librosa.istft(D_filtered)

    def _estimate_velocities(self, y: np.ndarray, onset_times: np.ndarray,
                             hop_length: int, window_ms: float = 10.0) -> List[int]:
        """Estima velocity MIDI (0-127) basado en amplitud RMS."""
        velocities = []
        window_samples = int(window_ms * self.sr / 1000)

        for t in onset_times:
            start = int(t * self.sr)
            end = min(start + window_samples, len(y))

            if start < len(y):
                rms = np.sqrt(np.mean(y[start:end] ** 2))
                # Normalizar a 0-127 (asumiendo rms max ~0.5)
                vel = int(min(127, max(1, rms * 254)))
            else:
                vel = 100

            velocities.append(vel)

        return velocities
