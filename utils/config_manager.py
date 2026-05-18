"""
Z32 Nexus - Configuration Manager
Handles config.ini file persistence for user settings
"""

import configparser
import os
from pathlib import Path
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration via config.ini"""
    
    _instance = None
    
    DEFAULT_CONFIG = {
        'General': {
            'theme': 'matrix',
            'theme_color': '#00ff41',
            'font_family': 'Consolas',
            'font_size': '14',
            'language_from': 'en',
            'language_to': 'es',
            'first_run': 'true',
        },
        'Audio': {
            'volume': '80',
            'alarm_sound': 'alarm_default.wav',
            'notification_sound': 'notification.wav',
            'tts_enabled': 'true',
            'tts_speed': '150',
        },
        'Schedule': {
            'fajr_enabled': 'true',
            'fajr_offset': '0',
            'sleep_time': '22:30',
            'sleep_reminder_minutes': '15',
            'reminder_interval': '60',
        },
        'Learning': {
            'daily_word_goal': '10',
            'pomodoro_duration': '25',
            'break_duration': '5',
            'auto_play_pronunciation': 'true',
            'show_context_sentences': 'true',
        },
        'System': {
            'run_on_startup': 'false',
            'minimize_to_tray': 'true',
            'check_updates': 'true',
            'debug_mode': 'false',
        },
        'Progress': {
            'current_phase': '0',
            'total_xp': '0',
            'level': '1',
        }
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.config = configparser.ConfigParser()
        self.config_path = self._get_config_path()
        self._load_or_create()
    
    def _get_config_path(self) -> Path:
        """Get the path to config.ini in the app directory"""
        # Use app directory for config
        app_dir = Path(__file__).parent
        return app_dir / 'config.ini'
    
    def _load_or_create(self):
        """Load existing config or create with defaults"""
        if self.config_path.exists():
            try:
                self.config.read(self.config_path, encoding='utf-8')
                logger.info(f"Loaded config from {self.config_path}")
                # Ensure all default sections/keys exist
                self._merge_defaults()
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                self._create_default()
        else:
            self._create_default()
    
    def _create_default(self):
        """Create config with default values"""
        for section, options in self.DEFAULT_CONFIG.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)
        self.save()
        logger.info(f"Created default config at {self.config_path}")
    
    def _merge_defaults(self):
        """Merge default values for any missing sections/keys"""
        changed = False
        for section, options in self.DEFAULT_CONFIG.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
                changed = True
            for key, value in options.items():
                if not self.config.has_option(section, key):
                    self.config.set(section, key, value)
                    changed = True
        if changed:
            self.save()
    
    def get(self, section: str, key: str, fallback: str = '') -> str:
        """Get a config value"""
        try:
            return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """Get a config value as integer"""
        try:
            return self.config.getint(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get a config value as float"""
        try:
            return self.config.getfloat(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get a config value as boolean"""
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def set(self, section: str, key: str, value: Any):
        """Set a config value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save()
    
    def save(self):
        """Save config to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    # Convenience methods for common settings
    @property
    def theme_color(self) -> str:
        return self.get('General', 'theme_color', '#00ff41')
    
    @theme_color.setter
    def theme_color(self, value: str):
        self.set('General', 'theme_color', value)
    
    @property
    def volume(self) -> int:
        return self.get_int('Audio', 'volume', 80)
    
    @volume.setter
    def volume(self, value: int):
        self.set('Audio', 'volume', value)
    
    @property
    def current_phase(self) -> int:
        return self.get_int('Progress', 'current_phase', 0)
    
    @current_phase.setter
    def current_phase(self, value: int):
        self.set('Progress', 'current_phase', value)
    
    @property
    def daily_word_goal(self) -> int:
        return self.get_int('Learning', 'daily_word_goal', 10)
    
    @property
    def pomodoro_duration(self) -> int:
        return self.get_int('Learning', 'pomodoro_duration', 25)
    
    @property
    def reminder_interval(self) -> int:
        return self.get_int('Schedule', 'reminder_interval', 60)
    
    @property
    def sleep_time(self) -> str:
        return self.get('Schedule', 'sleep_time', '22:30')
    
    @property
    def total_xp(self) -> int:
        return self.get_int('Progress', 'total_xp', 0)
    
    @total_xp.setter
    def total_xp(self, value: int):
        self.set('Progress', 'total_xp', value)
    
    @property
    def level(self) -> int:
        return self.get_int('Progress', 'level', 1)
    
    @level.setter
    def level(self, value: int):
        self.set('Progress', 'level', value)
    
    def add_xp(self, amount: int) -> bool:
        """Add XP and check for level up. Returns True if leveled up."""
        self.total_xp += amount
        # Level formula: XP needed = level * 100
        xp_for_next = self.level * 100
        if self.total_xp >= xp_for_next:
            self.level += 1
            return True
        return False


# Singleton instance
config = ConfigManager()
