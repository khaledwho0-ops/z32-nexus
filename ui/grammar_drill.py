"""
Z32 Nexus - Grammar Drill Tab
Feature 18: Grammar Pattern Drills

Provides focused grammar exercises:
- Verb conjugation practice
- Sentence transformation exercises
- Fill-in-the-blank grammar
- Tense identification
"""

import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QScrollArea, QComboBox, QGroupBox,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from utils.signal_bus import signal_bus

logger = logging.getLogger(__name__)


# Verb conjugation exercises
VERB_CONJUGATIONS = {
    'hablar': {
        'infinitive': 'hablar',
        'english': 'to speak',
        'type': '-ar regular',
        'present': {
            'yo': 'hablo', 'tú': 'hablas', 'él/ella': 'habla',
            'nosotros': 'hablamos', 'vosotros': 'habláis', 'ellos': 'hablan'
        },
        'preterite': {
            'yo': 'hablé', 'tú': 'hablaste', 'él/ella': 'habló',
            'nosotros': 'hablamos', 'vosotros': 'hablasteis', 'ellos': 'hablaron'
        },
        'imperfect': {
            'yo': 'hablaba', 'tú': 'hablabas', 'él/ella': 'hablaba',
            'nosotros': 'hablábamos', 'vosotros': 'hablabais', 'ellos': 'hablaban'
        },
    },
    'comer': {
        'infinitive': 'comer',
        'english': 'to eat',
        'type': '-er regular',
        'present': {
            'yo': 'como', 'tú': 'comes', 'él/ella': 'come',
            'nosotros': 'comemos', 'vosotros': 'coméis', 'ellos': 'comen'
        },
        'preterite': {
            'yo': 'comí', 'tú': 'comiste', 'él/ella': 'comió',
            'nosotros': 'comimos', 'vosotros': 'comisteis', 'ellos': 'comieron'
        },
        'imperfect': {
            'yo': 'comía', 'tú': 'comías', 'él/ella': 'comía',
            'nosotros': 'comíamos', 'vosotros': 'comíais', 'ellos': 'comían'
        },
    },
    'vivir': {
        'infinitive': 'vivir',
        'english': 'to live',
        'type': '-ir regular',
        'present': {
            'yo': 'vivo', 'tú': 'vives', 'él/ella': 'vive',
            'nosotros': 'vivimos', 'vosotros': 'vivís', 'ellos': 'viven'
        },
        'preterite': {
            'yo': 'viví', 'tú': 'viviste', 'él/ella': 'vivió',
            'nosotros': 'vivimos', 'vosotros': 'vivisteis', 'ellos': 'vivieron'
        },
        'imperfect': {
            'yo': 'vivía', 'tú': 'vivías', 'él/ella': 'vivía',
            'nosotros': 'vivíamos', 'vosotros': 'vivíais', 'ellos': 'vivían'
        },
    },
    'ser': {
        'infinitive': 'ser',
        'english': 'to be (permanent)',
        'type': 'irregular',
        'present': {
            'yo': 'soy', 'tú': 'eres', 'él/ella': 'es',
            'nosotros': 'somos', 'vosotros': 'sois', 'ellos': 'son'
        },
        'preterite': {
            'yo': 'fui', 'tú': 'fuiste', 'él/ella': 'fue',
            'nosotros': 'fuimos', 'vosotros': 'fuisteis', 'ellos': 'fueron'
        },
        'imperfect': {
            'yo': 'era', 'tú': 'eras', 'él/ella': 'era',
            'nosotros': 'éramos', 'vosotros': 'erais', 'ellos': 'eran'
        },
    },
    'estar': {
        'infinitive': 'estar',
        'english': 'to be (temporary)',
        'type': 'irregular',
        'present': {
            'yo': 'estoy', 'tú': 'estás', 'él/ella': 'está',
            'nosotros': 'estamos', 'vosotros': 'estáis', 'ellos': 'están'
        },
        'preterite': {
            'yo': 'estuve', 'tú': 'estuviste', 'él/ella': 'estuvo',
            'nosotros': 'estuvimos', 'vosotros': 'estuvisteis', 'ellos': 'estuvieron'
        },
        'imperfect': {
            'yo': 'estaba', 'tú': 'estabas', 'él/ella': 'estaba',
            'nosotros': 'estábamos', 'vosotros': 'estabais', 'ellos': 'estaban'
        },
    },
    'tener': {
        'infinitive': 'tener',
        'english': 'to have',
        'type': 'irregular',
        'present': {
            'yo': 'tengo', 'tú': 'tienes', 'él/ella': 'tiene',
            'nosotros': 'tenemos', 'vosotros': 'tenéis', 'ellos': 'tienen'
        },
        'preterite': {
            'yo': 'tuve', 'tú': 'tuviste', 'él/ella': 'tuvo',
            'nosotros': 'tuvimos', 'vosotros': 'tuvisteis', 'ellos': 'tuvieron'
        },
        'imperfect': {
            'yo': 'tenía', 'tú': 'tenías', 'él/ella': 'tenía',
            'nosotros': 'teníamos', 'vosotros': 'teníais', 'ellos': 'tenían'
        },
    },
    'ir': {
        'infinitive': 'ir',
        'english': 'to go',
        'type': 'irregular',
        'present': {
            'yo': 'voy', 'tú': 'vas', 'él/ella': 'va',
            'nosotros': 'vamos', 'vosotros': 'vais', 'ellos': 'van'
        },
        'preterite': {
            'yo': 'fui', 'tú': 'fuiste', 'él/ella': 'fue',
            'nosotros': 'fuimos', 'vosotros': 'fuisteis', 'ellos': 'fueron'
        },
        'imperfect': {
            'yo': 'iba', 'tú': 'ibas', 'él/ella': 'iba',
            'nosotros': 'íbamos', 'vosotros': 'ibais', 'ellos': 'iban'
        },
    },
    'hacer': {
        'infinitive': 'hacer',
        'english': 'to do/make',
        'type': 'irregular',
        'present': {
            'yo': 'hago', 'tú': 'haces', 'él/ella': 'hace',
            'nosotros': 'hacemos', 'vosotros': 'hacéis', 'ellos': 'hacen'
        },
        'preterite': {
            'yo': 'hice', 'tú': 'hiciste', 'él/ella': 'hizo',
            'nosotros': 'hicimos', 'vosotros': 'hicisteis', 'ellos': 'hicieron'
        },
        'imperfect': {
            'yo': 'hacía', 'tú': 'hacías', 'él/ella': 'hacía',
            'nosotros': 'hacíamos', 'vosotros': 'hacíais', 'ellos': 'hacían'
        },
    },
}


