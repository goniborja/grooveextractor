# GROOVE EXTRACTOR — Prompt Final para Claude Code

## CONTEXTO

El usuario tiene una aplicación PyQt6 llamada "Groove Extractor" con estética vintage jamaicana. La interfaz actual está muy plana y necesita mejoras visuales. El usuario ya ha colocado los assets gráficos en su proyecto.

## ESTRUCTURA DE ASSETS (ya colocados por el usuario)

```
D:\Groove Extractor\
├── assets\
│   ├── textures\
│   │   ├── rasta_wood_background.png   ← FONDO PRINCIPAL (listones rasta)
│   │   ├── rasta_wood_alt.png          ← Alternativa
│   │   └── wood_dark.png
│   └── icons\
│       ├── screw_small.png (16x16)
│       ├── screw_medium.png (24x24)
│       ├── screw_large.png (32x32)
│       ├── led_glow_red.png (48x48)
│       ├── led_glow_green.png (48x48)
│       └── led_glow_yellow.png (48x48)
├── ui\
│   ├── styles.py
│   ├── main_window.py
│   └── widgets\
│       ├── vu_meter.py
│       ├── led_indicator.py
│       └── industrial_button.py
└── main_vintage.py
```

## TAREA

Modifica los archivos para integrar los assets y mejorar la estética. NO toques la lógica de procesamiento (threads, análisis, Excel).

---

## 1. MODIFICAR: `ui/styles.py`

Encuentra la función `get_stylesheet()` y realiza estos cambios:

### 1.1. QMainWindow — Usar textura rasta como fondo:

```python
QMainWindow {{
    background-image: url(assets/textures/rasta_wood_background.png);
    background-repeat: no-repeat;
    background-position: center;
    color: {COLORS['text_warm']};
}}
```

### 1.2. QGroupBox — Bisel real con transparencia (para ver el fondo):

```python
QGroupBox {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(74, 55, 40, 220),
        stop:0.02 rgba(45, 32, 19, 240),
        stop:0.98 rgba(45, 32, 19, 240),
        stop:1 rgba(26, 16, 8, 255));
    border: 3px solid;
    border-color: #6E5B4B #1A1008 #1A1008 #6E5B4B;
    border-radius: 6px;
    margin-top: 14px;
    padding: 18px 12px 12px 12px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 3px 12px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #6E5B4B, stop:1 #4A3728);
    border: 2px solid;
    border-color: #7F6C5C #3D3020 #3D3020 #7F6C5C;
    border-radius: 3px;
    color: {COLORS['rasta_yellow']};
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 2px;
}}
```

### 1.3. QLineEdit y QSpinBox — Displays LCD con bisel inset:

```python
QLineEdit, QSpinBox {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0A0A00,
        stop:0.03 #12120A,
        stop:0.97 #12120A,
        stop:1 #0A0A00);
    border: 3px solid;
    border-color: #1A1A1A #505040 #505040 #1A1A1A;
    border-radius: 2px;
    color: {COLORS['lcd_yellow']};
    font-family: "Consolas", "Courier New", monospace;
    font-size: 16px;
    font-weight: bold;
    padding: 6px 10px;
    letter-spacing: 3px;
}}

QLineEdit:focus, QSpinBox:focus {{
    border-color: #1A1A1A {COLORS['rasta_yellow']} {COLORS['rasta_yellow']} #1A1A1A;
}}

QLineEdit:disabled, QSpinBox:disabled {{
    background: #1A1A1A;
    color: {COLORS['text_dim']};
    border-color: #1A1A1A #353530 #353530 #1A1A1A;
}}
```

### 1.4. QComboBox — Dropdown con bisel:

