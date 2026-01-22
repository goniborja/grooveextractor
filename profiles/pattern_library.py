"""
Book of Drums - Pattern Library

Biblioteca de patrones MIDI para diferentes estilos jamaicanos.

Los patrones definen la estructura ritmica BASE (sin humanizacion).
La humanizacion se aplica despues segun el perfil del baterista.

Cada evento tiene: (instrumento, beat, subdivision, es_acento)
- beat: 1-4 (en compas 4/4)
- subdivision: 0 = en el beat, 0.5 = offbeat (el "y")
- es_acento: True/False para marcar golpes principales
"""

from typing import Dict, List, Tuple

# Tipo para eventos de patron: (instrumento, beat, subdivision, es_acento)
PatternEvent = Tuple[str, int, float, bool]

# ==============================================================================
# PATTERN LIBRARY
# ==============================================================================

PATTERN_LIBRARY: Dict[str, dict] = {

    # ==========================================================================
    # ONE-DROP PATTERNS (Carlton Barrett style)
    # ==========================================================================

    "one-drop-basic": {
        "name": "One-Drop Basico",
        "style": "one-drop",
        "type": "rhythm",
        "length_bars": 1,
        "description": "El patron fundamental del reggae roots",
        "compatible_drummers": ["carlton-barrett", "santa-davis"],
        "events": [
            # Hi-hat en offbeats
            ("hihat", 1, 0.5, False),
            ("hihat", 2, 0.5, True),      # Acento en 2
            ("kick", 3, 0, True),          # ONE-DROP: bombo solo en 3
            ("snare", 3, 0, True),         # Caja junto con bombo
            ("hihat", 3, 0.5, False),
            ("hihat", 4, 0.5, True),       # Acento en 4
        ]
    },

    "one-drop-ghost": {
        "name": "One-Drop con Ghosts",
        "style": "one-drop",
        "type": "rhythm",
        "length_bars": 1,
        "description": "One-drop con ghost notes en la caja",
        "compatible_drummers": ["carlton-barrett", "santa-davis"],
        "events": [
            ("hihat", 1, 0.5, False),
            ("snare", 2, 0, False),        # Ghost note suave
            ("hihat", 2, 0.5, True),
            ("kick", 3, 0, True),
            ("snare", 3, 0, True),
            ("hihat", 3, 0.5, False),
            ("snare", 4, 0, False),        # Ghost note suave
            ("hihat", 4, 0.5, True),
        ]
    },

    "one-drop-hihat-open": {
        "name": "One-Drop Hi-Hat Abierto",
        "style": "one-drop",
        "type": "rhythm",
        "length_bars": 1,
        "description": "One-drop con hi-hat abierto en el 4",
        "compatible_drummers": ["carlton-barrett", "santa-davis"],
        "events": [
            ("hihat", 1, 0.5, False),
            ("hihat", 2, 0.5, True),
            ("kick", 3, 0, True),
            ("snare", 3, 0, True),
            ("hihat", 3, 0.5, False),
            ("hihat_open", 4, 0.5, True),  # Abierto en el 4
        ]
    },

    # ==========================================================================
    # STEPPERS PATTERNS (Sly Dunbar style)
    # ==========================================================================

    "steppers-basic": {
        "name": "Steppers Basico",
        "style": "steppers",
        "type": "rhythm",
        "length_bars": 1,
        "description": "Bombo en los 4 beats - hipnotico y trance",
        "compatible_drummers": ["sly-dunbar"],
        "events": [
            ("kick", 1, 0, True),
            ("hihat", 1, 0, False),
            ("hihat", 1, 0.5, False),
            ("kick", 2, 0, True),
            ("hihat", 2, 0, False),
            ("hihat", 2, 0.5, False),
            ("kick", 3, 0, True),
            ("snare", 3, 0, True),
            ("hihat", 3, 0, False),
            ("hihat", 3, 0.5, False),
            ("kick", 4, 0, True),
            ("hihat", 4, 0, False),
            ("hihat", 4, 0.5, False),
        ]
    },

    "steppers-heavy": {
        "name": "Steppers Pesado",
        "style": "steppers",
        "type": "rhythm",
        "length_bars": 1,
        "description": "Steppers con mas peso en el bombo",
        "compatible_drummers": ["sly-dunbar"],
        "events": [
            ("kick", 1, 0, True),
            ("hihat", 1, 0.5, False),
            ("kick", 2, 0, True),
            ("hihat", 2, 0.5, False),
            ("kick", 3, 0, True),
            ("snare", 3, 0, True),
            ("hihat", 3, 0.5, False),
            ("kick", 4, 0, True),
            ("hihat", 4, 0.5, False),
        ]
    },

    # ==========================================================================
    # ROCKERS PATTERNS
    # ==========================================================================

    "rockers-basic": {
        "name": "Rockers Basico",
        "style": "rockers",
        "type": "rhythm",
        "length_bars": 1,
        "description": "Variante mas sincopada del steppers",
        "compatible_drummers": ["sly-dunbar", "horsemouth-wallace"],
        "events": [
            ("kick", 1, 0, True),
            ("hihat", 1, 0.5, False),
            ("kick", 2, 0.5, False),       # Kick sincopado
            ("hihat", 2, 0.5, True),
            ("kick", 3, 0, True),
            ("snare", 3, 0, True),
            ("hihat", 3, 0.5, False),
            ("kick", 4, 0, True),
            ("hihat", 4, 0.5, True),
        ]
    },

    "rockers-syncopated": {
        "name": "Rockers Sincopado",
        "style": "rockers",
        "type": "rhythm",
        "length_bars": 1,
        "description": "Rockers con mas sincopa",
        "compatible_drummers": ["horsemouth-wallace"],
        "events": [
            ("kick", 1, 0, True),
            ("hihat", 1, 0, False),
            ("hihat", 1, 0.5, False),
            ("kick", 2, 0.5, True),        # Sincopa fuerte
            ("hihat", 2, 0, False),
            ("hihat", 2, 0.5, False),
            ("kick", 3, 0, True),
            ("snare", 3, 0, True),
            ("hihat", 3, 0, False),
            ("hihat", 3, 0.5, False),
            ("kick", 4, 0.5, False),       # Sincopa
            ("hihat", 4, 0, False),
            ("hihat", 4, 0.5, True),
        ]
    },

    # ==========================================================================
    # SKA PATTERNS (Lloyd Knibb style)
    # ==========================================================================

    "ska-basic": {
        "name": "Ska Basico",
        "style": "ska",
        "type": "rhythm",
        "length_bars": 1,
        "description": "El afterbeat clasico del ska",
        "compatible_drummers": ["lloyd-knibb"],
        "events": [
            ("kick", 1, 0, True),
            ("hihat", 1, 0, False),
            ("snare", 2, 0, True),         # Afterbeat
            ("hihat", 2, 0, True),
            ("kick", 3, 0, True),
            ("hihat", 3, 0, False),
            ("snare", 4, 0, True),         # Afterbeat
            ("hihat", 4, 0, True),
        ]
    },

    "ska-shuffle": {
        "name": "Ska Shuffle",
        "style": "ska",
        "type": "rhythm",
        "length_bars": 1,
        "description": "Ska con feel de shuffle",
        "compatible_drummers": ["lloyd-knibb"],
        "events": [
            ("kick", 1, 0, True),
            ("hihat", 1, 0, False),
            ("hihat", 1, 0.5, False),
            ("snare", 2, 0, True),
            ("hihat", 2, 0, True),
            ("hihat", 2, 0.5, False),
            ("kick", 3, 0, True),
            ("hihat", 3, 0, False),
            ("hihat", 3, 0.5, False),
            ("snare", 4, 0, True),
            ("hihat", 4, 0, True),
            ("hihat", 4, 0.5, False),
        ]
    },

    # ==========================================================================
    # ROOTS PATTERNS
    # ==========================================================================

    "roots-basic": {
        "name": "Roots Basico",
        "style": "roots",
        "type": "rhythm",
        "length_bars": 1,
        "description": "Patron roots reggae clasico",
        "compatible_drummers": ["carlton-barrett", "santa-davis"],
        "events": [
            ("hihat", 1, 0.5, False),
            ("hihat", 2, 0.5, True),
            ("kick", 3, 0, True),
            ("snare", 3, 0, True),
            ("hihat", 3, 0.5, False),
            ("hihat", 4, 0.5, True),
        ]
    },

    # ==========================================================================
    # FILLS
    # ==========================================================================

    "fill-1bar-simple": {
        "name": "Fill Simple 1 Compas",
        "style": "generic",
        "type": "fill",
        "length_bars": 1,
        "description": "Fill basico de 1 compas",
        "compatible_drummers": ["carlton-barrett", "sly-dunbar", "lloyd-knibb", "santa-davis", "horsemouth-wallace"],
        "events": [
            ("kick", 1, 0, True),
            ("snare", 2, 0, True),
            ("snare", 2, 0.5, False),
            ("snare", 3, 0, True),
            ("snare", 3, 0.5, False),
            ("snare", 4, 0, True),
            ("kick", 4, 0.5, True),
        ]
    },

    "fill-1bar-tom": {
        "name": "Fill con Toms 1 Compas",
        "style": "generic",
        "type": "fill",
        "length_bars": 1,
        "description": "Fill con toms descendentes",
        "compatible_drummers": ["carlton-barrett", "sly-dunbar", "lloyd-knibb", "santa-davis", "horsemouth-wallace"],
        "events": [
            ("kick", 1, 0, True),
            ("snare", 2, 0, True),
            ("snare", 3, 0, True),
            ("snare", 3, 0.5, True),
            ("snare", 4, 0, True),
            ("snare", 4, 0.5, True),
            ("kick", 4, 0.5, True),
        ]
    },

    "fill-2bar-buildup": {
        "name": "Fill Buildup 2 Compases",
        "style": "generic",
        "type": "fill",
        "length_bars": 2,
        "description": "Fill con crescendo de 2 compases",
        "compatible_drummers": ["carlton-barrett", "sly-dunbar", "santa-davis"],
        "events": [
            # Compas 1 - mas espaciado
            ("kick", 1, 0, True),
            ("snare", 2, 0, False),
            ("snare", 3, 0, True),
            ("snare", 4, 0, False),
            # Compas 2 - mas denso (beat + 4 = compas 2)
            ("snare", 5, 0, True),
            ("snare", 5, 0.5, False),
            ("snare", 6, 0, True),
            ("snare", 6, 0.5, True),
            ("snare", 7, 0, True),
            ("snare", 7, 0.5, True),
            ("kick", 8, 0, True),
            ("snare", 8, 0, True),
        ]
    },

    "fill-half-bar": {
        "name": "Fill Medio Compas",
        "style": "generic",
        "type": "fill",
        "length_bars": 1,
        "description": "Fill corto de medio compas (beats 3-4)",
        "compatible_drummers": ["carlton-barrett", "sly-dunbar", "lloyd-knibb", "santa-davis", "horsemouth-wallace"],
        "events": [
            # Mantener groove en beats 1-2
            ("hihat", 1, 0.5, False),
            ("hihat", 2, 0.5, True),
            # Fill en beats 3-4
            ("snare", 3, 0, True),
            ("snare", 3, 0.5, False),
            ("snare", 4, 0, True),
            ("kick", 4, 0.5, True),
        ]
    },

    # ==========================================================================
    # INTROS Y OUTROS
    # ==========================================================================

    "intro-count-2bar": {
        "name": "Intro Count-in 2 Compases",
        "style": "generic",
        "type": "intro",
        "length_bars": 2,
        "description": "Count-in con hi-hat",
        "compatible_drummers": ["carlton-barrett", "sly-dunbar", "lloyd-knibb", "santa-davis", "horsemouth-wallace"],
        "events": [
            # Solo hi-hat contando
            ("hihat", 1, 0, True),
            ("hihat", 2, 0, True),
            ("hihat", 3, 0, True),
            ("hihat", 4, 0, True),
            ("hihat", 5, 0, True),
            ("hihat", 6, 0, True),
            ("hihat", 7, 0, True),
            ("hihat", 8, 0, True),
        ]
    },

    "intro-sticks-1bar": {
        "name": "Intro Sticks 1 Compas",
        "style": "generic",
        "type": "intro",
        "length_bars": 1,
        "description": "Count-in con baquetas (rimshot)",
        "compatible_drummers": ["carlton-barrett", "sly-dunbar", "lloyd-knibb", "santa-davis", "horsemouth-wallace"],
        "events": [
            ("rimshot", 1, 0, True),
            ("rimshot", 2, 0, True),
            ("rimshot", 3, 0, True),
            ("rimshot", 4, 0, True),
        ]
    },

    "outro-hit": {
        "name": "Outro Hit Final",
        "style": "generic",
        "type": "outro",
        "length_bars": 1,
        "description": "Golpe final contundente",
        "compatible_drummers": ["carlton-barrett", "sly-dunbar", "lloyd-knibb", "santa-davis", "horsemouth-wallace"],
        "events": [
            ("kick", 1, 0, True),
            ("snare", 1, 0, True),
            ("hihat_open", 1, 0, True),
        ]
    },

    "outro-fade": {
        "name": "Outro Fade",
        "style": "generic",
        "type": "outro",
        "length_bars": 2,
        "description": "Outro con fade out gradual",
        "compatible_drummers": ["carlton-barrett", "sly-dunbar", "lloyd-knibb", "santa-davis", "horsemouth-wallace"],
        "events": [
            # Compas 1 - normal
            ("kick", 3, 0, True),
            ("snare", 3, 0, True),
            ("hihat", 1, 0.5, False),
            ("hihat", 2, 0.5, True),
            ("hihat", 3, 0.5, False),
            ("hihat", 4, 0.5, True),
            # Compas 2 - solo hi-hat
            ("hihat", 5, 0.5, False),
            ("hihat", 6, 0.5, False),
            ("hihat", 7, 0.5, False),
            ("hihat_open", 8, 0, True),
        ]
    },

    # ==========================================================================
    # BREAKS
    # ==========================================================================

    "break-stop": {
        "name": "Break Stop",
        "style": "generic",
        "type": "break",
        "length_bars": 1,
        "description": "Silencio dramatico de 1 compas",
        "compatible_drummers": ["carlton-barrett", "sly-dunbar", "lloyd-knibb", "santa-davis", "horsemouth-wallace"],
        "events": []  # Silencio total
    },

    "break-kick-only": {
        "name": "Break Solo Bombo",
        "style": "generic",
        "type": "break",
        "length_bars": 1,
        "description": "Solo bombo en beat 1",
        "compatible_drummers": ["carlton-barrett", "sly-dunbar", "lloyd-knibb", "santa-davis", "horsemouth-wallace"],
        "events": [
            ("kick", 1, 0, True),
        ]
    },
}


