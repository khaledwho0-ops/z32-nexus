"""
Z32 Nexus - Analytics Tab
Features 23-27: Learning Analytics Dashboard

Comprehensive learning statistics and progress visualization:
- Vocabulary Strength Meter (Feature 23)
- Learning Velocity Tracker (Feature 24)
- CEFR Level Estimation (Feature 27)
- Retention Rate Display (Feature 8)
- Optimal Study Time (Feature 29)
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QProgressBar, QTabWidget,
    QGroupBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen

from database import db, Vocabulary, LearningAnalytics
from utils.signal_bus import signal_bus
from utils.cefr_analyzer import cefr_analyzer
from utils.study_optimizer import study_optimizer
from ui.progress_widgets import ProgressRing

logger = logging.getLogger(__name__)


class StatCard(QFrame):
    """A card widget displaying a single statistic."""
    
    def __init__(self, title: str, value: str, subtitle: str = '', 
                 color: str = '#00ff41', parent=None):
        super().__init__(parent)
        self.setObjectName('statCard')
        self.setStyleSheet(f"""
            #statCard {{
                background-color: #1a1a1a;
                border: 1px solid {color};
                border-radius: 8px;
                padding: 10px;
            }}
            #statCard:hover {{
                border: 2px solid {color};
                background-color: #252525;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: #888888; font-size: 11px;")
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        self.value_label = value_label
        layout.addWidget(value_label)
        
        # Subtitle
        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setStyleSheet("color: #666666; font-size: 10px;")
            layout.addWidget(sub_label)
        
        self.setMinimumWidth(120)
        self.setMaximumHeight(100)
    
    def update_value(self, value: str):
        """Update the displayed value."""
        self.value_label.setText(value)


class CEFRProgressWidget(QWidget):
    """Displays CEFR level progress with visual indicators."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_level = 'A1'
        self._progress_to_next = 0
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("CEFR Level Progress")
        header.setStyleSheet("color: #00ff41; font-size: 14px; font-weight: bold;")
        layout.addWidget(header)
        
        # Level indicators
        levels_layout = QHBoxLayout()
        self.level_labels = {}
        
        for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            level_frame = QFrame()
            level_frame.setFixedSize(50, 50)
            level_frame.setStyleSheet("""
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 25px;
            """)
            
            level_label = QLabel(level, level_frame)
            level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            level_label.setGeometry(0, 0, 50, 50)
            level_label.setStyleSheet("color: #666666; font-size: 12px; font-weight: bold;")
            
            self.level_labels[level] = (level_frame, level_label)
            levels_layout.addWidget(level_frame)
        
        layout.addLayout(levels_layout)
        
        # Progress bar to next level
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 5px;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00ff41;
                border-radius: 4px;
            }
        """)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel("0 words to next level")
        self.progress_label.setStyleSheet("color: #888888; font-size: 11px;")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)
    
    def set_level(self, level: str, progress: int, words_to_next: int):
        """Update the displayed level and progress."""
        self._current_level = level
        self._progress_to_next = progress
        
        # Update level indicators
        levels_order = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        current_index = levels_order.index(level) if level in levels_order else 0
        
        for i, lvl in enumerate(levels_order):
            frame, label = self.level_labels[lvl]
            if i < current_index:
                # Completed levels
                frame.setStyleSheet("""
                    background-color: #00ff41;
                    border: 2px solid #00ff41;
                    border-radius: 25px;
                """)
                label.setStyleSheet("color: #0f0f0f; font-size: 12px; font-weight: bold;")
            elif i == current_index:
                # Current level
                frame.setStyleSheet("""
                    background-color: #1a3d1a;
                    border: 2px solid #00ff41;
                    border-radius: 25px;
                """)
                label.setStyleSheet("color: #00ff41; font-size: 12px; font-weight: bold;")
            else:
                # Future levels
                frame.setStyleSheet("""
                    background-color: #1a1a1a;
                    border: 2px solid #333333;
                    border-radius: 25px;
                """)
                label.setStyleSheet("color: #666666; font-size: 12px; font-weight: bold;")
        
        # Update progress bar
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"{words_to_next} words to reach {levels_order[min(current_index + 1, 5)]}")


