"""
CONFIG - Configuración Centralizada de Groove Extractor
========================================================
Centraliza todas las rutas y parámetros del proyecto.
"""

import sys
import os
from pathlib import Path

# Configurar encoding UTF-8 para consola Windows (soporta emojis)
if sys.platform == 'win32':
    # Intentar configurar stdout/stderr con UTF-8
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, OSError):
        # Python < 3.7 o error de reconfiguración
        pass
    # Variable de entorno como fallback
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

# =============================================================================
# RUTAS DEL PROYECTO
# =============================================================================

# Directorio raíz del proyecto (donde está este archivo)
PROJECT_ROOT = Path(__file__).parent.resolve()

# Rutas de archivos principales
PATHS = {
    'database': PROJECT_ROOT / 'database.xlsx',
    'stems': PROJECT_ROOT / 'stems',
    'assets': PROJECT_ROOT / 'assets',
    'textures': PROJECT_ROOT / 'assets' / 'textures',
}


# =============================================================================
# CONFIGURACIÓN DE AUDIO
# =============================================================================

AUDIO = {
    # Sample rate por defecto (None = usar el del archivo)
    'default_sr': None,

    # Formatos de audio soportados
    'supported_formats': ['wav', 'mp3', 'flac', 'ogg', 'm4a'],

    # Extensiones para diálogos de archivo
    'file_filter': "Audio fitxategiak (*.wav *.mp3 *.flac *.ogg *.m4a *.WAV *.MP3 *.FLAC);;Fitxategi guztiak (*)",
}


# =============================================================================
# CONFIGURACIÓN DSP - DETECCIÓN DE ONSETS
# =============================================================================

# Parámetros por método de detección
ONSET_DETECTION = {
    # Método optimizado para reggae (70-110 BPM)
    'reggae_optimized': {
        'hop_length': 256,      # ~5.8ms @ 44.1kHz - alta resolución temporal
        'fmax': 8000,           # Frecuencia máxima (rango de batería)
        'n_mels': 128,          # Bandas mel para análisis espectral
        'pre_max': 5,           # Ventana pre-pico (más amplia para tempos lentos)
        'post_max': 5,          # Ventana post-pico
        'pre_avg': 5,           # Promedio pre-pico
        'post_avg': 7,          # Promedio post-pico
        'delta': 0.15,          # Umbral sensible (reggae tiene dinámica variada)
        'wait': 15,             # Mínimo espacio entre onsets (evitar dobles)
        'backtrack': True,      # Refinar posición temporal
    },

    # Método sensible para grooves sutiles
    'sensitive': {
        'hop_length': 128,      # ~2.9ms @ 44.1kHz - máxima resolución
        'fmax': 8000,
        'n_mels': 128,
        'pre_max': 3,
        'post_max': 3,
        'pre_avg': 3,
        'post_avg': 5,
        'delta': 0.1,           # Umbral muy bajo
        'wait': 10,
        'backtrack': True,
    },

    # Método estándar (fallback)
    'standard': {
        'hop_length': 512,      # ~11.6ms @ 44.1kHz
        'fmax': 8000,
        'n_mels': 128,
        'pre_max': 3,
        'post_max': 3,
        'pre_avg': 3,
        'post_avg': 5,
        'delta': 0.2,
        'wait': 10,
        'backtrack': True,
    },
}


# =============================================================================
# CONFIGURACIÓN DSP - ANÁLISIS MULTI-BANDA
# =============================================================================

FREQUENCY_BANDS = {
    # Banda de bajos (kick drum)
    'bass': {
        'low': 20,
        'high': 150,
        'weight': 0.35,         # Peso en combinación para reggae
    },

    # Banda de medios (snare)
    'mid': {
        'low': 150,
        'high': 2000,
        'weight': 0.40,         # Énfasis en "one drop"
    },

    # Banda de altos (hihat/cymbals)
    'high': {
        'low': 2000,
        'high': 8000,
        'weight': 0.25,
    },
}

# Orden del filtro Butterworth
FILTER_ORDER = 5


# =============================================================================
# CONFIGURACIÓN DSP - ANÁLISIS DE DINÁMICA
# =============================================================================

DYNAMICS = {
    # Ventana de análisis de amplitud (segundos)
    'window_size_seconds': 0.025,   # ±25ms alrededor del onset

    # Mapeo dB a MIDI velocity
    'db_min': -60,                  # Silencio
    'db_max': -6,                   # Fuerte

    # Rango MIDI velocity
    'velocity_min': 1,
    'velocity_max': 127,

    # Umbral de ruido (velocidades menores se filtran)
    'velocity_threshold': 20,
}


# =============================================================================
# CONFIGURACIÓN MIDI
# =============================================================================

MIDI = {
    # Ticks por negra (resolución MIDI estándar)
    'ticks_per_beat': 480,

    # Compás por defecto
    'time_signature': '4/4',

    # Pasos por compás (16th notes en 4/4)
    'steps_per_bar': 16,
}


