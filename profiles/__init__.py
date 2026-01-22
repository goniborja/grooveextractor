"""
Book of Drums - Profiles Module

Perfiles de bateristas jamaicanos y biblioteca de patrones.

Uso:
    from profiles import get_profile, list_drummers, get_pattern, list_patterns

    # Obtener perfil de Carlton Barrett
    profile = get_profile("carlton-barrett")

    # Listar todos los bateristas
    drummers = list_drummers()

    # Obtener patron one-drop basico
    pattern = get_pattern("one-drop-basic")
"""

from .drummer_profiles import (
    DRUMMER_PROFILES,
    get_profile,
    list_drummers,
    get_drummers_by_style,
    get_available_styles,
)

from .pattern_library import (
    PATTERN_LIBRARY,
    get_pattern,
    list_patterns,
    get_patterns_by_style,
    get_patterns_by_type,
    get_patterns_for_drummer,
    get_available_pattern_types,
)

__all__ = [
    # Drummer profiles
    "DRUMMER_PROFILES",
    "get_profile",
    "list_drummers",
    "get_drummers_by_style",
    "get_available_styles",
    # Pattern library
    "PATTERN_LIBRARY",
    "get_pattern",
    "list_patterns",
    "get_patterns_by_style",
    "get_patterns_by_type",
    "get_patterns_for_drummer",
    "get_available_pattern_types",
]
