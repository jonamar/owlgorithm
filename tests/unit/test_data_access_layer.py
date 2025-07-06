#!/usr/bin/env python3
"""
Tests for Data Access Layer
Tests DataManager, StorageBackend interfaces, and storage abstraction.
"""

import pytest
import tempfile
import json
import os
import time
from pathlib import Path
from unittest.mock import patch, Mock

from src.data.data_manager import DataManager, DataAccessError
from src.data.storage_interface import FileStorageBackend, StorageManager


class TestDataManager:
    """Test the centralized data manager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def data_manager(self, temp_dir):
        """Create data manager with temporary paths."""
        # Mock config to use temp directory
        with patch('src.data.data_manager.cfg') as mock_cfg:
            mock_cfg.DATA_DIR = str(temp_dir / "data")
            mock_cfg.LOG_DIR = str(temp_dir / "logs")
            mock_cfg.CONFIG_DIR = str(temp_dir / "config")
            mock_cfg.STATE_FILE = str(temp_dir / "tracker_state.json")
            mock_cfg.NOTIFIER_CONFIG_FILE = str(temp_dir / "config" / "pushover_config.json")
            mock_cfg.MARKDOWN_FILE = str(temp_dir / "progress-dashboard.md")
            mock_cfg.USERNAME = "testuser"
            
            yield DataManager()
    
    def test_directory_creation(self, data_manager):
        """Test that required directories are created."""
        # DataManager should create directories on initialization
        assert os.path.exists(data_manager._state_repo.file_path.parent)
        assert os.path.exists(data_manager._pushover_config_repo.file_path.parent)
    
    def test_tracker_state_operations(self, data_manager):
        """Test tracker state save/load operations."""
        test_state = {
            "total_lessons_completed": 150,
            "daily_lessons_completed": 5,
            "last_scrape_date": "2025-06-29"
        }
        
        # Save state
        data_manager.save_tracker_state(test_state)
        
        # Load state
        loaded_state = data_manager.load_tracker_state()
        
        # Should have the data plus schema version
        assert loaded_state["total_lessons_completed"] == 150
        assert loaded_state["daily_lessons_completed"] == 5
        assert "schema_version" in loaded_state
    
    def test_tracker_state_default_handling(self, data_manager):
        """Test tracker state loading with defaults."""
        default_state = {"initialized": True}
        
        # Load non-existent state with default
        loaded_state = data_manager.load_tracker_state(default_state)
        
        assert loaded_state["initialized"] is True
        assert "schema_version" in loaded_state
    
    def test_tracker_state_error_handling(self, data_manager):
        """Test error handling in state operations."""
        # Mock repository to raise exception
        with patch.object(data_manager._state_repo, 'save', side_effect=Exception("Mock error")):
            with pytest.raises(DataAccessError) as exc_info:
                data_manager.save_tracker_state({"test": "data"})
            assert "Failed to save tracker state" in str(exc_info.value)
    
    def test_pushover_config_operations(self, data_manager):
        """Test Pushover configuration save/load."""
        config = {
            "user_key": "test_user_key",
            "api_token": "test_api_token"
        }
        
        # Save config
        data_manager.save_pushover_config(config)
        
        # Load config
        loaded_config = data_manager.load_pushover_config()
        
        assert loaded_config["user_key"] == "test_user_key"
        assert loaded_config["api_token"] == "test_api_token"
    
    def test_pushover_config_missing_error(self, data_manager):
        """Test error when Pushover config is missing."""
        with pytest.raises(DataAccessError) as exc_info:
            data_manager.load_pushover_config()
        assert "Pushover config file is empty or missing" in str(exc_info.value)
    
    def test_scrape_data_operations(self, data_manager, temp_dir):
        """Test scrape data save/load/list operations."""
        scrape_data = {
            "sessions": [{"id": 1, "type": "lesson"}],
            "scraped_at": "2025-06-29T12:00:00"
        }
        
        # Save scrape data
        saved_path = data_manager.save_scrape_data(scrape_data)
        assert saved_path is not None
        assert "duome_raw_testuser_" in saved_path
        
        # Load scrape data
        loaded_data = data_manager.load_scrape_data(saved_path)
        assert loaded_data["sessions"][0]["id"] == 1
        assert loaded_data["scraped_at"] == "2025-06-29T12:00:00"
        
        # Find latest scrape file
        latest_file = data_manager.find_latest_scrape_file()
        assert latest_file == saved_path
        
        # List scrape files
        files = data_manager.list_scrape_files()
        assert len(files) == 1
        assert files[0] == saved_path
    
    def test_scrape_data_cleanup(self, data_manager):
        """Test cleanup of old scrape files."""
        # Create multiple scrape files
        created_files = []
        for i in range(15):
            scrape_data = {"session_id": i, "timestamp": f"2025-06-29T{i:02d}:00:00"}
            created_path = data_manager.save_scrape_data(scrape_data)
            created_files.append(created_path)
            time.sleep(0.01)  # Ensure different creation times
        
        # Should have 15 main files (ignoring backup files)
        files_before = data_manager.list_scrape_files()
        main_files_before = [f for f in files_before if "backup" not in f]
        assert len(main_files_before) == 15
        
        # Cleanup, keeping only 5
        deleted_count = data_manager.cleanup_old_scrape_files(keep_count=5)
        assert deleted_count == 10
        
        # Should have 5 main files remaining
        files_after = data_manager.list_scrape_files()
        main_files_after = [f for f in files_after if "backup" not in f]
        assert len(main_files_after) == 5
    
    def test_markdown_operations(self, data_manager):
        """Test markdown file operations."""
        markdown_content = """# Test Markdown
        