# Fill-in-the-blank exercises
GRAMMAR_EXERCISES = [
    # Ser vs Estar
    {
        'type': 'ser_estar',
        'sentence': 'Yo ___ estudiante.',
        'answer': 'soy',
        'english': 'I am a student.',
        'explanation': 'Use "ser" for permanent characteristics like profession.',
    },
    {
        'type': 'ser_estar',
        'sentence': 'María ___ cansada hoy.',
        'answer': 'está',
        'english': 'María is tired today.',
        'explanation': 'Use "estar" for temporary states like being tired.',
    },
    {
        'type': 'ser_estar',
        'sentence': 'La casa ___ grande.',
        'answer': 'es',
        'english': 'The house is big.',
        'explanation': 'Use "ser" for inherent characteristics.',
    },
    {
        'type': 'ser_estar',
        'sentence': 'Nosotros ___ en Madrid.',
        'answer': 'estamos',
        'english': 'We are in Madrid.',
        'explanation': 'Use "estar" for location.',
    },
    # Por vs Para
    {
        'type': 'por_para',
        'sentence': 'Este regalo es ___ ti.',
        'answer': 'para',
        'english': 'This gift is for you.',
        'explanation': 'Use "para" for recipient or destination.',
    },
    {
        'type': 'por_para',
        'sentence': 'Trabajo ___ una empresa grande.',
        'answer': 'para',
        'english': 'I work for a big company.',
        'explanation': 'Use "para" when indicating employment.',
    },
    {
        'type': 'por_para', 
        'sentence': 'Gracias ___ tu ayuda.',
        'answer': 'por',
        'english': 'Thanks for your help.',
        'explanation': 'Use "por" to express gratitude or reason.',
    },
    {
        'type': 'por_para',
        'sentence': 'Caminamos ___ el parque.',
        'answer': 'por',
        'english': 'We walked through the park.',
        'explanation': 'Use "por" for movement through a place.',
    },
    # Article agreement
    {
        'type': 'articles',
        'sentence': '___ agua está fría.',
        'answer': 'El',
        'english': 'The water is cold.',
        'explanation': '"Agua" is feminine but takes "el" because it starts with stressed "a".',
    },
    {
        'type': 'articles',
        'sentence': '___ problemas son difíciles.',
        'answer': 'Los',
        'english': 'The problems are difficult.',
        'explanation': '"Problema" is masculine (ends in -ma from Greek).',
    },
]


