"""
Book of Drums - Groove Extractor Importer

Importa datos de Groove Extractor (database.xlsx) para generar
perfiles de bateristas automaticamente basados en analisis real.

El flujo es:
1. Leer database.xlsx generado por Groove Extractor
2. Agrupar canciones por baterista (segun carpeta o metadatos)
3. Calcular estadisticas de timing/velocity/swing
4. Generar/actualizar perfiles automaticamente
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

# Intentar importar pandas, mostrar mensaje si no esta disponible
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class GrooveExtractorImporter:
    """
    Importa datos de Groove Extractor y genera perfiles de bateristas.

    Groove Extractor produce un archivo database.xlsx con:
    - filename: nombre del archivo analizado
    - bpm: tempo detectado
    - style: estilo sugerido (one-drop, steppers, etc.)
    - kick_onsets, snare_onsets, hihat_onsets: tiempos de golpes
    - swing_amount: cantidad de swing
    - timing_variations: desviaciones del grid

    Este importador agrupa los datos por baterista y genera perfiles
    con valores reales derivados del analisis.
    """

    # Mapeo de estilos de Groove Extractor a Book of Drums
    STYLE_MAP = {
        "one_drop": "one-drop",
        "one-drop": "one-drop",
        "steppers": "steppers",
        "rockers": "rockers",
        "ska": "ska",
        "roots": "roots",
        "reggae": "one-drop",  # Default reggae -> one-drop
        "dub": "one-drop",
        "unknown": "one-drop",
    }

    # Mapeo de feel segun variacion de timing
    FEEL_MAP = {
        "very_consistent": "on-beat",      # < 20% variacion
        "consistent": "on-beat",           # 20-35%
        "normal": "laid-back",             # 35-55%
        "expressive": "laid-back",         # 55-70%
        "very_expressive": "deep-pocket",  # > 70%
    }

    def __init__(self, database_path: str):
        """
        Args:
            database_path: Ruta a database.xlsx de Groove Extractor
        """
        if not PANDAS_AVAILABLE:
            raise ImportError(
                "pandas es necesario para importar datos de Groove Extractor. "
                "Instalar con: pip install pandas openpyxl"
            )

        self.database_path = Path(database_path)
        self.data: Optional[pd.DataFrame] = None

    def load_database(self) -> 'pd.DataFrame':
        """
        Carga el Excel de Groove Extractor.

        Returns:
            DataFrame con los datos del analisis

        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        if not self.database_path.exists():
            raise FileNotFoundError(f"No se encontro: {self.database_path}")

        self.data = pd.read_excel(self.database_path)
        return self.data

    def extract_drummer_from_path(self, filepath: str) -> Optional[str]:
        """
        Extrae el nombre del baterista desde la ruta del archivo.

        Asume estructura: .../style/era/drummer/song.wav
        o: .../drummer/song.wav

        Args:
            filepath: Ruta del archivo de audio

        Returns:
            Slug del baterista o None si no se puede determinar
        """
        parts = Path(filepath).parts

        if len(parts) >= 2:
            # Intentar obtener el directorio padre como nombre de baterista
            potential_drummer = parts[-2]

            # Limpiar y convertir a slug
            slug = self._to_slug(potential_drummer)

            # Verificar que no sea un directorio generico
            generic_dirs = ["audio", "music", "songs", "tracks", "drums", "samples"]
            if slug not in generic_dirs:
                return slug

        return None

    def _to_slug(self, name: str) -> str:
        """
        Convierte un nombre a slug.

        Args:
            name: Nombre original

        Returns:
            Slug en formato lowercase-with-dashes
        """
        # Convertir a minusculas y reemplazar espacios/underscores con guiones
        slug = name.lower().replace(" ", "-").replace("_", "-")

        # Eliminar caracteres especiales
        slug = "".join(c for c in slug if c.isalnum() or c == "-")

        # Eliminar guiones duplicados
        while "--" in slug:
            slug = slug.replace("--", "-")

        return slug.strip("-")

    def group_by_drummer(self) -> Dict[str, 'pd.DataFrame']:
        """
        Agrupa las canciones por baterista.

        Returns:
            Diccionario {drummer_slug: DataFrame con sus canciones}
        """
        if self.data is None:
            self.load_database()

        # Intentar usar columna 'drummer' si existe
        if 'drummer' in self.data.columns:
            return {name: group for name, group in self.data.groupby('drummer')}

        # Si no, extraer del path
        self.data['drummer'] = self.data['filename'].apply(self.extract_drummer_from_path)
        self.data = self.data.dropna(subset=['drummer'])

        return {name: group for name, group in self.data.groupby('drummer')}

    def calculate_profile_stats(self, drummer_data: 'pd.DataFrame') -> dict:
        """
        Calcula estadisticas para generar un perfil.

        Args:
            drummer_data: DataFrame con canciones de un baterista

        Returns:
            Diccionario con estadisticas calculadas
        """
        stats = {
            "num_songs": len(drummer_data),
            "bpm_mean": drummer_data['bpm'].mean() if 'bpm' in drummer_data.columns else 75,
            "bpm_min": drummer_data['bpm'].min() if 'bpm' in drummer_data.columns else 65,
            "bpm_max": drummer_data['bpm'].max() if 'bpm' in drummer_data.columns else 85,
        }

        # Swing
        if 'swing_amount' in drummer_data.columns:
            swing_values = drummer_data['swing_amount'].dropna()
            if len(swing_values) > 0:
                stats['swing_mean'] = swing_values.mean()
                stats['swing_std'] = swing_values.std()
                # Convertir a porcentaje (50 = sin swing, 66 = shuffle completo)
                stats['swing_percent'] = 50 + (stats['swing_mean'] * 16)
            else:
                stats['swing_percent'] = 55

        # Timing variations (para calcular humanize_percent)
        if 'timing_variations' in drummer_data.columns:
            var_values = drummer_data['timing_variations'].dropna()
            if len(var_values) > 0:
                var_mean = var_values.mean()
                # Mapear a escala 15-85
                stats['humanize_percent'] = min(85, max(15, int(var_mean * 100)))
            else:
                stats['humanize_percent'] = 50

        # Offset de timing (si hay datos de deviation)
        if 'kick_timing_deviation' in drummer_data.columns:
            kick_dev = drummer_data['kick_timing_deviation'].dropna()
            if len(kick_dev) > 0:
                # Convertir desviacion en ms a ticks (asumiendo 480 ticks/beat, 75 BPM)
                # 1 beat = 800ms a 75 BPM, 1 tick = 800/480 = 1.67ms
                avg_dev_ms = kick_dev.mean()
                stats['kick_offset_ticks'] = int(avg_dev_ms / 1.67)

        if 'snare_timing_deviation' in drummer_data.columns:
            snare_dev = drummer_data['snare_timing_deviation'].dropna()
            if len(snare_dev) > 0:
                avg_dev_ms = snare_dev.mean()
                stats['snare_offset_ticks'] = int(avg_dev_ms / 1.67)

        # Estilo mas comun
        if 'style' in drummer_data.columns:
            style_counts = drummer_data['style'].value_counts()
            if len(style_counts) > 0:
                raw_style = style_counts.index[0]
                stats['style'] = self.STYLE_MAP.get(str(raw_style).lower(), 'one-drop')

        return stats

    def _determine_feel(self, humanize_percent: int) -> str:
        """
        Determina el feel basado en humanize_percent.

        Args:
            humanize_percent: Porcentaje de humanizacion (15-85)

        Returns:
            String del feel: 'on-top', 'on-beat', 'laid-back', 'deep-pocket'
        """
        if humanize_percent < 25:
            return "on-beat"
        elif humanize_percent < 45:
            return "on-beat"
        elif humanize_percent < 65:
            return "laid-back"
        else:
            return "deep-pocket"

    def generate_profile(self, drummer_slug: str, drummer_data: 'pd.DataFrame') -> dict:
        """
        Genera un perfil de baterista a partir de datos analizados.

        Args:
            drummer_slug: ID del baterista
            drummer_data: DataFrame con sus canciones

        Returns:
            Diccionario con el perfil generado
        """
        stats = self.calculate_profile_stats(drummer_data)

        # Nombre legible
        name = drummer_slug.replace("-", " ").title()

        # Determinar valores basados en estilo y estadisticas
        style = stats.get('style', 'one-drop')
        humanize = stats.get('humanize_percent', 50)
        swing = stats.get('swing_percent', 55)

        # Ajustar beats segun estilo
        kick_beats = [3] if style == "one-drop" else [1, 3] if style in ["ska", "roots"] else [1, 2, 3, 4]
        snare_beats = [3] if style in ["one-drop", "steppers", "roots", "rockers"] else [2, 4]

        profile = {
            "name": name,
            "slug": drummer_slug,
            "signature": f"Perfil generado desde {stats['num_songs']} canciones",
            "style": style,
            "era": "auto-detected",
            "bpm_range": (int(stats['bpm_min']), int(stats['bpm_max'])),
            "source": "groove-extractor",
            "num_analyzed_songs": stats['num_songs'],

            "kick": {
                "beats": kick_beats,
                "offset_ticks": stats.get('kick_offset_ticks', 8),
                "velocity_base": 100,
                "velocity_variance": 5,
                "ghost_probability": 0.1,
                "ghost_beats": [1],
                "ghost_velocity": 40
            },

            "snare": {
                "beats": snare_beats,
                "offset_ticks": stats.get('snare_offset_ticks', 10),
                "velocity_base": 100,
                "velocity_variance": 8,
                "rimshot_probability": 0.8,
                "ghost_probability": 0.25,
                "ghost_beats": ["2", "2+", "4", "4+"],
                "ghost_velocity": 35,
                "flam_probability": 0.05,
                "drag_probability": 0.02
            },

            "hihat": {
                "pattern": "offbeat" if style in ["one-drop", "roots"] else "8ths",
                "swing_percent": int(swing),
                "open_on_beats": ["4"],
                "velocity_base": 80,
                "velocity_variance": 12,
                "accent_beats": ["2", "4"],
                "tightness": "medium"
            },

            "global": {
                "feel": self._determine_feel(humanize),
                "humanize_percent": humanize
            }
        }

        return profile

    def import_all_profiles(self) -> Dict[str, dict]:
        """
        Importa todos los bateristas del database.xlsx.

        Returns:
            Diccionario de perfiles generados
        """
        groups = self.group_by_drummer()
        profiles = {}

        for drummer_slug, data in groups.items():
            if drummer_slug:
                profile = self.generate_profile(drummer_slug, data)
                profiles[drummer_slug] = profile
                print(f"  Generado perfil para: {profile['name']} ({len(data)} canciones)")

        return profiles

    def export_to_python(self, profiles: Dict[str, dict], output_path: str):
        """
        Exporta los perfiles a un archivo Python.

        Args:
            profiles: Diccionario de perfiles
            output_path: Ruta del archivo de salida
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('"""Perfiles generados automaticamente desde Groove Extractor."""\n\n')
            f.write("IMPORTED_PROFILES = ")
            f.write(json.dumps(profiles, indent=4, ensure_ascii=False))
            f.write("\n")

        print(f"Exportado a: {output_path}")

    def export_to_json(self, profiles: Dict[str, dict], output_path: str):
        """
        Exporta los perfiles a un archivo JSON.

        Args:
            profiles: Diccionario de perfiles
            output_path: Ruta del archivo de salida
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=4, ensure_ascii=False)

        print(f"Exportado a: {output_path}")

    def merge_with_existing(self, new_profiles: Dict[str, dict],
                           existing_profiles: Dict[str, dict],
                           prefer_existing: bool = True) -> Dict[str, dict]:
        """
        Combina perfiles nuevos con existentes.

        Args:
            new_profiles: Perfiles importados
            existing_profiles: Perfiles existentes
            prefer_existing: Si True, mantiene valores existentes cuando hay conflicto

        Returns:
            Diccionario combinado de perfiles
        """
        merged = existing_profiles.copy()

        for slug, new_profile in new_profiles.items():
            if slug in merged:
                if prefer_existing:
                    # Solo actualizar campos que no existen
                    for key, value in new_profile.items():
                        if key not in merged[slug]:
                            merged[slug][key] = value
                    # Actualizar info de fuente
                    merged[slug]["also_analyzed_by"] = "groove-extractor"
                    merged[slug]["analyzed_songs"] = new_profile.get("num_analyzed_songs", 0)
                else:
                    # Reemplazar completamente
                    merged[slug] = new_profile
            else:
                # Nuevo baterista
                merged[slug] = new_profile

        return merged


