#!/usr/bin/env python3
"""
Data Access Layer for Owlgorithm
Centralizes all data operations with consistent error handling and path management.
"""

import os
import json
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .repository import AtomicJSONRepository
from config import app_config as cfg


class DataAccessError(Exception):
    """Raised when data access operations fail."""
    pass


class DataManager:
    """
    Centralized data access layer for Owlgorithm.
    
    Provides high-level data operations with consistent error handling,
    path management, and abstraction for future database migration.
    """
    
    def __init__(self):
        """Initialize data manager with configured paths."""
        self._ensure_directories()
        
        # Initialize repositories for known data files
        self._state_repo = AtomicJSONRepository(cfg.STATE_FILE, auto_migrate=True)
        self._pushover_config_repo = AtomicJSONRepository(cfg.NOTIFIER_CONFIG_FILE, auto_migrate=False)
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for directory in [cfg.DATA_DIR, cfg.LOG_DIR, cfg.CONFIG_DIR]:
            Path(directory).mkdir(exist_ok=True, parents=True)
    
    # === State Management ===
    
    def load_tracker_state(self, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load tracker state with default handling.
        
        Args:
            default: Default state if file doesn't exist
            
        Returns:
            Current tracker state
            
        Raises:
            DataAccessError: If state loading fails
        """
        try:
            return self._state_repo.load(default or {})
        except Exception as e:
            raise DataAccessError(f"Failed to load tracker state: {e}") from e
    
    def save_tracker_state(self, state: Dict[str, Any]) -> None:
        """
        Save tracker state atomically.
        
        Args:
            state: State data to save
            
        Raises:
            DataAccessError: If state saving fails
        """
        try:
            success = self._state_repo.save(state)
            if not success:
                raise DataAccessError("Atomic save operation failed")
        except Exception as e:
            raise DataAccessError(f"Failed to save tracker state: {e}") from e
    
    def get_state_last_modified(self) -> Optional[datetime]:
        """Get last modification time of tracker state file."""
        return self._state_repo.get_last_modified()
    
    # === Configuration Management ===
    
    def load_pushover_config(self) -> Dict[str, Any]:
        """
        Load Pushover notification configuration.
        
        Returns:
            Pushover configuration
            
        Raises:
            DataAccessError: If config loading fails
        """
        try:
            config = self._pushover_config_repo.load({})
            if not config:
                raise DataAccessError("Pushover config file is empty or missing")
            return config
        except Exception as e:
            raise DataAccessError(f"Failed to load Pushover config: {e}") from e
    
    def save_pushover_config(self, config: Dict[str, Any]) -> None:
        """
        Save Pushover configuration.
        
        Args:
            config: Configuration to save
            
        Raises:
            DataAccessError: If config saving fails
        """
        try:
            success = self._pushover_config_repo.save(config)
            if not success:
                raise DataAccessError("Failed to save Pushover config")
        except Exception as e:
            raise DataAccessError(f"Failed to save Pushover config: {e}") from e
    
    # === Scraped Data Management ===
    
    def find_latest_scrape_file(self, username: str = None) -> Optional[str]:
        """
        Find the most recent scraped data file.
        
        Args:
            username: Username to search for (defaults to configured username)
            
        Returns:
            Path to latest scrape file or None if not found
            
        Raises:
            DataAccessError: If file search fails
        """
        try:
            username = username or cfg.USERNAME
            pattern = os.path.join(cfg.DATA_DIR, f"duome_raw_{username}_*.json")
            
            files = glob.glob(pattern)
            if not files:
                return None
            
            # Sort by creation time, newest first
            latest_file = max(files, key=os.path.getctime)
            return latest_file
            
        except Exception as e:
            raise DataAccessError(f"Failed to find latest scrape file: {e}") from e
    
    def load_scrape_data(self, file_path: str) -> Dict[str, Any]:
        """
        Load scraped data from specified file.
        
        Args:
            file_path: Path to scrape data file
            
        Returns:
            Scraped data
            
        Raises:
            DataAccessError: If data loading fails
        """
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise DataAccessError(f"Scrape file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise DataAccessError(f"Invalid JSON in scrape file {file_path}: {e}")
        except Exception as e:
            raise DataAccessError(f"Failed to load scrape data from {file_path}: {e}") from e
    
    def save_scrape_data(self, data: Dict[str, Any], username: str = None) -> str:
        """
        Save scraped data with timestamped filename.
        
        Args:
            data: Scraped data to save
            username: Username (defaults to configured username)
            
        Returns:
            Path to saved file
            
        Raises:
            DataAccessError: If data saving fails
        """
        try:
            username = username or cfg.USERNAME
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"duome_raw_{username}_{timestamp}.json"
            file_path = os.path.join(cfg.DATA_DIR, filename)
            
            # Use atomic repository for safe saving
            repo = AtomicJSONRepository(file_path, auto_migrate=False)
            success = repo.save(data)
            
            if not success:
                raise DataAccessError("Failed to save scrape data")
            
            return file_path
            
        except Exception as e:
            raise DataAccessError(f"Failed to save scrape data: {e}") from e
    
    def list_scrape_files(self, username: str = None, limit: int = None) -> List[str]:
        """
        List scraped data files for a user.
        
        Args:
            username: Username to search for (defaults to configured username)
            limit: Maximum number of files to return (newest first)
            
        Returns:
            List of file paths sorted by creation time (newest first)
            
        Raises:
            DataAccessError: If file listing fails
        """
        try:
            username = username or cfg.USERNAME
            pattern = os.path.join(cfg.DATA_DIR, f"duome_raw_{username}_*.json")
            
            files = glob.glob(pattern)
            # Sort by creation time, newest first
            files.sort(key=os.path.getctime, reverse=True)
            
            if limit:
                files = files[:limit]
            
            return files
            
        except Exception as e:
            raise DataAccessError(f"Failed to list scrape files: {e}") from e
    
    def cleanup_old_scrape_files(self, username: str = None, keep_count: int = 10) -> int:
        """
        Clean up old scraped data files, keeping only the most recent.
        
        Args:
            username: Username to clean up (defaults to configured username)
            keep_count: Number of recent files to keep
            
        Returns:
            Number of files deleted
            
        Raises:
            DataAccessError: If cleanup fails
        """
        try:
            files = self.list_scrape_files(username)
            
            if len(files) <= keep_count:
                return 0
            
            files_to_delete = files[keep_count:]
            deleted_count = 0
            
            for file_path in files_to_delete:
                try:
                    os.unlink(file_path)
                    deleted_count += 1
                except OSError:
                    # Continue cleaning up other files if one fails
                    continue
            
            return deleted_count
            
        except Exception as e:
            raise DataAccessError(f"Failed to cleanup scrape files: {e}") from e
    
    # === Markdown File Management ===
    
    def load_markdown_content(self) -> str:
        """
        Load markdown file content.
        
        Returns:
            Markdown file content
            
        Raises:
            DataAccessError: If markdown loading fails
        """
        try:
            with open(cfg.MARKDOWN_FILE, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise DataAccessError(f"Markdown file not found: {cfg.MARKDOWN_FILE}")
        except Exception as e:
            raise DataAccessError(f"Failed to load markdown file: {e}") from e
    
    def save_markdown_content(self, content: str) -> None:
        """
        Save markdown file content.
        
        Args:
            content: Markdown content to save
            
        Raises:
            DataAccessError: If markdown saving fails
        """
        try:
            # Create backup before modifying
            backup_path = f"{cfg.MARKDOWN_FILE}.backup"
            if os.path.exists(cfg.MARKDOWN_FILE):
                with open(cfg.MARKDOWN_FILE, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
            
            # Write new content
            with open(cfg.MARKDOWN_FILE, 'w') as f:
                f.write(content)
                
        except Exception as e:
            raise DataAccessError(f"Failed to save markdown file: {e}") from e
    
    # === Path Management ===
    
    def get_data_path(self, filename: str) -> str:
        """Get full path for a data file."""
        return os.path.join(cfg.DATA_DIR, filename)
    
    def get_log_path(self, filename: str) -> str:
        """Get full path for a log file."""
        return os.path.join(cfg.LOG_DIR, filename)
    
    def get_config_path(self, filename: str) -> str:
        """Get full path for a config file."""
        return os.path.join(cfg.CONFIG_DIR, filename)
    
    # === Health Check ===
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on data layer.
        
        Returns:
            Health status information
        """
        health = {
            "status": "healthy",
            "checks": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Check directories
        for name, path in [
            ("data_dir", cfg.DATA_DIR),
            ("log_dir", cfg.LOG_DIR),
            ("config_dir", cfg.CONFIG_DIR)
        ]:
            health["checks"][name] = {
                "exists": os.path.exists(path),
                "writable": os.access(path, os.W_OK) if os.path.exists(path) else False
            }
        
        # Check key files
        health["checks"]["tracker_state"] = {
            "exists": self._state_repo.exists(),
            "last_modified": self.get_state_last_modified().isoformat() if self.get_state_last_modified() else None
        }
        
        health["checks"]["markdown_file"] = {
            "exists": os.path.exists(cfg.MARKDOWN_FILE)
        }
        
        # Check recent scrape data
        latest_scrape = self.find_latest_scrape_file()
        health["checks"]["latest_scrape"] = {
            "exists": latest_scrape is not None,
            "path": latest_scrape,
            "age_hours": None
        }
        
        if latest_scrape:
            age_seconds = os.path.getctime(latest_scrape)
            age_hours = (datetime.now().timestamp() - age_seconds) / 3600
            health["checks"]["latest_scrape"]["age_hours"] = round(age_hours, 2)
        
        # Determine overall health
        failed_checks = [
            name for name, check in health["checks"].items()
            if isinstance(check, dict) and not check.get("exists", True)
        ]
        
        if failed_checks:
            health["status"] = "degraded"
            health["failed_checks"] = failed_checks
        
        return health


# Global instance for convenient access
data_manager = DataManager()