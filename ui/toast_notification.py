"""
Z32 Nexus - Toast Notification Widget
Custom slide-in notifications with spiritual messages
"""

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, pyqtProperty
from PyQt6.QtGui import QFont, QColor
import random


class ToastNotification(QFrame):
    """
    Custom toast notification that slides in from the corner.
    Includes motivational/spiritual messages.
    """
    
    SPIRITUAL_MESSAGES = [
        "Rabbi Zidni Ilma",  # My Lord, increase me in knowledge
        "Alhamdulillah",     # Praise be to God
        "SubhanAllah",       # Glory be to God
        "MashaAllah",        # God has willed it
        "Bismillah",         # In the name of God
        "JazakAllah Khair",  # May God reward you
        "Barakallah",        # May God bless you
        "In sha Allah",      # If God wills
    ]
    
    MOTIVATIONAL_MESSAGES = [
        "Keep pushing forward!",
        "Excellent progress!",
        "You're doing great!",
        "One step at a time.",
        "Consistency is key.",
        "Small wins matter.",
        "Stay focused.",
        "You've got this!",
    ]
    
    def __init__(self, parent=None, title: str = "", message: str = "", 
                 duration: int = 5000, toast_type: str = "success"):
        super().__init__(parent)
        self.duration = duration
        self.toast_type = toast_type
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.Tool |
                           Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        self._setup_ui(title, message)
        self._opacity = 1.0
        
    def _setup_ui(self, title: str, message: str):
        """Setup the toast UI"""
        # Colors based on type
        colors = {
            'success': ('#44ff44', '#1a3a1a'),
            'info': ('#00d4ff', '#1a2a3a'),
            'warning': ('#ffaa00', '#3a2a1a'),
            'error': ('#ff4444', '#3a1a1a'),
            'spiritual': ('#ffdd00', '#2a2a1a'),
        }
        
        accent, bg = colors.get(self.toast_type, colors['info'])
        
        self.setStyleSheet(f"""
            ToastNotification {{
                background-color: {bg};
                border: 2px solid {accent};
                border-radius: 8px;
                padding: 0px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Title
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                color: {accent};
                font-family: Consolas;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            """)
            layout.addWidget(title_label)
        
        # Message
        if message:
            msg_label = QLabel(message)
            msg_label.setStyleSheet(f"""
                color: #cccccc;
                font-family: Consolas;
                font-size: 12px;
                background: transparent;
            """)
            msg_label.setWordWrap(True)
            layout.addWidget(msg_label)
        
        self.setMinimumWidth(280)
        self.setMaximumWidth(350)
        self.adjustSize()
    
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def show_toast(self, parent_widget=None):
        """Show the toast with slide-in animation"""
        # Position in top-right corner
        if parent_widget:
            parent_pos = parent_widget.mapToGlobal(QPoint(0, 0))
            x = parent_pos.x() + parent_widget.width() - self.width() - 20
            y = parent_pos.y() + 20
        else:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                x = geo.right() - self.width() - 20
                y = geo.top() + 20
            else:
                x, y = 100, 100
        
        # Start position (off-screen to the right)
        self.move(x + 100, y)
        self.show()
        
        # Slide in animation
        self.slide_anim = QPropertyAnimation(self, b"pos")
        self.slide_anim.setDuration(300)
        self.slide_anim.setStartValue(QPoint(x + 100, y))
        self.slide_anim.setEndValue(QPoint(x, y))
        self.slide_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.slide_anim.start()
        
        # Auto-dismiss timer
        QTimer.singleShot(self.duration, self.fade_out)
    
    def fade_out(self):
        """Fade out and close the toast"""
        self.fade_anim = QPropertyAnimation(self, b"opacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_anim.finished.connect(self.close)
        self.fade_anim.start()
    
    @classmethod
    def show_success(cls, parent, title: str = "Success!", message: str = ""):
        """Show a success toast"""
        toast = cls(parent, title, message, toast_type="success")
        toast.show_toast(parent)
        return toast
    
    @classmethod
    def show_spiritual(cls, parent, custom_message: str = None):
        """Show a spiritual motivation toast"""
        message = custom_message or random.choice(cls.SPIRITUAL_MESSAGES)
        toast = cls(parent, "Blessed!", message, toast_type="spiritual")
        toast.show_toast(parent)
        return toast
    
    @classmethod
    def show_motivation(cls, parent, custom_message: str = None):
        """Show a motivational toast"""
        message = custom_message or random.choice(cls.MOTIVATIONAL_MESSAGES)
        toast = cls(parent, "Keep Going!", message, toast_type="info")
        toast.show_toast(parent)
        return toast
    
    @classmethod
    def show_error(cls, parent, title: str = "Error", message: str = ""):
        """Show an error toast"""
        toast = cls(parent, title, message, toast_type="error")
        toast.show_toast(parent)
        return toast
    
    @classmethod
    def show_warning(cls, parent, title: str = "Warning", message: str = ""):
        """Show a warning toast"""
        toast = cls(parent, title, message, toast_type="warning")
        toast.show_toast(parent)
        return toast


class ToastManager:
    """Manages multiple toast notifications with stacking"""
    
    _active_toasts = []
    
    @classmethod
    def show(cls, parent, title: str, message: str, toast_type: str = "info", duration: int = 5000):
        """Show a toast and manage stacking"""
        toast = ToastNotification(parent, title, message, duration, toast_type)
        
        # Calculate position based on active toasts
        offset = sum(t.height() + 10 for t in cls._active_toasts if not t.isHidden())
        
        if parent:
            parent_pos = parent.mapToGlobal(QPoint(0, 0))
            x = parent_pos.x() + parent.width() - toast.width() - 20
            y = parent_pos.y() + 20 + offset
        else:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                x = geo.right() - toast.width() - 20
                y = geo.top() + 20 + offset
            else:
                x, y = 100, 100 + offset
        
        toast.move(x, y)
        toast.show()
        
        cls._active_toasts.append(toast)
        
        # Clean up when toast closes
        toast.destroyed.connect(lambda: cls._active_toasts.remove(toast) if toast in cls._active_toasts else None)
        
        # Auto-dismiss
        QTimer.singleShot(duration, toast.fade_out)
        
        return toast
