#!/usr/bin/env python3
"""
Storage Interface for Future Database Migration
Defines abstract interfaces that can be implemented for different storage backends.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


class StorageBackend(ABC):
    """Abstract interface for data storage backends."""
    
    @abstractmethod
    def save(self, key: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save data with a given key.
        
        Args:
            key: Unique identifier for the data
            data: Data to store
            metadata: Optional metadata (tags, timestamps, etc.)
            
        Returns:
            True if save was successful
        """
        pass
    
    @abstractmethod
    def load(self, key: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load data by key.
        
        Args:
            key: Unique identifier for the data
            default: Default value if key doesn't exist
            
        Returns:
            Stored data or default
        """
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists in storage."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data by key."""
        pass
    
    @abstractmethod
    def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        List all keys, optionally filtered by pattern.
        
        Args:
            pattern: Optional pattern to filter keys
            
        Returns:
            List of matching keys
        """
        pass
    
    @abstractmethod
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a key."""
        pass


class FileStorageBackend(StorageBackend):
    """
    File-based storage backend implementation.
    
    This is the current implementation that uses AtomicJSONRepository
    for file-based storage. In the future, this can be swapped out
    for database backends while maintaining the same interface.
    """
    
    def __init__(self, data_manager):
        """
        Initialize with data manager.
        
        Args:
            data_manager: DataManager instance for file operations
        """
        self.data_manager = data_manager
        self._repositories = {}  # Cache of AtomicJSONRepository instances
    
    def _get_repository(self, key: str):
        """Get or create repository for a given key."""
        if key not in self._repositories:
            from .repository import AtomicJSONRepository
            
            # Map logical keys to actual file paths
            if key == "tracker_state":
                file_path = self.data_manager._state_repo.file_path
                auto_migrate = True
            elif key == "pushover_config":
                file_path = self.data_manager._pushover_config_repo.file_path
                auto_migrate = False
            elif key.startswith("scrape_"):
                # For scrape data, use the key as filename
                filename = key.replace("scrape_", "") + ".json"
                file_path = self.data_manager.get_data_path(filename)
                auto_migrate = False
            else:
                # Generic data file
                file_path = self.data_manager.get_data_path(f"{key}.json")
                auto_migrate = False
            
            self._repositories[key] = AtomicJSONRepository(
                str(file_path), 
                auto_migrate=auto_migrate
            )
        
        return self._repositories[key]
    
    def save(self, key: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Save data to file storage."""
        repo = self._get_repository(key)
        
        # Add metadata to data if provided
        if metadata:
            data = data.copy()
            if "metadata" not in data:
                data["metadata"] = {}
            data["metadata"].update(metadata)
        
        return repo.save(data)
    
    def load(self, key: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Load data from file storage."""
        repo = self._get_repository(key)
        return repo.load(default or {})
    
    def exists(self, key: str) -> bool:
        """Check if key exists in file storage."""
        repo = self._get_repository(key)
        return repo.exists()
    
    def delete(self, key: str) -> bool:
        """Delete file for given key."""
        repo = self._get_repository(key)
        try:
            if repo.exists():
                repo.file_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """List available keys (simplified implementation)."""
        # This is a simplified implementation for file storage
        # In a real database, this would be much more efficient
        import glob
        
        data_dir = self.data_manager.get_data_path("")
        json_files = glob.glob(f"{data_dir}/*.json")
        
        keys = []
        for file_path in json_files:
            filename = file_path.split("/")[-1]
            key = filename.replace(".json", "")
            
            # Convert special files to logical keys
            if key == "tracker_state":
                keys.append("tracker_state")
            elif key.startswith("duome_raw_"):
                keys.append(f"scrape_{key}")
            else:
                keys.append(key)
        
        if pattern:
            import fnmatch
            keys = [k for k in keys if fnmatch.fnmatch(k, pattern)]
        
        return keys
    
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a key."""
        try:
            data = self.load(key)
            return data.get("metadata")
        except Exception:
            return None


class DatabaseStorageBackend(StorageBackend):
    """
    Database storage backend (future implementation).
    
    This is a placeholder for future database implementation.
    When ready, this can be implemented with SQLite, PostgreSQL, etc.
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize database backend.
        
        Args:
            connection_string: Database connection string
        """
        self.connection_string = connection_string
        raise NotImplementedError("Database backend not yet implemented")
    
    def save(self, key: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> bool:
        raise NotImplementedError("Database backend not yet implemented")
    
    def load(self, key: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError("Database backend not yet implemented")
    
    def exists(self, key: str) -> bool:
        raise NotImplementedError("Database backend not yet implemented")
    
    def delete(self, key: str) -> bool:
        raise NotImplementedError("Database backend not yet implemented")
    
    def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        raise NotImplementedError("Database backend not yet implemented")
    
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("Database backend not yet implemented")


class StorageManager:
    """
    High-level storage manager that abstracts the storage backend.
    
    This allows switching between file storage and database storage
    without changing the application code.
    """
    
    def __init__(self, backend: StorageBackend):
        """
        Initialize with a storage backend.
        
        Args:
            backend: Storage backend implementation
        """
        self.backend = backend
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """Save tracker state."""
        return self.backend.save("tracker_state", state)
    
    def load_state(self, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Load tracker state."""
        return self.backend.load("tracker_state", default)
    
    def save_config(self, config_name: str, config: Dict[str, Any]) -> bool:
        """Save configuration."""
        return self.backend.save(f"config_{config_name}", config)
    
    def load_config(self, config_name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Load configuration."""
        return self.backend.load(f"config_{config_name}", default)
    
    def save_scrape_data(self, timestamp: str, data: Dict[str, Any]) -> bool:
        """Save scraped data with timestamp."""
        metadata = {
            "scrape_timestamp": timestamp,
            "saved_at": datetime.now().isoformat()
        }
        return self.backend.save(f"scrape_{timestamp}", data, metadata)
    
    def load_latest_scrape(self) -> Optional[Dict[str, Any]]:
        """Load the most recent scrape data."""
        scrape_keys = [k for k in self.backend.list_keys() if k.startswith("scrape_")]
        if not scrape_keys:
            return None
        
        # Sort by timestamp in key (assuming ISO format)
        latest_key = max(scrape_keys)
        return self.backend.load(latest_key)
    
    def cleanup_old_scrapes(self, keep_count: int = 10) -> int:
        """Clean up old scrape data, keeping only the most recent."""
        scrape_keys = [k for k in self.backend.list_keys() if k.startswith("scrape_")]
        
        if len(scrape_keys) <= keep_count:
            return 0
        
        # Sort by timestamp and delete oldest
        scrape_keys.sort()
        to_delete = scrape_keys[:-keep_count]
        
        deleted = 0
        for key in to_delete:
            if self.backend.delete(key):
                deleted += 1
        
        return deleted
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on storage layer."""
        return {
            "backend_type": type(self.backend).__name__,
            "tracker_state_exists": self.backend.exists("tracker_state"),
            "available_keys_count": len(self.backend.list_keys()),
            "timestamp": datetime.now().isoformat()
        }