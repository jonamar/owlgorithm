#!/usr/bin/env python3
"""
Atomic JSON Repository
Provides safe, atomic operations for JSON file handling with corruption recovery.
"""

import json
import os
import fcntl
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from contextlib import contextmanager

# Import migration framework
try:
    from .migrations.migrator import ensure_schema_version, CURRENT_SCHEMA_VERSION
    MIGRATIONS_AVAILABLE = True
except ImportError:
    MIGRATIONS_AVAILABLE = False


class AtomicJSONRepository:
    """Atomic JSON file operations with corruption recovery and schema versioning."""
    
    def __init__(self, file_path: str, backup_dir: Optional[str] = None, 
                 auto_migrate: bool = True, target_version: Optional[str] = None):
        """
        Initialize atomic JSON repository.
        
        Args:
            file_path: Path to the JSON file
            backup_dir: Directory for backups (defaults to same dir as file)
            auto_migrate: Whether to automatically migrate data to latest version
            target_version: Target schema version (defaults to current)
        """
        self.file_path = Path(file_path)
        self.backup_dir = Path(backup_dir) if backup_dir else self.file_path.parent
        self.backup_dir.mkdir(exist_ok=True, parents=True)
        self.auto_migrate = auto_migrate and MIGRATIONS_AVAILABLE
        self.target_version = target_version if target_version else (
            CURRENT_SCHEMA_VERSION if MIGRATIONS_AVAILABLE else None
        )
        
        # Ensure parent directory exists
        self.file_path.parent.mkdir(exist_ok=True, parents=True)
    
    @contextmanager
    def _file_lock(self, file_path: Path, mode: str = 'r'):
        """Context manager for file locking."""
        with open(file_path, mode) as f:
            try:
                # Acquire exclusive lock for writes, shared for reads
                lock_type = fcntl.LOCK_EX if 'w' in mode else fcntl.LOCK_SH
                fcntl.flock(f.fileno(), lock_type)
                yield f
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def _create_backup(self) -> Optional[Path]:
        """Create timestamped backup of current file."""
        if not self.file_path.exists():
            return None
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"{self.file_path.stem}_backup_{timestamp}.json"
        
        try:
            shutil.copy2(self.file_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"⚠️ Failed to create backup: {e}")
            return None
    
    def _validate_json_data(self, data: Any) -> bool:
        """Validate that data can be serialized to JSON."""
        try:
            json.dumps(data)
            return True
        except (TypeError, ValueError):
            return False
    
    def load(self, default_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Atomically load JSON data with corruption recovery and auto-migration.
        
        Args:
            default_data: Default data to return if file doesn't exist
            
        Returns:
            Loaded JSON data or default_data, migrated to current version if needed
        """
        if not self.file_path.exists():
            default = default_data or {}
            # Add schema version to new data if versioning is available
            if self.auto_migrate and self.target_version:
                default = self._ensure_schema_version(default)
            return default
        
        try:
            with self._file_lock(self.file_path, 'r') as f:
                data = json.load(f)
                
                # Validate loaded data
                if not isinstance(data, dict):
                    raise ValueError("JSON data must be a dictionary")
                
                # Handle schema migration if enabled
                if self.auto_migrate and self.target_version:
                    original_version = data.get("schema_version", "1.0")
                    data = self._ensure_schema_version(data)
                    current_version = data.get("schema_version", "1.0")
                    if original_version != current_version:
                        print(f"📝 Data migrated to schema version {self.target_version}")
                        # Save migrated data back to file
                        self.save(data, create_backup=True)
                
                return data
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ JSON corruption detected in {self.file_path}: {e}")
            
            # Try to recover from backup
            backup_data = self._recover_from_backup()
            if backup_data is not None:
                print(f"✅ Recovered data from backup")
                # Apply migration to recovered data if needed
                if self.auto_migrate and self.target_version:
                    original_version = backup_data.get("schema_version", "1.0")
                    backup_data = self._ensure_schema_version(backup_data)
                    current_version = backup_data.get("schema_version", "1.0")
                    if original_version != current_version:
                        print(f"📝 Recovered data migrated to schema version {self.target_version}")
                return backup_data
                
            print(f"❌ No valid backup found, using default data")
            default = default_data or {}
            if self.auto_migrate and self.target_version:
                default = self._ensure_schema_version(default)
            return default
    
    def save(self, data: Dict[str, Any], create_backup: bool = True) -> bool:
        """
        Atomically save JSON data with backup and validation.
        
        Args:
            data: Data to save
            create_backup: Whether to create backup before saving
            
        Returns:
            True if save was successful, False otherwise
        """
        # Validate data before attempting save
        if not self._validate_json_data(data):
            print(f"❌ Invalid data cannot be serialized to JSON")
            return False
        
        # Create backup before modifying
        backup_path = None
        if create_backup and self.file_path.exists():
            backup_path = self._create_backup()
        
        # Use atomic write: write to temp file, then rename
        temp_fd = None
        temp_path = None
        
        try:
            # Create temporary file in same directory for atomic rename
            temp_fd, temp_path = tempfile.mkstemp(
                suffix='.tmp', 
                prefix=f'{self.file_path.name}_',
                dir=self.file_path.parent
            )
            temp_path = Path(temp_path)
            
            # Write data to temporary file
            with os.fdopen(temp_fd, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            temp_fd = None  # File is now closed
            
            # Atomic rename (works on same filesystem)
            temp_path.replace(self.file_path)
            
            # Cleanup old backups (keep last 5)
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save {self.file_path}: {e}")
            
            # Cleanup temporary file
            if temp_fd is not None:
                try:
                    os.close(temp_fd)
                except OSError:
                    pass  # File descriptor may already be closed
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass  # May fail if file doesn't exist
            
            # Restore from backup if available
            if backup_path and backup_path.exists():
                try:
                    shutil.copy2(backup_path, self.file_path)
                    print(f"✅ Restored from backup after failed save")
                except Exception as restore_error:
                    print(f"❌ Failed to restore backup: {restore_error}")
            
            return False
    
    def _recover_from_backup(self) -> Optional[Dict[str, Any]]:
        """Try to recover data from most recent backup."""
        backup_pattern = f"{self.file_path.stem}_backup_*.json"
        backups = list(self.backup_dir.glob(backup_pattern))
        
        if not backups:
            return None
        
        # Sort by modification time, newest first
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        
        for backup_path in backups:
            try:
                with open(backup_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except (json.JSONDecodeError, OSError):
                continue
        
        return None
    
    def _cleanup_old_backups(self, keep_count: int = 5):
        """Remove old backup files, keeping only the most recent ones."""
        backup_pattern = f"{self.file_path.stem}_backup_*.json"
        backups = list(self.backup_dir.glob(backup_pattern))
        
        if len(backups) <= keep_count:
            return
        
        # Sort by modification time, newest first
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        
        # Remove old backups
        for old_backup in backups[keep_count:]:
            try:
                old_backup.unlink()
            except OSError:
                pass  # Ignore errors removing old backups
    
    def exists(self) -> bool:
        """Check if the JSON file exists."""
        return self.file_path.exists()
    
    def get_last_modified(self) -> Optional[datetime]:
        """Get last modification time of the JSON file."""
        if not self.file_path.exists():
            return None
        return datetime.fromtimestamp(self.file_path.stat().st_mtime)
    
    def _ensure_schema_version(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure data has the correct schema version, migrating if necessary.
        
        Args:
            data: Data to check/migrate
            
        Returns:
            Data with correct schema version
        """
        if not MIGRATIONS_AVAILABLE or not self.target_version:
            # Add schema version to data if not present, but don't migrate
            if "schema_version" not in data:
                data = data.copy()
                data["schema_version"] = self.target_version or "1.0"
            return data
        
        migrated_data, was_migrated = ensure_schema_version(data, self.target_version)
        return migrated_data


# Convenience functions for common operations
def load_json_safe(file_path: str, default_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load JSON data safely with automatic corruption recovery."""
    repo = AtomicJSONRepository(file_path, auto_migrate=False)
    return repo.load(default_data)


def save_json_safe(file_path: str, data: Dict[str, Any], create_backup: bool = True) -> bool:
    """Save JSON data safely with atomic operations."""
    repo = AtomicJSONRepository(file_path, auto_migrate=False)
    return repo.save(data, create_backup)