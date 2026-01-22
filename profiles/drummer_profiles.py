"""
Book of Drums - Drummer Profiles

Perfiles completos de bateristas jamaicanos con valores de humanización
basados en conocimiento experto del género.

Cada perfil captura las características únicas del baterista:
- Timing offsets (adelante/atrás del beat)
- Velocity y variación dinámica
- Swing percentage
- Ghost notes y probabilidades
"""

from typing import Dict, List

# ==============================================================================
# DRUMMER PROFILES
# ==============================================================================

DRUMMER_PROFILES: Dict[str, dict] = {

    # ==========================================================================
    # CARLTON BARRETT - El rey del one-drop
    # ==========================================================================
    "carlton-barrett": {
        "name": "Carlton Barrett",
        "slug": "carlton-barrett",
        "signature": "El rey del one-drop",
        "style": "one-drop",
        "era": "70s-80s",
        "bands": ["Bob Marley & The Wailers"],
        "bpm_range": (65, 80),

        "kick": {
            "beats": [3],                    # One-drop: bombo solo en beat 3
            "offset_ticks": 8,               # Ligeramente atrasado - laid-back feel
            "velocity_base": 100,
            "velocity_variance": 5,
            "ghost_probability": 0.15,
            "ghost_beats": [1],
            "ghost_velocity": 40
        },

        "snare": {
            "beats": [3],                    # Caja junto con bombo en beat 3
            "offset_ticks": 10,              # Un poco más atrasado que el bombo
            "velocity_base": 100,
            "velocity_variance": 8,
            "rimshot_probability": 0.9,      # Usa mucho rimshots
            "ghost_probability": 0.3,
            "ghost_beats": ["2", "2+", "4", "4+"],
            "ghost_velocity": 35,
            "flam_probability": 0.05,
            "drag_probability": 0.02
        },

        "hihat": {
            "pattern": "offbeat",            # Solo offbeats - característico reggae
            "swing_percent": 62,             # Swing medio-alto
            "open_on_beats": ["4"],          # Abre en el 4
            "velocity_base": 80,
            "velocity_variance": 12,
            "accent_beats": ["2", "4"],
            "tightness": "medium"
        },

        "global": {
            "feel": "laid-back",             # Detrás del beat
            "humanize_percent": 60           # Variación expresiva
        }
    },

    # ==========================================================================
    # SLY DUNBAR - El arquitecto del steppers
    # ==========================================================================
    "sly-dunbar": {
        "name": "Sly Dunbar",
        "slug": "sly-dunbar",
        "signature": "El arquitecto del steppers",
        "style": "steppers",
        "era": "70s-actualidad",
        "bands": ["Sly & Robbie", "The Revolutionaries"],
        "bpm_range": (70, 85),

        "kick": {
            "beats": [1, 2, 3, 4],           # Steppers: bombo en TODOS los beats
            "offset_ticks": 3,               # Más "en el beat" que Carlton
            "velocity_base": 105,
            "velocity_variance": 3,          # Muy consistente
            "ghost_probability": 0.05,
            "ghost_beats": [],
            "ghost_velocity": 35
        },

        "snare": {
            "beats": [3],
            "offset_ticks": 5,
            "velocity_base": 100,
            "velocity_variance": 5,
            "rimshot_probability": 0.7,
            "ghost_probability": 0.15,
            "ghost_beats": ["2+", "4+"],
            "ghost_velocity": 30,
            "flam_probability": 0.02,
            "drag_probability": 0.01
        },

        "hihat": {
            "pattern": "8ths",               # Corcheas rectas
            "swing_percent": 52,             # Casi recto - mecánico
            "open_on_beats": [],
            "velocity_base": 75,
            "velocity_variance": 8,
            "accent_beats": ["1", "2", "3", "4"],
            "tightness": "tight"
        },

        "global": {
            "feel": "on-beat",               # Justo en el tiempo
            "humanize_percent": 30           # Muy consistente - casi máquina
        }
    },

    # ==========================================================================
    # LLOYD KNIBB - El padre del ska
    # ==========================================================================
    "lloyd-knibb": {
        "name": "Lloyd Knibb",
        "slug": "lloyd-knibb",
        "signature": "El padre del ska",
        "style": "ska",
        "era": "50s-60s",
        "bands": ["The Skatalites"],
        "bpm_range": (100, 140),

        "kick": {
            "beats": [1, 3],                 # Bombo en 1 y 3
            "offset_ticks": 0,               # En el beat - energía ska
            "velocity_base": 95,
            "velocity_variance": 8,
            "ghost_probability": 0.1,
            "ghost_beats": ["2+", "4+"],
            "ghost_velocity": 45
        },

        "snare": {
            "beats": [2, 4],                 # Afterbeat clásico del ska
            "offset_ticks": 2,
            "velocity_base": 95,
            "velocity_variance": 10,
            "rimshot_probability": 0.6,
            "ghost_probability": 0.25,
            "ghost_beats": ["1+", "3+"],
            "ghost_velocity": 40,
            "flam_probability": 0.08,
            "drag_probability": 0.03
        },

        "hihat": {
            "pattern": "quarters",           # Negras - influencia jazz
            "swing_percent": 58,             # Un poco de swing jazzy
            "open_on_beats": ["2", "4"],
            "velocity_base": 85,
            "velocity_variance": 15,
            "accent_beats": ["2", "4"],
            "tightness": "loose"
        },

        "global": {
            "feel": "on-top",                # Energético, ligeramente adelante
            "humanize_percent": 55
        }
    },

    # ==========================================================================
    # SANTA DAVIS - El complemento perfecto
    # ==========================================================================
    "santa-davis": {
        "name": "Santa Davis",
        "slug": "santa-davis",
        "signature": "El complemento perfecto",
        "style": "roots",
        "era": "70s-80s",
        "bands": ["Soul Syndicate", "varios"],
        "bpm_range": (68, 82),

        "kick": {
            "beats": [3],
            "offset_ticks": 6,
            "velocity_base": 98,
            "velocity_variance": 6,
            "ghost_probability": 0.12,
            "ghost_beats": [1, "2+"],
            "ghost_velocity": 38
        },

        "snare": {
            "beats": [3],
            "offset_ticks": 8,
            "velocity_base": 98,
            "velocity_variance": 7,
            "rimshot_probability": 0.85,
            "ghost_probability": 0.28,
            "ghost_beats": ["2", "2+", "4", "4+"],
            "ghost_velocity": 33,
            "flam_probability": 0.04,
            "drag_probability": 0.02
        },

        "hihat": {
            "pattern": "offbeat",
            "swing_percent": 60,
            "open_on_beats": ["4"],
            "velocity_base": 78,
            "velocity_variance": 10,
            "accent_beats": ["2", "4"],
            "tightness": "medium"
        },

        "global": {
            "feel": "laid-back",
            "humanize_percent": 55
        }
    },

    # ==========================================================================
    # HORSEMOUTH WALLACE - El expresivo
    # ==========================================================================
    "horsemouth-wallace": {
        "name": "Leroy 'Horsemouth' Wallace",
        "slug": "horsemouth-wallace",
        "signature": "El expresivo",
        "style": "rockers",
        "era": "70s-80s",
        "bands": ["The Aggrovators", "varios"],
        "bpm_range": (72, 88),

        "kick": {
            "beats": [1, 3],
            "offset_ticks": 5,
            "velocity_base": 102,
            "velocity_variance": 8,
            "ghost_probability": 0.18,
            "ghost_beats": ["2", "4"],
            "ghost_velocity": 42
        },

        "snare": {
            "beats": [3],
            "offset_ticks": 7,
            "velocity_base": 100,
            "velocity_variance": 10,
            "rimshot_probability": 0.75,
            "ghost_probability": 0.35,
            "ghost_beats": ["1+", "2", "2+", "4", "4+"],
            "ghost_velocity": 36,
            "flam_probability": 0.06,
            "drag_probability": 0.03
        },

        "hihat": {
            "pattern": "8ths",
            "swing_percent": 58,
            "open_on_beats": ["4", "4+"],
            "velocity_base": 82,
            "velocity_variance": 14,
            "accent_beats": ["2", "4"],
            "tightness": "medium"
        },

        "global": {
            "feel": "on-beat",
            "humanize_percent": 65
        }
    },
}


