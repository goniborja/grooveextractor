#!/usr/bin/env python3
"""
Script de verificación de instalación para Groove Extractor.
Verifica que todas las dependencias estén correctamente instaladas.
"""

import sys

def test_imports():
    """Prueba que todas las librerías necesarias puedan importarse."""

    print("=" * 60)
    print("GROOVE EXTRACTOR - Test de Instalación")
    print("=" * 60)
    print()

    tests = {
        'PyQt6': 'PyQt6',
        'NumPy': 'numpy',
        'SciPy': 'scipy',
        'Librosa': 'librosa',
        'SoundFile': 'soundfile',
        'Pandas': 'pandas',
        'Matplotlib': 'matplotlib',
        'Madmom (opcional)': 'madmom'
    }

    results = {}

    for name, module in tests.items():
        try:
            __import__(module)
            results[name] = '✅ OK'
        except ImportError as e:
            if 'opcional' in name.lower():
                results[name] = '⚠️  No instalado (opcional)'
            else:
                results[name] = f'❌ ERROR: {str(e)}'

    # Mostrar resultados
    print("Resultados de las pruebas:\n")
    for name, status in results.items():
        print(f"  {name:25} {status}")

    print()
    print("-" * 60)

    # Verificar versiones de librerías críticas
    try:
        import numpy as np
        import librosa
        print(f"\nVersiones:")
        print(f"  NumPy: {np.__version__}")
        print(f"  Librosa: {librosa.__version__}")

        try:
            import madmom
            print(f"  Madmom: {madmom.__version__}")
        except:
            print(f"  Madmom: No instalado (se usará solo librosa)")

    except Exception as e:
        print(f"\nError al verificar versiones: {e}")

    print()
    print("=" * 60)

    # Verificar si se puede importar el módulo de análisis
    try:
        from groove_analyzer import GrooveAnalyzer
        print("✅ Módulo groove_analyzer importado correctamente")
    except Exception as e:
        print(f"❌ Error al importar groove_analyzer: {e}")
        return False

    # Verificar Python version
    python_version = sys.version_info
    print(f"\nPython {python_version.major}.{python_version.minor}.{python_version.micro}")

    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("⚠️  Advertencia: Se recomienda Python 3.8 o superior")
    else:
        print("✅ Versión de Python compatible")

    print()
    print("=" * 60)
    print("Instalación verificada. Puedes ejecutar: python extractor_app.py")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
