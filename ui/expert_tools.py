"""
Z32 Nexus - Expert Tools Panel
Features 6, 7, 15, 16: Memory Palace, Mnemonics, Passive Listening, Reading Analyzer

Provides advanced vocabulary enrichment tools:
- Memory Palace location tagging
- Mnemonic generation and display
- Text reading level analysis
- Audio pronunciation (TTS)
"""

import logging
from typing import Optional, Dict, List
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTextEdit, QLineEdit, QComboBox, QGroupBox,
    QScrollArea, QDialog, QDialogButtonBox, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from database import db, Vocabulary, Mnemonic, WordContext
from utils.signal_bus import signal_bus
from utils.mnemonic_engine import mnemonic_engine
from utils.cefr_analyzer import cefr_analyzer
from utils.word_family import word_family_expander

logger = logging.getLogger(__name__)


class TTSWorker(QThread):
    """Background worker for text-to-speech"""
    
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, text: str, language: str = 'es'):
        super().__init__()
        self.text = text
        self.language = language
    
    def run(self):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            # Set voice for Spanish if available
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.setProperty('rate', 150)  # Slightly slower for learning
            engine.say(self.text)
            engine.runAndWait()
            
            self.finished.emit()
        except Exception as e:
            logger.error(f"TTS error: {e}")
            self.error.emit(str(e))


