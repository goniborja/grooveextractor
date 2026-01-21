"""Separador de stems de bateria usando audio-separator en dos fases.

FLUJO DE SEPARACION:
====================
FASE 1 - DEMUCS: Extraer bateria de mezcla completa
    Input: Mezcla completa (vocals, bass, drums, guitar, etc.)
    Output: Stem de bateria pura (drums.wav)
    Modelo: htdemucs_ft

FASE 2 - DRUMSEP: Separar bateria en componentes
    Input: Stem de bateria pura (de Fase 1)
    Output: kick.wav, snare.wav, hihat.wav, toms.wav
    Modelo: MDX23C-DrumSep-aufr33-jarredou.ckpt
"""
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


# Nombres de modelos
MODEL_DEMUCS = "htdemucs_ft.yaml"  # Para extraer drums de mezcla
MODEL_DRUMSEP = "MDX23C-DrumSep-aufr33-jarredou.ckpt"  # Para separar kick/snare/hihat


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
    Separa bateria en stems individuales (kick, snare, hihat) en dos fases.

    Fase 1: Demucs extrae bateria de mezcla completa
    Fase 2: DrumSep separa bateria en kick/snare/hihat/toms

    Si audio-separator no esta disponible, usa separacion por frecuencia como fallback.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Inicializa el separador.

        Args:
            output_dir: Directorio para archivos temporales
        """
        self.output_dir = output_dir or tempfile.mkdtemp(prefix="drum_sep_")
        self._demucs_separator = None
        self._drumsep_separator = None

        if not HAS_LIBROSA:
            raise ImportError("librosa es requerido. Instalar con: pip install librosa")

    @property
    def is_available(self) -> bool:
        """Verifica si audio-separator esta disponible."""
        return HAS_AUDIO_SEPARATOR

    def _init_demucs(self):
        """Inicializa el separador Demucs para Fase 1."""
        if not HAS_AUDIO_SEPARATOR:
            return

        if self._demucs_separator is None:
            self._demucs_separator = Separator(
                output_dir=self.output_dir,
                output_format="wav"
            )
            self._demucs_separator.load_model(MODEL_DEMUCS)

    def _init_drumsep(self):
        """Inicializa el separador DrumSep para Fase 2."""
        if not HAS_AUDIO_SEPARATOR:
            return

        if self._drumsep_separator is None:
            self._drumsep_separator = Separator(
                output_dir=self.output_dir,
                output_format="wav"
            )
            self._drumsep_separator.load_model(MODEL_DRUMSEP)

    # =========================================================================
    # FASE 1: Extraer bateria de mezcla completa
    # =========================================================================

    def extract_drums_from_mix(self, y: np.ndarray, sr: int) -> Tuple[np.ndarray, int]:
        """
        FASE 1: Extrae stem de bateria de una mezcla completa usando Demucs.

        Args:
            y: Audio array de la mezcla completa
            sr: Sample rate

        Returns:
            Tuple de (drums_audio, sr)
        """
        if not HAS_AUDIO_SEPARATOR:
            print("[ANALISIS] Fase 1: audio-separator no disponible, usando audio original")
            return y, sr

        print("[ANALISIS] Fase 1: Extrayendo bateria con Demucs...")

        # Guardar a archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
            sf.write(temp_path, y, sr)

        try:
            self._init_demucs()
            output_files = self._demucs_separator.separate(temp_path)

            # Buscar el stem de drums
            for output_file in output_files:
                full_path = os.path.join(self.output_dir, output_file)
                if "drum" in output_file.lower():
                    drums_audio, drums_sr = librosa.load(full_path, sr=None)
                    print(f"[ANALISIS] Fase 1 completada: drums extraido ({len(drums_audio)/drums_sr:.2f}s)")
                    return drums_audio, drums_sr

            # Si no encontramos drums, devolver audio original
            print("[ANALISIS] Fase 1: No se encontro stem de drums, usando audio original")
            return y, sr

        finally:
            os.unlink(temp_path)

    def extract_drums_from_mix_file(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """
        FASE 1: Extrae stem de bateria de un archivo de mezcla.

        Args:
            audio_path: Ruta al archivo de audio

        Returns:
            Tuple de (drums_audio, sr)
        """
        y, sr = librosa.load(audio_path, sr=None)
        return self.extract_drums_from_mix(y, sr)

    # =========================================================================
    # FASE 2: Separar bateria en componentes
    # =========================================================================

    def separate_drums(self, drums_y: np.ndarray, sr: int) -> SeparatedStems:
        """
        FASE 2: Separa audio de bateria en kick/snare/hihat usando DrumSep.

        Args:
            drums_y: Audio array de bateria (ya separado de la mezcla)
            sr: Sample rate

        Returns:
            SeparatedStems con kick, snare, hihat, toms
        """
        if not HAS_AUDIO_SEPARATOR:
            print("[ANALISIS] Fase 2: audio-separator no disponible, usando separacion por frecuencia")
            return self._split_drums_by_frequency(drums_y, sr)

        print("[ANALISIS] Fase 2: Separando kick/snare/hihat con DrumSep...")

        # Guardar a archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
            sf.write(temp_path, drums_y, sr)

        try:
            self._init_drumsep()
            output_files = self._drumsep_separator.separate(temp_path)

            # Cargar stems
            stems = SeparatedStems(sr=sr)

            for output_file in output_files:
                full_path = os.path.join(self.output_dir, output_file)
                file_lower = output_file.lower()

                if "(kick)" in file_lower:
                    stems.kick, stems.sr = librosa.load(full_path, sr=None)
                elif "(snare)" in file_lower:
                    stems.snare, stems.sr = librosa.load(full_path, sr=None)
                elif "(hh)" in file_lower:
                    stems.hihat, stems.sr = librosa.load(full_path, sr=None)
                elif "(toms)" in file_lower:
                    stems.toms, stems.sr = librosa.load(full_path, sr=None)

            print(f"[ANALISIS] Fase 2 completada: kick={stems.kick is not None}, "
                  f"snare={stems.snare is not None}, hihat={stems.hihat is not None}")

            return stems

        finally:
            os.unlink(temp_path)

    def separate_drums_file(self, drums_path: str) -> SeparatedStems:
        """
        FASE 2: Separa archivo de bateria en componentes.

        Args:
            drums_path: Ruta al archivo de bateria

        Returns:
            SeparatedStems
        """
        y, sr = librosa.load(drums_path, sr=None)
        return self.separate_drums(y, sr)

    # =========================================================================
    # FLUJO COMPLETO: Fase 1 + Fase 2
    # =========================================================================

    def separate_full_pipeline(self, y: np.ndarray, sr: int) -> SeparatedStems:
        """
        Pipeline completo: Extrae bateria de mezcla y separa en componentes.

        FLUJO:
        Mezcla → Demucs → drums.wav → DrumSep → kick/snare/hihat

        Args:
            y: Audio array de la mezcla completa
            sr: Sample rate

        Returns:
            SeparatedStems con kick, snare, hihat, toms
        """
        # Fase 1: Extraer drums de la mezcla
        drums_audio, drums_sr = self.extract_drums_from_mix(y, sr)

        # Fase 2: Separar drums en componentes
        stems = self.separate_drums(drums_audio, drums_sr)

        return stems

    def separate_full_pipeline_file(self, audio_path: str) -> SeparatedStems:
        """
        Pipeline completo desde archivo.

        Args:
            audio_path: Ruta al archivo de mezcla

        Returns:
            SeparatedStems
        """
        y, sr = librosa.load(audio_path, sr=None)
        return self.separate_full_pipeline(y, sr)

    # =========================================================================
    # FLUJO HIBRIDO: Combina lo mejor de cada metodo
    # =========================================================================

    def separate_hybrid(self, y: np.ndarray, sr: int) -> SeparatedStems:
        """
        Separacion hibrida: combina lo mejor de cada metodo.

        PROBLEMA:
        - Demucs + DrumSep: separa bien kick/snare pero hihat se contamina con guitarra
        - DrumSep directo: kick se confunde con bajo, pero hihat sale muy definido

        SOLUCION:
        - Kick y Snare: del pipeline Demucs + DrumSep (mejor separacion de graves)
        - Hihat: de DrumSep directo sobre la mezcla (mejor ataque de hihat)

        Args:
            y: Audio array de la mezcla
            sr: Sample rate

        Returns:
            SeparatedStems con kick/snare de pipeline y hihat de directo
        """
        print("[ANALISIS] Modo hibrido: kick/snare de Demucs+DrumSep, hihat de DrumSep directo")

        if not HAS_AUDIO_SEPARATOR:
            print("[ANALISIS] audio-separator no disponible, usando separacion por frecuencia")
            return self._split_drums_by_frequency(y, sr)

        # PASO 1: Pipeline completo para kick y snare
        print("[ANALISIS] Paso 1/2: Ejecutando Demucs + DrumSep para kick/snare...")
        stems_pipeline = self.separate_full_pipeline(y, sr)

        # PASO 2: DrumSep directo para hihat
        print("[ANALISIS] Paso 2/2: Ejecutando DrumSep directo para hihat...")
        stems_direct = self.separate_drums(y, sr)

        # COMBINAR: kick/snare de pipeline, hihat de directo
        hybrid_stems = SeparatedStems(
            kick=stems_pipeline.kick,
            snare=stems_pipeline.snare,
            hihat=stems_direct.hihat,
            toms=stems_pipeline.toms,  # toms del pipeline
            sr=stems_pipeline.sr
        )

        print(f"[ANALISIS] Modo hibrido completado: kick={hybrid_stems.kick is not None}, "
              f"snare={hybrid_stems.snare is not None}, hihat={hybrid_stems.hihat is not None}")

        return hybrid_stems

    def separate_hybrid_file(self, audio_path: str) -> SeparatedStems:
        """
        Separacion hibrida desde archivo.

        Args:
            audio_path: Ruta al archivo de mezcla

        Returns:
            SeparatedStems
        """
        y, sr = librosa.load(audio_path, sr=None)
        return self.separate_hybrid(y, sr)

    # =========================================================================
    # FLUJO OLDIE/NEWIE: Para grabaciones vintage vs modernas
    # =========================================================================

    def _extract_hihat_by_frequency(self, y: np.ndarray, sr: int,
                                     low_freq: float, high_freq: float) -> np.ndarray:
        """
        Extrae hi-hat usando filtro de frecuencia.

        Args:
            y: Audio array (stem de bateria)
            sr: Sample rate
            low_freq: Frecuencia minima del filtro
            high_freq: Frecuencia maxima del filtro

        Returns:
            Audio array con solo el rango de frecuencias del hi-hat
        """
        D = librosa.stft(y)
        freqs = librosa.fft_frequencies(sr=sr)

        # Mascara de frecuencia para hi-hat
        hihat_mask = (freqs >= low_freq) & (freqs <= high_freq)

        # Aplicar mascara
        D_hihat = D * hihat_mask[:, np.newaxis]

        # Reconstruir audio
        hihat = librosa.istft(D_hihat)

        return hihat

    def separate_oldie(self, y: np.ndarray, sr: int) -> SeparatedStems:
        """
        Separacion para grabaciones VINTAGE jamaicanas (ska, rocksteady, early reggae).

        FLUJO:
        Mezcla -> Demucs -> drums -> filtro 3500-8500 Hz -> hihat (vintage)
                                  -> DrumSep -> kick, snare

        Los hi-hats vintage jamaicanos (especialmente open hihat) tienen
        frecuencias mas bajas y calidas (3500-8500 Hz).

        Args:
            y: Audio array de la mezcla
            sr: Sample rate

        Returns:
            SeparatedStems con hihat de filtro vintage y kick/snare de DrumSep
        """
        print("[ANALISIS] Modo OLDIE: hi-hat vintage (3500-8500 Hz)")

        if not HAS_AUDIO_SEPARATOR:
            print("[ANALISIS] audio-separator no disponible, usando separacion por frecuencia")
            return self._split_drums_by_frequency(y, sr)

        # PASO 1: Extraer drums con Demucs
        print("[ANALISIS] Paso 1/3: Extrayendo bateria con Demucs...")
        drums_audio, drums_sr = self.extract_drums_from_mix(y, sr)

        # PASO 2: Extraer hi-hat con filtro vintage (3500-8500 Hz)
        print("[ANALISIS] Paso 2/3: Filtrando hi-hat vintage (3500-8500 Hz)...")
        hihat_filtered = self._extract_hihat_by_frequency(drums_audio, drums_sr, 3500, 8500)

        # PASO 3: Extraer kick/snare con DrumSep
        print("[ANALISIS] Paso 3/3: Separando kick/snare con DrumSep...")
        stems_drumsep = self.separate_drums(drums_audio, drums_sr)

        # COMBINAR: hihat del filtro, kick/snare de DrumSep
        oldie_stems = SeparatedStems(
            kick=stems_drumsep.kick,
            snare=stems_drumsep.snare,
            hihat=hihat_filtered,
            toms=stems_drumsep.toms,
            sr=drums_sr
        )

        print(f"[ANALISIS] Modo OLDIE completado: kick={oldie_stems.kick is not None}, "
              f"snare={oldie_stems.snare is not None}, hihat={oldie_stems.hihat is not None}")

        return oldie_stems

    def separate_oldie_file(self, audio_path: str) -> SeparatedStems:
        """Separacion OLDIE desde archivo."""
        y, sr = librosa.load(audio_path, sr=None)
        return self.separate_oldie(y, sr)

    def separate_newie(self, y: np.ndarray, sr: int) -> SeparatedStems:
        """
        Separacion para grabaciones MODERNAS.

        FLUJO:
        Mezcla -> Demucs -> drums -> filtro 4500-10000 Hz -> hihat (moderno)
                                  -> DrumSep -> kick, snare

        Los hi-hats modernos tienen frecuencias mas altas y brillantes (4500-10000 Hz).

        Args:
            y: Audio array de la mezcla
            sr: Sample rate

        Returns:
            SeparatedStems con hihat de filtro moderno y kick/snare de DrumSep
        """
        print("[ANALISIS] Modo NEWIE: hi-hat moderno (4500-10000 Hz)")

        if not HAS_AUDIO_SEPARATOR:
            print("[ANALISIS] audio-separator no disponible, usando separacion por frecuencia")
            return self._split_drums_by_frequency(y, sr)

        # PASO 1: Extraer drums con Demucs
        print("[ANALISIS] Paso 1/3: Extrayendo bateria con Demucs...")
        drums_audio, drums_sr = self.extract_drums_from_mix(y, sr)

        # PASO 2: Extraer hi-hat con filtro moderno (4500-10000 Hz)
        print("[ANALISIS] Paso 2/3: Filtrando hi-hat moderno (4500-10000 Hz)...")
        hihat_filtered = self._extract_hihat_by_frequency(drums_audio, drums_sr, 4500, 10000)

        # PASO 3: Extraer kick/snare con DrumSep
        print("[ANALISIS] Paso 3/3: Separando kick/snare con DrumSep...")
        stems_drumsep = self.separate_drums(drums_audio, drums_sr)

        # COMBINAR: hihat del filtro, kick/snare de DrumSep
        newie_stems = SeparatedStems(
            kick=stems_drumsep.kick,
            snare=stems_drumsep.snare,
            hihat=hihat_filtered,
            toms=stems_drumsep.toms,
            sr=drums_sr
        )

        print(f"[ANALISIS] Modo NEWIE completado: kick={newie_stems.kick is not None}, "
              f"snare={newie_stems.snare is not None}, hihat={newie_stems.hihat is not None}")

        return newie_stems

    def separate_newie_file(self, audio_path: str) -> SeparatedStems:
        """Separacion NEWIE desde archivo."""
        y, sr = librosa.load(audio_path, sr=None)
        return self.separate_newie(y, sr)

    def separate_by_mode(self, y: np.ndarray, sr: int, mode: str = "oldie") -> SeparatedStems:
        """
        Separacion segun modo seleccionado.

        Args:
            y: Audio array de la mezcla
            sr: Sample rate
            mode: "oldie" para vintage jamaicano, "newie" para moderno

        Returns:
            SeparatedStems
        """
        if mode.lower() == "oldie":
            return self.separate_oldie(y, sr)
        elif mode.lower() == "newie":
            return self.separate_newie(y, sr)
        else:
            print(f"[ANALISIS] Modo desconocido '{mode}', usando 'oldie' por defecto")
            return self.separate_oldie(y, sr)

    # =========================================================================
    # METODOS LEGACY (compatibilidad hacia atras)
    # =========================================================================

    def separate(self, audio_path: str) -> SeparatedStems:
        """
        Separa audio en stems de bateria (metodo legacy).

        Si el audio ya es bateria pura, usa solo Fase 2.
        Si es mezcla completa, usa pipeline completo.

        Args:
            audio_path: Ruta al archivo de audio

        Returns:
            SeparatedStems
        """
        # Por defecto, asumimos que es bateria pura y usamos solo Fase 2
        return self.separate_drums_file(audio_path)

    def separate_array(self, y: np.ndarray, sr: int) -> SeparatedStems:
        """
        Separa array de audio en stems (metodo legacy).

        Args:
            y: Audio array
            sr: Sample rate

        Returns:
            SeparatedStems
        """
        # Por defecto, asumimos que es bateria pura y usamos solo Fase 2
        return self.separate_drums(y, sr)

    # =========================================================================
    # FALLBACK: Separacion por frecuencia
    # =========================================================================

    def _split_drums_by_frequency(self, y: np.ndarray, sr: int) -> SeparatedStems:
        """
        Divide audio de bateria en stems por bandas de frecuencia (fallback).

        Bandas:
        - Kick: 20-150 Hz
        - Snare: 150-5000 Hz
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

    # =========================================================================
    # UTILIDADES
    # =========================================================================

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