This is test content.

- Item 1
- Item 2
"""
        
        # Save markdown
        data_manager.save_markdown_content(markdown_content)
        
        # Load markdown
        loaded_content = data_manager.load_markdown_content()
        assert loaded_content == markdown_content
    
    def test_markdown_backup_creation(self, data_manager):
        """Test that markdown backup is created."""
        # Create initial markdown file
        initial_content = "Initial content"
        data_manager.save_markdown_content(initial_content)
        
        # Update with new content
        new_content = "Updated content"
        data_manager.save_markdown_content(new_content)
        
        # Check backup was created
        backup_path = f"{data_manager._pushover_config_repo.file_path.parent.parent / 'progress-dashboard.md'}.backup"
        with patch('src.data.data_manager.cfg.MARKDOWN_FILE', str(data_manager._pushover_config_repo.file_path.parent.parent / 'progress-dashboard.md')):
            assert os.path.exists(backup_path)
    
    def test_path_management(self, data_manager):
        """Test path utility methods."""
        data_path = data_manager.get_data_path("test.json")
        log_path = data_manager.get_log_path("test.log")
        config_path = data_manager.get_config_path("test.conf")
        
        assert "data" in data_path
        assert "test.json" in data_path
        assert "logs" in log_path
        assert "test.log" in log_path
        assert "config" in config_path
        assert "test.conf" in config_path
    
    def test_health_check(self, data_manager):
        """Test health check functionality."""
        # Create some test data
        data_manager.save_tracker_state({"test": "data"})
        data_manager.save_scrape_data({"test": "scrape"})
        
        health = data_manager.health_check()
        
        assert health["status"] in ["healthy", "degraded"]
        assert "checks" in health
        assert "timestamp" in health
        
        # Check specific health items
        assert "tracker_state" in health["checks"]
        assert "latest_scrape" in health["checks"]
        assert health["checks"]["tracker_state"]["exists"] is True


class TestStorageInterface:
    """Test the storage interface abstraction."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def mock_data_manager(self, temp_dir):
        """Create mock data manager."""
        mock_dm = Mock()
        mock_dm.get_data_path.side_effect = lambda x: str(temp_dir / x)
        mock_dm._state_repo = Mock()
        mock_dm._state_repo.file_path = temp_dir / "tracker_state.json"
        mock_dm._pushover_config_repo = Mock()
        mock_dm._pushover_config_repo.file_path = temp_dir / "pushover_config.json"
        return mock_dm
    
    def test_file_storage_backend(self, mock_data_manager):
        """Test file storage backend implementation."""
        backend = FileStorageBackend(mock_data_manager)
        
        # Test save and load
        test_data = {"key": "value", "number": 42}
        assert backend.save("test_key", test_data) is True
        
        loaded_data = backend.load("test_key")
        assert loaded_data["key"] == "value"
        assert loaded_data["number"] == 42
        
        # Test exists
        assert backend.exists("test_key") is True
        assert backend.exists("nonexistent_key") is False
    
    def test_file_storage_with_metadata(self, mock_data_manager):
        """Test file storage with metadata."""
        backend = FileStorageBackend(mock_data_manager)
        
        test_data = {"content": "test"}
        metadata = {"created_by": "test", "version": "1.0"}
        
        backend.save("test_with_meta", test_data, metadata)
        
        loaded_data = backend.load("test_with_meta")
        assert loaded_data["content"] == "test"
        assert loaded_data["metadata"]["created_by"] == "test"
        assert loaded_data["metadata"]["version"] == "1.0"
    
    def test_storage_manager(self, mock_data_manager):
        """Test high-level storage manager."""
        backend = FileStorageBackend(mock_data_manager)
        storage = StorageManager(backend)
        
        # Test state operations
        state = {"lessons": 100, "date": "2025-06-29"}
        assert storage.save_state(state) is True
        
        loaded_state = storage.load_state()
        assert loaded_state["lessons"] == 100
        
        # Test config operations
        config = {"api_key": "test_key"}
        assert storage.save_config("pushover", config) is True
        
        loaded_config = storage.load_config("pushover")
        assert loaded_config["api_key"] == "test_key"
        
        # Test scrape operations
        scrape_data = {"sessions": [1, 2, 3]}
        timestamp = "20250629_120000"
        assert storage.save_scrape_data(timestamp, scrape_data) is True
    
    def test_storage_manager_health_check(self, mock_data_manager):
        """Test storage manager health check."""
        backend = FileStorageBackend(mock_data_manager)
        storage = StorageManager(backend)
        
        health = storage.health_check()
        
        assert "backend_type" in health
        assert "tracker_state_exists" in health
        assert "timestamp" in health
        assert health["backend_type"] == "FileStorageBackend"


