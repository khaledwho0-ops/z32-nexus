"""
Z32 Nexus - Journal Tab
Daily 100-word journal with auto-save
"""

from datetime import datetime, date

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCharFormat, QColor

from database import db, UserProgress
from utils.signal_bus import signal_bus
from ui.toast_notification import ToastNotification

import logging
logger = logging.getLogger(__name__)


class JournalTab(QWidget):
    """Daily journaling tab with word count tracking"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_locked = False
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.timeout.connect(self._auto_save)
        self._auto_save_timer.start(30000)  # Auto-save every 30 seconds
        
        self._setup_ui()
        self._load_today_entry()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("DAILY JOURNAL")
        title.setFont(QFont('Consolas', 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Date display
        today = date.today()
        self.date_label = QLabel(today.strftime("%A, %B %d, %Y"))
        self.date_label.setStyleSheet("color: #888888;")
        header_layout.addWidget(self.date_label)
        
        layout.addLayout(header_layout)
        
        # Instructions
        instructions = QLabel(
            "Write your daily reflection (aim for 100+ words). "
            "This entry will auto-save and lock after submission."
        )
        instructions.setStyleSheet("color: #666666; font-size: 12px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Journal text area
        self.journal_text = QTextEdit()
        self.journal_text.setPlaceholderText(
            "What did you learn today?\n"
            "How do you feel about your progress?\n"
            "What will you focus on tomorrow?\n\n"
            "Write freely - this is your personal reflection space..."
        )
        self.journal_text.setMinimumHeight(300)
        self.journal_text.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.journal_text)
        
        # Word count
        count_frame = QFrame()
        count_layout = QHBoxLayout(count_frame)
        count_layout.setContentsMargins(0, 0, 0, 0)
        
        self.word_count_label = QLabel("Words: 0/100")
        self.word_count_label.setStyleSheet("color: #888888;")
        count_layout.addWidget(self.word_count_label)
        
        count_layout.addStretch()
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666666; font-size: 11px;")
        count_layout.addWidget(self.status_label)
        
        layout.addWidget(count_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("SAVE DRAFT")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._save_draft)
        buttons_layout.addWidget(self.save_btn)
        
        self.submit_btn = QPushButton("SUBMIT & LOCK")
        self.submit_btn.setObjectName("successButton")
        self.submit_btn.setMinimumHeight(40)
        self.submit_btn.clicked.connect(self._submit_entry)
        buttons_layout.addWidget(self.submit_btn)
        
        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self._clear_text)
        buttons_layout.addWidget(self.clear_btn)
        
        layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Locked state message
        self.locked_message = QLabel(
            "Today's entry has been submitted and locked.\n"
            "Come back tomorrow for a new entry!"
        )
        self.locked_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.locked_message.setStyleSheet("color: #888888; font-size: 14px;")
        self.locked_message.setVisible(False)
        layout.addWidget(self.locked_message)
    
    def _load_today_entry(self):
        """Load today's journal entry if it exists"""
        session = db.get_session()
        try:
            today = date.today()
            progress = session.query(UserProgress).filter_by(date=today).first()
            
            if progress and progress.journal_entry:
                self.journal_text.setText(progress.journal_entry)
                
                # Check if already submitted (has word count >= 100)
                word_count = len(progress.journal_entry.split())
                # For now, we'll consider entries with 100+ words as "submitted"
                # A proper implementation would have a separate locked flag
        finally:
            session.close()
        
        self._update_word_count()
    
    def _on_text_changed(self):
        """Handle text changes"""
        self._update_word_count()
    
    def _update_word_count(self):
        """Update the word count display"""
        text = self.journal_text.toPlainText()
        words = text.split()
        count = len(words)
        
        # Update label with color based on progress
        if count >= 100:
            color = "#44ff44"  # Green
            status = "Goal reached!"
        elif count >= 50:
            color = "#ffaa00"  # Yellow
            status = "Halfway there..."
        else:
            color = "#888888"  # Gray
            status = ""
        
        self.word_count_label.setText(f"Words: {count}/100")
        self.word_count_label.setStyleSheet(f"color: {color};")
        self.status_label.setText(status)
    
    def _save_draft(self):
        """Save the current text as draft"""
        text = self.journal_text.toPlainText()
        
        session = db.get_session()
        try:
            today = date.today()
            progress = session.query(UserProgress).filter_by(date=today).first()
            
            if progress:
                progress.journal_entry = text
                session.commit()
                
                self.status_label.setText("Draft saved!")
                QTimer.singleShot(2000, lambda: self.status_label.setText(""))
                
                logger.info("Journal draft saved")
        except Exception as e:
            logger.error(f"Failed to save journal draft: {e}")
            session.rollback()
        finally:
            session.close()
    
    def _auto_save(self):
        """Auto-save the journal entry"""
        if not self._is_locked and self.journal_text.toPlainText().strip():
            self._save_draft()
    
    def _submit_entry(self):
        """Submit and lock the journal entry"""
        text = self.journal_text.toPlainText()
        words = text.split()
        
        if len(words) < 50:
            reply = QMessageBox.question(
                self, "Short Entry",
                f"Your entry only has {len(words)} words.\n"
                "Are you sure you want to submit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Save the entry
        session = db.get_session()
        try:
            today = date.today()
            progress = session.query(UserProgress).filter_by(date=today).first()
            
            if progress:
                progress.journal_entry = text
                session.commit()
                
                self._is_locked = True
                self.journal_text.setReadOnly(True)
                self.save_btn.setEnabled(False)
                self.submit_btn.setEnabled(False)
                self.clear_btn.setEnabled(False)
                
                ToastNotification.show_spiritual(self)
                
                logger.info(f"Journal entry submitted: {len(words)} words")
                
        except Exception as e:
            logger.error(f"Failed to submit journal entry: {e}")
            session.rollback()
            QMessageBox.critical(self, "Error", "Failed to submit entry.")
        finally:
            session.close()
    
    def _clear_text(self):
        """Clear the journal text"""
        if self._is_locked:
            return
        
        reply = QMessageBox.question(
            self, "Clear Entry",
            "Are you sure you want to clear your journal entry?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.journal_text.clear()