```python
QComboBox {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #6E5B4B,
        stop:0.1 #4A3728,
        stop:0.9 #4A3728,
        stop:1 #2D2013);
    border: 3px solid;
    border-color: #7F6C5C #2D2013 #2D2013 #7F6C5C;
    border-radius: 4px;
    color: {COLORS['text_warm']};
    padding: 6px 10px;
    min-width: 150px;
    font-size: 13px;
    font-weight: bold;
}}

QComboBox:hover {{
    border-color: {COLORS['rasta_yellow']} #2D2013 #2D2013 {COLORS['rasta_yellow']};
}}

QComboBox:on {{
    border-color: #2D2013 #7F6C5C #7F6C5C #2D2013;
}}

QComboBox::drop-down {{
    border-left: 1px solid #2D2013;
    width: 25px;
    background: transparent;
}}

QComboBox::down-arrow {{
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 7px solid {COLORS['text_warm']};
    margin-right: 6px;
}}

QComboBox QAbstractItemView {{
    background: #2D2013;
    color: {COLORS['text_warm']};
    selection-background-color: {COLORS['rasta_red']};
    selection-color: white;
    border: 2px solid #4A3728;
    padding: 4px;
}}
```

### 1.5. QProgressBar — Barra con bisel y brillo:

```python
QProgressBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #080808, stop:0.5 #121212, stop:1 #080808);
    border: 3px solid;
    border-color: #1A1A1A #4A4A4A #4A4A4A #1A1A1A;
    border-radius: 4px;
    text-align: center;
    color: {COLORS['rasta_yellow']};
    font-weight: bold;
    font-size: 12px;
    height: 28px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #20E870,
        stop:0.15 #15C050,
        stop:0.5 #0D8140,
        stop:0.85 #15C050,
        stop:1 #20E870);
    border: 1px solid #0A6A30;
    border-radius: 2px;
    margin: 3px;
}}
```

### 1.6. QTextEdit — Display de estado (terminal):

```python
QTextEdit {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #040404, stop:0.02 #0A0A05, stop:0.98 #0A0A05, stop:1 #040404);
    border: 3px solid;
    border-color: #151515 #3A3A3A #3A3A3A #151515;
    border-radius: 4px;
    color: #00FF00;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    padding: 8px;
    selection-background-color: {COLORS['rasta_green']};
}}
```

### 1.7. QPushButton — Botones secundarios:

```python
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #6E5B4B,
        stop:0.1 #5D4A3A,
        stop:0.9 #4A3728,
        stop:1 #3D3020);
    border: 3px solid;
    border-color: #7F6C5C #2D2013 #2D2013 #7F6C5C;
    border-radius: 4px;
    color: {COLORS['text_warm']};
    padding: 8px 16px;
    font-size: 12px;
    font-weight: bold;
}}

QPushButton:hover {{
    border-color: {COLORS['rasta_yellow']} #2D2013 #2D2013 {COLORS['rasta_yellow']};
}}

QPushButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3D3020,
        stop:0.1 #4A3728,
        stop:0.9 #5D4A3A,
        stop:1 #6E5B4B);
    border-color: #2D2013 #7F6C5C #7F6C5C #2D2013;
}}

QPushButton:disabled {{
    background: #3D3D3D;
    border-color: #4A4A4A #2A2A2A #2A2A2A #4A4A4A;
    color: {COLORS['text_dim']};
}}
```

### 1.8. QCheckBox — Con bisel:

```python
QCheckBox {{
    color: {COLORS['text_warm']};
    spacing: 8px;
    font-size: 12px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid;
    border-color: #1A1A1A #4A4A4A #4A4A4A #1A1A1A;
    border-radius: 3px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0A0A0A, stop:1 #1A1A1A);
}}

QCheckBox::indicator:hover {{
    border-color: #1A1A1A {COLORS['rasta_yellow']} {COLORS['rasta_yellow']} #1A1A1A;
}}

QCheckBox::indicator:checked {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #15C050,
        stop:0.5 #0D8140,
        stop:1 #085030);
    border-color: #0D8140 #053020 #053020 #0D8140;
}}
```

---

## 2. MODIFICAR: `ui/widgets/vu_meter.py`

### 2.1. Asegúrate de que estos imports estén al inicio:

```python
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen, QFont
from ..colors import COLORS
```

### 2.2. REEMPLAZA el método `paintEvent` completo:

```python
def paintEvent(self, event):
    """Dibujar VU meter con aspecto analógico profesional."""
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    width = self.width()
    height = self.height()

    # Área del label (top)
    label_height = 25
    meter_top = label_height
    meter_height = height - label_height
    meter_rect = QRect(2, meter_top + 2, width - 4, meter_height - 4)

    # 1. LABEL
    painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
    painter.setPen(QColor(COLORS['text_warm']))
    painter.drawText(0, 0, width, label_height, Qt.AlignmentFlag.AlignCenter, self.label_text)

    # 2. MARCO BISELADO (efecto inset profundo)
    self._draw_inset_frame(painter, meter_rect)

    # 3. SEGMENTOS
    inner_rect = meter_rect.adjusted(4, 4, -4, -4)
    segment_height = (inner_rect.height() - (self.num_segments - 1) * self.segment_gap) / self.num_segments
    active_segments = int(self.value * self.num_segments)
    peak_segment = int(self.peak_value * self.num_segments)

    for i in range(self.num_segments):
        segment_index = self.num_segments - 1 - i
        y = inner_rect.top() + i * (segment_height + self.segment_gap)
        
        is_active = segment_index < active_segments
        is_peak = segment_index == peak_segment - 1 and peak_segment > active_segments
        
        color = self._get_segment_color(segment_index)
        self._draw_segment(painter, inner_rect.left(), y, inner_rect.width(), 
                          segment_height, color, is_active or is_peak)

    # 4. REFLEXIÓN DE CRISTAL
    self._draw_glass_reflection(painter, inner_rect)
```

### 2.3. AÑADE estos nuevos métodos a la clase VUMeter:

```python
def _draw_inset_frame(self, painter, rect):
    """Marco con efecto inset 3D profundo."""
    # Sombra exterior (oscuro arriba-izquierda)
    painter.setPen(QPen(QColor('#0A0A0A'), 3))
    painter.drawLine(rect.topLeft(), rect.topRight())
    painter.drawLine(rect.topLeft(), rect.bottomLeft())
    
    # Highlight exterior (claro abajo-derecha)
    painter.setPen(QPen(QColor('#4A4A4A'), 2))
    painter.drawLine(rect.bottomLeft(), rect.bottomRight())
    painter.drawLine(rect.topRight(), rect.bottomRight())
    
    # Fondo con gradiente
    inner = rect.adjusted(3, 3, -3, -3)
    bg_gradient = QLinearGradient(float(inner.left()), float(inner.top()), 
                                   float(inner.right()), float(inner.top()))
    bg_gradient.setColorAt(0, QColor('#030303'))
    bg_gradient.setColorAt(0.5, QColor('#080808'))
    bg_gradient.setColorAt(1, QColor('#030303'))
    painter.fillRect(inner, bg_gradient)


def _draw_segment(self, painter, x, y, width, height, color, is_active):
    """Dibujar segmento individual con efecto 3D."""
    x, y, width, height = int(x), int(y), int(width), int(height)
    
    if is_active:
        # Gradiente vertical para volumen 3D
        gradient = QLinearGradient(float(x), float(y), float(x), float(y + height))
        gradient.setColorAt(0, color.lighter(160))
        gradient.setColorAt(0.15, color.lighter(130))
        gradient.setColorAt(0.5, color)
        gradient.setColorAt(0.85, color.darker(120))
        gradient.setColorAt(1, color.darker(150))
        painter.fillRect(x, y, width, height, gradient)
        
        # Línea de brillo superior
        painter.setPen(QPen(color.lighter(220), 1))
        painter.drawLine(x + 2, y + 1, x + width - 2, y + 1)
        
        # Borde sutil
        painter.setPen(QPen(color.darker(160), 1))
        painter.drawRect(x, y, width - 1, height - 1)
    else:
        # Segmento apagado
        painter.fillRect(x, y, width, height, QColor('#0A0A0A'))
        dark = QColor(color)
        dark.setAlpha(20)
        painter.fillRect(x + 1, y + 1, width - 2, height - 2, dark)


def _draw_glass_reflection(self, painter, rect):
    """Reflexión de cristal sobre el meter."""
    reflection_height = int(rect.height() * 0.35)
    glass = QLinearGradient(float(rect.left()), float(rect.top()), 
                            float(rect.left()), float(rect.top() + reflection_height))
    glass.setColorAt(0, QColor(255, 255, 255, 35))
    glass.setColorAt(0.5, QColor(255, 255, 255, 15))
    glass.setColorAt(1, QColor(255, 255, 255, 0))
    painter.fillRect(rect.left(), rect.top(), rect.width(), reflection_height, glass)
```

