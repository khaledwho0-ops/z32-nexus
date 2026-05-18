"""
Z32 Nexus - Database Models
SQLAlchemy ORM definitions for all application data
"""

from datetime import datetime, date
from typing import Optional, List
import json

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, Date, DateTime, Time, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool

Base = declarative_base()

# ============================================================================
# USER PROGRESS TABLE
# ============================================================================
class UserProgress(Base):
    """Daily progress tracking for the user"""
    __tablename__ = 'user_progress'
    
    date = Column(Date, primary_key=True, default=date.today)
    phase = Column(Integer, default=0)  # 0, 1, 2, or 3 (Omega)
    tasks_completed = Column(JSON, default=list)  # List of task IDs
    daily_score = Column(Integer, default=0)  # 0-100 percentage
    streak = Column(Integer, default=0)  # Consecutive days
    journal_entry = Column(Text, default='')  # Daily 100-word entry
    words_learned = Column(Integer, default=0)  # New words today
    reviews_completed = Column(Integer, default=0)  # Flashcard reviews
    focus_minutes = Column(Integer, default=0)  # Pomodoro time
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'date': str(self.date),
            'phase': self.phase,
            'tasks_completed': self.tasks_completed or [],
            'daily_score': self.daily_score,
            'streak': self.streak,
            'journal_entry': self.journal_entry,
            'words_learned': self.words_learned,
            'reviews_completed': self.reviews_completed,
            'focus_minutes': self.focus_minutes
        }


# ============================================================================
# SETTINGS TABLE
# ============================================================================
class Settings(Base):
    """Application settings storage"""
    __tablename__ = 'settings'
    
    key = Column(String(100), primary_key=True)
    value = Column(Text, default='')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Default settings
    DEFAULTS = {
        'theme_color': '#00ff41',  # Matrix Green
        'volume': '80',
        'fajr_offset': '0',
        'sleep_time': '22:30',
        'reminder_interval': '60',  # minutes
        'current_phase': '0',
        'language_from': 'en',
        'language_to': 'es',
        'daily_word_goal': '10',
        'pomodoro_duration': '25',
        'break_duration': '5',
    }


# ============================================================================
# VOCABULARY TABLE
# ============================================================================
class Vocabulary(Base):
    """Vocabulary items with spaced repetition data"""
    __tablename__ = 'vocabulary'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    english = Column(String(200), nullable=False)
    spanish = Column(String(200), nullable=False)
    context = Column(Text, default='')  # Example sentence
    category = Column(String(100), default='general')
    mastery_level = Column(Integer, default=0)  # 0-5 (SM-2)
    ease_factor = Column(Float, default=2.5)  # SM-2 ease factor
    interval = Column(Integer, default=1)  # Days until next review
    repetitions = Column(Integer, default=0)  # Total successful reviews
    next_review = Column(DateTime, default=datetime.utcnow)
    last_review = Column(DateTime, nullable=True)
    review_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    audio_cached = Column(Boolean, default=False)
    
    # NEW: Expert Learning Features
    register = Column(String(50), default='neutral')  # 'formal', 'informal', 'slang', 'neutral'
    region = Column(String(100), default='general')  # 'spain', 'mexico', 'argentina', 'general'
    memory_palace_location = Column(String(200), default='')  # Feature 6: Memory Palace
    word_family_root = Column(String(100), default='')  # Feature 10: Word Family
    ipa_pronunciation = Column(String(200), default='')  # Feature 45: Phonetic Transcription
    theme = Column(String(100), default='general')  # Feature 13: Thematic Clusters
    difficulty_rating = Column(Integer, default=0)  # 0-10 personal difficulty
    times_in_difficult_queue = Column(Integer, default=0)  # Feature 5: Difficult Words
    cefr_level = Column(String(10), default='A1')  # Feature 27: CEFR Level
    part_of_speech = Column(String(50), default='')  # noun, verb, adjective, etc.
    frequency_rank = Column(Integer, default=10000)  # Feature 39: Word Frequency
    is_cognate = Column(Boolean, default=False)  # Feature 44: Cognate Detection
    is_false_friend = Column(Boolean, default=False)  # Feature 44: False cognates

    
    def calculate_next_review(self, quality: int):
        """
        SM-2 Algorithm implementation
        quality: 0-5 (0=complete blackout, 5=perfect response)
        """
        if quality < 3:
            # Failed - reset
            self.repetitions = 0
            self.interval = 1
        else:
            # Passed
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.ease_factor)
            
            self.repetitions += 1
        
        # Update ease factor
        self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        # Set next review date
        from datetime import timedelta
        self.next_review = datetime.utcnow() + timedelta(days=self.interval)
        self.last_review = datetime.utcnow()
        self.review_count += 1
        if quality >= 3:
            self.correct_count += 1
            self.mastery_level = min(5, self.mastery_level + 1)
        else:
            self.mastery_level = max(0, self.mastery_level - 1)
    
    def to_dict(self):
        return {
            'id': self.id,
            'english': self.english,
            'spanish': self.spanish,
            'context': self.context,
            'category': self.category,
            'mastery_level': self.mastery_level,
            'next_review': str(self.next_review) if self.next_review else None,
            'review_count': self.review_count,
            'correct_count': self.correct_count
        }


