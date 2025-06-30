#!/usr/bin/env python3
"""
Tests for AtomicJSONRepository
Tests atomic operations, corruption recovery, file locking, and backup functionality.
"""

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from src.data.repository import AtomicJSONRepository, load_json_safe, save_json_safe


class TestAtomicJSONRepository:
    """Test atomic JSON repository operations."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def repo(self, temp_dir):
        """Create repository instance with temporary file."""
        file_path = temp_dir / "test_data.json"
        # Disable auto-migration for core repository tests to maintain predictable behavior
        return AtomicJSONRepository(str(file_path), auto_migrate=False)
    
    def test_save_and_load_basic(self, repo):
        """Test basic save and load operations."""
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        
        # Save data
        assert repo.save(test_data) is True
        assert repo.exists() is True
        
        # Load data
        loaded_data = repo.load()
        assert loaded_data == test_data
    
    def test_load_nonexistent_file(self, repo):
        """Test loading from nonexistent file returns default."""
        default_data = {"default": True}
        
        # File doesn't exist
        assert repo.exists() is False
        
        # Load with default
        loaded_data = repo.load(default_data)
        assert loaded_data == default_data
        
        # Load without default
        loaded_data = repo.load()
        assert loaded_data == {}
    
    def test_backup_creation(self, repo):
        """Test that backups are created before saves."""
        initial_data = {"version": 1}
        updated_data = {"version": 2}
        
        # Save initial data
        assert repo.save(initial_data) is True
        
        # Save updated data (should create backup)
        assert repo.save(updated_data) is True
        
        # Check backup was created
        backup_pattern = f"{repo.file_path.stem}_backup_*.json"
        backups = list(repo.backup_dir.glob(backup_pattern))
        assert len(backups) >= 1
        
        # Verify backup contains initial data
        with open(backups[0], 'r') as f:
            backup_data = json.load(f)
        assert backup_data == initial_data
        
        # Verify current file has updated data
        current_data = repo.load()
        assert current_data == updated_data
    
    def test_corruption_recovery(self, repo):
        """Test recovery from corrupted JSON files."""
        valid_data = {"status": "good"}
        
        # Save valid data first (creates backup)
        assert repo.save(valid_data) is True
        
        # Save again to ensure backup is created (first save doesn't create backup)
        time.sleep(0.01)  # Ensure different timestamp
        updated_data = {"status": "updated"}
        assert repo.save(updated_data) is True
        
        # Corrupt the main file
        with open(repo.file_path, 'w') as f:
            f.write("invalid json {")
        
        # Load should recover from backup (should be the original valid_data)
        loaded_data = repo.load({"default": True})
        assert loaded_data == valid_data
    
    def test_atomic_write_failure_recovery(self, repo):
        """Test recovery when atomic write fails."""
        good_data = {"status": "good"}
        
        # Save initial good data
        assert repo.save(good_data) is True
        
        # Mock tempfile creation to fail during save
        with patch('tempfile.mkstemp', side_effect=OSError("Disk full")):
            bad_data = {"status": "bad"}
            result = repo.save(bad_data)
            assert result is False
        
        # Original data should be preserved
        loaded_data = repo.load()
        assert loaded_data == good_data
    
    def test_invalid_data_validation(self, repo):
        """Test that invalid data is rejected."""
        # Non-serializable data
        invalid_data = {"function": lambda x: x}
        
        result = repo.save(invalid_data)
        assert result is False
        
        # File should not be created/modified
        assert repo.exists() is False
    
    def test_concurrent_access(self, repo):
        """Test concurrent reads and writes with file locking."""
        results = []
        errors = []
        
        def write_worker(worker_id):
            try:
                data = {"worker": worker_id, "timestamp": time.time()}
                result = repo.save(data)
                results.append((worker_id, result))
            except Exception as e:
                errors.append((worker_id, e))
        
        def read_worker(worker_id):
            try:
                time.sleep(0.1)  # Let writers start first
                data = repo.load()
                results.append((f"reader_{worker_id}", data.get("worker", "unknown")))
            except Exception as e:
                errors.append((f"reader_{worker_id}", e))
        
        # Start concurrent workers
        threads = []
        for i in range(3):
            t1 = threading.Thread(target=write_worker, args=(i,))
            t2 = threading.Thread(target=read_worker, args=(i,))
            threads.extend([t1, t2])
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Check results
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        assert len(results) == 6  # 3 writers + 3 readers
        
        # Verify final state is consistent
        final_data = repo.load()
        assert "worker" in final_data
    
    def test_backup_cleanup(self, repo):
        """Test cleanup of old backup files."""
        # Create multiple saves to generate backups
        for i in range(10):
            data = {"version": i}
            repo.save(data)
            time.sleep(0.01)  # Ensure different timestamps
        
        # Check that old backups were cleaned up (should keep only 5)
        backup_pattern = f"{repo.file_path.stem}_backup_*.json"
        backups = list(repo.backup_dir.glob(backup_pattern))
        assert len(backups) <= 5
    
    def test_get_last_modified(self, repo):
        """Test getting last modification time."""
        # No file exists
        assert repo.get_last_modified() is None
        
        # Save data
        repo.save({"test": True})
        
        # Should have modification time
        mod_time = repo.get_last_modified()
        assert mod_time is not None
        
        # Modification time should be recent
        time_diff = (mod_time.timestamp() - time.time())
        assert abs(time_diff) < 5  # Within 5 seconds


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary file path."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass
    
    def test_load_json_safe(self, temp_file):
        """Test safe JSON loading convenience function."""
        test_data = {"safe": True, "test": "data"}
        
        # Save data using standard json
        with open(temp_file, 'w') as f:
            json.dump(test_data, f)
        
        # Load using safe function
        loaded_data = load_json_safe(temp_file)
        assert loaded_data == test_data
        
        # Test with default data for nonexistent file
        nonexistent = temp_file + "_missing"
        default_data = {"default": True}
        loaded_data = load_json_safe(nonexistent, default_data)
        assert loaded_data == default_data
    
    def test_save_json_safe(self, temp_file):
        """Test safe JSON saving convenience function."""
        test_data = {"safe": True, "save": "test"}
        
        # Save using safe function
        result = save_json_safe(temp_file, test_data)
        assert result is True
        
        # Verify data was saved correctly
        with open(temp_file, 'r') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data
    
    def test_convenience_functions_integration(self, temp_file):
        """Test integration between save and load convenience functions."""
        original_data = {"integration": "test", "numbers": [1, 2, 3]}
        
        # Save and load using convenience functions
        assert save_json_safe(temp_file, original_data) is True
        loaded_data = load_json_safe(temp_file)
        
        assert loaded_data == original_data


class TestRealWorldScenarios:
    """Test realistic scenarios from daily tracker usage."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def state_repo(self, temp_dir):
        """Create repository for tracker state file."""
        state_file = temp_dir / "tracker_state.json"
        # Disable auto-migration for core repository tests to maintain predictable behavior
        return AtomicJSONRepository(str(state_file), auto_migrate=False)
    
    def test_daily_tracker_state_operations(self, state_repo):
        """Test typical daily tracker state operations."""
        # Initial state (like first run)
        initial_state = {
            "total_lessons_completed": 150,
            "daily_lessons_today": 5,
            "last_scrape_date": "2025-06-29",
            "completed_units": ["Unit 1", "Unit 2"]
        }
        
        # Save initial state
        assert state_repo.save(initial_state) is True
        
        # Load and update (like during daily run)
        current_state = state_repo.load()
        current_state["total_lessons_completed"] = 155
        current_state["daily_lessons_today"] = 10
        current_state["last_scrape_date"] = "2025-06-30"
        
        # Save updated state
        assert state_repo.save(current_state) is True
        
        # Verify state persisted correctly
        final_state = state_repo.load()
        assert final_state["total_lessons_completed"] == 155
        assert final_state["daily_lessons_today"] == 10
        assert final_state["last_scrape_date"] == "2025-06-30"
        assert final_state["completed_units"] == ["Unit 1", "Unit 2"]
    
    def test_power_failure_simulation(self, state_repo):
        """Test behavior during simulated power failure."""
        good_state = {
            "total_lessons_completed": 100,
            "status": "good"
        }
        
        # Save good state
        assert state_repo.save(good_state) is True
        
        # Simulate power failure during temp file creation
        with patch('tempfile.mkstemp', side_effect=OSError("Power failure")):
            bad_state = {"status": "bad"}
            result = state_repo.save(bad_state)
            assert result is False
        
        # Original state should be preserved
        current_state = state_repo.load()
        assert current_state == good_state
    
    def test_disk_space_exhaustion(self, state_repo):
        """Test behavior when disk space is exhausted."""
        good_state = {"disk_space": "available"}
        
        # Save initial state
        assert state_repo.save(good_state) is True
        
        # Simulate disk space exhaustion during temp file creation
        with patch('tempfile.mkstemp', side_effect=OSError("No space left on device")):
            result = state_repo.save({"disk_space": "exhausted"})
            assert result is False
        
        # Should still be able to read original state
        current_state = state_repo.load()
        assert current_state == good_state