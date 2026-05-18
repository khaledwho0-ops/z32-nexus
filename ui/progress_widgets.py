"""
Z32 Nexus - Circular Progress Ring Widget
Custom QPainter widget for daily goal visualization
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QBrush, QLinearGradient
import math


class ProgressRing(QWidget):
    """
    Circular progress ring widget with animated transitions.
    Shows daily completion percentage with color gradient.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._max_value = 100
        self._ring_width = 15
        self._animation = None
        
        # Colors
        self._bg_color = QColor('#1a1a1a')
        self._start_color = QColor('#ff4444')  # Red at 0%
        self._mid_color = QColor('#ffaa00')    # Yellow at 50%
        self._end_color = QColor('#44ff44')    # Green at 100%
        self._text_color = QColor('#00ff41')
        
        self.setMinimumSize(150, 150)
    
    def get_value(self):
        return self._value
    
    def set_value(self, value):
        self._value = max(0, min(value, self._max_value))
        self.update()
    
    value = pyqtProperty(int, get_value, set_value)
    
    def animate_to(self, target_value: int, duration: int = 500):
        """Animate the progress to a target value"""
        if self._animation:
            self._animation.stop()
        
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setDuration(duration)
        self._animation.setStartValue(self._value)
        self._animation.setEndValue(target_value)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.start()
    
    def _get_progress_color(self) -> QColor:
        """Get the color based on current progress"""
        ratio = self._value / self._max_value
        
        if ratio < 0.5:
            # Interpolate between red and yellow
            t = ratio * 2
            r = int(self._start_color.red() + t * (self._mid_color.red() - self._start_color.red()))
            g = int(self._start_color.green() + t * (self._mid_color.green() - self._start_color.green()))
            b = int(self._start_color.blue() + t * (self._mid_color.blue() - self._start_color.blue()))
        else:
            # Interpolate between yellow and green
            t = (ratio - 0.5) * 2
            r = int(self._mid_color.red() + t * (self._end_color.red() - self._mid_color.red()))
            g = int(self._mid_color.green() + t * (self._end_color.green() - self._mid_color.green()))
            b = int(self._mid_color.blue() + t * (self._end_color.blue() - self._mid_color.blue()))
        
        return QColor(r, g, b)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate dimensions
        size = min(self.width(), self.height())
        rect = QRectF(
            (self.width() - size) / 2 + self._ring_width,
            (self.height() - size) / 2 + self._ring_width,
            size - 2 * self._ring_width,
            size - 2 * self._ring_width
        )
        
        # Draw background circle
        bg_pen = QPen(self._bg_color)
        bg_pen.setWidth(self._ring_width)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Draw progress arc
        if self._value > 0:
            progress_color = self._get_progress_color()
            progress_pen = QPen(progress_color)
            progress_pen.setWidth(self._ring_width)
            progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(progress_pen)
            
            # Calculate arc span (start from top, go clockwise)
            span_angle = int(-360 * (self._value / self._max_value) * 16)
            start_angle = 90 * 16  # Start from top
            
            painter.drawArc(rect, start_angle, span_angle)
        
        # Draw center text
        painter.setPen(self._text_color)
        font = QFont('Consolas', 28, QFont.Weight.Bold)
        painter.setFont(font)
        
        text = f"{self._value}%"
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)
        
        # Draw label
        label_font = QFont('Consolas', 10)
        painter.setFont(label_font)
        painter.setPen(QColor('#888888'))
        
        label_rect = self.rect()
        label_rect.moveTop(label_rect.top() + 35)
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, "DAILY GOAL")
    
    def set_colors(self, text_color: str):
        """Update the text color"""
        self._text_color = QColor(text_color)
        self.update()


class StreakCounter(QWidget):
    """Widget to display streak count with fire icon"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._streak = 0
        self._text_color = QColor('#00ff41')
        self.setMinimumSize(100, 80)
    
    @property
    def streak(self):
        return self._streak
    
    @streak.setter
    def streak(self, value: int):
        self._streak = max(0, value)
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw fire emoji/icon
        icon_font = QFont('Segoe UI Emoji', 24)
        painter.setFont(icon_font)
        painter.setPen(QColor('#ff6600'))
        
        icon_rect = self.rect()
        icon_rect.setHeight(40)
        # Use a simple character instead of emoji for compatibility
        painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "*")
        
        # Draw streak number
        num_font = QFont('Consolas', 20, QFont.Weight.Bold)
        painter.setFont(num_font)
        painter.setPen(self._text_color)
        
        num_rect = self.rect()
        num_rect.setTop(35)
        painter.drawText(num_rect, Qt.AlignmentFlag.AlignCenter, str(self._streak))
        
        # Draw label
        label_font = QFont('Consolas', 9)
        painter.setFont(label_font)
        painter.setPen(QColor('#888888'))
        
        label_rect = self.rect()
        label_rect.setTop(60)
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, "STREAK")
    
    def set_color(self, color: str):
        self._text_color = QColor(color)
        self.update()


class StatusDot(QWidget):
    """Small status indicator dot"""
    
    STATUS_COLORS = {
        'green': '#44ff44',
        'yellow': '#ffaa00',
        'red': '#ff4444',
        'gray': '#666666',
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._status = 'gray'
        self._pulse = False
        self.setFixedSize(16, 16)
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value: str):
        if value in self.STATUS_COLORS:
            self._status = value
            self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        color = QColor(self.STATUS_COLORS.get(self._status, '#666666'))
        
        # Draw outer glow
        glow_color = QColor(color)
        glow_color.setAlpha(100)
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 16, 16)
        
        # Draw inner dot
        painter.setBrush(QBrush(color))
        painter.drawEllipse(4, 4, 8, 8)
