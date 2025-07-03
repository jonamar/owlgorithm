"""
Validation utilities for Owlgorithm project.
Common validation patterns to eliminate duplication.
"""

import os
from typing import Optional, List
from config import app_config as cfg


def validate_venv_python(print_error: bool = True) -> bool:
    """
    Validate that virtual environment Python executable exists.
    
    Args:
        print_error (bool): Whether to print error message if not found
        
    Returns:
        bool: True if virtual environment Python exists
    """
    venv_python = cfg.VENV_PYTHON_PATH
    exists = os.path.exists(venv_python)
    
    if not exists and print_error:
        print("❌ Virtual environment python not found. Please ensure duolingo_env is set up.")
    
    return exists


def validate_config_file(filepath: str, description: str = "config file", print_error: bool = True) -> bool:
    """
    Validate that a configuration file exists.
    
    Args:
        filepath (str): Path to configuration file
        description (str): Human-readable description of file
        print_error (bool): Whether to print error message if not found
        
    Returns:
        bool: True if file exists
    """
    exists = os.path.exists(filepath)
    
    if not exists and print_error:
        print(f"❌ {description} not found: {filepath}")
    
    return exists


def validate_data_directory(create_if_missing: bool = True) -> bool:
    """
    Validate that data directory exists, optionally creating it.
    
    Args:
        create_if_missing (bool): Whether to create directory if missing
        
    Returns:
        bool: True if directory exists or was created successfully
    """
    data_dir = cfg.DATA_DIR
    
    if os.path.exists(data_dir):
        return True
    
    if create_if_missing:
        try:
            os.makedirs(data_dir, exist_ok=True)
            print(f"✅ Created data directory: {data_dir}")
            return True
        except OSError as e:
            print(f"❌ Failed to create data directory {data_dir}: {e}")
            return False
    else:
        print(f"❌ Data directory not found: {data_dir}")
        return False


def validate_required_files(files: List[str], create_missing: bool = False) -> bool:
    """
    Validate that a list of required files exist.
    
    Args:
        files (List[str]): List of file paths to validate
        create_missing (bool): Whether to create empty files if missing
        
    Returns:
        bool: True if all files exist or were created successfully
    """
    all_exist = True
    
    for filepath in files:
        if os.path.exists(filepath):
            continue
            
        all_exist = False
        
        if create_missing:
            try:
                # Create parent directory if needed
                parent_dir = os.path.dirname(filepath)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
                
                # Create empty file
                with open(filepath, 'w') as f:
                    f.write("{}\n" if filepath.endswith('.json') else "")
                    
                print(f"✅ Created missing file: {filepath}")
                all_exist = True
                
            except OSError as e:
                print(f"❌ Failed to create missing file {filepath}: {e}")
        else:
            print(f"❌ Required file not found: {filepath}")
    
    return all_exist


def get_project_status() -> dict:
    """
    Get overall project validation status.
    
    Returns:
        dict: Status of various project components
    """
    status = {
        'venv_python': validate_venv_python(print_error=False),
        'data_directory': validate_data_directory(create_if_missing=False),
        'state_file': os.path.exists(cfg.STATE_FILE),
        'markdown_file': os.path.exists(cfg.MARKDOWN_FILE),
        'notifier_config': os.path.exists(cfg.NOTIFIER_CONFIG_FILE)
    }
    
    status['all_valid'] = all(status.values())
    
    return status