class OptimalTimeWidget(QWidget):
    """Displays optimal study times based on performance data."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🕐 Optimal Study Times")
        header.setStyleSheet("color: #ffb000; font-size: 14px; font-weight: bold;")
        layout.addWidget(header)
        
        # Time slots container
        self.times_layout = QVBoxLayout()
        layout.addLayout(self.times_layout)
        
        # Placeholder
        self.placeholder = QLabel("Complete more sessions to see your optimal times")
        self.placeholder.setStyleSheet("color: #666666; font-size: 11px; font-style: italic;")
        self.times_layout.addWidget(self.placeholder)
    
    def update_times(self, optimal_hours: List[Dict]):
        """Update displayed optimal times."""
        # Clear existing
        while self.times_layout.count():
            item = self.times_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not optimal_hours:
            self.placeholder = QLabel("Complete more sessions to see your optimal times")
            self.placeholder.setStyleSheet("color: #666666; font-size: 11px;")
            self.times_layout.addWidget(self.placeholder)
            return
        
        for i, time_data in enumerate(optimal_hours[:3]):
            time_frame = QFrame()
            time_layout = QHBoxLayout(time_frame)
            time_layout.setContentsMargins(5, 5, 5, 5)
            
            # Medal icon
            medals = ['🥇', '🥈', '🥉']
            medal = QLabel(medals[i] if i < 3 else '⭐')
            medal.setStyleSheet("font-size: 20px;")
            time_layout.addWidget(medal)
            
            # Time label
            time_label = QLabel(time_data['time_label'])
            time_label.setStyleSheet("color: #ffffff; font-size: 12px;")
            time_layout.addWidget(time_label)
            
            time_layout.addStretch()
            
            # Accuracy
            accuracy_label = QLabel(f"{time_data['accuracy']}%")
            color = '#00ff41' if time_data['accuracy'] >= 80 else '#ffb000' if time_data['accuracy'] >= 60 else '#ff4444'
            accuracy_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")
            time_layout.addWidget(accuracy_label)
            
            self.times_layout.addWidget(time_frame)


class WeakAreasWidget(QWidget):
    """Displays weak areas that need attention."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("⚠️ Areas Needing Attention")
        header.setStyleSheet("color: #ff6600; font-size: 14px; font-weight: bold;")
        layout.addWidget(header)
        
        # Areas container
        self.areas_layout = QVBoxLayout()
        layout.addLayout(self.areas_layout)
        
        # Placeholder
        placeholder = QLabel("Great job! No weak areas detected.")
        placeholder.setStyleSheet("color: #00ff41; font-size: 11px;")
        self.areas_layout.addWidget(placeholder)
    
    def update_weak_areas(self, weak_areas: List[Dict]):
        """Update displayed weak areas."""
        # Clear existing
        while self.areas_layout.count():
            item = self.areas_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not weak_areas:
            placeholder = QLabel("✅ Great job! No weak areas detected.")
            placeholder.setStyleSheet("color: #00ff41; font-size: 11px;")
            self.areas_layout.addWidget(placeholder)
            return
        
        for area in weak_areas[:5]:
            area_frame = QFrame()
            area_frame.setStyleSheet("""
                background-color: #2a1a1a;
                border: 1px solid #ff4444;
                border-radius: 5px;
                padding: 5px;
            """)
            
            area_layout = QVBoxLayout(area_frame)
            area_layout.setSpacing(3)
            
            # Category and accuracy
            top_layout = QHBoxLayout()
            cat_label = QLabel(area['category'].title())
            cat_label.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: bold;")
            top_layout.addWidget(cat_label)
            
            top_layout.addStretch()
            
            acc_label = QLabel(f"{area['accuracy']}%")
            acc_label.setStyleSheet("color: #ff4444; font-size: 12px;")
            top_layout.addWidget(acc_label)
            
            area_layout.addLayout(top_layout)
            
            # Recommendation
            rec_label = QLabel(area['recommendation'])
            rec_label.setWordWrap(True)
            rec_label.setStyleSheet("color: #888888; font-size: 10px;")
            area_layout.addWidget(rec_label)
            
            self.areas_layout.addWidget(area_frame)


