#!/usr/bin/env python3
"""
test_assets.py - Verifica que todos los assets de la UI existen.
Ejecutar antes de hacer push para garantizar integridad.
"""

from pathlib import Path
import sys

# Rutas base
ASSETS_BASE = Path("assets") / "ui" / "vintage_obsession"
ASSETS_DIR = ASSETS_BASE / "Assets"
ONESHOTS_DIR = ASSETS_DIR / "Animations" / "Oneshots"
STRIPS_DIR = ASSETS_DIR / "Animations" / "Strips"
VU_METER_DIR = ONESHOTS_DIR / "VU_meter"

# Assets individuales requeridos
REQUIRED_ASSETS = {
    # Wallpaper
    ASSETS_BASE / "Vintage_GUI_KIT_wallpaper_a.png": "Fondo de ventana",

    # Screen
    ASSETS_DIR / "screen.png": "VintageScreen background",

    # Pads (Oneshots)
    ONESHOTS_DIR / "pad_off.png": "ImagePad estado OFF",
    ONESHOTS_DIR / "pad_on.png": "ImagePad estado ON",

    # Switches (Oneshots)
    ONESHOTS_DIR / "switch_hor_st1.png": "ImageSwitch estado 1",
    ONESHOTS_DIR / "switch_hor_st2.png": "ImageSwitch estado 2",

    # Filmstrips (Strips)
    STRIPS_DIR / "Ver_slider.png": "FilmstripSlider vertical",
    STRIPS_DIR / "Hor_slider.png": "FilmstripSlider horizontal",
    STRIPS_DIR / "Knob_mid.png": "FilmstripKnob",
    STRIPS_DIR / "LED_meter.png": "AnimatedLED",
    STRIPS_DIR / "but_big_rectangle.png": "ImageButton",
}

# VU Meter frames (256 frames individuales)
VU_METER_FRAMES = 256


def check_single_assets():
    """Verifica que todos los assets individuales existen."""
    print("\n=== VERIFICANDO ASSETS INDIVIDUALES ===")
    errors = []

    for path, description in REQUIRED_ASSETS.items():
        if path.exists():
            print(f"  OK: {path.name} ({description})")
        else:
            print(f"  ERROR: {path} NO EXISTE ({description})")
            errors.append(path)

    return errors


def check_vu_meter_frames():
    """Verifica que todos los frames del VU meter existen."""
    print(f"\n=== VERIFICANDO VU METER ({VU_METER_FRAMES} frames) ===")

    if not VU_METER_DIR.exists():
        print(f"  ERROR: Directorio {VU_METER_DIR} NO EXISTE")
        return [VU_METER_DIR]

    errors = []
    found = 0

    for i in range(VU_METER_FRAMES):
        frame_path = VU_METER_DIR / f"VU_meter_{i:04d}.png"
        if frame_path.exists():
            found += 1
        else:
            errors.append(frame_path)

    if not errors:
        print(f"  OK: {found}/{VU_METER_FRAMES} frames encontrados")
    else:
        print(f"  ERROR: {len(errors)} frames faltantes")
        for e in errors[:5]:  # Mostrar solo los primeros 5
            print(f"    - {e}")
        if len(errors) > 5:
            print(f"    ... y {len(errors) - 5} más")

    return errors


def check_str_conversion():
    """Verifica que main_window.py use str() en todas las llamadas a QPixmap."""
    print("\n=== VERIFICANDO USO DE str() EN QPIXMAP ===")

    main_window_path = Path("ui") / "main_window.py"
    if not main_window_path.exists():
        print(f"  ERROR: {main_window_path} no existe")
        return [main_window_path]

    content = main_window_path.read_text()
    errors = []

    # Buscar patrones problemáticos
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        # Buscar QPixmap sin str()
        if 'QPixmap(' in line and '_DIR /' in line and 'str(' not in line:
            errors.append(f"Línea {i}: QPixmap sin str() - {line.strip()}")

    if not errors:
        print("  OK: Todas las llamadas QPixmap usan str()")
    else:
        print(f"  ERROR: {len(errors)} llamadas QPixmap sin str():")
        for e in errors:
            print(f"    - {e}")

    return errors


def main():
    """Ejecuta todas las verificaciones."""
    print("=" * 60)
    print("  TEST DE ASSETS PARA GROOVE EXTRACTOR")
    print("=" * 60)

    all_errors = []

    # Verificar assets individuales
    all_errors.extend(check_single_assets())

    # Verificar VU meter frames
    all_errors.extend(check_vu_meter_frames())

    # Verificar uso de str() en QPixmap
    str_errors = check_str_conversion()
    all_errors.extend(str_errors)

    # Resumen
    print("\n" + "=" * 60)
    if all_errors:
        print(f"  RESULTADO: FALLÓ - {len(all_errors)} errores encontrados")
        print("=" * 60)
        return 1
    else:
        print("  RESULTADO: PASÓ - Todos los assets verificados")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
