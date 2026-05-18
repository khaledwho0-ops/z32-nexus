"""
Z32 Nexus - Error Logging System
Comprehensive logging with rotation and crash detection
"""

import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


class LogManager:
    """Manages application logging"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging with file rotation"""
        # Get log file path
        log_dir = Path(__file__).parent.parent
        log_file = log_dir / 'debug.log'
        crash_file = log_dir / 'crash.log'
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create rotating file handler (max 10MB, keep 3 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Set up global exception handler
        self._crash_file = crash_file
        sys.excepthook = self._handle_exception
        
        logging.info("=" * 60)
        logging.info("Z32 Nexus - Application Started")
        logging.info(f"Log file: {log_file}")
        logging.info("=" * 60)
    
    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Allow Ctrl+C to exit normally
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Log the exception
        logging.critical("Uncaught exception!", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Write to crash log
        with open(self._crash_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"CRASH at {datetime.now().isoformat()}\n")
            f.write(f"{'=' * 60}\n")
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
    
    def check_unclean_shutdown(self) -> bool:
        """Check if there was an unclean shutdown"""
        lock_file = Path(__file__).parent.parent / '.running'
        if lock_file.exists():
            logging.warning("Detected unclean shutdown from previous session")
            return True
        return False
    
    def set_running(self, running: bool):
        """Set the running state"""
        lock_file = Path(__file__).parent.parent / '.running'
        if running:
            lock_file.touch()
        elif lock_file.exists():
            lock_file.unlink()


# Initialize logging on import
log_manager = LogManager()
