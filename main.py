"""Trading Signal System - Main Entry Point."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from utils.logger import setup_logger
from database.db_manager import DatabaseManager
from database.seed_data import seed_database


def main():
    """Main application entry point."""
    logger = setup_logger()
    logger.info("Starting Trading Signal System...")

    try:
        # Initialize database
        db = DatabaseManager()
        db.create_tables()
        seed_database()
        logger.info("Database initialized.")

        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Trading Signal System")
        app.setOrganizationName("Universal Trading")

        # Set application style
        app.setStyle("Fusion")

        # Create and show main window
        from gui.main_window import MainWindow
        window = MainWindow()
        window.show()

        logger.info("Application started successfully.")
        sys.exit(app.exec())

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
