"""
Widgets custom basados en imágenes PNG del kit Vintage Obsession.
Todos los widgets usan QPainter para dibujar, sin CSS.
"""

from .image_pad import ImagePad
from .image_switch import ImageSwitch
from .image_button import ImageButton
from .filmstrip_slider import FilmstripSlider
from .filmstrip_knob import FilmstripKnob
from .animated_vu_meter import AnimatedVUMeter
from .animated_led import AnimatedLED
from .vintage_screen import VintageScreen

__all__ = [
    'ImagePad',
    'ImageSwitch',
    'ImageButton',
    'FilmstripSlider',
    'FilmstripKnob',
    'AnimatedVUMeter',
    'AnimatedLED',
    'VintageScreen',
]
