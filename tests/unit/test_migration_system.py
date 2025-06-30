#!/usr/bin/env python3
"""
Tests for the schema migration system.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
from datetime import datetime

from src.data.repository import AtomicJSONRepository
from src.data.migrations.migrator import SchemaMigrator, ensure_schema_version, CURRENT_SCHEMA_VERSION
from src.data.migrations.v1_0_to_v1_1 import V1_0_to_V1_1_Migration


class TestMigrationSystem:
    """Test the schema migration framework."""
    
    def test_v1_0_to_v1_1_migration(self):
        """Test the V1.0 to V1.1 migration."""
        migration = V1_0_to_V1_1_Migration()
        
        # Sample V1.0 data (current tracker_state format)
        v1_0_data = {
            "processed_units": ["Requests", "Grooming"],
            "total_completed_units": 86,
            "total_lessons_completed": 172,
            "last_scrape_date": "2025-06-29",
            "last_update_timestamp": "2025-06-16T20:12:31.076801",
            "daily_lessons_completed": 15,
            "daily_goal_lessons": 15,
            "last_daily_reset": "2025-06-29"
        }
        
        # Test validation
        assert migration.validate_before(v1_0_data)
        
        # Perform migration
        migrated_data = migration.migrate(v1_0_data)
        
        # Test validation after migration
        assert migration.validate_after(migrated_data)
        
        # Verify migration changes
        assert "metadata" in migrated_data
        assert "created_at" in migrated_data["metadata"]
        assert "migration_history" in migrated_data["metadata"]
        
        # Check that date fields are updated to ISO format
        assert migrated_data["last_scrape_date"] == "2025-06-29T00:00:00"
        assert migrated_data["last_daily_reset"] == "2025-06-29T00:00:00"
        
        # Verify created_at uses existing timestamp
        assert migrated_data["metadata"]["created_at"] == "2025-06-16T20:12:31.076801"
        
        # Verify original data is preserved
        assert migrated_data["total_lessons_completed"] == 172
        assert migrated_data["daily_lessons_completed"] == 15
    
    def test_schema_migrator_functionality(self):
        """Test the SchemaMigrator class."""
        migrator = SchemaMigrator()
        migration = V1_0_to_V1_1_Migration()
        migrator.register_migration(migration)
        
        # Test version detection
        data_without_version = {"some": "data"}
        assert migrator.get_current_version(data_without_version) == "1.0"
        
        data_with_version = {"schema_version": "1.1", "some": "data"}
        assert migrator.get_current_version(data_with_version) == "1.1"
        
        # Test needs_migration
        assert migrator.needs_migration(data_without_version, "1.1")
        assert not migrator.needs_migration(data_with_version, "1.1")
        
        # Test migration path finding
        path = migrator.find_migration_path("1.0", "1.1")
        assert len(path) == 1
        assert path[0].from_version == "1.0"
        assert path[0].to_version == "1.1"
    
    def test_ensure_schema_version_function(self):
        """Test the ensure_schema_version convenience function."""
        v1_0_data = {
            "total_lessons_completed": 100,
            "last_scrape_date": "2025-06-29"
        }
        
        # Test migration
        migrated_data, was_migrated = ensure_schema_version(v1_0_data, "1.1")
        
        assert was_migrated
        assert migrated_data["schema_version"] == "1.1"
        assert "metadata" in migrated_data
        
        # Test no migration needed
        already_migrated, was_migrated_again = ensure_schema_version(migrated_data, "1.1")
        assert not was_migrated_again
        assert already_migrated["schema_version"] == "1.1"


class TestAtomicRepositoryWithVersioning:
    """Test AtomicJSONRepository with schema versioning."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_repository_with_versioning_enabled(self, temp_dir):
        """Test repository with auto-migration enabled."""
        file_path = temp_dir / "test_data.json"
        
        # Create repository with versioning enabled
        repo = AtomicJSONRepository(str(file_path), auto_migrate=True, target_version="1.1")
        
        # Test loading non-existent file with versioning
        data = repo.load({"default": "value"})
        assert data["schema_version"] == "1.1"
        assert "default" in data
    
    def test_repository_migration_on_load(self, temp_dir):
        """Test that repository migrates data on load."""
        file_path = temp_dir / "tracker_state.json"
        
        # Create a V1.0 format file manually
        v1_0_data = {
            "total_lessons_completed": 172,
            "last_scrape_date": "2025-06-29",
            "last_update_timestamp": "2025-06-16T20:12:31.076801",
            "daily_lessons_completed": 15
        }
        
        with open(file_path, 'w') as f:
            json.dump(v1_0_data, f, indent=2)
        
        # Load with versioning enabled
        repo = AtomicJSONRepository(str(file_path), auto_migrate=True, target_version="1.1")
        loaded_data = repo.load()
        
        # Verify migration occurred
        assert loaded_data["schema_version"] == "1.1"
        assert "metadata" in loaded_data
        assert "created_at" in loaded_data["metadata"]
        assert loaded_data["last_scrape_date"] == "2025-06-29T00:00:00"
        
        # Verify file was updated with migrated data
        with open(file_path, 'r') as f:
            saved_data = json.load(f)
        assert saved_data["schema_version"] == "1.1"
        assert "metadata" in saved_data
    
    def test_repository_without_versioning(self, temp_dir):
        """Test repository with versioning disabled."""
        file_path = temp_dir / "test_data.json"
        
        # Create repository with versioning disabled
        repo = AtomicJSONRepository(str(file_path), auto_migrate=False)
        
        # Test loading and saving without versioning
        data = {"some": "data"}
        assert repo.save(data)
        
        loaded_data = repo.load()
        assert loaded_data == data
        assert "schema_version" not in loaded_data


if __name__ == "__main__":
    pytest.main([__file__])