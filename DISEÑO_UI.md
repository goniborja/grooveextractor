# DISEÑO_UI.md - Instrucciones para Claude Code

## ⚠️ IMPORTANTE: Borra este archivo cuando hayas terminado todo el trabajo.

---

## 1. OBJETIVO

Transformar la interfaz actual de Groove Extractor (widgets Qt nativos con CSS) en una interfaz profesional estilo VST vintage usando imágenes pre-renderizadas del kit "Vintage Obsession".

---

## 2. UBICACIÓN DE ASSETS

Los assets gráficos están en:
```
assets/ui/vintage_obsession/
├── Animations/
│   ├── Oneshots/        → Imágenes individuales (estados on/off)
│   └── Strips/          → Filmstrips (animaciones verticales)
├── back_a.png, back_b.png, back_c.png, back_d.png  → Fondos de panel
├── screen.png           → Display/pantalla
├── text_box.png         → Campo de texto
├── wallpaper_a.png, wallpaper_b.png  → Fondos completos
└── ...otros assets
```

### Mapeo de assets a usar:

| Elemento UI | Asset (en Strips/) | Asset alternativo (en Oneshots/) |
|-------------|-------------------|----------------------------------|
| Botones grandes | `but_big_rectangle.png` (5 frames) | `but_big_rec_on.png`, `but_big_rec_off.png` |
| Botones pequeños | `but_small_rectangle.png` | `but_small_rec_on.png`, `but_small_rec_off.png` |
| Pads | `pad.png` | `pad_on.png`, `pad_off.png` |
| Switch horizontal | `switch_hor.png` | `switch_hor_st1.png`, `switch_hor_st2.png` |
| Switch vertical | `switch_ver.png` | `switch_ver_st1.png`, `switch_ver_st2.png` |
| Sliders verticales | `Ver_slider.png` | Carpeta `Ver_slider/` |
| Sliders horizontales | `Hor_slider.png` | Carpeta `Hor_slider/` |
| Knob (selector estilo) | `Knob_mid.png` o `Knob_small.png` | Carpeta correspondiente |
| LED indicador | `LED_meter.png` (62 frames) | Carpeta `LED_meter/` |
| VU Meter | `VU_meter.png` | Carpeta `VU_meter/` |
| Flechas | `arrow.png` | `arrow_off.png`, `arrow_presed.png` |
| Screen/Display | `../screen.png` | - |
| Fondo panel | `../back_a.png` (o b/c/d) | - |
| Fondo ventana | `../wallpaper_a.png` | - |

---

## 3. DISEÑO APROBADO (6 ZONAS)

La interfaz tiene un layout de 3 columnas:
- Columna izquierda: Zonas A, D, G (apiladas verticalmente)
- Columna central: Zonas B (grande, arriba) y E (pequeña, abajo)
- Columna derecha: Zona C (toda la altura)

### ZONA A (Arriba izquierda):
- **1 Pad** → Importar canción (señal: `import_song_clicked`)
- **1 Switch horizontal** → Guardar metadatos (señal: `metadata_toggled(bool)`)
- **1 Switch horizontal** → Separar batería en BD/SN/HH (señal: `separate_drums_toggled(bool)`)

### ZONA B (Centro superior - grande):
- **1 VU Meter grande** con aguja animada
  - Se mueve durante el proceso
  - Vuelve a posición 0 cuando termina
  - Señal de entrada: `set_vu_level(float)` (0.0 a 1.0)
- **1 Screen** debajo → Mensajes de estado ("Analizando batería...", "Separando stems...")
  - Método: `set_status_message(str)`
- **3 Sliders verticales** → Bombo (Kick), Caja (Snare), Hi-Hat
  - Animados durante el proceso
  - En reposo: posición mínima (abajo)
  - Señales: `kick_level_changed(float)`, `snare_level_changed(float)`, `hihat_level_changed(float)`
- **1 LED** → Indicador de análisis en curso
  - Métodos: `set_analyzing(bool)`