class MemoryPalaceWidget(QFrame):
    """
    Feature 6: Memory Palace Integration
    Allows users to assign location tags to vocabulary words
    """
    
    location_updated = pyqtSignal(int, str)  # word_id, location
    
    # Predefined palace "rooms"
    PALACE_ROOMS = [
        "🚪 Front Door",
        "🛋️ Living Room", 
        "🍳 Kitchen",
        "🛏️ Bedroom",
        "🚿 Bathroom",
        "📚 Study/Office",
        "🌿 Garden",
        "🚗 Garage",
        "🎨 Custom Location",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_word_id = None
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            MemoryPalaceWidget {
                background-color: #1a1a2e;
                border: 1px solid #4a4a8a;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🏰 Memory Palace")
        header.setStyleSheet("color: #8888ff; font-size: 14px; font-weight: bold;")
        layout.addWidget(header)
        
        description = QLabel("Assign a location to help remember this word")
        description.setStyleSheet("color: #888888; font-size: 10px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Room selector
        self.room_combo = QComboBox()
        self.room_combo.addItems(self.PALACE_ROOMS)
        self.room_combo.setStyleSheet("""
            QComboBox {
                background-color: #252545;
                color: #ffffff;
                border: 1px solid #4a4a8a;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.room_combo)
        
        # Custom location input
        self.custom_input = QLineEdit()
        self.custom_input.setPlaceholderText("Enter custom location...")
        self.custom_input.setStyleSheet("""
            QLineEdit {
                background-color: #252545;
                color: #ffffff;
                border: 1px solid #4a4a8a;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        self.custom_input.setVisible(False)
        layout.addWidget(self.custom_input)
        
        # Show custom input when "Custom" selected
        self.room_combo.currentTextChanged.connect(self._on_room_changed)
        
        # Save button
        save_btn = QPushButton("📍 Save Location")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a8a;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6a6aaa;
            }
        """)
        save_btn.clicked.connect(self._save_location)
        layout.addWidget(save_btn)
        
        # Current location display
        self.current_location = QLabel("No location set")
        self.current_location.setStyleSheet("color: #666666; font-size: 11px; font-style: italic;")
        layout.addWidget(self.current_location)
    
    def _on_room_changed(self, text):
        self.custom_input.setVisible("Custom" in text)
    
    def set_word(self, word_id: int, current_location: str = ""):
        """Set the current word being edited"""
        self._current_word_id = word_id
        if current_location:
            self.current_location.setText(f"📍 Current: {current_location}")
        else:
            self.current_location.setText("No location set")
    
    def _save_location(self):
        """Save the memory palace location"""
        if not self._current_word_id:
            return
        
        location = self.room_combo.currentText()
        if "Custom" in location:
            location = self.custom_input.text().strip()
            if not location:
                return
        
        # Update database
        session = db.get_session()
        try:
            word = session.query(Vocabulary).filter_by(id=self._current_word_id).first()
            if word:
                word.memory_palace_location = location
                session.commit()
                
                self.current_location.setText(f"📍 Saved: {location}")
                self.location_updated.emit(self._current_word_id, location)
                signal_bus.memory_palace_updated.emit(self._current_word_id, location)
                
                logger.info(f"Memory palace location updated for word {self._current_word_id}")
        finally:
            session.close()


class MnemonicWidget(QFrame):
    """
    Feature 7: Mnemonic Generator and Display
    Shows memory tricks for vocabulary words
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_word = None
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            MnemonicWidget {
                background-color: #1a2e1a;
                border: 1px solid #4a8a4a;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🧠 Memory Tricks")
        header.setStyleSheet("color: #88ff88; font-size: 14px; font-weight: bold;")
        layout.addWidget(header)
        
        # Mnemonic display area
        self.mnemonic_display = QLabel("Select a word to see memory tricks")
        self.mnemonic_display.setStyleSheet("color: #cccccc; font-size: 12px;")
        self.mnemonic_display.setWordWrap(True)
        self.mnemonic_display.setMinimumHeight(100)
        layout.addWidget(self.mnemonic_display)
        
        # Generate button
        gen_btn = QPushButton("✨ Generate New Mnemonic")
        gen_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a8a4a;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6aaa6a;
            }
        """)
        gen_btn.clicked.connect(self._generate_mnemonic)
        layout.addWidget(gen_btn)
        
        # Custom mnemonic input
        self.custom_mnemonic = QLineEdit()
        self.custom_mnemonic.setPlaceholderText("Add your own memory trick...")
        self.custom_mnemonic.setStyleSheet("""
            QLineEdit {
                background-color: #254525;
                color: #ffffff;
                border: 1px solid #4a8a4a;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.custom_mnemonic)
        
        # Save custom button
        save_btn = QPushButton("💾 Save My Mnemonic")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #254525;
                color: #88ff88;
                border: 1px solid #4a8a4a;
                padding: 6px;
                border-radius: 5px;
            }
        """)
        save_btn.clicked.connect(self._save_custom_mnemonic)
        layout.addWidget(save_btn)
    
    def set_word(self, spanish: str, english: str, word_id: int = None):
        """Set the word to generate mnemonics for"""
        self._current_word = {
            'spanish': spanish,
            'english': english,
            'id': word_id
        }
        self._generate_mnemonic()
    
    def _generate_mnemonic(self):
        """Generate mnemonic for current word"""
        if not self._current_word:
            return
        
        spanish = self._current_word['spanish']
        english = self._current_word['english']
        
        # Use mnemonic engine
        result = mnemonic_engine.generate_mnemonic(spanish, english)
        
        # Format display
        display_text = ""
        
        sound_assoc = result.get('sound_association', ('', ''))
        if sound_assoc and sound_assoc[0]:
            display_text += f"🔊 <b>Sound:</b> {sound_assoc[0]}\n"
            if sound_assoc[1]:
                display_text += f"   💭 {sound_assoc[1]}\n\n"
        
        visual = result.get('visual_image', '')
        if visual:
            display_text += f"🎨 <b>Visual:</b> {visual}\n\n"
        
        # Check for cognate
        cognate_hint = mnemonic_engine.get_cognate_hint(spanish, english)
        if cognate_hint:
            display_text += f"🔗 <b>Cognate:</b> {cognate_hint}\n\n"
        
        tips = result.get('effectiveness_tips', [])
        if tips:
            display_text += f"💡 <b>Tip:</b> {tips[0]}"
        
        self.mnemonic_display.setText(display_text.replace('\n', '<br>'))
    
    def _save_custom_mnemonic(self):
        """Save user's custom mnemonic"""
        if not self._current_word or not self._current_word.get('id'):
            return
        
        custom_text = self.custom_mnemonic.text().strip()
        if not custom_text:
            return
        
        session = db.get_session()
        try:
            mnemonic = Mnemonic(
                vocabulary_id=self._current_word['id'],
                mnemonic_text=custom_text,
                is_user_created=True
            )
            session.add(mnemonic)
            session.commit()
            
            signal_bus.mnemonic_created.emit(self._current_word['id'], custom_text)
            self.custom_mnemonic.clear()
            self.custom_mnemonic.setPlaceholderText("✓ Saved! Add another...")
            
            logger.info(f"Custom mnemonic saved for word {self._current_word['id']}")
        finally:
            session.close()


class ReadingAnalyzerWidget(QFrame):
    """
    Feature 16: Reading Level Analyzer
    Analyzes Spanish text difficulty and highlights unknown words
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            ReadingAnalyzerWidget {
                background-color: #2e2e1a;
                border: 1px solid #8a8a4a;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📖 Reading Level Analyzer")
        header.setStyleSheet("color: #ffff88; font-size: 14px; font-weight: bold;")
        layout.addWidget(header)
        
        description = QLabel("Paste Spanish text to analyze difficulty")
        description.setStyleSheet("color: #888888; font-size: 10px;")
        layout.addWidget(description)
        
        # Text input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Paste Spanish text here...")
        self.text_input.setMaximumHeight(100)
        self.text_input.setStyleSheet("""
            QTextEdit {
                background-color: #3a3a2a;
                color: #ffffff;
                border: 1px solid #8a8a4a;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.text_input)
        
        # Analyze button
        analyze_btn = QPushButton("🔍 Analyze Text")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #8a8a4a;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #aaaa6a;
            }
        """)
        analyze_btn.clicked.connect(self._analyze_text)
        layout.addWidget(analyze_btn)
        
        # Results display
        self.results_frame = QFrame()
        results_layout = QVBoxLayout(self.results_frame)
        results_layout.setContentsMargins(0, 10, 0, 0)
        
        # Level badge
        self.level_label = QLabel("Level: --")
        self.level_label.setStyleSheet("""
            background-color: #4a4a2a;
            color: #ffff88;
            padding: 10px;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
        """)
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_layout.addWidget(self.level_label)
        
        # Stats
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #cccccc; font-size: 11px;")
        self.stats_label.setWordWrap(True)
        results_layout.addWidget(self.stats_label)
        
        # Unknown words list
        self.unknown_label = QLabel("")
        self.unknown_label.setStyleSheet("color: #ff8888; font-size: 11px;")
        self.unknown_label.setWordWrap(True)
        results_layout.addWidget(self.unknown_label)
        
        self.results_frame.setVisible(False)
        layout.addWidget(self.results_frame)
    
    def _analyze_text(self):
        """Analyze the input text"""
        text = self.text_input.toPlainText().strip()
        if not text:
            return
        
        # Use CEFR analyzer
        result = cefr_analyzer.analyze_text(text)
        
        # Display results
        self.results_frame.setVisible(True)
        
        level = result['estimated_level']
        confidence = result['confidence']
        
        # Color code by level
        level_colors = {
            'A1': '#66ff66', 'A2': '#88ff88',
            'B1': '#ffff66', 'B2': '#ffcc66',
            'C1': '#ff8888', 'C2': '#ff6666',
        }
        color = level_colors.get(level, '#ffffff')
        
        self.level_label.setText(f"📊 Level: {level} ({confidence*100:.0f}% confidence)")
        self.level_label.setStyleSheet(f"""
            background-color: #4a4a2a;
            color: {color};
            padding: 10px;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
        """)
        
        self.stats_label.setText(
            f"📝 Total words: {result['total_words']} | "
            f"Unique: {result['unique_words']} | "
            f"Avg length: {result['average_word_length']}"
        )
        
        unknown = result.get('unknown_words', [])[:10]
        if unknown:
            self.unknown_label.setText(
                f"❓ Unknown words: {', '.join(unknown)}"
            )
            self.unknown_label.setVisible(True)
        else:
            self.unknown_label.setVisible(False)
        
        # Emit signal
        signal_bus.reading_level_analyzed.emit(level, len(unknown))


class AudioPronunciationWidget(QFrame):
    """
    Feature 3: Audio Recognition / Pronunciation
    Plays Spanish audio using TTS
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tts_worker = None
        self._current_text = ""
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            AudioPronunciationWidget {
                background-color: #1a1a3e;
                border: 1px solid #6a6aaa;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🔊 Pronunciation")
        header.setStyleSheet("color: #aaaaff; font-size: 14px; font-weight: bold;")
        layout.addWidget(header)
        
        # Current word display
        self.word_label = QLabel("--")
        self.word_label.setStyleSheet("""
            color: #ffffff;
            font-size: 18px;
            padding: 10px;
            background-color: #2a2a4e;
            border-radius: 5px;
        """)
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.word_label)
        
        # Play button
        self.play_btn = QPushButton("▶️ Play Audio")
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #6a6aaa;
                color: #ffffff;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8a8acc;
            }
            QPushButton:disabled {
                background-color: #4a4a6a;
                color: #888888;
            }
        """)
        self.play_btn.clicked.connect(self._play_audio)
        layout.addWidget(self.play_btn)
        
        # Slow playback
        self.slow_btn = QPushButton("🐢 Play Slowly")
        self.slow_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a6a;
                color: #aaaaff;
                border: 1px solid #6a6aaa;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        self.slow_btn.clicked.connect(lambda: self._play_audio(slow=True))
        layout.addWidget(self.slow_btn)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888888; font-size: 10px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    def set_word(self, spanish: str):
        """Set the word to pronounce"""
        self._current_text = spanish
        self.word_label.setText(spanish)
        self.status_label.setText("")
    
    def _play_audio(self, slow: bool = False):
        """Play TTS audio"""
        if not self._current_text:
            return
        
        self.play_btn.setEnabled(False)
        self.slow_btn.setEnabled(False)
        self.status_label.setText("🔊 Playing...")
        
        # Use TTS worker
        self._tts_worker = TTSWorker(self._current_text)
        self._tts_worker.finished.connect(self._on_audio_finished)
        self._tts_worker.error.connect(self._on_audio_error)
        self._tts_worker.start()
    
    def _on_audio_finished(self):
        """Handle audio playback completion"""
        self.play_btn.setEnabled(True)
        self.slow_btn.setEnabled(True)
        self.status_label.setText("✓ Done")
    
    def _on_audio_error(self, error: str):
        """Handle audio error"""
        self.play_btn.setEnabled(True)
        self.slow_btn.setEnabled(True)
        self.status_label.setText(f"⚠️ Error: {error[:30]}...")


class ExpertToolsDialog(QDialog):
    """
    Dialog containing all expert vocabulary tools
    Features 3, 6, 7, 16 in one accessible dialog
    """
    
    def __init__(self, word_data: dict = None, parent=None):
        super().__init__(parent)
        self.word_data = word_data or {}
        self.setWindowTitle("Expert Vocabulary Tools")
        self.setMinimumSize(500, 600)
        self._setup_ui()
        
        if word_data:
            self._load_word_data()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0f0f0f;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Word header
        self.word_header = QLabel("Select a word to use tools")
        self.word_header.setStyleSheet("""
            color: #00ff41;
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
        """)
        self.word_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.word_header)
        
        # Tab widget for tools
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #0f0f0f;
            }
            QTabBar::tab {
                background-color: #1a1a1a;
                color: #888888;
                padding: 10px 15px;
                border: 1px solid #333333;
            }
            QTabBar::tab:selected {
                background-color: #0f0f0f;
                color: #00ff41;
            }
        """)
        
        # Audio tab
        self.audio_widget = AudioPronunciationWidget()
        tabs.addTab(self.audio_widget, "🔊 Audio")
        
        # Mnemonic tab
        self.mnemonic_widget = MnemonicWidget()
        tabs.addTab(self.mnemonic_widget, "🧠 Mnemonics")
        
        # Memory Palace tab
        self.palace_widget = MemoryPalaceWidget()
        tabs.addTab(self.palace_widget, "🏰 Palace")
        
        # Reading Analyzer tab
        self.reading_widget = ReadingAnalyzerWidget()
        tabs.addTab(self.reading_widget, "📖 Analyzer")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def _load_word_data(self):
        """Load the word data into all widgets"""
        spanish = self.word_data.get('spanish', '')
        english = self.word_data.get('english', '')
        word_id = self.word_data.get('id')
        location = self.word_data.get('memory_palace_location', '')
        
        self.word_header.setText(f"{english} → {spanish}")
        
        self.audio_widget.set_word(spanish)
        self.mnemonic_widget.set_word(spanish, english, word_id)
        self.palace_widget.set_word(word_id, location)
    
    def set_word(self, word_data: dict):
        """Set a new word"""
        self.word_data = word_data
        self._load_word_data()