class ConjugationDrill(QWidget):
    """Widget for verb conjugation practice."""
    
    completed = pyqtSignal(bool)  # Emits True if correct
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_verb = None
        self._current_tense = None
        self._current_pronoun = None
        self._correct_answer = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Question display
        self.question_frame = QFrame()
        self.question_frame.setStyleSheet("""
            background-color: #1a1a1a;
            border: 1px solid #00ff41;
            border-radius: 8px;
            padding: 15px;
        """)
        q_layout = QVBoxLayout(self.question_frame)
        
        self.verb_label = QLabel("Conjugate the verb:")
        self.verb_label.setStyleSheet("color: #888888; font-size: 12px;")
        q_layout.addWidget(self.verb_label)
        
        self.prompt_label = QLabel("")
        self.prompt_label.setStyleSheet("color: #00ff41; font-size: 20px; font-weight: bold;")
        q_layout.addWidget(self.prompt_label)
        
        self.hint_label = QLabel("")
        self.hint_label.setStyleSheet("color: #ffb000; font-size: 11px;")
        q_layout.addWidget(self.hint_label)
        
        layout.addWidget(self.question_frame)
        
        # Answer input
        input_layout = QHBoxLayout()
        
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Type your answer...")
        self.answer_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333333;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #00ff41;
            }
        """)
        self.answer_input.returnPressed.connect(self._check_answer)
        input_layout.addWidget(self.answer_input)
        
        self.check_btn = QPushButton("Check")
        self.check_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff41;
                color: #0f0f0f;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00cc33;
            }
        """)
        self.check_btn.clicked.connect(self._check_answer)
        input_layout.addWidget(self.check_btn)
        
        layout.addWidget(QWidget())  # Spacer
        layout.itemAt(layout.count() - 1).widget().setLayout(input_layout)
        
        # Feedback
        self.feedback_label = QLabel("")
        self.feedback_label.setStyleSheet("font-size: 14px;")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.feedback_label)
    
    def set_exercise(self, verb: str, tense: str, pronoun: str):
        """Set up a new conjugation exercise."""
        self._current_verb = verb
        self._current_tense = tense
        self._current_pronoun = pronoun
        
        verb_data = VERB_CONJUGATIONS.get(verb)
        if verb_data and tense in verb_data:
            self._correct_answer = verb_data[tense].get(pronoun, '')
        
        self.prompt_label.setText(f"{pronoun} _____ ({verb})")
        self.hint_label.setText(f"Tense: {tense.title()} | {verb_data['english']}")
        self.verb_label.setText(f"Conjugate '{verb}' ({verb_data['type']})")
        
        self.answer_input.clear()
        self.feedback_label.clear()
        self.answer_input.setFocus()
    
    def _check_answer(self):
        """Check the user's answer."""
        user_answer = self.answer_input.text().strip().lower()
        correct = user_answer == self._correct_answer.lower()
        
        if correct:
            self.feedback_label.setText("✅ ¡Correcto! Well done!")
            self.feedback_label.setStyleSheet("color: #00ff41; font-size: 14px;")
        else:
            self.feedback_label.setText(f"❌ The correct answer is: {self._correct_answer}")
            self.feedback_label.setStyleSheet("color: #ff4444; font-size: 14px;")
        
        self.completed.emit(correct)
    
    def generate_random_exercise(self):
        """Generate a random conjugation exercise."""
        verb = random.choice(list(VERB_CONJUGATIONS.keys()))
        tenses = ['present', 'preterite', 'imperfect']
        tense = random.choice(tenses)
        pronouns = ['yo', 'tú', 'él/ella', 'nosotros', 'ellos']
        pronoun = random.choice(pronouns)
        
        self.set_exercise(verb, tense, pronoun)


