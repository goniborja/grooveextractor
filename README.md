# 🥁 Groove Extractor

**Herramienta de Análisis DSP para Extracción de Grooves de Batería**

Groove Extractor es una aplicación de escritorio (Python/PyQt6) diseñada para analizar archivos de audio de batería y extraer información detallada sobre timing, dinámica y humanización, compatible con el proyecto "Book of Drums".

---

## 🎯 Características

### Análisis DSP Avanzado
- ✅ **Detección de Onsets**: Utiliza `librosa` y `madmom` para detección precisa de eventos percusivos
- ✅ **Análisis de Dinámica**: Extracción de amplitud (dB) y estimación de velocidad MIDI (0-127)
- ✅ **Micro-Timing**: Cálculo de desviaciones del grid métrico en milisegundos
- ✅ **Humanización**: Estadísticas de variación temporal y dinámica
- ✅ **Swing Factor**: Análisis de groove swing vs. straight

### Interfaz Gráfica
- 🖥️ Interfaz moderna con PyQt6
- 📊 Visualización de resultados en tiempo real
- 💾 Exportación a JSON y CSV
- ⚡ Procesamiento multi-thread (no bloquea la UI)

---

## 📦 Instalación

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd grooveextractor
```

### 2. Crear Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En Linux/Mac
# venv\Scripts\activate   # En Windows
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

**Nota sobre madmom**: Si `madmom` falla en la instalación, puedes usar solo `librosa` (la aplicación lo detecta automáticamente).

---

## 🚀 Uso

### Modo Gráfico (Recomendado)
```bash
python extractor_app.py
```

### Flujo de Trabajo:
1. **Cargar Audio**: Click en "Cargar WAV" y selecciona tu archivo
2. **Configurar Parámetros**: Ajusta el tempo (BPM) y time signature
3. **Analizar**: Click en "▶ Analizar Audio"
4. **Exportar**: Guarda los resultados en JSON o CSV

---

## 📁 Estructura del Proyecto

```
grooveextractor/
├── extractor_app.py           # Aplicación principal (GUI PyQt6)
├── groove_analyzer.py         # Módulo de análisis DSP
├── requirements.txt           # Dependencias Python
├── README.md                  # Este archivo
├── data_reference/            # Ejemplos y documentación
│   ├── example_groove.csv     # Estructura de datos de ejemplo
│   └── formato_json_salida.txt # Especificación del formato JSON
└── venv/                      # Entorno virtual (gitignored)
```

---

## 📊 Formato de Datos

### Salida JSON

```json
{
  "metadata": {
    "audio_file": "groove.wav",
    "sample_rate": 44100,
    "duration_seconds": 120.5,
    "tempo_bpm": 120.0,
    "time_signature": "4/4",
    "analyzed_date": "2026-01-18T10:30:00",
    "analyzer_version": "1.0.0"
  },
  "groove_data": [
    {
      "onset_time": 0.000,
      "beat_position": 1.0,
      "bar_number": 1,
      "drum_type": "kick",
      "velocity": 95,
      "amplitude_db": -12.5,
      "timing_deviation_ms": 0.0,
      "velocity_variation": 0.0,
      "onset_strength": 0.85
    }
  ],
  "humanization_stats": {
    "avg_timing_deviation_ms": 1.5,
    "std_timing_deviation_ms": 2.3,
    "avg_velocity_variation": 0.15,
    "swing_factor": 0.0
  }
}
```

### Campos Explicados

| Campo | Descripción | Unidad |
|-------|-------------|--------|
| `onset_time` | Tiempo del onset desde el inicio | segundos |
| `beat_position` | Posición métrica en el compás | beats (1.0-4.0) |
| `bar_number` | Número de compás | entero |
| `drum_type` | Instrumento detectado | string (kick/snare/hihat) |
| `velocity` | Velocidad MIDI estimada | 0-127 |
| `amplitude_db` | Amplitud RMS | dB |
| `timing_deviation_ms` | Desviación del grid | milisegundos |
| `velocity_variation` | Variación normalizada | 0.0-1.0 |
| `onset_strength` | Fuerza del onset detectado | 0.0-1.0 |

---

## 🔬 Detalles Técnicos

### Algoritmos Implementados

#### 1. Detección de Onsets (Librosa)
```python
# Configuración optimizada para percusión
hop_length = 512
onset_env = librosa.onset.onset_strength(
    y=audio, sr=sr,
    hop_length=hop_length,
    aggregate=np.median
)
onset_frames = librosa.onset.onset_detect(
    onset_envelope=onset_env,
    backtrack=True,
    pre_max=3, post_max=3,
    delta=0.2, wait=10
)
```

#### 2. Análisis de Dinámica
- Ventana de ±25ms alrededor de cada onset
- Cálculo RMS y conversión a dB
- Mapeo dB → MIDI velocity: `-60dB = 1`, `-6dB = 127`

#### 3. Micro-Timing
- Grid basado en subdivisión de 16th notes
- Cálculo de desviación: `deviation = (actual_time - expected_time) * 1000`

#### 4. Swing Factor
- Análisis de diferencias temporales entre subdivisiones pares/impares
- Rango: `0.0 = straight`, `>0.5 = swing pronunciado`

---

## 🛠️ Desarrollo y Extensiones

### Posibles Mejoras

1. **Clasificación de Instrumentos con ML**
   - Actualmente usa heurísticas simples
   - Podría implementarse con CNN o modelos pre-entrenados

2. **Detección de Tempo Automática**
   - Usar `librosa.beat.tempo()` o `madmom.features.tempo`

3. **Separación de Fuentes**
   - Integrar Spleeter o Demucs para aislar batería

4. **Visualización Avanzada**
   - Waveform con onsets marcados
   - Espectrograma
   - Grid rítmico interactivo

5. **Exportación a MIDI**
   - Convertir onsets detectados a archivo MIDI

---

## 📚 Referencias

### Librerías Utilizadas
- **librosa**: McFee et al., 2015 - "librosa: Audio and Music Signal Analysis in Python"
- **madmom**: Böck et al., 2016 - "madmom: A New Python Audio and Music Signal Processing Library"
- **PyQt6**: Qt for Python - Framework GUI moderno

### Datasets de Referencia
- **Groove MIDI Dataset** (Magenta/Google): 1,150 grooves anotados
- **ENST-Drums**: Dataset de batería con anotaciones multi-pista

---

## 👨‍💻 Autor

**Ingeniero DSP / Arquitecto de Datos**
Proyecto: Book of Drums - Groove Extractor
Versión: 1.0.0
Fecha: 2026-01-18

---

## 📄 Licencia

[Especificar licencia aquí]

---

## 🐛 Reporte de Bugs y Contribuciones

Para reportar bugs o sugerir mejoras, por favor abre un issue en el repositorio.

---

## ⚡ Quick Start

```bash
# Instalación rápida
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ejecutar aplicación
python extractor_app.py
```

---

**¡Happy Groove Extracting! 🥁🎵**
