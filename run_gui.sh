#!/bin/bash
# Script para ejecutar Groove Extractor GUI

echo "🥁 Iniciando Groove Extractor..."
echo ""

# Verificar si estamos en un entorno con display
if [ -z "$DISPLAY" ]; then
    echo "⚠️  No se detectó display gráfico."
    echo "Ejecutando con Xvfb (Virtual Framebuffer)..."
    export QT_QPA_PLATFORM=offscreen
    xvfb-run -a venv/bin/python extractor_app.py
else
    echo "✅ Display detectado: $DISPLAY"
    venv/bin/python extractor_app.py
fi
