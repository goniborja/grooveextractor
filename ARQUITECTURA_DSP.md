# 🔬 Arquitectura DSP - Groove Extractor

## Documento Técnico para Ingeniero DSP

---

## 1. Pipeline de Procesamiento

```
Audio WAV Input
       ↓
┌──────────────────────┐
│  Load & Preprocess   │ ← librosa.load()
│  - Resample si req.  │
│  - Normalize         │
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Onset Detection     │ ← librosa.onset / madmom.RNN
│  - Onset envelope    │
│  - Peak picking      │
│  - Backtracking      │
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Dynamic Analysis    │ ← RMS, dB, MIDI velocity
│  - Window extraction │
│  - Amplitude calc    │
│  - Velocity mapping  │
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Timing Analysis     │ ← Grid quantization
│  - Beat alignment    │
│  - Deviation calc    │
│  - Micro-timing      │
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Humanization Stats  │ ← Statistical analysis
│  - Timing variance   │
│  - Velocity variance │
│  - Swing detection   │
└──────────────────────┘
       ↓
JSON/CSV Output
```

---

## 2. Detección de Onsets

### 2.1 Método Librosa (Default)

**Parámetros clave:**
```python
hop_length = 512          # ~11.6ms @ 44.1kHz
aggregate = np.median     # Robustez contra outliers
backtrack = True          # Refinamiento temporal
pre_max = 3               # Contexto pre-pico
post_max = 3              # Contexto post-pico
delta = 0.2               # Umbral de detección
wait = 10                 # Frames entre onsets
```

**Onset Strength Function:**
```
S[t] = max(0, E[t] - median(E[t-w:t+w]))

Donde:
- E[t] = Espectrograma en frame t
- w = ventana de contexto
- S[t] = Onset strength en t
```

**Peak Picking:**
```
onset_detected[t] = True si:
  1. S[t] > S[t-pre_max:t]       # Máximo local pre
  2. S[t] > S[t:t+post_max]      # Máximo local post
  3. S[t] > threshold + delta     # Por encima de umbral
```

### 2.2 Método Madmom (Opcional - Alta Precisión)

Utiliza RNN (Recurrent Neural Network) entrenada en datasets de percusión:

```python
RNNOnsetProcessor → Activations
                         ↓
OnsetPeakPickingProcessor → Onset times
```

**Ventajas:**
- Mayor precisión en percusión compleja
- Menor tasa de falsos positivos
- Robusto ante reverberación

**Desventaja:**
- Mayor costo computacional

---

## 3. Análisis de Dinámica

### 3.1 Extracción de Amplitud

**Ventana de análisis:** ±25ms alrededor del onset
```
t_onset ± 25ms = t_onset ± (0.025 × sr) samples
```

**RMS (Root Mean Square):**
```
RMS = √(1/N ∑(x[n]²))

Donde:
- x[n] = samples en la ventana
- N = número de samples
```

**Conversión a dB:**
```
dB = 20 × log₁₀(RMS + ε)

Donde:
- ε = 1e-10 (evitar log(0))
```

### 3.2 Mapeo a Velocidad MIDI

**Rango típico de batería acústica:**
- Pianissimo (pp): -60 dB → velocity 1
- Fortissimo (ff): -6 dB → velocity 127

**Función de mapeo lineal:**
```python
velocity = ((dB - dB_min) / (dB_max - dB_min)) × 127

Con clipping:
velocity = clip(velocity, 1, 127)
```

**Mejora futura:** Mapeo logarítmico para mayor fidelidad perceptual
```
velocity = 127 × (log(dB - dB_min + 1) / log(dB_max - dB_min + 1))
```

---

## 4. Análisis de Micro-Timing

### 4.1 Grid Métrico

**Definición del grid:**
```
beat_interval = 60.0 / tempo_bpm        # Duración de un beat
grid_subdivision = 4                     # 16th notes
grid_interval = beat_interval / 4        # Intervalo de subdivisión
```

**Ejemplo @ 120 BPM:**
```
beat_interval = 60/120 = 0.5s = 500ms
grid_interval = 0.5/4 = 0.125s = 125ms
```

### 4.2 Cuantización al Grid

**Posición cuantizada más cercana:**
```
grid_position = round(onset_time / grid_interval)
expected_time = grid_position × grid_interval
```

**Desviación temporal:**
```
deviation_ms = (onset_time - expected_time) × 1000

Interpretación:
- deviation > 0  → onset adelantado (rushing)
- deviation < 0  → onset atrasado (dragging)
- |deviation| < 5ms → "en el beat"
```

### 4.3 Beat Position Normalizada

```
beat_position = (onset_time / beat_interval) % 4 + 1

Rango: [1.0, 5.0)
- 1.0, 2.0, 3.0, 4.0 → downbeats
- 1.5, 2.5, 3.5, 4.5 → offbeats
```

---

## 5. Estadísticas de Humanización

### 5.1 Timing Deviation Statistics

**Media (μ):**
```
μ = (1/N) ∑ deviation[i]
```
Indica tendencia general (rushing vs dragging)

**Desviación estándar (σ):**
```
σ = √((1/N) ∑ (deviation[i] - μ)²)
```
Indica consistencia temporal