# ==============================================================================
# ACCESS FUNCTIONS
# ==============================================================================

def get_profile(drummer_slug: str) -> dict:
    """
    Obtiene el perfil completo de un baterista.

    Args:
        drummer_slug: ID del baterista (ej: "carlton-barrett")

    Returns:
        Diccionario con el perfil completo

    Raises:
        ValueError: Si el baterista no existe
    """
    if drummer_slug not in DRUMMER_PROFILES:
        available = list_drummers()
        raise ValueError(
            f"Baterista '{drummer_slug}' no encontrado. "
            f"Disponibles: {', '.join(available)}"
        )
    return DRUMMER_PROFILES[drummer_slug]


def list_drummers() -> List[str]:
    """
    Lista todos los bateristas disponibles.

    Returns:
        Lista de slugs de bateristas
    """
    return list(DRUMMER_PROFILES.keys())


def get_drummers_by_style(style: str) -> List[str]:
    """
    Filtra bateristas por estilo.

    Args:
        style: Estilo a buscar (one-drop, steppers, ska, etc.)

    Returns:
        Lista de slugs de bateristas con ese estilo
    """
    return [
        slug for slug, profile in DRUMMER_PROFILES.items()
        if profile.get("style") == style
    ]


def get_available_styles() -> List[str]:
    """
    Lista todos los estilos disponibles.

    Returns:
        Lista de estilos únicos
    """
    return list(set(p["style"] for p in DRUMMER_PROFILES.values()))


# ==============================================================================
# TEST
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DE DRUMMER PROFILES")
    print("=" * 60)

    print(f"\nBateristas disponibles: {list_drummers()}")
    print(f"Estilos disponibles: {get_available_styles()}")

    print("\n--- Perfil de Carlton Barrett ---")
    carlton = get_profile("carlton-barrett")
    print(f"Nombre: {carlton['name']}")
    print(f"Estilo: {carlton['style']}")
    print(f"Era: {carlton['era']}")
    print(f"BPM range: {carlton['bpm_range']}")
    print(f"Kick offset: {carlton['kick']['offset_ticks']} ticks")
    print(f"Swing: {carlton['hihat']['swing_percent']}%")

    print("\n--- Bateristas por estilo ---")
    for style in get_available_styles():
        drummers = get_drummers_by_style(style)
        print(f"  {style}: {drummers}")

    print("\n" + "=" * 60)
    print("TEST PASADO")
    print("=" * 60)
