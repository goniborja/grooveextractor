# 🎨 Vista Previa de la Interfaz Gráfica

## Groove Extractor - Interfaz PyQt6

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                       🥁 GROOVE EXTRACTOR                              │
│                                                                         │
│           Herramienta de Análisis DSP para Extracción de Grooves       │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─ 1. Cargar Audio ──────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │  📁 test_groove.wav                      [Cargar WAV]          │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─ 2. Parámetros de Análisis ────────────────────────────────────┐   │
│  │                                                                 │   │
│  │  Tempo (BPM):     [120.0        ]                              │   │
│  │                                                                 │   │
│  │  Time Signature:  [4/4          ]                              │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│                   ┌──────────────────────────────┐                     │
│                   │    ▶ Analizar Audio         │                     │
│                   └──────────────────────────────┘                     │
│                                                                         │
│  ┌─ 3. Resultados del Análisis ───────────────────────────────────┐   │
│  │                                                                 │   │
│  │  === ANÁLISIS COMPLETADO ===                                   │   │
│  │                                                                 │   │
│  │  METADATA:                                                      │   │
│  │  - Archivo: test_groove.wav                                     │   │
│  │  - Sample Rate: 44100 Hz                                        │   │
│  │  - Duración: 4.00 s                                             │   │
│  │  - Tempo: 120 BPM                                               │   │
│  │  - Time Signature: 4/4                                          │   │
│  │                                                                 │   │
│  │  DETECCIÓN DE ONSETS:                                           │   │
│  │  - Total de onsets detectados: 11                               │   │
│  │                                                                 │   │
│  │  ESTADÍSTICAS DE HUMANIZACIÓN:                                  │   │
│  │  - Desviación temporal promedio: 4.28 ms                        │   │
│  │  - Desviación estándar: 3.07 ms                                 │   │
│  │  - Variación de velocidad promedio: 0.086                       │   │
│  │  - Factor de swing: 0.047                                       │   │
│  │                                                                 │   │
│  │  Primeros 5 onsets:                                             │   │
│  │                                                                 │   │
│  │    1. t=0.499s, vel=91, dev=-0.77ms                             │   │
│  │    2. t=0.743s, vel=62, dev=-6.96ms                             │   │
│  │    3. t=0.998s, vel=88, dev=-1.54ms                             │   │
│  │    4. t=1.498s, vel=85, dev=-2.31ms                             │   │
│  │    5. t=1.741s, vel=60, dev=-8.50ms                             │   │
│  │                                                                 │   │
│  │  [Desplazamiento vertical disponible para más resultados...]   │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│       ┌───────────────────┐      ┌───────────────────┐                │
│       │  💾 Exportar JSON │      │  📊 Exportar CSV  │                │
│       └───────────────────┘      └───────────────────┘                │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ Status: Análisis completado exitosamente                               │
└─────────────────────────────────────────────────────────────────────────┘
```

## Componentes de la Interfaz

### 1. Sección de Carga de Archivo
- **Label**: Muestra el nombre del archivo cargado
- **Botón "Cargar WAV"**: Abre diálogo de selección de archivo
- Formatos soportados: WAV

### 2. Parámetros de Análisis
- **Tempo (BPM)**: Campo de texto editable para especificar el tempo
- **Time Signature**: Campo de texto para la métrica (default: 4/4)

### 3. Botón de Análisis
- **"▶ Analizar Audio"**: Inicia el análisis en segundo plano
- Se deshabilita durante el procesamiento
- Muestra barra de progreso cuando está activo

### 4. Área de Resultados
- **Text Edit** (solo lectura): Muestra resumen del análisis
- Incluye:
  - Metadata del archivo
  - Número de onsets detectados
  - Estadísticas de humanización
  - Preview de primeros onsets
- Scroll vertical disponible para archivos largos

### 5. Botones de Exportación
- **💾 Exportar JSON**: Guarda análisis completo en formato JSON
- **📊 Exportar CSV**: Guarda tabla de onsets en formato CSV
- Se habilitan solo después de un análisis exitoso

### 6. Barra de Estado
- Muestra mensajes de progreso y estado de la aplicación

---

## Colores y Estilo

### Esquema de Colores
- **Background**: Blanco/Gris claro (#FFFFFF / #F0F0F0)
- **Títulos**: Negro (#000000)
- **Botón Principal**: Azul (#007AFF) con texto blanco
- **Labels de sección**: Gris oscuro (#333333)
- **Texto de resultados**: Negro (#000000) en fondo gris claro

### Tipografía
- **Título principal**: Sans-serif, 18pt, Bold
- **Subtítulo**: Sans-serif, 11pt, Regular
- **Contenido**: Monospace, 10pt (para resultados)
- **Botones**: Sans-serif, 12pt, Bold

---

## Estados de la Interfaz

### Estado Inicial
- Botón "Analizar Audio": Deshabilitado
- Botones de exportación: Deshabilitados
- Área de resultados: Vacía con placeholder
- Status: "Listo para cargar audio"

### Estado: Audio Cargado
- Botón "Analizar Audio": **Habilitado**
- Archivo mostrado en label
- Status: "Audio cargado: [nombre]"

### Estado: Analizando
- Botón "Analizar Audio": Deshabilitado
- **Barra de progreso visible**
- Status: "Analizando audio..."
- Progreso: 0% → 100%

### Estado: Análisis Completado
- Botón "Analizar Audio": Habilitado (para re-análisis)
- Botones de exportación: **Habilitados**
- Área de resultados: **Llena con datos**
- Barra de progreso: Oculta
- Status: "Análisis completado exitosamente"

### Estado: Error
- Área de resultados: Muestra mensaje de error en rojo
- Status: "Error en el análisis"
- Botones de exportación: Deshabilitados

---

## Flujo de Usuario

```
┌─────────────┐
│   Inicio    │
└──────┬──────┘
       │
       v