# ==============================================================================
# TEST / CLI
# ==============================================================================

if __name__ == "__main__":
    import sys

    if not PANDAS_AVAILABLE:
        print("ERROR: pandas no esta instalado.")
        print("Instalar con: pip install pandas openpyxl")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("=" * 60)
        print("GROOVE EXTRACTOR IMPORTER")
        print("=" * 60)
        print("\nUso: python from_groove_extractor.py <database.xlsx> [output.json]")
        print("\nEjemplos:")
        print("  python from_groove_extractor.py database.xlsx")
        print("  python from_groove_extractor.py database.xlsx imported_profiles.json")
        print("\nEl archivo database.xlsx es generado por Groove Extractor")
        print("al analizar archivos de audio.")
        sys.exit(0)

    database_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "imported_profiles.json"

    print("=" * 60)
    print("IMPORTADOR DE GROOVE EXTRACTOR")
    print("=" * 60)

    try:
        importer = GrooveExtractorImporter(database_path)

        print(f"\nCargando: {database_path}")
        importer.load_database()
        print(f"Canciones encontradas: {len(importer.data)}")

        print("\nGenerando perfiles...")
        profiles = importer.import_all_profiles()

        print(f"\nPerfiles generados: {len(profiles)}")

        # Exportar
        if output_path.endswith('.py'):
            importer.export_to_python(profiles, output_path)
        else:
            importer.export_to_json(profiles, output_path)

        print("\n" + "=" * 60)
        print("IMPORTACION COMPLETADA")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
