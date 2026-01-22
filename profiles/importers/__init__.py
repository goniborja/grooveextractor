"""
Book of Drums - Profile Importers

Importadores para generar perfiles de bateristas desde fuentes externas.

Uso:
    from profiles.importers import GrooveExtractorImporter

    # Importar perfiles desde database.xlsx
    importer = GrooveExtractorImporter("database.xlsx")
    profiles = importer.import_all_profiles()

Nota: Requiere pandas y openpyxl instalados.
    pip install pandas openpyxl
"""

try:
    from .from_groove_extractor import GrooveExtractorImporter
    _GE_AVAILABLE = True
except ImportError:
    _GE_AVAILABLE = False
    GrooveExtractorImporter = None

__all__ = [
    "GrooveExtractorImporter",
]


def is_groove_extractor_available() -> bool:
    """Verifica si el importador de Groove Extractor esta disponible."""
    return _GE_AVAILABLE