---

## 3. MODIFICAR: `ui/widgets/industrial_button.py`

### 3.1. REEMPLAZA `_draw_normal_button`:

```python
def _draw_normal_button(self, painter, rect):
    """Dibujar botón en estado normal con profundidad real."""
    gradient = QLinearGradient(float(rect.left()), float(rect.top()), 
                                float(rect.left()), float(rect.bottom()))
    color = QColor(COLORS['rasta_red'])

    gradient.setColorAt(0, color.lighter(170))
    gradient.setColorAt(0.12, color.lighter(130))
    gradient.setColorAt(0.5, color)
    gradient.setColorAt(0.88, color.darker(120))
    gradient.setColorAt(1, color.darker(160))

    painter.setBrush(gradient)
    painter.setPen(QPen(QColor('#2A2A2A'), 2))
    painter.drawRoundedRect(rect, 4, 4)
    
    # Línea de brillo superior
    painter.setPen(QPen(QColor(255, 255, 255, 80), 1))
    painter.drawLine(rect.left() + 6, rect.top() + 3, 
                     rect.right() - 6, rect.top() + 3)
```

### 3.2. REEMPLAZA `_draw_hover_button`:

```python
def _draw_hover_button(self, painter, rect):
    """Dibujar botón en estado hover (más brillante)."""
    gradient = QLinearGradient(float(rect.left()), float(rect.top()), 
                                float(rect.left()), float(rect.bottom()))
    color = QColor(COLORS['rasta_red']).lighter(115)

    gradient.setColorAt(0, color.lighter(165))
    gradient.setColorAt(0.12, color.lighter(135))
    gradient.setColorAt(0.5, color)
    gradient.setColorAt(0.88, color.darker(115))
    gradient.setColorAt(1, color.darker(150))

    painter.setBrush(gradient)
    painter.setPen(QPen(QColor(COLORS['rasta_yellow']), 3))
    painter.drawRoundedRect(rect, 4, 4)
    
    # Brillo más intenso en hover
    painter.setPen(QPen(QColor(255, 255, 255, 110), 1))
    painter.drawLine(rect.left() + 6, rect.top() + 3, 
                     rect.right() - 6, rect.top() + 3)
```

### 3.3. REEMPLAZA `_draw_pressed_button`:

```python
def _draw_pressed_button(self, painter, rect):
    """Dibujar botón en estado presionado (hundido)."""
    gradient = QLinearGradient(float(rect.left()), float(rect.top()), 
                                float(rect.left()), float(rect.bottom()))
    color = QColor(COLORS['rasta_red']).darker(115)

    # Gradiente invertido para efecto hundido
    gradient.setColorAt(0, color.darker(140))
    gradient.setColorAt(0.12, color.darker(110))
    gradient.setColorAt(0.5, color)
    gradient.setColorAt(0.88, color.lighter(105))
    gradient.setColorAt(1, color.lighter(115))

    painter.setBrush(gradient)
    painter.setPen(QPen(QColor('#1A1A1A'), 2))
    
    # Rect ligeramente más pequeño para efecto de presión
    pressed_rect = rect.adjusted(2, 2, -1, -1)
    painter.drawRoundedRect(pressed_rect, 4, 4)
```

