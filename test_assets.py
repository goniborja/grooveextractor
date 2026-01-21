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


def check_image_loader_module():
    """Verifica que el módulo image_loader.py existe."""
    print("\n=== VERIFICANDO MÓDULO IMAGE_LOADER ===")

    loader_path = Path("ui") / "widgets" / "image_loader.py"
    if loader_path.exists():
        print(f"  OK: {loader_path} existe")
        return []
    else:
        print(f"  ERROR: {loader_path} NO EXISTE")
        return [loader_path]


def check_widgets_use_load_pixmap():
    """Verifica que los widgets usen load_pixmap en lugar de QPixmap directo."""
    print("\n=== VERIFICANDO USO DE load_pixmap EN WIDGETS ===")

    widgets_dir = Path("ui") / "widgets"
    widget_files = [
        "filmstrip_knob.py",
        "filmstrip_slider.py",
        "animated_led.py",
        "animated_vu_meter.py",
        "image_button.py",
        "image_pad.py",
        "image_switch.py",
        "vintage_screen.py",
    ]

    errors = []
    for widget_file in widget_files:
        file_path = widgets_dir / widget_file
        if not file_path.exists():
            errors.append(f"{widget_file}: archivo no existe")
            continue

        content = file_path.read_text()

        # Verificar que importa load_pixmap
        if "from .image_loader import load_pixmap" not in content:
            errors.append(f"{widget_file}: no importa load_pixmap")

        # Verificar que no usa QPixmap( directamente para cargar archivos
        # (excepto en casos legítimos donde se usa internamente)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'QPixmap(' in line and ('path' in line.lower() or '.png' in line.lower()):
                if 'load_pixmap' not in line and '# Cargar' not in lines[i-2] if i > 1 else True:
                    # Solo reportar si parece una carga de archivo, no uso interno
                    if any(x in line for x in ['strip_path', 'frame_path', 'image', 'bg_image']):
                        errors.append(f"{widget_file}:{i}: QPixmap directo detectado")

    if not errors:
        print("  OK: Todos los widgets usan load_pixmap")
    else:
        print(f"  ADVERTENCIA: {len(errors)} posibles problemas:")
        for e in errors:
            print(f"    - {e}")

    return errors


def check_main_window():
    """Verifica que main_window.py use load_pixmap."""
    print("\n=== VERIFICANDO main_window.py ===")

    main_window_path = Path("ui") / "main_window.py"
    if not main_window_path.exists():
        print(f"  ERROR: {main_window_path} no existe")
        return [main_window_path]

    content = main_window_path.read_text()
    errors = []

    # Verificar que importa load_pixmap
    if "from .widgets.image_loader import load_pixmap" not in content:
        errors.append("main_window.py: no importa load_pixmap")

    # Verificar que usa load_pixmap para wallpaper
    if "load_pixmap(str(wallpaper_path))" in content:
        print("  OK: Wallpaper usa load_pixmap")
    elif "QPixmap(str(wallpaper_path))" in content:
        errors.append("main_window.py: wallpaper usa QPixmap directo")
    else:
        print("  INFO: Wallpaper no encontrado (verificar manualmente)")

    if not errors:
        print("  OK: main_window.py correctamente configurado")

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

    # Verificar módulo image_loader
    all_errors.extend(check_image_loader_module())

    # Verificar widgets usan load_pixmap
    all_errors.extend(check_widgets_use_load_pixmap())

    # Verificar main_window.py
    all_errors.extend(check_main_window())

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