class TestIntegration:
    """Test integration between data manager and storage interfaces."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_data_manager_storage_integration(self, temp_dir):
        """Test that DataManager can work with storage interfaces."""
        # Create DataManager with temp paths
        with patch('src.data.data_manager.cfg') as mock_cfg:
            mock_cfg.DATA_DIR = str(temp_dir / "data")
            mock_cfg.LOG_DIR = str(temp_dir / "logs")
            mock_cfg.CONFIG_DIR = str(temp_dir / "config")
            mock_cfg.STATE_FILE = str(temp_dir / "tracker_state.json")
            mock_cfg.NOTIFIER_CONFIG_FILE = str(temp_dir / "config" / "pushover_config.json")
            mock_cfg.MARKDOWN_FILE = str(temp_dir / "progress-dashboard.md")
            mock_cfg.USERNAME = "testuser"
            
            data_manager = DataManager()
            
            # Create storage manager using data manager
            backend = FileStorageBackend(data_manager)
            storage = StorageManager(backend)
            
            # Test that both interfaces work together
            test_state = {"total_lessons": 200, "date": "2025-06-29"}
            
            # Save via DataManager
            data_manager.save_tracker_state(test_state)
            
            # Load via StorageManager
            loaded_via_storage = storage.load_state()
            assert loaded_via_storage["total_lessons"] == 200
            
            # Save via StorageManager
            updated_state = {"total_lessons": 250, "date": "2025-06-30"}
            storage.save_state(updated_state)
            
            # Load via DataManager
            loaded_via_dm = data_manager.load_tracker_state()
            assert loaded_via_dm["total_lessons"] == 250


if __name__ == "__main__":
    pytest.main([__file__])