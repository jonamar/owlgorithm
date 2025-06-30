#!/usr/bin/env python3
"""
Schema Migration Framework
Handles versioning and migration of JSON data structures.
"""

import logging
from typing import Dict, Any, List, Callable, Optional, Tuple
from abc import ABC, abstractmethod
from packaging import version


# Current schema version
CURRENT_SCHEMA_VERSION = "1.1"


class Migration(ABC):
    """Base class for data migrations."""
    
    @property
    @abstractmethod
    def from_version(self) -> str:
        """Source version for this migration."""
        pass
    
    @property
    @abstractmethod
    def to_version(self) -> str:
        """Target version for this migration."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of this migration."""
        pass
    
    @abstractmethod
    def migrate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform the migration on the data.
        
        Args:
            data: The data to migrate
            
        Returns:
            The migrated data
            
        Raises:
            MigrationError: If migration fails
        """
        pass
    
    def validate_before(self, data: Dict[str, Any]) -> bool:
        """
        Validate data before migration (optional).
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid for this migration
        """
        return True
    
    def validate_after(self, data: Dict[str, Any]) -> bool:
        """
        Validate data after migration (optional).
        
        Args:
            data: Migrated data to validate
            
        Returns:
            True if migrated data is valid
        """
        return True


class MigrationError(Exception):
    """Raised when a migration fails."""
    pass


class SchemaMigrator:
    """Manages schema versions and migrations."""
    
    def __init__(self):
        self.migrations: List[Migration] = []
        self.logger = logging.getLogger(__name__)
    
    def register_migration(self, migration: Migration) -> None:
        """Register a migration."""
        self.migrations.append(migration)
        # Sort migrations by from_version to ensure proper ordering
        self.migrations.sort(key=lambda m: version.parse(m.from_version))
    
    def get_current_version(self, data: Dict[str, Any]) -> str:
        """
        Get the current schema version from data.
        
        Args:
            data: Data to check
            
        Returns:
            Schema version string, defaults to "1.0" if not present
        """
        return data.get("schema_version", "1.0")
    
    def set_version(self, data: Dict[str, Any], target_version: str) -> Dict[str, Any]:
        """
        Set the schema version in data.
        
        Args:
            data: Data to update
            target_version: Version to set
            
        Returns:
            Updated data with version set
        """
        data = data.copy()
        data["schema_version"] = target_version
        return data
    
    def needs_migration(self, data: Dict[str, Any], target_version: str = None) -> bool:
        """
        Check if data needs migration.
        
        Args:
            data: Data to check
            target_version: Target version (defaults to current)
            
        Returns:
            True if migration is needed
        """
        if target_version is None:
            target_version = CURRENT_SCHEMA_VERSION
        
        current = self.get_current_version(data)
        return version.parse(current) < version.parse(target_version)
    
    def find_migration_path(self, from_version: str, to_version: str) -> List[Migration]:
        """
        Find sequence of migrations to get from one version to another.
        
        Args:
            from_version: Starting version
            to_version: Target version
            
        Returns:
            List of migrations to apply in order
            
        Raises:
            MigrationError: If no migration path exists
        """
        if version.parse(from_version) >= version.parse(to_version):
            return []
        
        path = []
        current_version = from_version
        
        while version.parse(current_version) < version.parse(to_version):
            # Find migration from current_version
            next_migration = None
            for migration in self.migrations:
                if migration.from_version == current_version:
                    if (next_migration is None or 
                        version.parse(migration.to_version) <= version.parse(to_version)):
                        next_migration = migration
            
            if next_migration is None:
                raise MigrationError(
                    f"No migration found from version {current_version} "
                    f"towards {to_version}"
                )
            
            path.append(next_migration)
            current_version = next_migration.to_version
        
        return path
    
    def migrate(self, data: Dict[str, Any], target_version: str = None) -> Tuple[Dict[str, Any], List[str]]:
        """
        Migrate data to target version.
        
        Args:
            data: Data to migrate
            target_version: Target version (defaults to current)
            
        Returns:
            Tuple of (migrated_data, list_of_applied_migrations)
            
        Raises:
            MigrationError: If migration fails
        """
        if target_version is None:
            target_version = CURRENT_SCHEMA_VERSION
        
        current_version = self.get_current_version(data)
        
        if not self.needs_migration(data, target_version):
            return data, []
        
        self.logger.info(f"Migrating data from version {current_version} to {target_version}")
        
        # Find migration path
        migrations = self.find_migration_path(current_version, target_version)
        
        migrated_data = data.copy()
        applied_migrations = []
        
        for migration in migrations:
            self.logger.info(f"Applying migration: {migration.description}")
            
            # Validate before migration
            if not migration.validate_before(migrated_data):
                raise MigrationError(
                    f"Pre-migration validation failed for {migration.description}"
                )
            
            try:
                # Apply migration
                migrated_data = migration.migrate(migrated_data)
                
                # Update version
                migrated_data = self.set_version(migrated_data, migration.to_version)
                
                # Validate after migration
                if not migration.validate_after(migrated_data):
                    raise MigrationError(
                        f"Post-migration validation failed for {migration.description}"
                    )
                
                applied_migrations.append(migration.description)
                self.logger.info(f"Successfully applied migration to version {migration.to_version}")
                
            except Exception as e:
                raise MigrationError(
                    f"Migration failed: {migration.description}. Error: {str(e)}"
                ) from e
        
        return migrated_data, applied_migrations
    
    def get_available_migrations(self) -> List[Dict[str, str]]:
        """
        Get list of available migrations.
        
        Returns:
            List of migration info dictionaries
        """
        return [
            {
                "from_version": m.from_version,
                "to_version": m.to_version,
                "description": m.description
            }
            for m in self.migrations
        ]


# Global migrator instance
migrator = SchemaMigrator()


# Import and register migrations (must be after migrator instance creation)
try:
    from . import registry  # This triggers migration registration
except ImportError:
    pass  # Migrations not available


def ensure_schema_version(data: Dict[str, Any], target_version: str = None) -> Tuple[Dict[str, Any], bool]:
    """
    Ensure data is at the target schema version, migrating if necessary.
    
    Args:
        data: Data to check/migrate
        target_version: Target version (defaults to current)
        
    Returns:
        Tuple of (data, was_migrated)
    """
    if target_version is None:
        target_version = CURRENT_SCHEMA_VERSION
    
    if not migrator.needs_migration(data, target_version):
        # Ensure version is explicitly set even if no migration needed
        if "schema_version" not in data:
            data = migrator.set_version(data, target_version)
            return data, True
        return data, False
    
    migrated_data, applied_migrations = migrator.migrate(data, target_version)
    return migrated_data, True