### ZONA C (Derecha - toda la altura):
- **1 Pad** → Exportar pista de batería (señal: `export_drums_clicked`)
- **1 Switch horizontal** al lado → MIDI (izq) / WAV (der) (señal: `export_format_changed(str)`)
- **1 Button** → "Proiektua ireki" (abrir proyecto) (señal: `open_project_clicked`)
- **1 Button** → "Proiektua gorde" (guardar proyecto) (señal: `save_project_clicked`)
- **1 Slider vertical** → Función pendiente (reservado para futuro)

### ZONA D (Centro izquierda):
- **1 Knob** → Selector de estilo con 6 posiciones:
  1. Ska
  2. Rocksteady
  3. Early Reggae
  4. Roots Reggae
  5. Steppers
  6. Dub
  - Señal: `style_changed(str)`
- **1 Screen** a la derecha del knob → Muestra estilo seleccionado
- **1 Screen editable** → Nombre del batería (señal: `drummer_name_changed(str)`)
- **1 Screen editable** → BPM (señal: `bpm_changed(int)`)

### ZONA G (Abajo izquierda):
- **1 Pad** → Detectar BPM automáticamente (señal: `detect_bpm_clicked`)
- **1 Slider horizontal** → Animación mientras detecta BPM
  - Método: `set_detecting(bool)` para activar/desactivar animación

### ZONA E (Centro inferior):
- **1 Screen grande** → Porcentaje del proceso (ej: "75%")
  - Método: `set_progress(int)` (0-100)

---

## 4. WIDGETS CUSTOM A CREAR

Crea estos widgets en `ui/widgets/`:

### 4.1. ImagePad (`image_pad.py`)
```python
# Widget tipo pad que usa imágenes on/off
# Constructor: ImagePad(off_image, on_image, label_text)
# Señales: clicked()
# El pad se ilumina brevemente al hacer clic
```

### 4.2. ImageSwitch (`image_switch.py`)
```python
# Switch horizontal/vertical con dos estados
# Constructor: ImageSwitch(strip_path, orientation='horizontal')
# Señales: toggled(bool)
# Métodos: is_on(), set_state(bool)
```

### 4.3. FilmstripSlider (`filmstrip_slider.py`)
```python
# Slider que usa filmstrip vertical para animación
# Constructor: FilmstripSlider(strip_path, num_frames, orientation='vertical')
# Señales: value_changed(float)
# Métodos: set_value(float), get_value(), animate_to(float, duration_ms)
```

### 4.4. FilmstripKnob (`filmstrip_knob.py`)
```python
# Knob rotatorio con filmstrip
# Constructor: FilmstripKnob(strip_path, num_frames, num_positions=None)
# Si num_positions se especifica, el knob tiene paradas discretas
# Señales: value_changed(int) para discreto, value_changed(float) para continuo
# Métodos: set_value(), get_value(), set_labels(list) para mostrar texto
```

### 4.5. AnimatedVUMeter (`animated_vu_meter.py`)
```python
# VU Meter con aguja animada usando filmstrip
# Constructor: AnimatedVUMeter(strip_path, num_frames)
# Métodos: set_level(float), reset(), animate_needle(bool)
```

### 4.6. AnimatedLED (`animated_led.py`)
```python
# LED con múltiples frames para animación suave
# Constructor: AnimatedLED(strip_path_or_folder, num_frames)
# Métodos: turn_on(), turn_off(), pulse(), set_brightness(float)
```

### 4.7. ImageButton (`image_button.py`)
```python
# Botón con filmstrip de estados (normal, hover, pressed, disabled)
# Constructor: ImageButton(strip_path, num_frames=5, label_text='')
# Señales: clicked()
# El texto se dibuja encima del botón
```

### 4.8. VintageScreen (`vintage_screen.py`)
```python
# Display con fondo de imagen y texto
# Constructor: VintageScreen(bg_image, editable=False)
# Métodos: set_text(str), get_text(), set_editable(bool)
# Señales: text_changed(str) si es editable
```

---