class FillInBlankDrill(QWidget):
    """Widget for fill-in-the-blank grammar exercises."""
    
    completed = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_exercise = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Exercise type label
        self.type_label = QLabel("")
        self.type_label.setStyleSheet("color: #ffb000; font-size: 11px;")
        layout.addWidget(self.type_label)
        
        # Sentence display
        self.sentence_label = QLabel("")
        self.sentence_label.setStyleSheet("""
            color: #ffffff;
            font-size: 18px;
            padding: 15px;
            background-color: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 8px;
        """)
        self.sentence_label.setWordWrap(True)
        layout.addWidget(self.sentence_label)
        
        # English translation
        self.english_label = QLabel("")
        self.english_label.setStyleSheet("color: #888888; font-size: 12px; font-style: italic;")
        layout.addWidget(self.english_label)
        
        # Answer input
        input_layout = QHBoxLayout()
        
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Fill in the blank...")
        self.answer_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333333;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #00ff41;
            }
        """)
        self.answer_input.returnPressed.connect(self._check_answer)
        input_layout.addWidget(self.answer_input)
        
        self.check_btn = QPushButton("Check")
        self.check_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff41;
                color: #0f0f0f;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
        """)
        self.check_btn.clicked.connect(self._check_answer)
        input_layout.addWidget(self.check_btn)
        
        layout.addLayout(input_layout)
        
        # Feedback and explanation
        self.feedback_label = QLabel("")
        self.feedback_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.feedback_label)
        
        self.explanation_label = QLabel("")
        self.explanation_label.setStyleSheet("color: #888888; font-size: 11px;")
        self.explanation_label.setWordWrap(True)
        layout.addWidget(self.explanation_label)
    
    def set_exercise(self, exercise: Dict):
        """Set up a new fill-in-blank exercise."""
        self._current_exercise = exercise
        
        self.type_label.setText(exercise['type'].replace('_', ' vs ').upper())
        self.sentence_label.setText(exercise['sentence'])
        self.english_label.setText(f"({exercise['english']})")
        
        self.answer_input.clear()
        self.feedback_label.clear()
        self.explanation_label.clear()
        self.answer_input.setFocus()
    
    def _check_answer(self):
        """Check the user's answer."""
        if not self._current_exercise:
            return
        
        user_answer = self.answer_input.text().strip().lower()
        correct_answer = self._current_exercise['answer'].lower()
        
        correct = user_answer == correct_answer
        
        if correct:
            self.feedback_label.setText("✅ ¡Correcto!")
            self.feedback_label.setStyleSheet("color: #00ff41; font-size: 14px;")
        else:
            self.feedback_label.setText(f"❌ The correct answer is: {self._current_exercise['answer']}")
            self.feedback_label.setStyleSheet("color: #ff4444; font-size: 14px;")
        
        self.explanation_label.setText(self._current_exercise['explanation'])
        self.completed.emit(correct)
    
    def generate_random_exercise(self, exercise_type: str = None):
        """Generate a random exercise, optionally filtered by type."""
        if exercise_type:
            exercises = [e for e in GRAMMAR_EXERCISES if e['type'] == exercise_type]
        else:
            exercises = GRAMMAR_EXERCISES
        
        if exercises:
            self.set_exercise(random.choice(exercises))