# ==============================================================================
# ACCESS FUNCTIONS
# ==============================================================================

def get_pattern(pattern_id: str) -> dict:
    """
    Obtiene un patron por su ID.

    Args:
        pattern_id: ID del patron

    Returns:
        Diccionario con el patron

    Raises:
        ValueError: Si el patron no existe
    """
    if pattern_id not in PATTERN_LIBRARY:
        available = list_patterns()
        raise ValueError(
            f"Patron '{pattern_id}' no encontrado. "
            f"Disponibles: {', '.join(available[:5])}..."
        )
    return PATTERN_LIBRARY[pattern_id]


def list_patterns() -> List[str]:
    """
    Lista todos los patrones disponibles.

    Returns:
        Lista de IDs de patrones
    """
    return list(PATTERN_LIBRARY.keys())


def get_patterns_by_style(style: str) -> List[str]:
    """
    Filtra patrones por estilo.

    Args:
        style: Estilo a buscar (one-drop, steppers, ska, etc.)

    Returns:
        Lista de IDs de patrones con ese estilo
    """
    return [
        pid for pid, p in PATTERN_LIBRARY.items()
        if p.get("style") == style
    ]


def get_patterns_by_type(pattern_type: str) -> List[str]:
    """
    Filtra patrones por tipo.

    Args:
        pattern_type: Tipo a buscar (rhythm, fill, intro, outro, break)

    Returns:
        Lista de IDs de patrones de ese tipo
    """
    return [
        pid for pid, p in PATTERN_LIBRARY.items()
        if p.get("type") == pattern_type
    ]


