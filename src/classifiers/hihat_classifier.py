"""Clasificador de hi-hat abierto vs cerrado."""
import numpy as np
import librosa
from typing import List, Optional
from ..models import (
    HiHatType, HiHatFeatures, HiHatClassification, HiHatThresholds,
    OnsetData, OnsetList
)


class HiHatClassifier:
    """
    Clasifica golpes de hi-hat como abierto o cerrado.

    Algoritmo:
    - Extrae segmento post-onset (~300ms)
    - Features temporales: decay_time, amp_100ms, temporal_centroid
    - Features espectrales: spectral_centroid, bandwidth, flatness
    - Ponderacion: decay=40%, amp=25%, centroid=20%, spectral=15%

    Umbrales:
    - OPEN si decay > 200ms
    - CLOSED si decay < 100ms
    - Zona incertidumbre 100-200ms: basado en otros features
    """

    def __init__(self, sr: int = 22050, thresholds: Optional[HiHatThresholds] = None):
        self.sr = sr
        self.thresholds = thresholds or HiHatThresholds()
        self.segment_duration = 0.300  # 300ms post-onset

    def classify(self, y: np.ndarray, onset_time: float) -> HiHatClassification:
        """
        Clasifica un golpe de hi-hat.

        Args:
            y: Audio array completo (mono)
            onset_time: Tiempo del onset en segundos

        Returns:
            HiHatClassification con tipo, confianza y features
        """
        # Extraer segmento post-onset
        segment = self._extract_segment(y, onset_time)

        if len(segment) < 100:
            return HiHatClassification(
                hit_type=HiHatType.UNKNOWN,
                confidence=0.0
            )

        # Extraer features
        features = self._extract_features(segment)

        # Clasificar basado en features
        hit_type, confidence = self._classify_from_features(features)

        return HiHatClassification(
            hit_type=hit_type,
            confidence=confidence,
            features=features
        )

    def classify_onsets(self, y: np.ndarray, onsets: OnsetList) -> List[HiHatClassification]:
        """
        Clasifica todos los onsets de una lista.

        Args:
            y: Audio array completo
            onsets: Lista de onsets a clasificar

        Returns:
            Lista de clasificaciones
        """
        return [self.classify(y, onset.time) for onset in onsets]

    def _extract_segment(self, y: np.ndarray, onset_time: float) -> np.ndarray:
        """Extrae segmento de audio post-onset."""
        start_sample = int(onset_time * self.sr)
        end_sample = start_sample + int(self.segment_duration * self.sr)

        # Asegurar que no excedemos el audio
        start_sample = max(0, start_sample)
        end_sample = min(len(y), end_sample)

        return y[start_sample:end_sample]

    def _extract_features(self, segment: np.ndarray) -> HiHatFeatures:
        """Extrae todas las features del segmento."""
        # Features temporales
        decay_time = self._calculate_decay_time(segment)
        amp_100ms = self._calculate_amp_at_time(segment, 0.100)
        temporal_centroid = self._calculate_temporal_centroid(segment)

        # Features espectrales
        spectral_centroid = self._calculate_spectral_centroid(segment)
        spectral_bandwidth = self._calculate_spectral_bandwidth(segment)
        spectral_flatness = self._calculate_spectral_flatness(segment)

        return HiHatFeatures(
            decay_time=decay_time,
            amp_100ms=amp_100ms,
            temporal_centroid=temporal_centroid,
            spectral_centroid=spectral_centroid,
            spectral_bandwidth=spectral_bandwidth,
            spectral_flatness=spectral_flatness
        )

    def _calculate_decay_time(self, segment: np.ndarray) -> float:
        """
        Calcula tiempo de decay (tiempo hasta -20dB del pico).
        """
        # Envolvente de amplitud
        envelope = np.abs(segment)

        # Suavizar con ventana movil
        window_size = int(0.005 * self.sr)  # 5ms
        if window_size > 0 and len(envelope) > window_size:
            envelope = np.convolve(envelope, np.ones(window_size)/window_size, mode='same')

        peak_amplitude = np.max(envelope)
        if peak_amplitude == 0:
            return 0.0

        # Umbral: -20dB del pico
        threshold = peak_amplitude * 0.1

        # Encontrar donde cae por debajo del umbral
        peak_idx = np.argmax(envelope)
        below_threshold = np.where(envelope[peak_idx:] < threshold)[0]

        if len(below_threshold) > 0:
            decay_samples = below_threshold[0]
            return decay_samples / self.sr

        # Si no cae por debajo, usar todo el segmento
        return (len(segment) - peak_idx) / self.sr

    def _calculate_amp_at_time(self, segment: np.ndarray, time_offset: float) -> float:
        """Calcula amplitud RMS en un momento especifico."""
        sample_idx = int(time_offset * self.sr)
        window_size = int(0.010 * self.sr)  # 10ms window

        start = max(0, sample_idx - window_size // 2)
        end = min(len(segment), sample_idx + window_size // 2)

        if start >= end or start >= len(segment):
            return 0.0

        window = segment[start:end]
        return float(np.sqrt(np.mean(window ** 2)))

    def _calculate_temporal_centroid(self, segment: np.ndarray) -> float:
        """Calcula centroide temporal (centro de masa de energia)."""
        energy = segment ** 2
        total_energy = np.sum(energy)

        if total_energy == 0:
            return 0.0

        times = np.arange(len(segment)) / self.sr
        centroid = np.sum(times * energy) / total_energy

        return float(centroid)

    def _calculate_spectral_centroid(self, segment: np.ndarray) -> float:
        """Calcula centroide espectral promedio."""
        centroid = librosa.feature.spectral_centroid(y=segment, sr=self.sr)
        return float(np.mean(centroid))

    def _calculate_spectral_bandwidth(self, segment: np.ndarray) -> float:
        """Calcula ancho de banda espectral promedio."""
        bandwidth = librosa.feature.spectral_bandwidth(y=segment, sr=self.sr)
        return float(np.mean(bandwidth))

    def _calculate_spectral_flatness(self, segment: np.ndarray) -> float:
        """Calcula planitud espectral promedio (0=tonal, 1=ruido)."""
        flatness = librosa.feature.spectral_flatness(y=segment)
        return float(np.mean(flatness))

    def _classify_from_features(self, features: HiHatFeatures) -> tuple:
        """
        Clasifica basado en features ponderadas.

        Returns:
            Tuple de (HiHatType, confidence)
        """
        th = self.thresholds

        # Clasificacion rapida por decay
        if features.decay_time < th.decay_closed:
            # Claramente cerrado
            confidence = 0.8 + 0.2 * (1 - features.decay_time / th.decay_closed)
            return HiHatType.CLOSED, min(1.0, confidence)

        if features.decay_time > th.decay_open:
            # Claramente abierto
            confidence = 0.8 + 0.2 * min(1.0, (features.decay_time - th.decay_open) / th.decay_open)
            return HiHatType.OPEN, min(1.0, confidence)

        # Zona de incertidumbre (100-200ms): usar features ponderadas
        score = 0.0

        # Decay time score (40%)
        decay_normalized = (features.decay_time - th.decay_closed) / (th.decay_open - th.decay_closed)
        score += decay_normalized * th.weight_decay

        # Amplitud a 100ms score (25%) - mayor amp = mas abierto
        # Normalizar asumiendo amp_100ms tipico entre 0.01 y 0.1
        amp_normalized = min(1.0, features.amp_100ms / 0.1)
        score += amp_normalized * th.weight_amp

        # Temporal centroid score (20%) - mayor centroid = mas abierto
        # Normalizar asumiendo centroid tipico entre 0.02 y 0.15
        centroid_normalized = min(1.0, features.temporal_centroid / 0.15)
        score += centroid_normalized * th.weight_temporal

        # Spectral flatness score (15%) - hi-hat abierto tiende a ser mas "ruidoso"
        score += features.spectral_flatness * th.weight_spectral

        # Score > 0.5 = abierto
        if score > 0.5:
            hit_type = HiHatType.OPEN
            confidence = 0.5 + (score - 0.5)
        else:
            hit_type = HiHatType.CLOSED
            confidence = 0.5 + (0.5 - score)

        return hit_type, min(0.7, confidence)  # Max 0.7 en zona incertidumbre
