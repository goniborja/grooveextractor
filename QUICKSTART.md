# ⚡ QUICKSTART - Groove Extractor

## 🚀 Inicio Rápido en 3 Pasos

### 1. Instalar Dependencias
```bash
source venv/bin/activate
pip install PyQt6 librosa soundfile audioread numpy scipy pandas matplotlib
```

### 2. Probar el Motor DSP (sin GUI)
```bash
./demo_sin_gui.py
```

Este script:
- ✅ Crea un archivo de audio de prueba
- ✅ Detecta onsets automáticamente
- ✅ Calcula dinámica y micro-timing
- ✅ Genera estadísticas de humanización
- ✅ Exporta resultados a JSON

**Salida esperada:**
```
🥁 GROOVE EXTRACTOR - DEMOSTRACIÓN DSP
======================================

✅ Audio cargado: test_groove.wav
✅ Onsets detectados: 11
✅ Análisis completado

ESTADÍSTICAS DE HUMANIZACIÓN:
  - avg_timing_deviation_ms: -4.280
  - std_timing_deviation_ms: 3.066
  - avg_velocity_variation: 0.086
  - swing_factor: 0.047

🎵 Demostración completada exitosamente!
```

### 3. Ver Resultados
```bash
cat /tmp/groove_analysis_demo.json | head -50
```

---

## 🖥️ Ejecutar la GUI (si tienes display gráfico)

```bash
./run_gui.sh
```

Si no tienes display (servidor remoto), usa el demo sin GUI.

---

## 📊 Archivos Generados

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| Audio de prueba | `/tmp/test_groove.wav` | Archivo WAV sintético de 4 segundos |
| Análisis JSON | `/tmp/groove_analysis_demo.json` | Resultados completos del análisis |

---

## 🔧 Uso Programático

### Analizar tu propio archivo de audio:

```python
from groove_analyzer import GrooveAnalyzer

# Inicializar
analyzer = GrooveAnalyzer()

# Cargar tu archivo
analyzer.load_audio("mi_groove.wav")

# Detectar onsets
analyzer.detect_onsets(method='librosa')

# Analizar dinámica
analyzer.analyze_dynamics()

# Calcular micro-timing
analyzer.calculate_timing_deviations(tempo_bpm=120.0)

# Obtener resultados
results = analyzer.get_results()

# Exportar a JSON
import json
with open('mi_analisis.json', 'w') as f:
    json.dump(results, f, indent=2)
```

---

## 📁 Estructura de Salida JSON

```json
{
  "metadata": {
    "audio_file": "groove.wav",
    "sample_rate": 44100,
    "duration_seconds": 4.0,
    "tempo_bpm": 120.0,
    "time_signature": "4/4"
  },
  "groove_data": [
    {
      "onset_time": 0.499,
      "beat_position": 2.0,
      "bar_number": 1,
      "drum_type": "hihat",
      "velocity": 91,
      "amplitude_db": -20.97,
      "timing_deviation_ms": -0.77,
      "velocity_variation": 0.096,
      "onset_strength": 0.85
    }
  ],
  "humanization_stats": {
    "avg_timing_deviation_ms": -4.28,
    "std_timing_deviation_ms": 3.07,
    "avg_velocity_variation": 0.086,
    "swing_factor": 0.047
  }
}
```

---

## 🎯 Casos de Uso

### 1. Analizar timing de baterista
```bash
# Analizar un archivo de batería grabado
python -c "
from groove_analyzer import GrooveAnalyzer
import json

analyzer = GrooveAnalyzer()
analyzer.load_audio('grabacion_bateria.wav')
analyzer.detect_onsets()
analyzer.analyze_dynamics()
analyzer.calculate_timing_deviations(tempo_bpm=140)

results = analyzer.get_results()
print(f'Desviación temporal: {results[\"humanization_stats\"][\"avg_timing_deviation_ms\"]:.2f}ms')
print(f'Swing factor: {results[\"humanization_stats\"][\"swing_factor\"]:.3f}')
"
```

### 2. Comparar dos grooves
```bash
# Analizar y comparar dos archivos
./demo_sin_gui.py  # Genera análisis en /tmp/groove_analysis_demo.json
# Luego analizar otro archivo y comparar estadísticas
```

### 3. Batch processing
```python
import os
from groove_analyzer import GrooveAnalyzer
import json

# Procesar todos los WAV en una carpeta
audio_dir = "/path/to/grooves"
output_dir = "/path/to/results"

for filename in os.listdir(audio_dir):
    if filename.endswith('.wav'):
        print(f"Procesando {filename}...")

        analyzer = GrooveAnalyzer()
        analyzer.load_audio(os.path.join(audio_dir, filename))
        analyzer.detect_onsets()
        analyzer.analyze_dynamics()
        analyzer.calculate_timing_deviations(tempo_bpm=120)

        results = analyzer.get_results()

        output_file = os.path.join(output_dir, filename.replace('.wav', '.json'))
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"  ✅ Guardado en {output_file}")
```

---

## 🔍 Interpretación de Resultados

### Timing Deviation
- **< 5ms**: Timing muy preciso (cuantizado o casi)
- **5-15ms**: Timing natural humano
- **> 15ms**: Timing suelto o problemas técnicos

### Velocity Variation
- **< 0.1**: Dinámica uniforme (machine-like)
- **0.1-0.3**: Dinámica natural
- **> 0.3**: Alta expresividad

### Swing Factor
- **< 0.1**: Straight feel
- **0.1-0.3**: Swing ligero
- **> 0.3**: Swing pronunciado

---

## ❓ Troubleshooting

### Error: "No module named 'librosa'"
```bash
venv/bin/pip install librosa soundfile
```

### Error: "libEGL.so.1: cannot open shared object file"
```bash
sudo apt-get install libegl1 libxcb-cursor0
```

### Error con madmom
```bash
# madmom es opcional - la aplicación funciona sin él
# Si quieres instalarlo:
pip install Cython
pip install madmom
```

---

## 📚 Documentación Adicional

- **README.md**: Documentación completa del proyecto
- **ARQUITECTURA_DSP.md**: Detalles técnicos de algoritmos
- **GUI_PREVIEW.md**: Vista previa de la interfaz gráfica
- **data_reference/**: Ejemplos de formato de datos

---

## 🆘 Soporte

Si encuentras problemas, revisa:
1. Versión de Python: `python --version` (requiere 3.8+)
2. Dependencias instaladas: `pip list | grep librosa`
3. Permisos de archivos: `ls -la *.py`

---

**¡Listo para extraer grooves! 🥁🎵**