┌─────────────────────┐
│  Click "Cargar WAV" │
└──────┬──────────────┘
       │
       v
┌───────────────────────┐
│ Seleccionar archivo   │
└──────┬────────────────┘
       │
       v
┌─────────────────────────┐
│ Ajustar parámetros (BPM)│
└──────┬──────────────────┘
       │
       v
┌────────────────────────┐
│ Click "▶ Analizar Audio"│
└──────┬─────────────────┘
       │
       v
┌─────────────────┐
│ Procesamiento   │◄──── Barra de progreso
│ (Thread separado)│      (10% → 100%)
└──────┬──────────┘
       │
       v
┌──────────────────┐
│ Mostrar resultados│
└──────┬───────────┘
       │
       v
    ┌──┴───┐
    │      │
    v      v
┌────────┐ ┌────────┐
│  JSON  │ │  CSV   │
└────────┘ └────────┘
```

---

## Características Técnicas de la GUI

### Threading
- **QThread** para análisis en segundo plano
- **Signals**: progress, finished, error
- No bloquea la interfaz durante el procesamiento

### Diálogos
- **QFileDialog** para selección de archivos (input/output)
- Filtros: "*.wav" para input, "*.json" / "*.csv" para output

### Widgets Principales
- **QMainWindow**: Ventana principal
- **QVBoxLayout**: Layout vertical principal
- **QGroupBox**: Agrupación de secciones
- **QTextEdit**: Área de resultados
- **QProgressBar**: Indicador de progreso
- **QPushButton**: Botones de acción
- **QLineEdit**: Campos de entrada

---

## Dimensiones

- **Ventana**: 900 x 700 px (ajustable)
- **Posición inicial**: (100, 100) desde esquina superior izquierda
- **Mínimo recomendado**: 800 x 600 px

---

## Mensajes de Usuario

### Success
- ✅ "Audio cargado: [nombre]"
- ✅ "Análisis completado exitosamente"
- ✅ "JSON exportado: [ruta]"
- ✅ "CSV exportado: [ruta]"

### Info
- 📁 "No se ha cargado ningún archivo"
- ⏳ "Analizando audio..."
- 📊 "Los resultados aparecerán aquí después del análisis..."

### Errors
- ❌ "Error: Tempo debe ser un número"
- ❌ "ERROR EN EL ANÁLISIS: [detalles]"

---

**Para ejecutar la GUI con pantalla:**
```bash
./run_gui.sh
```

**Para demostración sin GUI:**
```bash
./demo_sin_gui.py
```
