"""
Z32 Nexus - Flashcard Widget
Interactive spaced repetition flashcard interface
"""

from datetime import datetime
from typing import Optional, List
import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QProgressBar, QSpacerItem,
    QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont

from database import db, Vocabulary
from utils.signal_bus import signal_bus
from utils.config_manager import config
from ui.toast_notification import ToastNotification

import logging
logger = logging.getLogger(__name__)


class FlashcardWidget(QFrame):
    """Single flashcard display widget with flip animation"""
    
    flipped = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_flipped = False
        self._word_data = None
        
        self.setStyleSheet("""
            FlashcardWidget {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 12px;
            }
        """)
        self.setMinimumSize(400, 250)
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Front side (English)
        self.front_widget = QWidget()
        front_layout = QVBoxLayout(self.front_widget)
        front_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.front_label = QLabel("?")
        self.front_label.setFont(QFont('Consolas', 32, QFont.Weight.Bold))
        self.front_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.front_label.setWordWrap(True)
        front_layout.addWidget(self.front_label)
        
        hint_label = QLabel("[ Click to reveal ]")
        hint_label.setStyleSheet("color: #666666; font-size: 12px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        front_layout.addWidget(hint_label)
        
        # Back side (Spanish)
        self.back_widget = QWidget()
        back_layout = QVBoxLayout(self.back_widget)
        back_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.back_label = QLabel("?")
        self.back_label.setFont(QFont('Consolas', 32, QFont.Weight.Bold))
        self.back_label.setStyleSheet("color: #ffb000;")  # Amber for Spanish
        self.back_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.back_label.setWordWrap(True)
        back_layout.addWidget(self.back_label)
        
        self.context_label = QLabel("")
        self.context_label.setStyleSheet("color: #888888; font-size: 12px;")
        self.context_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.context_label.setWordWrap(True)
        back_layout.addWidget(self.context_label)
        
        # Stacked widget for flip effect
        self.stack = QStackedWidget()
        self.stack.addWidget(self.front_widget)
        self.stack.addWidget(self.back_widget)
        
        layout.addWidget(self.stack)
        
        # Click to flip
        self.mousePressEvent = self._on_click
    
    def _on_click(self, event):
        """Handle click to flip card"""
        self.flip()
    
    def flip(self):
        """Flip the card"""
        self._is_flipped = not self._is_flipped
        self.stack.setCurrentIndex(1 if self._is_flipped else 0)
        self.flipped.emit(self._is_flipped)
    
    def set_word(self, word_data: dict):
        """Set the word to display"""
        self._word_data = word_data
        self._is_flipped = False
        self.stack.setCurrentIndex(0)
        
        self.front_label.setText(word_data.get('english', '?').upper())
        self.back_label.setText(word_data.get('spanish', '?').upper())
        
        context = word_data.get('context', '')
        self.context_label.setText(context if context else '')
    
    def get_word_data(self) -> Optional[dict]:
        """Get current word data"""
        return self._word_data
    
    @property
    def is_flipped(self) -> bool:
        return self._is_flipped


class FlashcardTab(QWidget):
    """Flashcard review tab with SM-2 spaced repetition"""
    
    # Review modes: Features 1-4
    MODE_NORMAL = 'normal'      # English → Spanish
    MODE_REVERSE = 'reverse'    # Spanish → English (Feature 1)
    MODE_CLOZE = 'cloze'        # Fill in the blank (Feature 2)
    MODE_SPEED = 'speed'        # Rapid-fire 5-second cards (Feature 4)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._current_words: List[dict] = []
        self._current_index = 0
        self._session_correct = 0
        self._session_total = 0
        self._current_mode = self.MODE_NORMAL
        self._speed_timer = None
        self._speed_start_time = None
        self._interleaved = False  # Feature 30: Interleaved Practice
        
        self._setup_ui()
        self._load_words()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("FLASHCARD REVIEW")
        title.setFont(QFont('Consolas', 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Mode selector - NEW (Features 1-4)
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("color: #888888;")
        mode_layout.addWidget(mode_label)
        
        from PyQt6.QtWidgets import QComboBox
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "📚 Normal (EN → ES)",
            "🔄 Reverse (ES → EN)",
            "📝 Cloze (Fill Blank)",
            "⚡ Speed Review",
        ])
        self.mode_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #00ff41;
                border: 1px solid #333333;
                padding: 5px 10px;
                border-radius: 5px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 1px solid #00ff41;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        
        header_layout.addLayout(mode_layout)
        
        # Session stats
        self.session_stats = QLabel("Session: 0/0 (0%)")
        self.session_stats.setStyleSheet("color: #888888;")
        header_layout.addWidget(self.session_stats)
        
        layout.addLayout(header_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Speed mode timer label - NEW (Feature 4)
        self.speed_timer_label = QLabel("⏱️ 5.0s")
        self.speed_timer_label.setStyleSheet("""
            color: #ffb000;
            font-size: 24px;
            font-weight: bold;
        """)
        self.speed_timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_timer_label.setVisible(False)
        layout.addWidget(self.speed_timer_label)
        
        # Card counter
        self.counter_label = QLabel("Card 0 of 0")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.counter_label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(self.counter_label)
        
        # Flashcard
        card_container = QHBoxLayout()
        card_container.addStretch()
        
        self.flashcard = FlashcardWidget()
        self.flashcard.flipped.connect(self._on_card_flipped)
        card_container.addWidget(self.flashcard)
        
        card_container.addStretch()
        layout.addLayout(card_container)
        
        # Cloze mode input - NEW (Feature 2)
        self.cloze_frame = QFrame()
        cloze_layout = QHBoxLayout(self.cloze_frame)
        
        from PyQt6.QtWidgets import QLineEdit
        self.cloze_input = QLineEdit()
        self.cloze_input.setPlaceholderText("Type the missing word...")
        self.cloze_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #333333;
                padding: 12px;
                font-size: 16px;
                border-radius: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #00ff41;
            }
        """)
        self.cloze_input.returnPressed.connect(self._check_cloze_answer)
        cloze_layout.addWidget(self.cloze_input)
        
        self.cloze_check_btn = QPushButton("Check")
        self.cloze_check_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff41;
                color: #0f0f0f;
                border: none;
                padding: 12px 24px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #00cc33;
            }
        """)
        self.cloze_check_btn.clicked.connect(self._check_cloze_answer)
        cloze_layout.addWidget(self.cloze_check_btn)
        
        self.cloze_frame.setVisible(False)
        layout.addWidget(self.cloze_frame)
        
        # Rating buttons (hidden until flipped)
        self.rating_frame = QFrame()
        rating_layout = QHBoxLayout(self.rating_frame)
        rating_layout.setSpacing(10)
        
        rating_layout.addStretch()
        
        # SM-2 quality ratings
        self.rating_buttons = []
        ratings = [
            ("AGAIN", 0, "#ff4444"),
            ("HARD", 2, "#ffaa00"),
            ("GOOD", 3, "#44ff44"),
            ("EASY", 5, "#00d4ff"),
        ]
        
        for label, quality, color in ratings:
            btn = QPushButton(label)
            btn.setProperty('quality', quality)
            btn.setMinimumWidth(80)
            btn.setMinimumHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid {color};
                    color: {color};
                    background-color: transparent;
                }}
                QPushButton:hover {{
                    background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2);
                }}
            """)
            btn.clicked.connect(self._on_rating_clicked)
            rating_layout.addWidget(btn)
            self.rating_buttons.append(btn)
        
        rating_layout.addStretch()
        
        self.rating_frame.setVisible(False)
        layout.addWidget(self.rating_frame)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("START REVIEW")
        self.start_btn.setObjectName("successButton")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.clicked.connect(self._start_session)
        controls_layout.addWidget(self.start_btn)
        
        self.skip_btn = QPushButton("SKIP")
        self.skip_btn.setMinimumHeight(40)
        self.skip_btn.clicked.connect(self._skip_card)
        self.skip_btn.setVisible(False)
        controls_layout.addWidget(self.skip_btn)
        
        self.shuffle_btn = QPushButton("SHUFFLE")
        self.shuffle_btn.setMinimumHeight(40)
        self.shuffle_btn.clicked.connect(self._shuffle_words)
        controls_layout.addWidget(self.shuffle_btn)
        
        # Difficult word button - NEW (Feature 5)
        self.difficult_btn = QPushButton("⚠️ MARK DIFFICULT")
        self.difficult_btn.setMinimumHeight(40)
        self.difficult_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #ff6600;
                color: #ff6600;
            }
            QPushButton:hover {
                background-color: rgba(255, 102, 0, 0.2);
            }
        """)
        self.difficult_btn.clicked.connect(self._mark_difficult)
        self.difficult_btn.setVisible(False)
        controls_layout.addWidget(self.difficult_btn)
        
        # Expert Tools button - Features 3, 6, 7
        self.expert_btn = QPushButton("🧠 EXPERT TOOLS")
        self.expert_btn.setMinimumHeight(40)
        self.expert_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #8888ff;
                color: #8888ff;
            }
            QPushButton:hover {
                background-color: rgba(136, 136, 255, 0.2);
            }
        """)
        self.expert_btn.clicked.connect(self._show_expert_tools)
        self.expert_btn.setVisible(False)
        controls_layout.addWidget(self.expert_btn)
        
        layout.addStretch()
        layout.addLayout(controls_layout)
        
        # No words message
        self.no_words_label = QLabel(
            "No words due for review!\n\n"
            "Use the Vocab Tool to add new words,\n"
            "or wait for existing words to become due."
        )
        self.no_words_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_words_label.setStyleSheet("color: #666666; font-size: 14px;")
        self.no_words_label.setVisible(False)
        layout.addWidget(self.no_words_label)
    
    def _on_mode_changed(self, index):
        """Handle mode selection change"""
        modes = [self.MODE_NORMAL, self.MODE_REVERSE, self.MODE_CLOZE, self.MODE_SPEED]
        self._current_mode = modes[index]
        
        # Update UI based on mode
        self.cloze_frame.setVisible(self._current_mode == self.MODE_CLOZE)
        self.speed_timer_label.setVisible(self._current_mode == self.MODE_SPEED)
        
        # Emit mode change signal
        signal_bus.flashcard_mode_changed.emit(self._current_mode)
        
        logger.info(f"Flashcard mode changed to: {self._current_mode}")

    
    def _load_words(self):
        """Load words due for review"""
        session = db.get_session()
        try:
            now = datetime.utcnow()
            words = session.query(Vocabulary).filter(
                Vocabulary.next_review <= now
            ).order_by(Vocabulary.next_review).limit(50).all()
            
            self._current_words = [w.to_dict() for w in words]
            self._current_index = 0
            
            if self._current_words:
                self.counter_label.setText(f"Card 1 of {len(self._current_words)}")
                self.no_words_label.setVisible(False)
                self.flashcard.setVisible(True)
            else:
                self.no_words_label.setVisible(True)
                self.flashcard.setVisible(False)
                self.counter_label.setText("No cards due")
            
            self.progress_bar.setMaximum(max(len(self._current_words), 1))
            self.progress_bar.setValue(0)
            
        finally:
            session.close()
    
    def _start_session(self):
        """Start a review session"""
        self._load_words()
        
        if not self._current_words:
            QMessageBox.information(
                self, "No Words",
                "No words are due for review right now.\n"
                "Add more words or wait for scheduled reviews."
            )
            return
        
        self._current_index = 0
        self._session_correct = 0
        self._session_total = 0
        
        self.start_btn.setVisible(False)
        self.skip_btn.setVisible(True)
        
        self._show_current_card()
    
    def _show_current_card(self):
        """Display the current flashcard based on selected mode"""
        if self._current_index >= len(self._current_words):
            self._end_session()
            return
        
        word = self._current_words[self._current_index]
        
        # Handle different modes
        if self._current_mode == self.MODE_REVERSE:
            # Feature 1: Reverse mode - show Spanish, ask for English
            display_word = {
                'id': word['id'],
                'english': word['spanish'],  # Show Spanish on front
                'spanish': word['english'],  # Show English on back
                'context': word.get('context', ''),
            }
            self.flashcard.set_word(display_word)
            self.flashcard.front_label.setStyleSheet("color: #ffb000;")  # Amber for Spanish
            self.flashcard.back_label.setStyleSheet("color: #00ff41;")  # Green for English
            
        elif self._current_mode == self.MODE_CLOZE:
            # Feature 2: Cloze mode - show context with blank
            context = word.get('context', '')
            if context and word['spanish'] in context:
                cloze_text = context.replace(word['spanish'], '_____')
            else:
                cloze_text = f"[ _____ ] = {word['english']}"
            
            display_word = {
                'id': word['id'],
                'english': cloze_text,
                'spanish': word['spanish'],
                'context': f"Fill in the Spanish word for: {word['english']}",
            }
            self.flashcard.set_word(display_word)
            self.cloze_input.setFocus()
            
        elif self._current_mode == self.MODE_SPEED:
            # Feature 4: Speed mode - start timer
            self.flashcard.set_word(word)
            self._start_speed_timer()
            
        else:
            # Normal mode
            self.flashcard.set_word(word)
            self.flashcard.front_label.setStyleSheet("color: #00ff41;")
            self.flashcard.back_label.setStyleSheet("color: #ffb000;")
        
        self.rating_frame.setVisible(False)
        self.difficult_btn.setVisible(True)
        self.expert_btn.setVisible(True)
        
        self.counter_label.setText(
            f"Card {self._current_index + 1} of {len(self._current_words)}"
        )
        self.progress_bar.setValue(self._current_index)

    
    def _on_card_flipped(self, is_flipped: bool):
        """Handle card flip"""
        self.rating_frame.setVisible(is_flipped)
    
    def _on_rating_clicked(self):
        """Handle rating button click"""
        btn = self.sender()
        quality = btn.property('quality')
        
        # Update word in database
        word_data = self.flashcard.get_word_data()
        if word_data:
            self._update_word_review(word_data['id'], quality)
            
            self._session_total += 1
            if quality >= 3:
                self._session_correct += 1
            
            self._update_session_stats()
        
        # Next card
        self._current_index += 1
        self._show_current_card()
    
    def _update_word_review(self, word_id: int, quality: int):
        """Update word with review result"""
        session = db.get_session()
        try:
            word = session.query(Vocabulary).filter_by(id=word_id).first()
            if word:
                word.calculate_next_review(quality)
                session.commit()
                
                signal_bus.flashcard_reviewed.emit(word_id, quality)
                logger.info(f"Reviewed word {word_id} with quality {quality}")
        except Exception as e:
            logger.error(f"Failed to update word review: {e}")
            session.rollback()
        finally:
            session.close()
    
    def _update_session_stats(self):
        """Update session statistics display"""
        if self._session_total > 0:
            accuracy = (self._session_correct / self._session_total) * 100
            self.session_stats.setText(
                f"Session: {self._session_correct}/{self._session_total} ({accuracy:.0f}%)"
            )
    
    def _skip_card(self):
        """Skip the current card"""
        self._current_index += 1
        self._show_current_card()
    
    def _shuffle_words(self):
        """Shuffle the word order"""
        if self._current_words:
            random.shuffle(self._current_words)
            self._current_index = 0
            self._show_current_card()
    
    def _end_session(self):
        """End the review session"""
        self.start_btn.setVisible(True)
        self.skip_btn.setVisible(False)
        self.rating_frame.setVisible(False)
        self.difficult_btn.setVisible(False)
        self.expert_btn.setVisible(False)
        
        # Stop speed timer if running
        if self._speed_timer:
            self._speed_timer.stop()
        
        self.progress_bar.setValue(len(self._current_words))
        
        # Show results
        if self._session_total > 0:
            accuracy = (self._session_correct / self._session_total) * 100
            
            signal_bus.review_session_complete.emit(
                self._session_correct, self._session_total
            )
            
            # For speed mode, calculate words per minute
            if self._current_mode == self.MODE_SPEED and self._speed_start_time:
                elapsed = (datetime.now() - self._speed_start_time).total_seconds() / 60
                wpm = self._session_total / max(elapsed, 0.01)
                signal_bus.speed_review_complete.emit(self._session_total, wpm)
                
                ToastNotification.show_success(
                    self, "Speed Session Complete!",
                    f"Reviewed {self._session_total} cards at {wpm:.1f} words/minute"
                )
            else:
                ToastNotification.show_success(
                    self, "Session Complete!",
                    f"Reviewed {self._session_total} cards ({accuracy:.0f}% correct)"
                )
            
            # Update daily progress
            session = db.get_session()
            try:
                from datetime import date
                from database import UserProgress
                
                today = date.today()
                progress = session.query(UserProgress).filter_by(date=today).first()
                if progress:
                    progress.reviews_completed = (
                        (progress.reviews_completed or 0) + self._session_total
                    )
                    session.commit()
            finally:
                session.close()
        
        self.flashcard.set_word({'english': 'Review Complete!', 'spanish': 'Well done!'})
        self.counter_label.setText("Session ended")
    
    def _check_cloze_answer(self):
        """
        Feature 2: Check cloze deletion answer
        """
        word_data = self.flashcard.get_word_data()
        if not word_data:
            return
        
        user_answer = self.cloze_input.text().strip().lower()
        correct_answer = word_data.get('spanish', '').lower()
        
        # Check if answer is correct (allow minor variations)
        is_correct = user_answer == correct_answer or user_answer in correct_answer
        
        if is_correct:
            # Correct - treat as quality 4
            self._update_word_review(word_data['id'], 4)
            self._session_correct += 1
            self._session_total += 1
            
            ToastNotification.show_success(
                self, "¡Correcto!",
                f"The answer is: {word_data['spanish']}"
            )
        else:
            # Wrong - treat as quality 1
            self._update_word_review(word_data['id'], 1)
            self._session_total += 1
            
            ToastNotification.show_error(
                self, "Not quite...",
                f"Correct answer: {word_data['spanish']}"
            )
        
        self._update_session_stats()
        self.cloze_input.clear()
        
        # Next card
        self._current_index += 1
        self._show_current_card()
    
    def _mark_difficult(self):
        """
        Feature 5: Mark current word as difficult
        """
        word_data = self.flashcard.get_word_data()
        if not word_data:
            return
        
        session = db.get_session()
        try:
            from database import DifficultWord
            
            word_id = word_data['id']
            
            # Check if already in difficult queue
            existing = session.query(DifficultWord).filter_by(
                vocabulary_id=word_id, resolved=False
            ).first()
            
            if existing:
                existing.times_failed += 1
                existing.last_failed = datetime.utcnow()
                existing.priority_score += 0.5
            else:
                difficult = DifficultWord(
                    vocabulary_id=word_id,
                    times_failed=1,
                    priority_score=1.0,
                    notes="Marked manually during review"
                )
                session.add(difficult)
            
            # Also update the vocabulary item
            word = session.query(Vocabulary).filter_by(id=word_id).first()
            if word:
                word.times_in_difficult_queue = (word.times_in_difficult_queue or 0) + 1
                word.difficulty_rating = min(10, (word.difficulty_rating or 0) + 2)
            
            session.commit()
            
            signal_bus.difficult_word_flagged.emit(word_id, "manual")
            
            ToastNotification.show_warning(
                self, "Marked as Difficult",
                f"'{word_data['english']}' added to difficult words queue"
            )
            
            logger.info(f"Word {word_id} marked as difficult")
            
        except Exception as e:
            logger.error(f"Failed to mark word as difficult: {e}")
            session.rollback()
        finally:
            session.close()
    
    def _start_speed_timer(self):
        """
        Feature 4: Start speed review timer (5 seconds per card)
        """
        if self._speed_timer is None:
            self._speed_timer = QTimer(self)
            self._speed_timer.timeout.connect(self._on_speed_timeout)
        
        self._speed_remaining = 5.0
        self._speed_timer.start(100)  # Update every 100ms
        self.speed_timer_label.setText(f"⏱️ {self._speed_remaining:.1f}s")
    
    def _on_speed_timeout(self):
        """Handle speed timer tick"""
        self._speed_remaining -= 0.1
        self.speed_timer_label.setText(f"⏱️ {max(0, self._speed_remaining):.1f}s")
        
        if self._speed_remaining <= 0:
            # Time's up - auto-fail and move to next
            self._speed_timer.stop()
            
            word_data = self.flashcard.get_word_data()
            if word_data:
                self._update_word_review(word_data['id'], 1)  # Fail
                self._session_total += 1
                self._update_session_stats()
            
            self._current_index += 1
            self._show_current_card()
    
    def _show_expert_tools(self):
        """
        Features 3, 6, 7: Show expert tools dialog
        - Audio pronunciation
        - Memory Palace
        - Mnemonic generation
        """
        word_data = self.flashcard.get_word_data()
        if not word_data:
            return
        
        try:
            from ui.expert_tools import ExpertToolsDialog
            dialog = ExpertToolsDialog(word_data, self)
            dialog.exec()
        except Exception as e:
            logger.error(f"Failed to open expert tools: {e}")
            ToastNotification.show_error(
                self, "Error", 
                "Could not open expert tools"
            )