class GrammarDrillTab(QWidget):
    """
    Main grammar drill tab.
    Feature 18: Grammar Pattern Drills
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._correct_count = 0
        self._total_count = 0
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📝 Grammar Drills")
        title.setStyleSheet("color: #00ff41; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Score display
        self.score_label = QLabel("Score: 0/0")
        self.score_label.setStyleSheet("color: #ffb000; font-size: 14px;")
        header_layout.addWidget(self.score_label)
        
        layout.addLayout(header_layout)
        
        # Drill type selector
        type_layout = QHBoxLayout()
        type_label = QLabel("Drill Type:")
        type_label.setStyleSheet("color: #888888;")
        type_layout.addWidget(type_label)
        
        self.drill_combo = QComboBox()
        self.drill_combo.addItems([
            "Verb Conjugation",
            "Ser vs Estar",
            "Por vs Para",
            "Articles",
            "Mixed Practice"
        ])
        self.drill_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333333;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        type_layout.addWidget(self.drill_combo)
        
        type_layout.addStretch()
        
        self.start_btn = QPushButton("Start Drill")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff41;
                color: #0f0f0f;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
        """)
        self.start_btn.clicked.connect(self._start_drill)
        type_layout.addWidget(self.start_btn)
        
        layout.addLayout(type_layout)
        
        # Drill content area
        self.drill_stack = QFrame()
        self.drill_stack.setStyleSheet("background-color: #0f0f0f;")
        drill_layout = QVBoxLayout(self.drill_stack)
        
        # Conjugation drill widget
        self.conjugation_drill = ConjugationDrill()
        self.conjugation_drill.completed.connect(self._on_drill_complete)
        self.conjugation_drill.hide()
        drill_layout.addWidget(self.conjugation_drill)
        
        # Fill-in-blank drill widget
        self.fill_drill = FillInBlankDrill()
        self.fill_drill.completed.connect(self._on_drill_complete)
        self.fill_drill.hide()
        drill_layout.addWidget(self.fill_drill)
        
        # Placeholder
        self.placeholder = QLabel("Select a drill type and click 'Start Drill' to begin!")
        self.placeholder.setStyleSheet("color: #666666; font-size: 14px;")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drill_layout.addWidget(self.placeholder)
        
        layout.addWidget(self.drill_stack)
        
        # Next button
        self.next_btn = QPushButton("Next Exercise →")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #00ff41;
                border: 1px solid #00ff41;
                padding: 12px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00ff41;
                color: #0f0f0f;
            }
        """)
        self.next_btn.clicked.connect(self._next_exercise)
        self.next_btn.hide()
        layout.addWidget(self.next_btn)
        
        layout.addStretch()
    
    def _start_drill(self):
        """Start a new drill session."""
        self._correct_count = 0
        self._total_count = 0
        self._update_score()
        
        self.placeholder.hide()
        self.next_btn.show()
        
        self._next_exercise()
        
        signal_bus.grammar_drill_started.emit(self.drill_combo.currentText())
    
    def _next_exercise(self):
        """Show the next exercise."""
        drill_type = self.drill_combo.currentText()
        
        if drill_type == "Verb Conjugation":
            self.conjugation_drill.show()
            self.fill_drill.hide()
            self.conjugation_drill.generate_random_exercise()
        else:
            self.conjugation_drill.hide()
            self.fill_drill.show()
            
            type_map = {
                "Ser vs Estar": "ser_estar",
                "Por vs Para": "por_para",
                "Articles": "articles",
                "Mixed Practice": None,
            }
            self.fill_drill.generate_random_exercise(type_map.get(drill_type))
    
    def _on_drill_complete(self, correct: bool):
        """Handle drill completion."""
        self._total_count += 1
        if correct:
            self._correct_count += 1
        self._update_score()
    
    def _update_score(self):
        """Update the score display."""
        self.score_label.setText(f"Score: {self._correct_count}/{self._total_count}")
        
        if self._total_count > 0:
            pct = self._correct_count / self._total_count * 100
            if pct >= 80:
                self.score_label.setStyleSheet("color: #00ff41; font-size: 14px;")
            elif pct >= 60:
                self.score_label.setStyleSheet("color: #ffb000; font-size: 14px;")
            else:
                self.score_label.setStyleSheet("color: #ff4444; font-size: 14px;")