class AnalyticsTab(QWidget):
    """
    Main analytics dashboard tab.
    Features 23-27: Complete learning analytics.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_data()
        
        # Refresh data every 5 minutes
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._load_data)
        self._refresh_timer.start(300000)  # 5 minutes
    
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Title
        title = QLabel("📊 Learning Analytics")
        title.setStyleSheet("color: #00ff41; font-size: 20px; font-weight: bold;")
        main_layout.addWidget(title)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0f0f0f;
            }
        """)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # ===== TOP STATS ROW =====
        stats_layout = QHBoxLayout()
        
        self.total_words_card = StatCard("Total Words", "0", "vocabulary size")
        stats_layout.addWidget(self.total_words_card)
        
        self.words_today_card = StatCard("Today", "0", "new words", "#ffb000")
        stats_layout.addWidget(self.words_today_card)
        
        self.accuracy_card = StatCard("Accuracy", "0%", "review rate", "#00d4ff")
        stats_layout.addWidget(self.accuracy_card)
        
        self.streak_card = StatCard("Streak", "0", "days", "#ff6600")
        stats_layout.addWidget(self.streak_card)
        
        self.xp_card = StatCard("Total XP", "0", "experience", "#aa55ff")
        stats_layout.addWidget(self.xp_card)
        
        content_layout.addLayout(stats_layout)
        
        # ===== CEFR PROGRESS =====
        self.cefr_widget = CEFRProgressWidget()
        content_layout.addWidget(self.cefr_widget)
        
        # ===== TWO COLUMN LAYOUT =====
        columns_layout = QHBoxLayout()
        
        # Left column: Optimal Times
        self.optimal_times_widget = OptimalTimeWidget()
        columns_layout.addWidget(self.optimal_times_widget)
        
        # Right column: Weak Areas
        self.weak_areas_widget = WeakAreasWidget()
        columns_layout.addWidget(self.weak_areas_widget)
        
        content_layout.addLayout(columns_layout)
        
        # ===== STUDY RECOMMENDATIONS =====
        rec_frame = QFrame()
        rec_frame.setStyleSheet("""
            background-color: #1a2a1a;
            border: 1px solid #00ff41;
            border-radius: 8px;
            padding: 10px;
        """)
        rec_layout = QVBoxLayout(rec_frame)
        
        rec_title = QLabel("💡 Today's Recommendation")
        rec_title.setStyleSheet("color: #00ff41; font-size: 14px; font-weight: bold;")
        rec_layout.addWidget(rec_title)
        
        self.recommendation_label = QLabel("Loading recommendations...")
        self.recommendation_label.setWordWrap(True)
        self.recommendation_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        rec_layout.addWidget(self.recommendation_label)
        
        content_layout.addWidget(rec_frame)
        
        # ===== REFRESH BUTTON =====
        refresh_btn = QPushButton("🔄 Refresh Analytics")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #00ff41;
                border: 1px solid #00ff41;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00ff41;
                color: #0f0f0f;
            }
        """)
        refresh_btn.clicked.connect(self._load_data)
        content_layout.addWidget(refresh_btn)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def _load_data(self):
        """Load all analytics data from database and calculators."""
        try:
            session = db.get_session()
            
            # Get vocabulary stats
            total_words = session.query(Vocabulary).count()
            
            # Get words learned today
            today = date.today()
            today_start = datetime.combine(today, datetime.min.time())
            words_today = session.query(Vocabulary).filter(
                Vocabulary.created_at >= today_start
            ).count()
            
            # Calculate accuracy from review data
            vocab_with_reviews = session.query(Vocabulary).filter(
                Vocabulary.review_count > 0
            ).all()
            
            if vocab_with_reviews:
                total_correct = sum(v.correct_count for v in vocab_with_reviews)
                total_reviews = sum(v.review_count for v in vocab_with_reviews)
                accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0
            else:
                accuracy = 0
            
            # Get streak from progress
            progress = db.get_today_progress()
            streak = progress.get('streak', 0)
            
            session.close()
            
            # Update cards
            self.total_words_card.update_value(str(total_words))
            self.words_today_card.update_value(str(words_today))
            self.accuracy_card.update_value(f"{accuracy:.0f}%")
            self.streak_card.update_value(str(streak))
            self.xp_card.update_value("0")  # TODO: Calculate XP
            
            # CEFR estimation
            cefr_data = cefr_analyzer.estimate_user_level(
                total_words, accuracy, 50  # grammar_score placeholder
            )
            
            current_level = cefr_data['current_level']
            words_to_next = cefr_data['words_to_next_level']
            
            # Calculate progress percentage
            vocab_ranges = {
                'A1': (0, 500), 'A2': (501, 1000), 'B1': (1001, 2500),
                'B2': (2501, 5000), 'C1': (5001, 10000), 'C2': (10001, 25000)
            }
            min_words, max_words = vocab_ranges.get(current_level, (0, 500))
            progress_pct = min(100, int((total_words - min_words) / max(1, max_words - min_words) * 100))
            
            self.cefr_widget.set_level(current_level, progress_pct, words_to_next)
            
            # Optimal times (using study optimizer)
            optimal_hours = study_optimizer.get_optimal_study_hours()
            self.optimal_times_widget.update_times(optimal_hours)
            
            # Weak areas
            weak_areas = study_optimizer.identify_weak_areas()
            self.weak_areas_widget.update_weak_areas(weak_areas)
            
            # Recommendation
            rec = study_optimizer.get_study_recommendation()
            tips = rec.get('tips', ['Keep up the great work!'])
            self.recommendation_label.setText(' '.join(tips))
            
            logger.info("Analytics data refreshed successfully")
            
        except Exception as e:
            logger.error(f"Error loading analytics: {e}", exc_info=True)
    
    def showEvent(self, event):
        """Refresh data when tab is shown."""
        super().showEvent(event)
        self._load_data()
