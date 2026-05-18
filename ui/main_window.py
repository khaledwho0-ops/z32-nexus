"""
Z32 Nexus - Main Window
Primary dashboard with system tray integration
"""

import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QListWidget, QListWidgetItem,
    QSystemTrayIcon, QMenu, QCheckBox, QFrame, QSpacerItem,
    QSizePolicy, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QIcon, QFont, QAction, QPixmap, QPainter, QColor

from .styles import get_stylesheet, get_theme_color
from .progress_widgets import ProgressRing, StreakCounter, StatusDot
from .toast_notification import ToastNotification
from utils.signal_bus import signal_bus
from utils.config_manager import config
from database import db, Task


class DashboardWidget(QWidget):
    """Main dashboard showing daily tasks and progress"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_data()
        self._connect_signals()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Section
        header = QHBoxLayout()
        
        # Title and Phase
        title_section = QVBoxLayout()
        
        self.title_label = QLabel("Z32 NEXUS")
        self.title_label.setObjectName("title")
        self.title_label.setFont(QFont('Consolas', 24, QFont.Weight.Bold))
        title_section.addWidget(self.title_label)
        
        self.phase_label = QLabel(f"PHASE {config.current_phase}")
        self.phase_label.setObjectName("subtitle")
        title_section.addWidget(self.phase_label)
        
        header.addLayout(title_section)
        header.addStretch()
        
        # Progress Ring
        self.progress_ring = ProgressRing()
        header.addWidget(self.progress_ring)
        
        # Streak Counter
        self.streak_counter = StreakCounter()
        header.addWidget(self.streak_counter)
        
        layout.addLayout(header)
        
        # Status Bar
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #1a1a1a; border-radius: 8px; padding: 8px;")
        status_layout = QHBoxLayout(status_frame)
        
        self.status_dot = StatusDot()
        status_layout.addWidget(self.status_dot)
        
        self.status_label = QLabel("ON TRACK")
        self.status_label.setStyleSheet("color: #888888; font-size: 12px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #888888; font-size: 12px;")
        status_layout.addWidget(self.time_label)
        
        layout.addWidget(status_frame)
        
        # Tasks Section
        tasks_header = QHBoxLayout()
        tasks_title = QLabel("DAILY PROTOCOL")
        tasks_title.setFont(QFont('Consolas', 14, QFont.Weight.Bold))
        tasks_header.addWidget(tasks_title)
        
        tasks_header.addStretch()
        
        self.words_today_label = QLabel("Words: 0")
        self.words_today_label.setStyleSheet("color: #888888;")
        tasks_header.addWidget(self.words_today_label)
        
        layout.addLayout(tasks_header)
        
        # Task List
        self.task_list = QListWidget()
        self.task_list.setMinimumHeight(200)
        layout.addWidget(self.task_list)
        
        # Anti-Fragile Buttons
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(10)
        
        self.istighfar_btn = QPushButton("ISTIGHFAR RESET")
        self.istighfar_btn.setObjectName("dangerButton")
        self.istighfar_btn.setToolTip("Reset daily progress to 0% but keep streak")
        self.istighfar_btn.clicked.connect(self._on_istighfar)
        buttons_layout.addWidget(self.istighfar_btn)
        
        self.sujood_btn = QPushButton("SUJOOD MODE")
        self.sujood_btn.setToolTip("5-minute silent countdown - mute everything")
        self.sujood_btn.clicked.connect(self._on_sujood)
        buttons_layout.addWidget(self.sujood_btn)
        
        buttons_layout.addStretch()
        
        layout.addWidget(buttons_frame)
        
        # Update time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        self._update_time()
    
    def _load_data(self):
        """Load data from database"""
        # Get today's progress
        progress = db.get_today_progress()
        self.progress_ring.animate_to(progress['daily_score'])
        self.streak_counter.streak = progress['streak']
        self.words_today_label.setText(f"Words: {progress['words_learned']}")
        
        # Update status
        score = progress['daily_score']
        if score >= 80:
            self.status_dot.status = 'green'
            self.status_label.setText("EXCELLENT!")
        elif score >= 50:
            self.status_dot.status = 'yellow'
            self.status_label.setText("ON TRACK")
        else:
            self.status_dot.status = 'red'
            self.status_label.setText("NEEDS ATTENTION")
        
        # Load tasks
        self._load_tasks()
    
    def _load_tasks(self):
        """Load tasks for current phase"""
        self.task_list.clear()
        
        session = db.get_session()
        try:
            current_phase = config.current_phase
            tasks = session.query(Task).filter(
                Task.phase_required <= current_phase,
                Task.is_active == True
            ).order_by(Task.order).all()
            
            progress = db.get_today_progress()
            completed_ids = progress.get('tasks_completed', []) or []
            
            for task in tasks:
                item = QListWidgetItem()
                
                checkbox = QCheckBox(f"{task.name} (+{task.xp_reward} XP)")
                checkbox.setChecked(task.id in completed_ids)
                checkbox.setProperty('task_id', task.id)
                checkbox.setProperty('xp_reward', task.xp_reward)
                checkbox.stateChanged.connect(self._on_task_toggled)
                
                if task.id in completed_ids:
                    checkbox.setStyleSheet("color: #666666; text-decoration: line-through;")
                
                self.task_list.addItem(item)
                self.task_list.setItemWidget(item, checkbox)
        finally:
            session.close()
    
    def _connect_signals(self):
        """Connect signal bus signals"""
        signal_bus.word_learned.connect(self._on_word_learned)
        signal_bus.daily_progress_updated.connect(self._on_progress_updated)
        signal_bus.streak_updated.connect(self._on_streak_updated)
    
    def _update_time(self):
        """Update the time display"""
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S | %Y-%m-%d"))
    
    @pyqtSlot(int)
    def _on_task_toggled(self, state):
        """Handle task checkbox toggle"""
        checkbox = self.sender()
        task_id = checkbox.property('task_id')
        xp_reward = checkbox.property('xp_reward')
        
        session = db.get_session()
        try:
            from datetime import date
            from database import UserProgress
            
            today = date.today()
            progress = session.query(UserProgress).filter_by(date=today).first()
            
            if progress:
                completed = progress.tasks_completed or []
                
                if state == Qt.CheckState.Checked.value:
                    if task_id not in completed:
                        completed.append(task_id)
                        # Add XP
                        if config.add_xp(xp_reward):
                            signal_bus.level_up.emit(config.level)
                        signal_bus.xp_gained.emit(xp_reward)
                        
                        # Show toast
                        ToastNotification.show_spiritual(self)
                        
                        checkbox.setStyleSheet("color: #666666; text-decoration: line-through;")
                else:
                    if task_id in completed:
                        completed.remove(task_id)
                        checkbox.setStyleSheet("")
                
                progress.tasks_completed = completed
                
                # Calculate new score
                session_tasks = session.query(Task).filter(
                    Task.phase_required <= config.current_phase,
                    Task.is_active == True
                ).count()
                
                new_score = int((len(completed) / max(session_tasks, 1)) * 100)
                progress.daily_score = new_score
                
                session.commit()
                
                self.progress_ring.animate_to(new_score)
                signal_bus.daily_progress_updated.emit(new_score)
                signal_bus.task_completed.emit(task_id)
        finally:
            session.close()
    
    def _on_istighfar(self):
        """Handle Istighfar reset"""
        reply = QMessageBox.question(
            self, "Istighfar Reset",
            "Reset daily progress to 0%?\n(Streak will be preserved)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            db.update_today_progress(daily_score=0, tasks_completed=[])
            self.progress_ring.animate_to(0)
            self._load_tasks()
            signal_bus.istighfar_reset.emit()
            ToastNotification.show_motivation(self, "Fresh start! Let's go!")
    
    def _on_sujood(self):
        """Handle Sujood panic mode"""
        signal_bus.sujood_mode_start.emit()
        # This will be handled by the main window to show a countdown dialog
    
    @pyqtSlot(str, str)
    def _on_word_learned(self, english, spanish):
        """Handle word learned signal"""
        progress = db.get_today_progress()
        self.words_today_label.setText(f"Words: {progress['words_learned']}")
    
    @pyqtSlot(int)
    def _on_progress_updated(self, new_score):
        """Handle progress update"""
        if new_score >= 80:
            self.status_dot.status = 'green'
            self.status_label.setText("EXCELLENT!")
        elif new_score >= 50:
            self.status_dot.status = 'yellow'
            self.status_label.setText("ON TRACK")
        else:
            self.status_dot.status = 'red'
            self.status_label.setText("NEEDS ATTENTION")
    
    @pyqtSlot(int)
    def _on_streak_updated(self, new_streak):
        """Handle streak update"""
        self.streak_counter.streak = new_streak


class MainWindow(QMainWindow):
    """Main application window with system tray support"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Z32 Nexus")
        self.setMinimumSize(800, 600)
        
        # Apply theme
        theme_color = config.theme_color
        self.setStyleSheet(get_stylesheet(theme_color))
        
        # Setup UI
        self._setup_ui()
        
        # Setup system tray
        self._setup_tray()
        
        # Connect signals
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Dashboard tab
        self.dashboard = DashboardWidget()
        self.tabs.addTab(self.dashboard, "📊 Dashboard")
        
        # Vocabulary tool tab
        from ui.vocab_tab import VocabTab
        self.vocab_tab = VocabTab()
        self.tabs.addTab(self.vocab_tab, "📚 Vocab Tool")
        
        # Flashcard tab
        from ui.flashcard_widget import FlashcardTab
        self.flashcard_tab = FlashcardTab()
        self.tabs.addTab(self.flashcard_tab, "🎴 Flashcards")
        
        # Grammar Drill tab - NEW (Feature 18)
        from ui.grammar_drill import GrammarDrillTab
        self.grammar_tab = GrammarDrillTab()
        self.tabs.addTab(self.grammar_tab, "📝 Grammar")
        
        # Journal tab
        from ui.journal_tab import JournalTab
        self.journal_tab = JournalTab()
        self.tabs.addTab(self.journal_tab, "✏️ Journal")
        
        # Analytics tab - NEW (Features 23-27)
        from ui.analytics_tab import AnalyticsTab
        self.analytics_tab = AnalyticsTab()
        self.tabs.addTab(self.analytics_tab, "📈 Analytics")
        
        layout.addWidget(self.tabs)
        
        # Status bar with daily quote
        self._show_daily_quote()

    
    def _setup_tray(self):
        """Setup system tray icon"""
        # Create a simple icon using QPainter
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(config.theme_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()
        
        icon = QIcon(pixmap)
        
        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("Z32 Nexus - Language Learning")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self._show_window)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        # Quick actions
        vocab_action = QAction("Quick Vocab Review", self)
        vocab_action.triggered.connect(lambda: self._quick_action('vocab'))
        tray_menu.addAction(vocab_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()
    
    def _connect_signals(self):
        """Connect signal bus signals"""
        signal_bus.show_toast.connect(self._show_toast)
        signal_bus.minimize_to_tray.connect(self.hide)
        signal_bus.restore_from_tray.connect(self._show_window)
        signal_bus.theme_changed.connect(self._on_theme_changed)
        signal_bus.sujood_mode_start.connect(self._start_sujood_mode)
    
    def closeEvent(self, event):
        """Override close event to minimize to tray instead of closing"""
        if self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Z32 Nexus",
                "Application minimized to system tray.\nRight-click the icon to quit.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            event.accept()
    
    def _show_window(self):
        """Show and activate the window"""
        self.show()
        self.activateWindow()
        self.raise_()
    
    def _quit_app(self):
        """Actually quit the application"""
        signal_bus.app_shutdown.emit()
        self.tray_icon.hide()
        QApplication.quit()
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()
    
    def _quick_action(self, action: str):
        """Handle quick actions from tray"""
        self._show_window()
        if action == 'vocab':
            self.tabs.setCurrentIndex(1)
    
    @pyqtSlot(str, str, int)
    def _show_toast(self, title: str, message: str, duration: int):
        """Show a toast notification"""
        ToastNotification(self, title, message, duration).show_toast(self)
    
    @pyqtSlot(str)
    def _on_theme_changed(self, new_color: str):
        """Handle theme change"""
        self.setStyleSheet(get_stylesheet(new_color))
    
    @pyqtSlot()
    def _start_sujood_mode(self):
        """Start Sujood panic mode - 5 minute silent countdown"""
        # This would show a fullscreen timer
        # For now, just show a message
        self.tray_icon.showMessage(
            "Sujood Mode",
            "5-minute silent mode activated.\nTake a breath.",
            QSystemTrayIcon.MessageIcon.Information,
            5000
        )
    
    def _show_daily_quote(self):
        """
        Feature 14: Daily Immersion Quotes
        Display a Spanish quote in the status bar
        """
        import random
        
        # Sample quotes (in production, load from database)
        quotes = [
            ("El que no arriesga, no gana", "He who doesn't risk, doesn't win", "Spanish Proverb"),
            ("La práctica hace al maestro", "Practice makes the master", "Spanish Proverb"),
            ("Más vale tarde que nunca", "Better late than never", "Spanish Proverb"),
            ("No hay mal que por bien no venga", "Every cloud has a silver lining", "Spanish Proverb"),
            ("Poco a poco se va lejos", "Little by little one goes far", "Spanish Proverb"),
            ("Quien mucho abarca, poco aprieta", "Don't bite off more than you can chew", "Spanish Proverb"),
            ("El saber no ocupa lugar", "Knowledge takes up no space", "Spanish Proverb"),
            ("A mal tiempo, buena cara", "In bad times, a good face", "Spanish Proverb"),
            ("Donde hay voluntad, hay camino", "Where there's a will, there's a way", "Spanish Proverb"),
            ("Cada día es una nueva oportunidad", "Every day is a new opportunity", "Unknown"),
        ]
        
        quote = random.choice(quotes)
        spanish, english, author = quote
        
        # Update status bar with quote
        self.statusBar().showMessage(f"💬 {spanish} — \"{english}\" ({author})")
        
        # Emit signal for other components
        signal_bus.daily_quote_shown.emit(spanish, english, author)
