"""
VintageScreen - Display con fondo de imagen y texto estilo LCD.
"""

from PyQt6.QtWidgets import QWidget, QLineEdit
from PyQt6.QtCore import pyqtSignal, Qt, QRect
from PyQt6.QtGui import QPainter, QPixmap, QFont, QColor, QFontMetrics


class VintageScreen(QWidget):
    """
    Display vintage con fondo de imagen y texto estilo LCD.
    Puede ser editable o solo lectura.
    """

    text_changed = pyqtSignal(str)

    def __init__(self, bg_image: str, editable: bool = False, parent=None):
        """
        Constructor del VintageScreen.

        Args:
            bg_image: Ruta a la imagen de fondo del display.
            editable: Si True, permite editar el texto.
            parent: Widget padre.
        """
        super().__init__(parent)
        self._text = ""
        self._editable = editable
        self._text_color = QColor("#00FF00")  # Verde LCD por defecto
        self._font = QFont("Courier New", 14, QFont.Weight.Bold)
        self._padding = 15

        # Cargar imagen de fondo
        self._bg_image = QPixmap(bg_image)
        if self._bg_image.isNull():
            raise FileNotFoundError(f"No se pudo cargar: {bg_image}")

        # Fijar tamaño al tamaño de la imagen
        self.setFixedSize(self._bg_image.size())

        # Campo de texto oculto para edición
        if editable:
            self._line_edit = QLineEdit(self)
            self._line_edit.setStyleSheet(
                "background: transparent; border: none; color: transparent;"
            )
            self._line_edit.setGeometry(
                self._padding,
                self._padding,
                self.width() - 2 * self._padding,
                self.height() - 2 * self._padding
            )
            self._line_edit.textChanged.connect(self._on_text_changed)
            self._line_edit.setFont(self._font)
        else:
            self._line_edit = None

    def paintEvent(self, event):
        """Dibuja el display con el texto."""
        painter = QPainter(self)

        # Dibujar fondo
        painter.drawPixmap(0, 0, self._bg_image)

        # Configurar fuente y color
        painter.setFont(self._font)
        painter.setPen(self._text_color)

        # Área de texto
        text_rect = QRect(
            self._padding,
            0,
            self.width() - 2 * self._padding,
            self.height()
        )

        # Dibujar texto centrado verticalmente
        painter.drawText(text_rect,
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        self._text)

    def _on_text_changed(self, text: str):
        """Maneja cambios en el texto editable."""
        self._text = text
        self.update()
        self.text_changed.emit(text)

    def set_text(self, text: str):
        """
        Establece el texto del display.

        Args:
            text: Texto a mostrar.
        """
        self._text = text
        if self._line_edit:
            self._line_edit.setText(text)
        self.update()

    def get_text(self) -> str:
        """Retorna el texto actual."""
        return self._text

    def set_editable(self, editable: bool):
        """
        Cambia si el display es editable.

        Args:
            editable: True para permitir edición.
        """
        self._editable = editable
        if self._line_edit:
            self._line_edit.setVisible(editable)

    def is_editable(self) -> bool:
        """Retorna True si el display es editable."""
        return self._editable

    def set_text_color(self, color: str):
        """
        Establece el color del texto.

        Args:
            color: Color en formato hex (ej: "#00FF00").
        """
        self._text_color = QColor(color)
        self.update()

    def set_font_size(self, size: int):
        """
        Establece el tamaño de la fuente.

        Args:
            size: Tamaño en puntos.
        """
        self._font.setPointSize(size)
        if self._line_edit:
            self._line_edit.setFont(self._font)
        self.update()

    def set_amber_color(self):
        """Establece color ámbar estilo LCD."""
        self._text_color = QColor("#FFB000")
        self.update()

    def set_green_color(self):
        """Establece color verde estilo LCD."""
        self._text_color = QColor("#00FF00")
        self.update()

    def clear(self):
        """Limpia el texto del display."""
        self.set_text("")

    def mousePressEvent(self, event):
        """Permite focus en el campo editable."""
        if self._editable and self._line_edit:
            self._line_edit.setFocus()
        super().mousePressEvent(event)