def get_patterns_for_drummer(drummer_slug: str) -> List[str]:
    """
    Obtiene patrones compatibles con un baterista.

    Args:
        drummer_slug: ID del baterista

    Returns:
        Lista de IDs de patrones compatibles
    """
    return [
        pid for pid, p in PATTERN_LIBRARY.items()
        if drummer_slug in p.get("compatible_drummers", [])
    ]


def get_available_pattern_types() -> List[str]:
    """
    Lista todos los tipos de patron disponibles.

    Returns:
        Lista de tipos unicos
    """
    return list(set(p["type"] for p in PATTERN_LIBRARY.values()))


# ==============================================================================
# TEST
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DE PATTERN LIBRARY")
    print("=" * 60)

    print(f"\nPatrones disponibles: {len(list_patterns())}")
    print(f"Tipos disponibles: {get_available_pattern_types()}")

    print("\n--- Patrones por estilo ---")
    for style in ["one-drop", "steppers", "ska", "rockers", "roots", "generic"]:
        patterns = get_patterns_by_style(style)
        print(f"  {style}: {len(patterns)} patrones")

    print("\n--- Patrones por tipo ---")
    for ptype in get_available_pattern_types():
        patterns = get_patterns_by_type(ptype)
        print(f"  {ptype}: {patterns}")

    print("\n--- Patrones para Carlton Barrett ---")
    carlton_patterns = get_patterns_for_drummer("carlton-barrett")
    print(f"  {len(carlton_patterns)} patrones: {carlton_patterns[:5]}...")

    print("\n--- Detalle de one-drop-basic ---")
    pattern = get_pattern("one-drop-basic")
    print(f"  Nombre: {pattern['name']}")
    print(f"  Estilo: {pattern['style']}")
    print(f"  Duracion: {pattern['length_bars']} compas(es)")
    print(f"  Eventos: {len(pattern['events'])}")
    for event in pattern['events']:
        inst, beat, sub, accent = event
        sub_str = "+" if sub == 0.5 else ""
        acc_str = "*" if accent else ""
        print(f"    {inst}: beat {beat}{sub_str} {acc_str}")

    print("\n" + "=" * 60)
    print("TEST PASADO")
    print("=" * 60)