### 3.4. REEMPLAZA `_draw_beveled_rect`:

```python
def _draw_beveled_rect(self, painter, rect, base_color, outset=True):
    """Rectángulo con efecto biselado pronunciado."""
    color = QColor(base_color)

    # Colores más contrastados
    light_color = color.lighter(175)
    dark_color = color.darker(190)

    if outset:
        top_left_color = light_color
        bottom_right_color = dark_color
    else:
        top_left_color = dark_color
        bottom_right_color = light_color

    # Relleno base con gradiente
    base_gradient = QLinearGradient(float(rect.left()), float(rect.top()), 
                                     float(rect.left()), float(rect.bottom()))
    base_gradient.setColorAt(0, color.lighter(115))
    base_gradient.setColorAt(0.5, color)
    base_gradient.setColorAt(1, color.darker(115))
    painter.setBrush(base_gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRect(rect)

    # Bordes biselados (4px)
    bevel_width = 4

    painter.setPen(QPen(top_left_color, bevel_width))
    painter.drawLine(rect.topLeft(), rect.topRight())
    painter.drawLine(rect.topLeft(), rect.bottomLeft())

    painter.setPen(QPen(bottom_right_color, bevel_width))
    painter.drawLine(rect.bottomLeft(), rect.bottomRight())
    painter.drawLine(rect.topRight(), rect.bottomRight())
```

### 3.5. MODIFICA `paintEvent` para añadir sombra proyectada:

Busca el método `paintEvent` y añade esto AL INICIO, antes de dibujar el marco:

```python
def paintEvent(self, event):
    """Dibujar botón industrial con marco y centro."""
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    width = self.width()
    height = self.height()

    # ========== NUEVO: SOMBRA PROYECTADA ==========
    shadow_offset = 4
    shadow_color = QColor(0, 0, 0, 70)
    shadow_rect = QRect(shadow_offset, shadow_offset, width - 2, height - 2)
    painter.fillRect(shadow_rect, shadow_color)
    # ==============================================

    # Dimensiones del marco y botón (ajustar para la sombra)
    frame_margin = 6
    button_margin = 10

    # 1. MARCO EXTERIOR (amarillo con biselado outset)
    frame_rect = QRect(0, 0, width - shadow_offset, height - shadow_offset)
    self._draw_beveled_rect(painter, frame_rect, COLORS['rasta_yellow'], outset=True)

    # ... el resto del código sigue igual ...
```

---

## 4. VERIFICACIÓN FINAL

Después de hacer los cambios, ejecuta:

```bash
python main_vintage.py
```

Deberías ver:

1. ✅ Fondo con listones de madera rasta (rojo, verde, amarillo)
2. ✅ VU meters con brillo, bisel y reflexión de cristal
3. ✅ Botón EDABEA con sombra proyectada y gradiente 3D pronunciado
4. ✅ Paneles con bordes biselados reales
5. ✅ Displays LCD con aspecto hundido
6. ✅ Todos los controles con profundidad visual

---

## NOTAS TÉCNICAS PyQt6

**IMPORTANTE — Evitar errores:**

1. **QLinearGradient siempre con floats:**
   ```python
   # ✅ CORRECTO:
   QLinearGradient(float(rect.left()), float(rect.top()), float(rect.left()), float(rect.bottom()))
   
   # ❌ INCORRECTO (causa TypeError):
   QLinearGradient(rect.topLeft(), rect.bottomLeft())
   ```

2. **setAlpha() usa 0-255:**
   ```python
   color.setAlpha(128)  # 50% transparencia
   ```

3. **Bisel real en QSS = 4 valores de border-color:**
   ```css
   border-color: #CLARO #OSCURO #OSCURO #CLARO;  /* OUTSET */
   border-color: #OSCURO #CLARO #CLARO #OSCURO;  /* INSET */
   ```
