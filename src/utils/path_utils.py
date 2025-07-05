"""
Path utilities for Owlgorithm project.
Provides standard path operations and project setup functions.
"""

import os
import sys
from typing import Optional
from .constants import DUOME_BASE_URL


def setup_project_paths() -> None:
    """
    Standard project path setup for all scripts.
    Eliminates duplicate sys.path manipulation across files.
    """
    # Get the project root directory (two levels up from this file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    # Add project root and src directory to Python path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    src_dir = os.path.join(project_root, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


def build_duome_url(username: str) -> str:
    """
    Build duome.eu profile URL for a given username.
    Eliminates duplicate URL construction across scrapers.
    
    Args:
        username (str): Duolingo username
        
    Returns:
        str: Full duome.eu profile URL
    """
    return f"{DUOME_BASE_URL}/{username}"


def get_data_file_path(filename: str, data_dir: str = "data") -> str:
    """
    Get full path to a data file.
    
    Args:
        filename (str): Name of the data file
        data_dir (str): Data directory name (default: "data")
        
    Returns:
        str: Full path to the data file
    """
    # Get project root (three levels up from this file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    return os.path.join(project_root, data_dir, filename)


def ensure_directory_exists(dirpath: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        dirpath (str): Path to directory
        
    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        os.makedirs(dirpath, exist_ok=True)
        return True
    except OSError:
        return False


def get_project_root() -> str:
    """
    Get the project root directory.
    
    Returns:
        str: Path to project root
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(current_dir))