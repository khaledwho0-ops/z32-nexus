"""
Z32 Nexus - Background Workers
QThread workers for alarms, time checking, and reminders
"""

import logging
from datetime import datetime, time, timedelta, date
from typing import List, Optional
import requests

from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, QTimer
import pytz

from utils.signal_bus import signal_bus
from utils.config_manager import config
from database import db, FajrCache, Alarm

logger = logging.getLogger(__name__)


class TimeCheckerWorker(QThread):
    """
    Background worker that checks time events:
    - Midnight reset
    - Fajr alarm
    - Sleep reminder
    - Vocabulary reminders
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self._mutex = QMutex()
        self._condition = QWaitCondition()
        
        # Egypt timezone
        self.timezone = pytz.timezone('Africa/Cairo')
        
        # Track last triggered times to avoid duplicates
        self._last_midnight = None
        self._last_fajr = None
        self._last_sleep_reminder = None
        self._last_vocab_reminder = None
        
        # Fajr time cache
        self._fajr_time = None
        self._fajr_cache_date = None
    
    def run(self):
        """Main worker loop"""
        logger.info("TimeCheckerWorker started")
        
        while self._running:
            try:
                now = datetime.now(self.timezone)
                
                # Check midnight reset
                self._check_midnight(now)
                
                # Check Fajr alarm
                self._check_fajr(now)
                
                # Check sleep reminder
                self._check_sleep_reminder(now)
                
                # Check vocab reminder
                self._check_vocab_reminder(now)
                
            except Exception as e:
                logger.error(f"TimeCheckerWorker error: {e}")
            
            # Wait for 30 seconds or until woken
            self._mutex.lock()
            self._condition.wait(self._mutex, 30000)  # 30 seconds
            self._mutex.unlock()
        
        logger.info("TimeCheckerWorker stopped")
    
    def stop(self):
        """Stop the worker"""
        self._running = False
        self._mutex.lock()
        self._condition.wakeAll()
        self._mutex.unlock()
    
    def _check_midnight(self, now: datetime):
        """Check for midnight reset"""
        today = now.date()
        
        if self._last_midnight != today and now.hour == 0 and now.minute < 5:
            logger.info("Midnight reset triggered")
            self._last_midnight = today
            signal_bus.midnight_reset.emit()
    
    def _check_fajr(self, now: datetime):
        """Check for Fajr alarm"""
        today = now.date()
        
        # Get Fajr time (from cache or API)
        fajr_time = self._get_fajr_time(today)
        
        if fajr_time and self._last_fajr != today:
            # Check if we're within 5 minutes after Fajr
            fajr_datetime = datetime.combine(today, fajr_time)
            fajr_datetime = self.timezone.localize(fajr_datetime)
            
            if fajr_datetime <= now <= fajr_datetime + timedelta(minutes=5):
                logger.info("Fajr alarm triggered")
                self._last_fajr = today
                signal_bus.fajr_alarm_triggered.emit()
    
    def _check_sleep_reminder(self, now: datetime):
        """Check for sleep reminder"""
        today = now.date()
        
        if self._last_sleep_reminder != today:
            # Parse sleep time from config
            sleep_time_str = config.sleep_time
            try:
                hour, minute = map(int, sleep_time_str.split(':'))
                sleep_time = time(hour, minute)
                
                # Reminder 15 minutes before
                reminder_minutes = config.get_int('Schedule', 'sleep_reminder_minutes', 15)
                
                sleep_datetime = datetime.combine(today, sleep_time)
                sleep_datetime = self.timezone.localize(sleep_datetime)
                reminder_datetime = sleep_datetime - timedelta(minutes=reminder_minutes)
                
                # Check if we're within the reminder window
                if reminder_datetime <= now <= reminder_datetime + timedelta(minutes=2):
                    logger.info("Sleep reminder triggered")
                    self._last_sleep_reminder = today
                    signal_bus.sleep_alarm_triggered.emit()
            except Exception as e:
                logger.error(f"Error parsing sleep time: {e}")
    
    def _check_vocab_reminder(self, now: datetime):
        """Check for vocabulary reminder"""
        interval = config.reminder_interval  # minutes
        
        if self._last_vocab_reminder is None:
            self._last_vocab_reminder = now
        
        if (now - self._last_vocab_reminder).total_seconds() >= interval * 60:
            # Get a random word due for review
            words = db.get_words_due_for_review(limit=1)
            if words:
                word = words[0]
                logger.info(f"Vocab reminder: {word.english} -> {word.spanish}")
                self._last_vocab_reminder = now
                signal_bus.vocab_reminder.emit(word.english, word.spanish)
    
    def _get_fajr_time(self, target_date: date) -> Optional[time]:
        """Get Fajr time from cache or API"""
        # Check memory cache
        if self._fajr_cache_date == target_date and self._fajr_time:
            return self._fajr_time
        
        # Check database cache
        session = db.get_session()
        try:
            cached = session.query(FajrCache).filter_by(date=target_date).first()
            if cached:
                self._fajr_time = cached.fajr_time
                self._fajr_cache_date = target_date
                return cached.fajr_time
        finally:
            session.close()
        
        # Fetch from API
        fajr_time = self._fetch_fajr_from_api(target_date)
        
        if fajr_time:
            # Cache it
            self._cache_fajr_time(target_date, fajr_time)
            self._fajr_time = fajr_time
            self._fajr_cache_date = target_date
            return fajr_time
        
        # Fallback to 5:00 AM
        logger.warning("Using fallback Fajr time: 05:00")
        return time(5, 0)
    
    def _fetch_fajr_from_api(self, target_date: date) -> Optional[time]:
        """Fetch Fajr time from Aladhan API"""
        try:
            # Cairo coordinates
            lat = 30.0444
            lon = 31.2357
            
            url = f"http://api.aladhan.com/v1/timings/{target_date.day}-{target_date.month}-{target_date.year}"
            params = {
                'latitude': lat,
                'longitude': lon,
                'method': 5,  # Egyptian General Authority of Survey
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            fajr_str = data['data']['timings']['Fajr']
            
            # Parse time (format: "HH:MM")
            hour, minute = map(int, fajr_str.split(':'))
            
            logger.info(f"Fetched Fajr time from API: {hour:02d}:{minute:02d}")
            return time(hour, minute)
            
        except Exception as e:
            logger.error(f"Failed to fetch Fajr time from API: {e}")
            return None
    
    def _cache_fajr_time(self, target_date: date, fajr_time: time):
        """Cache Fajr time in database"""
        session = db.get_session()
        try:
            cached = FajrCache(
                date=target_date,
                fajr_time=fajr_time,
                location='Egypt'
            )
            session.merge(cached)
            session.commit()
            logger.info(f"Cached Fajr time for {target_date}")
        except Exception as e:
            logger.error(f"Failed to cache Fajr time: {e}")
            session.rollback()
        finally:
            session.close()


class VocabReminderWorker(QThread):
    """
    Worker that shows periodic vocabulary reminders.
    Uses Windows toast notifications.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self._mutex = QMutex()
        self._condition = QWaitCondition()
    
    def run(self):
        """Main worker loop"""
        logger.info("VocabReminderWorker started")
        
        while self._running:
            try:
                interval = config.reminder_interval * 60 * 1000  # Convert to ms
                
                # Wait for interval or until woken
                self._mutex.lock()
                self._condition.wait(self._mutex, interval)
                self._mutex.unlock()
                
                if not self._running:
                    break
                
                # Trigger a vocab reminder
                words = db.get_words_due_for_review(limit=1)
                if words:
                    word = words[0]
                    signal_bus.vocab_reminder.emit(word.english, word.spanish)
                
            except Exception as e:
                logger.error(f"VocabReminderWorker error: {e}")
        
        logger.info("VocabReminderWorker stopped")
    
    def stop(self):
        """Stop the worker"""
        self._running = False
        self._mutex.lock()
        self._condition.wakeAll()
        self._mutex.unlock()