**Interpretación:**
- σ < 5ms: Timing muy preciso (cuantizado)
- 5ms < σ < 15ms: Timing humano natural
- σ > 15ms: Timing suelto o problemas técnicos

### 5.2 Velocity Variation

**Variación normalizada:**
```
v_var[i] = |velocity[i] - velocity_mean| / 127

Rango: [0.0, 1.0]
```

**Media de variación:**
```
μ_var = (1/N) ∑ v_var[i]
```

**Interpretación:**
- μ_var < 0.1: Dinámica uniforme (machine-like)
- 0.1 < μ_var < 0.3: Dinámica natural
- μ_var > 0.3: Alta expresividad dinámica

### 5.3 Swing Factor

**Definición:** Diferencia temporal entre subdivisiones pares e impares

```
Subdivisiones PARES: 1.0, 1.5, 2.0, 2.5...
Subdivisiones IMPARES: 1.25, 1.75, 2.25...

swing_factor = |mean(dev_odd) - mean(dev_even)| / 100
```

**Interpretación:**
- swing = 0.0: Straight feel
- 0.0 < swing < 0.3: Swing ligero
- swing > 0.3: Swing pronunciado

**Mejora futura:** Implementar triplet swing detection

---

## 6. Clasificación de Instrumentos

### 6.1 Método Actual (Heurístico)

**Reglas simples:**
```python
if on_downbeat:
    if velocity > 90:
        return 'kick'
    else:
        return 'snare'
else:
    return 'hihat'
```

### 6.2 Método Propuesto (ML)

**Features para clasificación:**
1. **Espectrales:**
   - Spectral centroid
   - Spectral rolloff
   - MFCCs (13 coefs)
   - Zero-crossing rate

2. **Temporales:**
   - Attack time
   - Decay time
   - Sustain level
   - Onset strength

3. **Contextuales:**
   - Beat position
   - Velocity
   - Intervalo temporal con onset anterior

**Arquitectura sugerida:**
```
Input (20 features)
      ↓
Dense (64, ReLU)
      ↓
Dropout (0.3)
      ↓
Dense (32, ReLU)
      ↓
Dense (N_classes, Softmax)

Classes: [kick, snare, hihat, tom, crash, ride, other]
```

---

## 7. Formato de Salida

### 7.1 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["metadata", "groove_data", "humanization_stats"],
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "audio_file": {"type": "string"},
        "sample_rate": {"type": "integer"},
        "duration_seconds": {"type": "number"},
        "tempo_bpm": {"type": "number"},
        "time_signature": {"type": "string"},
        "analyzed_date": {"type": "string", "format": "date-time"},
        "analyzer_version": {"type": "string"}
      }
    },
    "groove_data": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "onset_time": {"type": "number"},
          "beat_position": {"type": "number"},
          "bar_number": {"type": "integer"},
          "drum_type": {"type": "string"},
          "velocity": {"type": "integer", "minimum": 1, "maximum": 127},
          "amplitude_db": {"type": "number"},
          "timing_deviation_ms": {"type": "number"},
          "velocity_variation": {"type": "number", "minimum": 0, "maximum": 1},
          "onset_strength": {"type": "number", "minimum": 0, "maximum": 1}
        }
      }
    },
    "humanization_stats": {
      "type": "object",
      "properties": {
        "avg_timing_deviation_ms": {"type": "number"},
        "std_timing_deviation_ms": {"type": "number"},
        "avg_velocity_variation": {"type": "number"},
        "swing_factor": {"type": "number"}
      }
    }
  }
}
```

---

## 8. Optimizaciones y Mejoras Futuras

### 8.1 Performance
- [ ] Implementar procesamiento por chunks para archivos largos
- [ ] Paralelizar análisis de múltiples archivos
- [ ] Cache de onset detection para re-análisis con diferentes parámetros

### 8.2 Precisión
- [ ] Detector de tempo automático (librosa.beat.tempo)
- [ ] Separación de fuentes (Demucs/Spleeter) antes del análisis
- [ ] Clasificador ML de instrumentos
- [ ] Detección de poliritmias

### 8.3 Features
- [ ] Exportación a MIDI
- [ ] Visualización interactiva (waveform + onsets + grid)
- [ ] Análisis comparativo entre grooves
- [ ] Generador de variaciones humanizadas

### 8.4 Validación
- [ ] Test suite con audio sintético
- [ ] Benchmark contra datasets anotados (ENST-Drums, Groove MIDI)
- [ ] Métricas de precisión: F1-score, precision, recall

---

## 9. Referencias Académicas

### Papers Clave

1. **Onset Detection:**
   - Böck, S., & Widmer, G. (2013). "Maximum Filter Vibrato Suppression for Onset Detection"
   - Dixon, S. (2006). "Onset Detection Revisited"

2. **Humanización:**
   - Kilchenmann, L., & Senn, O. (2015). "Microtiming in Swing and Funk affects the body movement behavior of music expert listeners"
   - Davies, M. et al. (2013). "Evaluation of Audio Beat Tracking and Music Tempo Extraction Algorithms"

3. **Drum Classification:**
   - Gillet, O., & Richard, G. (2006). "ENST-Drums: An Extensive Audio-Visual Database for Drum Signals Processing"

---

**Versión:** 1.0.0
**Autor:** DSP Engineer
**Fecha:** 2026-01-18