# =============================================================================
# CONFIGURACIÓN DE TEMPO
# =============================================================================

TEMPO = {
    # Rango válido de BPM
    'min_bpm': 40,
    'max_bpm': 200,

    # BPM por defecto (típico reggae)
    'default_bpm': 85,

    # Detección automática de BPM
    'detection': {
        'start_percent': 35,    # Empezar análisis en 35% del audio
        'end_percent': 65,      # Terminar en 65% (evita intro/outro)
    },
}


# =============================================================================
# CONFIGURACIÓN DE DEMUCS (SEPARACIÓN DE AUDIO)
# =============================================================================

DEMUCS = {
    # Modelo por defecto
    'model_name': 'htdemucs',

    # Dispositivo de cómputo
    'default_device': 'cpu',    # 'cpu' o 'cuda'

    # Stems que separa htdemucs
    'stems': ['drums', 'bass', 'other', 'vocals'],

    # Índice del stem de batería
    'drums_index': 0,
}


# =============================================================================
# CONFIGURACIÓN DE EXCEL (DATABASE)
# =============================================================================

EXCEL = {
    # Nombres de hojas esperadas
    'sheets': {
        'humanizacion': 'HUMANIZACION',
        'patrones': 'PATRONES',
        'instrumentos': 'INSTRUMENTOS',
        'midi_config': 'MIDI_CONFIG',
        'estilos': 'ESTILOS',
    },

    # Mapeo de instrumentos detectados a IDs de Excel
    'instrument_mapping': {
        'kick': 'kick',
        'snare': 'snare_full',
        'hihat': 'hihat_closed',
        'tom': 'tom',
        'crash': 'crash',
        'ride': 'ride',
        'rim': 'rim',
    },

    # Estructura de columnas en HUMANIZACION
    'columns': {
        'id_patron': 1,         # A
        'instrumento': 2,       # B
        'velocities_start': 3,  # C (V1-V16: columnas 3-18)
        'timings_start': 19,    # S (T1-T16: columnas 19-34)
        'duration': 35,         # AI
    },
}


# =============================================================================
# CONFIGURACIÓN DE UI
# =============================================================================

UI = {
    # Tamaño de ventana principal
    'main_window': {
        'width': 900,
        'height': 700,
    },

    # Tamaño de ventana vintage
    'vintage_window': {
        'width': 1280,
        'height': 800,
    },

    # Estilos por defecto (si no se cargan desde Excel)
    'default_styles': [
        'ska', 'rocksteady', 'early reggae', 'roots reggae',
        'dub', 'one drop', 'steppers'
    ],

    # Animación de VU meters
    'vu_animation': {
        'interval_ms': 100,     # Intervalo de actualización
        'decay_factor': 0.85,   # Factor de decay
    },
}


# =============================================================================
# INFORMACIÓN DE LA APLICACIÓN
# =============================================================================

APP_INFO = {
    'name': 'Groove Extractor',
    'version': '2.2.0',
    'organization': 'Book of Drums',
    'description': 'Analisi Multi-banda Automatikoa - Kick + Snare + Hi-hat',
}


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def get_database_path():
    """
    Obtiene la ruta al archivo database.xlsx.

    Returns:
        Path: Ruta al archivo database.xlsx
    """
    return PATHS['database']


def get_stems_path(style=None):
    """
    Obtiene la ruta a la carpeta de stems.

    Args:
        style (str, optional): Estilo musical para subcarpeta

    Returns:
        Path: Ruta a la carpeta de stems
    """
    stems_path = PATHS['stems']
    if style:
        style_clean = style.lower().replace(' ', '_')
        return stems_path / style_clean
    return stems_path


def get_onset_params(method='reggae_optimized'):
    """
    Obtiene los parámetros de detección de onsets para un método.

    Args:
        method (str): Método de detección ('reggae_optimized', 'sensitive', 'standard')

    Returns:
        dict: Parámetros de detección
    """
    return ONSET_DETECTION.get(method, ONSET_DETECTION['standard'])


def get_band_config(band_name):
    """
    Obtiene la configuración de una banda de frecuencia.

    Args:
        band_name (str): Nombre de la banda ('bass', 'mid', 'high')

    Returns:
        dict: Configuración de la banda
    """
    return FREQUENCY_BANDS.get(band_name, {})


def validate_bpm(bpm):
    """
    Valida que el BPM esté en rango válido.

    Args:
        bpm (float): BPM a validar

    Returns:
        float: BPM ajustado al rango válido
    """
    min_bpm = TEMPO['min_bpm']
    max_bpm = TEMPO['max_bpm']

    while bpm < min_bpm:
        bpm *= 2
    while bpm > max_bpm:
        bpm /= 2

    return round(bpm, 1)
