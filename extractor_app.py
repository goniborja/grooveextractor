#!/usr/bin/env python3
"""
GROOVE EXTRACTOR
================
Herramienta de análisis DSP para extracción de grooves de batería.

Autor: DSP Engineer / Data Architect
Fecha: 2026-01-18
Versión: 2.0.0

Esta versión usa widgets custom del paquete ui.widgets.
"""

import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    """Función principal."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
