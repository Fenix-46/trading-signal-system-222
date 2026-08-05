"""Database manager for SQLite operations."""

import logging
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base
from config.settings import AppSettings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and sessions."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        settings = AppSettings()
        db_path = settings.db_path
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False}
        )
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully.")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def drop_tables(self):
        """Drop all database tables."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped.")
        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
            raise

    def backup_database(self, backup_path: str):
        """Backup the database file."""
        import shutil
        settings = AppSettings()
        db_path = settings.db_path
        if db_path.exists():
            shutil.copy2(str(db_path), backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        return False

    def restore_database(self, backup_path: str):
        """Restore database from backup."""
        import shutil
        settings = AppSettings()
        db_path = settings.db_path
        if Path(backup_path).exists():
            shutil.copy2(backup_path, str(db_path))
            logger.info(f"Database restored from {backup_path}")
            return True
        return False
