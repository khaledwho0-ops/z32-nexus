"""
Z32 Nexus - Vocabulary Tab UI
Interface for extracting and translating vocabulary from text
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QProgressBar, QListWidget, QListWidgetItem,
    QFrame, QSplitter, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

from utils.signal_bus import signal_bus
from utils.vocab_processor import vocab_processor
from ui.toast_notification import ToastNotification

import logging
logger = logging.getLogger(__name__)


class TranslationWorker(QThread):
    """Background worker for translation to avoid UI freezing"""
    
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(list, int)  # translations, new_count
    error = pyqtSignal(str)
    
    def __init__(self, text: str):
        super().__init__()
        self.text = text
    
    def run(self):
        try:
            def on_progress(current, total):
                self.progress.emit(current, total)
            
            results, new_count = vocab_processor.process_text(
                self.text, 
                progress_callback=on_progress
            )
            self.finished.emit(results, new_count)
        except Exception as e:
            logger.error(f"Translation worker error: {e}")
            self.error.emit(str(e))


class VocabTab(QWidget):
    """Vocabulary extraction and translation tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._worker = None
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("VOCABULARY EXTRACTOR")
        header.setFont(QFont('Consolas', 18, QFont.Weight.Bold))
        layout.addWidget(header)
        
        subtitle = QLabel("Paste English text below to extract and translate vocabulary to Spanish")
        subtitle.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(subtitle)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Input
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        input_label = QLabel("INPUT TEXT")
        input_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(input_label)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(
            "Paste your English text here...\n\n"
            "The tool will:\n"
            "1. Extract unique words (3+ characters)\n"
            "2. Filter out common stop words\n"
            "3. Translate each word to Spanish\n"
            "4. Add to your vocabulary database"
        )
        self.input_text.setMinimumHeight(300)
        left_layout.addWidget(self.input_text)
        
        # Word count
        self.word_count_label = QLabel("Words: 0 | Estimated time: 0s")
        self.word_count_label.setStyleSheet("color: #888888; font-size: 11px;")
        left_layout.addWidget(self.word_count_label)
        
        # Connect text change to update word count
        self.input_text.textChanged.connect(self._update_word_count)
        
        splitter.addWidget(left_widget)
        
        # Right side: Results
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        results_label = QLabel("TRANSLATIONS")
        results_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(results_label)
        
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(300)
        right_layout.addWidget(self.results_list)
        
        # Results stats
        self.results_stats = QLabel("No translations yet")
        self.results_stats.setStyleSheet("color: #888888; font-size: 11px;")
        right_layout.addWidget(self.results_stats)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])
        
        layout.addWidget(splitter)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.process_btn = QPushButton("PROCESS TEXT")
        self.process_btn.setObjectName("successButton")
        self.process_btn.setMinimumHeight(40)
        self.process_btn.clicked.connect(self._on_process)
        buttons_layout.addWidget(self.process_btn)
        
        self.export_btn = QPushButton("EXPORT TO CSV")
        self.export_btn.setMinimumHeight(40)
        self.export_btn.clicked.connect(self._on_export)
        buttons_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self._on_clear)
        buttons_layout.addWidget(self.clear_btn)
        
        layout.addWidget(QFrame())  # Spacer
        layout.addLayout(buttons_layout)
    
    def _update_word_count(self):
        """Update word count estimate"""
        text = self.input_text.toPlainText()
        words = vocab_processor.extract_words(text)
        count = len(words)
        
        # Estimate time (200ms per word + overhead)
        estimated_time = count * 0.25  # seconds
        
        self.word_count_label.setText(
            f"Unique words: {count} | Estimated time: {estimated_time:.1f}s"
        )
    
    def _on_process(self):
        """Start processing the input text"""
        text = self.input_text.toPlainText().strip()
        
        if not text:
            QMessageBox.warning(self, "No Input", "Please enter some text to process.")
            return
        
        # Extract words first to check count
        words = vocab_processor.extract_words(text)
        if not words:
            QMessageBox.warning(
                self, "No Words Found", 
                "No valid words found in the text.\n"
                "Words must be 3+ characters and not stop words."
            )
            return
        
        if len(words) > 500:
            reply = QMessageBox.question(
                self, "Large Input",
                f"Processing {len(words)} words may take a while.\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Disable buttons and show progress
        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(words))
        self.results_list.clear()
        
        # Start background worker
        self._worker = TranslationWorker(text)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()
    
    def _on_progress(self, current: int, total: int):
        """Update progress bar"""
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"Translating... {current}/{total}")
    
    def _on_finished(self, results: list, new_count: int):
        """Handle translation completion"""
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Populate results list
        self.results_list.clear()
        for english, spanish in results:
            item = QListWidgetItem(f"{english} → {spanish}")
            self.results_list.addItem(item)
        
        # Update stats
        self.results_stats.setText(
            f"Translated: {len(results)} | New words added: {new_count}"
        )
        
        # Emit signals
        for english, spanish in results:
            signal_bus.word_learned.emit(english, spanish)
        
        signal_bus.translation_complete.emit(len(results))
        
        # Show toast
        ToastNotification.show_spiritual(self)
        
        logger.info(f"Translation complete: {len(results)} words, {new_count} new")
    
    def _on_error(self, error_msg: str):
        """Handle translation error"""
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        QMessageBox.critical(
            self, "Translation Error",
            f"An error occurred during translation:\n{error_msg}"
        )
    
    def _on_export(self):
        """Export results to CSV"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV",
            "my_anki_deck.csv",
            "CSV Files (*.csv)"
        )
        
        if path:
            try:
                vocab_processor.export_to_csv(path)
                QMessageBox.information(
                    self, "Export Complete",
                    f"Vocabulary exported to:\n{path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Export Error",
                    f"Failed to export:\n{e}"
                )
    
    def _on_clear(self):
        """Clear input and results"""
        self.input_text.clear()
        self.results_list.clear()
        self.results_stats.setText("No translations yet")
        self.word_count_label.setText("Words: 0 | Estimated time: 0s")