class WakeDetectorWorker(QThread):
    """
    Detects when the PC wakes from sleep to trigger missed alarms.
    """
    
    wake_detected = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self._last_check = datetime.now()
        self._mutex = QMutex()
        self._condition = QWaitCondition()
    
    def run(self):
        """Main worker loop"""
        logger.info("WakeDetectorWorker started")
        
        while self._running:
            now = datetime.now()
            
            # If more than 2 minutes have passed since last check,
            # we likely just woke from sleep
            if (now - self._last_check).total_seconds() > 120:
                logger.info("Wake from sleep detected!")
                self.wake_detected.emit()
            
            self._last_check = now
            
            # Check every minute
            self._mutex.lock()
            self._condition.wait(self._mutex, 60000)
            self._mutex.unlock()
        
        logger.info("WakeDetectorWorker stopped")
    
    def stop(self):
        """Stop the worker"""
        self._running = False
        self._mutex.lock()
        self._condition.wakeAll()
        self._mutex.unlock()


class PassiveListeningWorker(QThread):
    """
    Feature 15: Passive Listening Mode
    Periodically plays Spanish vocabulary audio for passive exposure.
    Helps with subconscious language acquisition.
    """
    
    word_played = pyqtSignal(str, str)  # spanish, english
    
    def __init__(self, interval_minutes: int = 30, parent=None):
        super().__init__(parent)
        self._running = True
        self._enabled = False  # User must enable this
        self._interval = interval_minutes * 60 * 1000  # Convert to ms
        self._mutex = QMutex()
        self._condition = QWaitCondition()
    
    def run(self):
        """Main worker loop"""
        logger.info("PassiveListeningWorker started")
        
        while self._running:
            try:
                if self._enabled:
                    # Get a random word
                    words = db.get_words_due_for_review(limit=5)
                    if words:
                        import random
                        word = random.choice(words)
                        
                        # Play audio using TTS
                        self._play_word_audio(word.spanish)
                        
                        # Emit signal
                        self.word_played.emit(word.spanish, word.english)
                        signal_bus.passive_exposure_word.emit(word.spanish, word.english)
                        
                        logger.info(f"Passive listening: {word.spanish} ({word.english})")
                
            except Exception as e:
                logger.error(f"PassiveListeningWorker error: {e}")
            
            # Wait for interval or until woken
            self._mutex.lock()
            self._condition.wait(self._mutex, self._interval)
            self._mutex.unlock()
        
        logger.info("PassiveListeningWorker stopped")
    
    def _play_word_audio(self, text: str):
        """Play TTS audio for the word"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            # Try to set Spanish voice
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.setProperty('rate', 130)  # Slow for clarity
            engine.setProperty('volume', 0.7)  # Not too loud
            
            engine.say(text)
            engine.runAndWait()
            
        except Exception as e:
            logger.warning(f"Passive listening TTS failed: {e}")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable passive listening"""
        self._enabled = enabled
        logger.info(f"Passive listening {'enabled' if enabled else 'disabled'}")
    
    def set_interval(self, minutes: int):
        """Set the interval between words"""
        self._interval = minutes * 60 * 1000
    
    def stop(self):
        """Stop the worker"""
        self._running = False
        self._mutex.lock()
        self._condition.wakeAll()
        self._mutex.unlock()


def start_background_workers() -> List[QThread]:
    """Start all background workers and return them"""
    workers = []
    
    # Time checker worker
    time_checker = TimeCheckerWorker()
    time_checker.start()
    workers.append(time_checker)
    
    # Wake detector
    wake_detector = WakeDetectorWorker()
    wake_detector.wake_detected.connect(lambda: logger.info("Processing missed alarms..."))
    wake_detector.start()
    workers.append(wake_detector)
    
    # Passive listening worker (Feature 15)
    passive_listener = PassiveListeningWorker(interval_minutes=30)
    passive_listener.word_played.connect(
        lambda sp, en: logger.debug(f"Passive exposure: {sp}")
    )
    passive_listener.start()
    workers.append(passive_listener)
    
    logger.info(f"Started {len(workers)} background workers")
    return workers
