"""Separador de stems de bateria usando audio-separator/DrumSep."""
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Tuple
import tempfile
import os

try:
    from audio_separator.separator import Separator
    HAS_AUDIO_SEPARATOR = True
except ImportError:
    HAS_AUDIO_SEPARATOR = False

try:
    import librosa
    import soundfile as sf
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False


@dataclass
class SeparatedStems:
    """Stems de bateria separados."""
    kick: Optional[np.ndarray] = None
    snare: Optional[np.ndarray] = None
    hihat: Optional[np.ndarray] = None
    toms: Optional[np.ndarray] = None
    other: Optional[np.ndarray] = None
    sr: int = 22050

    def has_all_stems(self) -> bool:
        """Verifica si todos los stems principales estan presentes."""
        return all([self.kick is not None, self.snare is not None, self.hihat is not None])


class DrumSeparator:
    """
    Separa bateria en stems individuales (kick, snare, hihat).

    Usa audio-separator con modelos de separacion de fuentes.
    Si no esta disponible, proporciona separacion basica por frecuencia.

    Modelos soportados:
    - MDX-Net: Separacion general (vocals, drums, bass, other)
    - Demucs: Alta calidad pero mas lento
    - DrumSep: Especializado en bateria (si disponible)
    """

    def __init__(self, model_name: str = "htdemucs", output_dir: Optional[str] = None):
        """
        Inicializa el separador.

        Args:
            model_name: Nombre del modelo a usar
            output_dir: Directorio para archivos temporales
        """
        self.model_name = model_name
        self.output_dir = output_dir or tempfile.mkdtemp(prefix="drum_sep_")
        self._separator = None

        if not HAS_LIBROSA:
            raise ImportError("librosa es requerido. Instalar con: pip install librosa")

    @property
    def is_available(self) -> bool:
        """Verifica si audio-separator esta disponible."""
        return HAS_AUDIO_SEPARATOR

    def _init_separator(self):
        """Inicializa el separador de audio-separator."""
        if not HAS_AUDIO_SEPARATOR:
            return

        if self._separator is None:
            self._separator = Separator(
                output_dir=self.output_dir,
                output_format="wav"
            )
            self._separator.load_model(self.model_name)

    def separate(self, audio_path: str) -> SeparatedStems:
        """
        Separa audio en stems de bateria.

        Args:
            audio_path: Ruta al archivo de audio

        Returns:
            SeparatedStems con los stems separados
        """
        if HAS_AUDIO_SEPARATOR:
            return self._separate_with_model(audio_path)
        else:
            return self._separate_by_frequency(audio_path)

    def separate_array(self, y: np.ndarray, sr: int) -> SeparatedStems:
        """
        Separa array de audio en stems.

        Args:
            y: Audio array
            sr: Sample rate

        Returns:
            SeparatedStems
        """
        # Guardar a archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
            sf.write(temp_path, y, sr)

        try:
            stems = self.separate(temp_path)
        finally:
            os.unlink(temp_path)

        return stems

    def _separate_with_model(self, audio_path: str) -> SeparatedStems:
        """Separa usando audio-separator."""
        self._init_separator()

        # Separar
        output_files = self._separator.separate(audio_path)

        # Cargar stems
        stems = SeparatedStems()

        for output_file in output_files:
            file_lower = output_file.lower()

            if "drums" in file_lower or "bateria" in file_lower:
                # Si tenemos stem de drums, hacer separacion adicional por frecuencia
                drums_audio, sr = librosa.load(output_file, sr=None)
                stems.sr = sr
                drum_stems = self._split_drums_by_frequency(drums_audio, sr)
                stems.kick = drum_stems.kick
                stems.snare = drum_stems.snare
                stems.hihat = drum_stems.hihat

            elif "kick" in file_lower or "bombo" in file_lower:
                stems.kick, stems.sr = librosa.load(output_file, sr=None)

            elif "snare" in file_lower or "caja" in file_lower:
                stems.snare, stems.sr = librosa.load(output_file, sr=None)

            elif "hihat" in file_lower or "hi-hat" in file_lower:
                stems.hihat, stems.sr = librosa.load(output_file, sr=None)

        return stems

    def _separate_by_frequency(self, audio_path: str) -> SeparatedStems:
        """
        Separacion basica por bandas de frecuencia.

        No es tan precisa como modelos ML pero funciona sin dependencias.
        """
        y, sr = librosa.load(audio_path, sr=None)
        return self._split_drums_by_frequency(y, sr)

    def _split_drums_by_frequency(self, y: np.ndarray, sr: int) -> SeparatedStems:
        """
        Divide audio de bateria en stems por bandas de frecuencia.

        Bandas:
        - Kick: 20-150 Hz
        - Snare: 150-5000 Hz (con enfasis en 200-400 Hz para cuerpo)
        - Hi-hat: 5000-16000 Hz
        """
        # STFT
        D = librosa.stft(y)
        freqs = librosa.fft_frequencies(sr=sr)

        # Mascaras de frecuencia
        kick_mask = (freqs >= 20) & (freqs <= 150)
        snare_mask = (freqs >= 150) & (freqs <= 5000)
        hihat_mask = (freqs >= 5000) & (freqs <= 16000)

        # Aplicar mascaras
        D_kick = D * kick_mask[:, np.newaxis]
        D_snare = D * snare_mask[:, np.newaxis]
        D_hihat = D * hihat_mask[:, np.newaxis]

        # Reconstruir audio
        kick = librosa.istft(D_kick)
        snare = librosa.istft(D_snare)
        hihat = librosa.istft(D_hihat)

        return SeparatedStems(
            kick=kick,
            snare=snare,
            hihat=hihat,
            sr=sr
        )

    def save_stems(self, stems: SeparatedStems, output_dir: str,
                   prefix: str = "stem") -> Dict[str, str]:
        """
        Guarda stems a archivos WAV.

        Args:
            stems: Stems a guardar
            output_dir: Directorio de salida
            prefix: Prefijo para nombres de archivo

        Returns:
            Dict con rutas de archivos guardados
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        if stems.kick is not None:
            path = output_dir / f"{prefix}_kick.wav"
            sf.write(str(path), stems.kick, stems.sr)
            saved_files['kick'] = str(path)

        if stems.snare is not None:
            path = output_dir / f"{prefix}_snare.wav"
            sf.write(str(path), stems.snare, stems.sr)
            saved_files['snare'] = str(path)

        if stems.hihat is not None:
            path = output_dir / f"{prefix}_hihat.wav"
            sf.write(str(path), stems.hihat, stems.sr)
            saved_files['hihat'] = str(path)

        if stems.toms is not None:
            path = output_dir / f"{prefix}_toms.wav"
            sf.write(str(path), stems.toms, stems.sr)
            saved_files['toms'] = str(path)

        if stems.other is not None:
            path = output_dir / f"{prefix}_other.wav"
            sf.write(str(path), stems.other, stems.sr)
            saved_files['other'] = str(path)

        return saved_files