# ============================================================================
# ALARMS TABLE
# ============================================================================
class Alarm(Base):
    """Alarm definitions"""
    __tablename__ = 'alarms'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    time = Column(Time, nullable=False)
    enabled = Column(Boolean, default=True)
    sound_file = Column(String(300), default='alarm_default.wav')
    alarm_type = Column(String(50), default='custom')  # 'critical', 'reminder', 'custom'
    recurrence = Column(String(50), default='daily')  # 'daily', 'weekly', 'once'
    days_of_week = Column(JSON, default=list)  # [0,1,2,3,4,5,6] for Mon-Sun
    snooze_count = Column(Integer, default=0)
    max_snoozes = Column(Integer, default=3)
    last_triggered = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# SESSIONS TABLE
# ============================================================================
class Session(Base):
    """Study session tracking"""
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_type = Column(String(50), nullable=False)  # 'vocab', 'flashcard', 'journal', 'pomodoro'
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    items_completed = Column(Integer, default=0)
    score = Column(Integer, default=0)  # Performance metric
    notes = Column(Text, default='')


# ============================================================================
# TASKS TABLE
# ============================================================================
class Task(Base):
    """Daily protocol tasks"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default='')
    phase_required = Column(Integer, default=0)  # Minimum phase to see this task
    category = Column(String(100), default='daily')  # 'daily', 'weekly', 'milestone'
    order = Column(Integer, default=0)  # Display order
    is_active = Column(Boolean, default=True)
    xp_reward = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# ACHIEVEMENTS TABLE
# ============================================================================
class Achievement(Base):
    """User achievements"""
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default='')
    icon = Column(String(100), default='trophy')
    xp_reward = Column(Integer, default=50)
    is_rare = Column(Boolean, default=False)
    unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)
    criteria_type = Column(String(50), default='count')  # 'count', 'streak', 'milestone'
    criteria_value = Column(Integer, default=1)


# ============================================================================
# MISTAKES TABLE
# ============================================================================
class Mistake(Base):
    """Track common errors for targeted review"""
    __tablename__ = 'mistakes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    word_id = Column(Integer, ForeignKey('vocabulary.id'), nullable=True)
    mistake_type = Column(String(50), default='spelling')  # 'spelling', 'grammar', 'false_friend'
    user_answer = Column(String(200), default='')
    correct_answer = Column(String(200), default='')
    occurred_at = Column(DateTime, default=datetime.utcnow)
    reviewed = Column(Boolean, default=False)


# ============================================================================
# CULTURAL NOTES TABLE
# ============================================================================
class CulturalNote(Base):
    """Spanish cultural information"""
    __tablename__ = 'cultural_notes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    region = Column(String(100), default='general')  # 'spain', 'mexico', 'argentina', 'general'
    category = Column(String(100), default='culture')  # 'culture', 'holiday', 'etiquette'
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# TRANSLATION CACHE TABLE
# ============================================================================
class TranslationCache(Base):
    """Cache for translations to reduce API calls"""
    __tablename__ = 'translation_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_text = Column(String(500), nullable=False, unique=True)
    source_lang = Column(String(10), default='en')
    target_lang = Column(String(10), default='es')
    translated_text = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# FAJR TIME CACHE TABLE
# ============================================================================
class FajrCache(Base):
    """Cache for Fajr prayer times"""
    __tablename__ = 'fajr_cache'
    
    date = Column(Date, primary_key=True)
    fajr_time = Column(Time, nullable=False)
    sunrise_time = Column(Time, nullable=True)
    location = Column(String(100), default='Egypt')
    fetched_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# WORD CONTEXT TABLE (Feature 9: Sentence Context Bank)
# ============================================================================
class WordContext(Base):
    """Multiple context sentences for each vocabulary word"""
    __tablename__ = 'word_contexts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vocabulary_id = Column(Integer, ForeignKey('vocabulary.id'), nullable=False)
    sentence_spanish = Column(Text, nullable=False)  # Spanish sentence
    sentence_english = Column(Text, nullable=False)  # English translation
    source = Column(String(200), default='user')  # Where the sentence came from
    difficulty_level = Column(String(10), default='B1')  # CEFR level
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# MNEMONIC TABLE (Feature 7: Mnemonic Generator)
# ============================================================================
class Mnemonic(Base):
    """Memory tricks and associations for vocabulary"""
    __tablename__ = 'mnemonics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vocabulary_id = Column(Integer, ForeignKey('vocabulary.id'), nullable=False)
    mnemonic_text = Column(Text, nullable=False)  # The memory trick
    image_association = Column(Text, default='')  # Visual description
    sound_association = Column(Text, default='')  # Sound-alike words
    is_user_created = Column(Boolean, default=False)
    effectiveness_rating = Column(Integer, default=0)  # 0-5 user rating
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# STUDY SESSION TABLE (Feature 29: Optimal Study Time)
# ============================================================================
class StudySession(Base):
    """Detailed study session tracking for analytics"""
    __tablename__ = 'study_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_type = Column(String(50), nullable=False)  # 'flashcard', 'dictation', 'grammar', etc.
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    words_reviewed = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    hour_of_day = Column(Integer, default=0)  # 0-23 for optimal time tracking
    day_of_week = Column(Integer, default=0)  # 0-6 for Mon-Sun
    focus_score = Column(Integer, default=0)  # 0-100 concentration metric
    mode = Column(String(50), default='normal')  # 'normal', 'speed', 'reverse', 'cloze'


# ============================================================================
# DAILY QUOTE TABLE (Feature 14: Daily Immersion Quotes)
# ============================================================================
class DailyQuote(Base):
    """Spanish quotes and proverbs for daily exposure"""
    __tablename__ = 'daily_quotes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spanish_text = Column(Text, nullable=False)
    english_text = Column(Text, nullable=False)
    author = Column(String(200), default='Unknown')
    category = Column(String(100), default='proverb')  # 'proverb', 'quote', 'saying', 'idiom'
    difficulty_level = Column(String(10), default='B1')
    times_shown = Column(Integer, default=0)
    last_shown = Column(Date, nullable=True)


# ============================================================================
# COLLOCATION TABLE (Feature 11: Collocations Database)
# ============================================================================
class Collocation(Base):
    """Common word pairings and their Spanish equivalents"""
    __tablename__ = 'collocations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    english_base = Column(String(100), nullable=False)  # Base word
    english_collocation = Column(String(300), nullable=False)  # Full collocation
    spanish_equivalent = Column(String(300), nullable=False)
    literal_translation = Column(String(300), default='')  # What NOT to say
    category = Column(String(100), default='verb')  # 'verb', 'adjective', 'noun'
    frequency_rank = Column(Integer, default=1000)  # Lower = more common
    is_false_friend = Column(Boolean, default=False)  # Common mistake
    notes = Column(Text, default='')


# ============================================================================
# WORD FAMILY TABLE (Feature 10: Word Family Expansion)
# ============================================================================
class WordFamily(Base):
    """Related word forms (noun/verb/adjective variations)"""
    __tablename__ = 'word_families'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    root_word = Column(String(100), nullable=False)  # Base/root form
    word_form = Column(String(100), nullable=False)  # The related word
    part_of_speech = Column(String(50), nullable=False)  # 'noun', 'verb', 'adjective', 'adverb'
    spanish_translation = Column(String(200), nullable=False)
    english_meaning = Column(String(200), nullable=False)
    example_sentence = Column(Text, default='')
    frequency_rank = Column(Integer, default=5000)


# ============================================================================
# GRAMMAR PATTERN TABLE (Feature 18: Grammar Pattern Drills)
# ============================================================================
class GrammarPattern(Base):
    """Grammar patterns and conjugation exercises"""
    __tablename__ = 'grammar_patterns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_name = Column(String(200), nullable=False)  # e.g., "Present Tense -AR verbs"
    pattern_description = Column(Text, nullable=False)
    difficulty_level = Column(String(10), default='A1')  # CEFR level
    category = Column(String(100), default='conjugation')  # 'conjugation', 'structure', 'tense'
    example_spanish = Column(Text, nullable=False)
    example_english = Column(Text, nullable=False)
    drill_template = Column(Text, default='')  # Template for generating exercises
    times_practiced = Column(Integer, default=0)
    mastery_level = Column(Integer, default=0)  # 0-5


# ============================================================================
# WRITING PROMPT TABLE (Feature 17: Writing Prompts Generator)
# ============================================================================
class WritingPrompt(Base):
    """Daily writing challenge prompts"""
    __tablename__ = 'writing_prompts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_english = Column(Text, nullable=False)
    prompt_spanish = Column(Text, nullable=False)
    difficulty_level = Column(String(10), default='A2')  # CEFR level
    category = Column(String(100), default='general')  # 'personal', 'descriptive', 'narrative'
    target_word_count = Column(Integer, default=50)
    vocabulary_focus = Column(JSON, default=list)  # List of target words to use
    grammar_focus = Column(String(200), default='')  # e.g., "past tense"
    times_used = Column(Integer, default=0)
    last_used = Column(Date, nullable=True)


# ============================================================================
# LEARNING ANALYTICS TABLE (Feature 23-27: Analytics & Tracking)
# ============================================================================
class LearningAnalytics(Base):
    """Daily learning statistics and analytics"""
    __tablename__ = 'learning_analytics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=date.today, unique=True)
    
    # Vocabulary metrics
    total_words_learned = Column(Integer, default=0)
    words_reviewed = Column(Integer, default=0)
    new_words_today = Column(Integer, default=0)
    retention_rate = Column(Float, default=0.0)  # % of words correctly recalled
    
    # Study time metrics
    total_study_minutes = Column(Integer, default=0)
    flashcard_minutes = Column(Integer, default=0)
    reading_minutes = Column(Integer, default=0)
    listening_minutes = Column(Integer, default=0)
    writing_minutes = Column(Integer, default=0)
    speaking_minutes = Column(Integer, default=0)
    
    # Performance metrics
    best_hour = Column(Integer, default=0)  # 0-23, most productive hour
    accuracy_rate = Column(Float, default=0.0)  # Overall accuracy
    words_per_minute = Column(Float, default=0.0)  # Review speed
    
    # CEFR progress estimation
    estimated_vocabulary_size = Column(Integer, default=0)
    estimated_level = Column(String(10), default='A1')  # A1, A2, B1, B2, C1, C2
    
    # Streak and motivation
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    xp_earned_today = Column(Integer, default=0)
    level = Column(Integer, default=1)
    total_xp = Column(Integer, default=0)


# ============================================================================
# DIFFICULT WORDS TABLE (Feature 5: Difficult Words Queue)
# ============================================================================
class DifficultWord(Base):
    """Priority queue for frequently missed words"""
    __tablename__ = 'difficult_words'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vocabulary_id = Column(Integer, ForeignKey('vocabulary.id'), nullable=False)
    times_failed = Column(Integer, default=1)
    last_failed = Column(DateTime, default=datetime.utcnow)
    priority_score = Column(Float, default=1.0)  # Higher = review sooner
    notes = Column(Text, default='')  # Why it's difficult
    resolved = Column(Boolean, default=False)  # Mastered after practice


# ============================================================================
# CEFR LEVEL WORDS TABLE (Feature 27: CEFR Level Estimation)
# ============================================================================
class CEFRWord(Base):
    """Words tagged by CEFR level for progression tracking"""
    __tablename__ = 'cefr_words'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spanish_word = Column(String(100), nullable=False, unique=True)
    english_translation = Column(String(200), nullable=False)
    cefr_level = Column(String(10), nullable=False)  # A1, A2, B1, B2, C1, C2
    frequency_rank = Column(Integer, default=10000)  # Word frequency ranking
    part_of_speech = Column(String(50), default='')
    category = Column(String(100), default='general')


# ============================================================================
# DATABASE MANAGER
# ============================================================================
class DatabaseManager:
    """Manages database connections and sessions"""
    
    _instance = None
    _engine = None
    _Session = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, db_path: str = 'z32_nexus.db'):
        """Initialize the database connection"""
        self._engine = create_engine(
            f'sqlite:///{db_path}',
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
            echo=False
        )
        Base.metadata.create_all(self._engine)
        self._Session = sessionmaker(bind=self._engine)
        
        # Initialize default settings
        self._init_default_settings()
        
        # Initialize default tasks
        self._init_default_tasks()
        
        # Initialize achievements
        self._init_achievements()
    
    def get_session(self):
        """Get a new database session"""
        if self._Session is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._Session()
    
    def _init_default_settings(self):
        """Initialize default settings if not exist"""
        session = self.get_session()
        try:
            for key, value in Settings.DEFAULTS.items():
                existing = session.query(Settings).filter_by(key=key).first()
                if not existing:
                    session.add(Settings(key=key, value=value))
            session.commit()
        finally:
            session.close()
    
    def _init_default_tasks(self):
        """Initialize default daily protocol tasks"""
        session = self.get_session()
        try:
            if session.query(Task).count() == 0:
                default_tasks = [
                    # Phase 0 tasks
                    Task(name="Complete 10 Anki Cards", description="Review flashcards", phase_required=0, order=1, xp_reward=15),
                    Task(name="Language Transfer Track", description="Complete one audio lesson", phase_required=0, order=2, xp_reward=20),
                    Task(name="Read 1 Spanish Article", description="Read news or blog in Spanish", phase_required=0, order=3, xp_reward=15),
                    Task(name="Write 100-Word Journal", description="Daily reflection in English", phase_required=0, order=4, xp_reward=10),
                    
                    # Phase 1 tasks
                    Task(name="Listen to Spanish Radio (15min)", description="Radio Garden or podcast", phase_required=1, order=5, xp_reward=20),
                    Task(name="Learn 5 New Words", description="Vocab extraction tool", phase_required=1, order=6, xp_reward=15),
                    Task(name="Practice Speaking (5min)", description="Record yourself speaking", phase_required=1, order=7, xp_reward=25),
                    
                    # Phase 2 tasks
                    Task(name="Watch Spanish Video (20min)", description="TV or YouTube with subtitles", phase_required=2, order=8, xp_reward=30),
                    Task(name="Write Spanish Paragraph", description="Short writing practice", phase_required=2, order=9, xp_reward=35),
                    Task(name="Conversation Practice", description="Speak with native or AI", phase_required=2, order=10, xp_reward=40),
                ]
                for task in default_tasks:
                    session.add(task)
                session.commit()
        finally:
            session.close()
    
    def _init_achievements(self):
        """Initialize achievement definitions"""
        session = self.get_session()
        try:
            if session.query(Achievement).count() == 0:
                achievements = [
                    Achievement(name="First Steps", description="Learn your first word", icon="🌱", xp_reward=10, criteria_type='count', criteria_value=1),
                    Achievement(name="Vocabulary Builder", description="Learn 50 words", icon="📚", xp_reward=50, criteria_type='count', criteria_value=50),
                    Achievement(name="Word Master", description="Learn 100 words", icon="🎓", xp_reward=100, criteria_type='count', criteria_value=100),
                    Achievement(name="Lexicon Expert", description="Learn 500 words", icon="👑", xp_reward=500, is_rare=True, criteria_type='count', criteria_value=500),
                    Achievement(name="Week Warrior", description="7-day streak", icon="🔥", xp_reward=70, criteria_type='streak', criteria_value=7),
                    Achievement(name="Month Master", description="30-day streak", icon="💪", xp_reward=300, is_rare=True, criteria_type='streak', criteria_value=30),
                    Achievement(name="Century Streak", description="100-day streak", icon="🏆", xp_reward=1000, is_rare=True, criteria_type='streak', criteria_value=100),
                    Achievement(name="Early Bird", description="Complete task before 6 AM", icon="🌅", xp_reward=25, criteria_type='milestone', criteria_value=1),
                    Achievement(name="Night Owl", description="Study after 11 PM", icon="🦉", xp_reward=25, criteria_type='milestone', criteria_value=1),
                    Achievement(name="Phase 1 Complete", description="Unlock Phase 1", icon="⭐", xp_reward=100, criteria_type='milestone', criteria_value=1),
                    Achievement(name="Phase 2 Complete", description="Unlock Phase 2", icon="⭐⭐", xp_reward=200, criteria_type='milestone', criteria_value=2),
                    Achievement(name="Omega Unlocked", description="Reach Omega Phase", icon="Ω", xp_reward=500, is_rare=True, criteria_type='milestone', criteria_value=3),
                    Achievement(name="Perfect Day", description="Complete all daily tasks", icon="✨", xp_reward=50, criteria_type='milestone', criteria_value=1),
                    Achievement(name="Speed Learner", description="Learn 20 words in one day", icon="⚡", xp_reward=75, criteria_type='milestone', criteria_value=20),
                    Achievement(name="Focused Mind", description="Complete 5 Pomodoro sessions", icon="🎯", xp_reward=50, criteria_type='count', criteria_value=5),
                ]
                for achievement in achievements:
                    session.add(achievement)
                session.commit()
        finally:
            session.close()
    
    def get_setting(self, key: str, default: str = '') -> str:
        """Get a setting value"""
        session = self.get_session()
        try:
            setting = session.query(Settings).filter_by(key=key).first()
            return setting.value if setting else default
        finally:
            session.close()
    
    def set_setting(self, key: str, value: str):
        """Set a setting value"""
        session = self.get_session()
        try:
            setting = session.query(Settings).filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                session.add(Settings(key=key, value=value))
            session.commit()
        finally:
            session.close()
    
    def get_today_progress(self) -> dict:
        """Get or create today's progress record as a dict"""
        session = self.get_session()
        try:
            today = date.today()
            progress = session.query(UserProgress).filter_by(date=today).first()
            if not progress:
                # Get yesterday's streak
                from datetime import timedelta
                yesterday = today - timedelta(days=1)
                yesterday_progress = session.query(UserProgress).filter_by(date=yesterday).first()
                
                streak = 0
                if yesterday_progress and yesterday_progress.daily_score >= 50:
                    streak = yesterday_progress.streak + 1
                
                progress = UserProgress(date=today, streak=streak)
                session.add(progress)
                session.commit()
                session.refresh(progress)
            
            # Return as dict to avoid detached instance issues
            return progress.to_dict()
        finally:
            session.close()
    
    def update_today_progress(self, **kwargs):
        """Update today's progress with given values"""
        session = self.get_session()
        try:
            today = date.today()
            progress = session.query(UserProgress).filter_by(date=today).first()
            if progress:
                for key, value in kwargs.items():
                    if hasattr(progress, key):
                        setattr(progress, key, value)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_words_due_for_review(self, limit: int = 20) -> List[Vocabulary]:
        """Get vocabulary items due for review"""
        session = self.get_session()
        try:
            now = datetime.utcnow()
            words = session.query(Vocabulary).filter(
                Vocabulary.next_review <= now
            ).order_by(Vocabulary.next_review).limit(limit).all()
            return words
        finally:
            session.close()


# Singleton instance
db = DatabaseManager()
