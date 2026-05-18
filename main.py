"""
Z32 Nexus - Main Entry Point
Desktop Lifecycle Manager & Language Acquisition Accelerator

This is the main entry point for the application.
It handles:
- Single instance locking (prevents multiple instances)
- Database initialization
- System tray persistence
- Background worker threads
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Initialize logging first
from utils.logger import log_manager
import logging

logger = logging.getLogger(__name__)


def check_single_instance():
    """Ensure only one instance of the app is running"""
    try:
        import fasteners
        lock_file = project_root / '.z32_nexus.lock'
        lock = fasteners.InterProcessLock(str(lock_file))
        
        if not lock.acquire(blocking=False):
            logger.warning("Another instance is already running!")
            return None
        
        return lock
    except Exception as e:
        logger.error(f"Failed to acquire instance lock: {e}")
        return True  # Continue anyway if lock fails


def main():
    """Main entry point"""
    logger.info("Starting Z32 Nexus...")
    
    # Check single instance
    instance_lock = check_single_instance()
    if instance_lock is None:
        # Show message and exit
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication(sys.argv)
        QMessageBox.warning(
            None,
            "Z32 Nexus",
            "Another instance of Z32 Nexus is already running.\n"
            "Check your system tray."
        )
        return 1
    
    # Initialize database
    from database import db
    db.initialize()
    logger.info("Database initialized")
    
    # Check for unclean shutdown
    if log_manager.check_unclean_shutdown():
        logger.warning("Detected unclean shutdown - checking data integrity")
    
    # Mark as running
    log_manager.set_running(True)
    
    try:
        # Create application
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Enable high DPI scaling
        app = QApplication(sys.argv)
        app.setApplicationName("Z32 Nexus")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Z32")
        
        # Prevent app from quitting when last window closes (for tray)
        app.setQuitOnLastWindowClosed(False)
        
        # Create and show main window
        from ui.main_window import MainWindow
        window = MainWindow()
        window.show()
        
        logger.info("Application started successfully")
        
        # Start background workers
        from workers import start_background_workers
        workers = start_background_workers()
        
        # Run event loop
        exit_code = app.exec()
        
        # Cleanup
        logger.info("Application shutting down...")
        log_manager.set_running(False)
        
        # Stop workers
        for worker in workers:
            worker.stop()
            worker.wait(3000)  # Wait up to 3 seconds
        
        return exit_code
        
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        log_manager.set_running(False)
        raise
    finally:
        # Release instance lock
        if instance_lock and hasattr(instance_lock, 'release'):
            try:
                instance_lock.release()
            except:
                pass


if __name__ == '__main__':
    sys.exit(main())