## 5. ESTRUCTURA DEL MAIN_WINDOW.PY

Modifica `ui/main_window.py` para:

1. **Eliminar** todos los widgets Qt nativos actuales (QComboBox, QSpinBox, QPushButton, etc.)
2. **Eliminar** el archivo `ui/styles.py` (ya no se usa CSS)
3. **Crear** el layout de 3 columnas con las 6 zonas
4. **Usar** los widgets custom con los assets de vintage_obsession
5. **Mantener** toda la lógica de señales/slots existente, solo reconectando a los nuevos widgets
6. **Aplicar** el fondo `wallpaper_a.png` a la ventana principal

### Layout sugerido:
```python
# Layout principal
main_layout = QHBoxLayout()

# Columna izquierda (A, D, G)
left_column = QVBoxLayout()
left_column.addWidget(zone_a)
left_column.addWidget(zone_d)
left_column.addWidget(zone_g)

# Columna central (B, E)
center_column = QVBoxLayout()
center_column.addWidget(zone_b, stretch=3)
center_column.addWidget(zone_e, stretch=1)

# Columna derecha (C)
right_column = QVBoxLayout()
right_column.addWidget(zone_c)

main_layout.addLayout(left_column)
main_layout.addLayout(center_column, stretch=2)
main_layout.addLayout(right_column)
```

---

## 6. TEXTOS DE LA INTERFAZ (en Euskera)

- Importar canción: "KARGATU" o "INPORTATU"
- Exportar batería: "ESPORTATU"
- Detectar BPM: "BPM ANTZEMAN"
- Abrir proyecto: "PROIEKTUA IREKI"
- Guardar proyecto: "PROIEKTUA GORDE"
- Metadatos: "METADATUAK"
- Separar batería: "BANATU BD/SN/HH"
- Analizando: "AZTERTZEN..."
- Estilo: "ESTILOA"
- Batería (músico): "BATERIA"
- Formato MIDI/WAV: "MIDI" / "WAV"

---

## 7. COLORES Y FUENTES

- Texto en screens: Verde (#00FF00) o ámbar (#FFB000) estilo LCD
- Texto en labels: Gris claro (#AAAAAA)
- Fuente para displays: Monospace (Courier New, o mejor: fuente DSEG si disponible)
- Fuente para labels: Sans-serif pequeña

---

## 8. ORDEN DE TRABAJO

1. Primero: Crear todos los widgets custom en `ui/widgets/`
2. Segundo: Probar cada widget individualmente
3. Tercero: Modificar `main_window.py` con el nuevo layout
4. Cuarto: Conectar señales a la lógica existente
5. Quinto: Probar la aplicación completa
6. Sexto: Ajustar tamaños y posiciones si es necesario

---

## 9. TESTING

Después de implementar, ejecuta:
```bash
python main_vintage.py
```

Verifica:
- [ ] Todos los widgets se muestran correctamente
- [ ] Los filmstrips se animan suavemente
- [ ] Los clicks en pads/botones emiten señales
- [ ] Los switches cambian de estado
- [ ] El knob de estilos tiene 6 posiciones
- [ ] Los screens editables permiten escribir
- [ ] El VU meter responde a `set_level()`
- [ ] El LED se enciende/apaga correctamente

---

## 10. LIMPIEZA FINAL

Cuando todo funcione correctamente:

1. **Borra este archivo** (`DISEÑO_UI.md`)
2. Borra `ui/styles.py` si aún existe
3. Elimina cualquier import no usado en los archivos modificados

---

## 11. NOTAS ADICIONALES

- Los filmstrips son imágenes verticales donde cada frame está apilado debajo del anterior
- Para calcular qué frame mostrar: `frame_index = int(value * (num_frames - 1))`
- Usa `QPainter` para dibujar el frame correcto recortando la imagen
- El VU meter con aguja requiere calcular el frame según el nivel de audio
- Los sliders en reposo deben mostrar el frame 0 (posición mínima)

---

**¡Buena suerte! Cuando termines, borra este archivo.**
