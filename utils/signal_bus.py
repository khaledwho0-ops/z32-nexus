"""
Z32 Nexus - Signal Bus
Centralized signal management for cross-component communication
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional


class SignalBus(QObject):
    """
    Singleton signal bus for application-wide event communication.
    All signals are defined here to prevent spaghetti connections.
    """
    
    _instance: Optional['SignalBus'] = None
    
    # ========================================
    # ALARM SIGNALS
    # ========================================
    fajr_alarm_triggered = pyqtSignal()
    sleep_alarm_triggered = pyqtSignal()
    custom_alarm_triggered = pyqtSignal(str)  # alarm name
    midnight_reset = pyqtSignal()
    
    # ========================================
    # PROGRESS SIGNALS
    # ========================================
    task_completed = pyqtSignal(int)  # task ID
    daily_progress_updated = pyqtSignal(int)  # new percentage
    streak_updated = pyqtSignal(int)  # new streak count
    phase_unlocked = pyqtSignal(int)  # new phase number
    
    # ========================================
    # VOCABULARY SIGNALS
    # ========================================
    word_learned = pyqtSignal(str, str)  # english, spanish
    translation_complete = pyqtSignal(int)  # number of words translated
    flashcard_reviewed = pyqtSignal(int, int)  # word_id, quality (0-5)
    review_session_complete = pyqtSignal(int, int)  # correct, total
    
    # ========================================
    # REMINDER SIGNALS
    # ========================================
    vocab_reminder = pyqtSignal(str, str)  # english, spanish
    microlearning_start = pyqtSignal()
    
    # ========================================
    # SYSTEM SIGNALS
    # ========================================
    settings_changed = pyqtSignal(str, str)  # key, value
    theme_changed = pyqtSignal(str)  # new theme color
    minimize_to_tray = pyqtSignal()
    restore_from_tray = pyqtSignal()
    app_shutdown = pyqtSignal()
    
    # ========================================
    # ACHIEVEMENT SIGNALS
    # ========================================
    achievement_unlocked = pyqtSignal(str, str, int)  # name, icon, xp
    level_up = pyqtSignal(int)  # new level
    xp_gained = pyqtSignal(int)  # amount
    
    # ========================================
    # TOAST/NOTIFICATION SIGNALS
    # ========================================
    show_toast = pyqtSignal(str, str, int)  # title, message, duration_ms
    show_notification = pyqtSignal(str, str)  # title, message
    
    # ========================================
    # POMODORO SIGNALS
    # ========================================
    pomodoro_started = pyqtSignal(int)  # duration in minutes
    pomodoro_complete = pyqtSignal()
    pomodoro_break_start = pyqtSignal(int)  # break duration
    pomodoro_break_end = pyqtSignal()
    
    # ========================================
    # ANTI-FRAGILE SIGNALS
    # ========================================
    istighfar_reset = pyqtSignal()  # Reset daily progress
    sujood_mode_start = pyqtSignal()  # 5-minute silent mode
    sujood_mode_end = pyqtSignal()
    
    # ========================================
    # EXPERT LEARNING: FLASHCARD MODES (Features 1-4)
    # ========================================
    flashcard_mode_changed = pyqtSignal(str)  # 'normal', 'reverse', 'cloze', 'audio', 'speed'
    speed_review_started = pyqtSignal()  # Feature 4: Speed Review
    speed_review_complete = pyqtSignal(int, float)  # words_count, words_per_minute
    difficult_word_flagged = pyqtSignal(int, str)  # word_id, reason  # Feature 5
    interleaved_mode_toggle = pyqtSignal(bool)  # Feature 30: Interleaved Practice
    
    # ========================================
    # EXPERT LEARNING: CONTEXT & MEMORY (Features 6-9)
    # ========================================
    mnemonic_created = pyqtSignal(int, str)  # word_id, mnemonic_text  # Feature 7
    memory_palace_updated = pyqtSignal(int, str)  # word_id, location  # Feature 6
    context_sentence_added = pyqtSignal(int, str, str)  # word_id, spanish, english  # Feature 9
    word_family_expanded = pyqtSignal(str, list)  # root_word, related_words  # Feature 10
    
    # ========================================
    # EXPERT LEARNING: ANALYTICS (Features 23-29)
    # ========================================
    analytics_updated = pyqtSignal(dict)  # Full analytics data  # Feature 23
    cefr_level_estimated = pyqtSignal(str)  # 'A1', 'A2', etc.  # Feature 27
    weak_area_detected = pyqtSignal(str, str)  # area_type, details  # Feature 25
    optimal_time_detected = pyqtSignal(int)  # hour_of_day  # Feature 29
    weekly_report_ready = pyqtSignal(dict)  # report_data  # Feature 28
    retention_rate_updated = pyqtSignal(float)  # percentage  # Feature 8
    
    # ========================================
    # EXPERT LEARNING: PRODUCTION (Features 17-22)
    # ========================================
    writing_prompt_generated = pyqtSignal(str, str)  # english, spanish  # Feature 17
    grammar_drill_started = pyqtSignal(str)  # pattern_name  # Feature 18
    grammar_drill_complete = pyqtSignal(int, int)  # correct, total
    dictation_started = pyqtSignal()  # Feature 21
    dictation_complete = pyqtSignal(int, int)  # correct_words, total_words
    shadowing_started = pyqtSignal(str)  # audio_text  # Feature 19
    translation_challenge_started = pyqtSignal()  # Feature 20
    translation_challenge_complete = pyqtSignal(int, int)  # correct, total
    conversation_scenario_started = pyqtSignal(str)  # scenario_name  # Feature 22
    
    # ========================================
    # EXPERT LEARNING: IMMERSION (Features 14-16)
    # ========================================
    daily_quote_shown = pyqtSignal(str, str, str)  # spanish, english, author  # Feature 14
    passive_exposure_word = pyqtSignal(str, str)  # spanish, english  # Feature 15
    reading_level_analyzed = pyqtSignal(str, int)  # cefr_level, unknown_count  # Feature 16
    collocation_learned = pyqtSignal(str, str)  # english, spanish  # Feature 11
    register_warning = pyqtSignal(str, str)  # word, correct_register  # Feature 12
    

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True


# Global singleton instance
signal_bus = SignalBus()
