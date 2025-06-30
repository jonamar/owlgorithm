#!/usr/bin/env python3
"""
Migration from schema version 1.0 to 1.1
Adds metadata tracking to tracker state.
"""

from typing import Dict, Any
from .migrator import Migration


class V1_0_to_V1_1_Migration(Migration):
    """
    Example migration that adds metadata tracking.
    
    Changes in V1.1:
    - Add 'metadata' section with created_at timestamp
    - Add 'migration_history' to track applied migrations
    - Ensure all date fields are in ISO format
    """
    
    @property
    def from_version(self) -> str:
        return "1.0"
    
    @property
    def to_version(self) -> str:
        return "1.1"
    
    @property
    def description(self) -> str:
        return "Add metadata tracking and migration history"
    
    def validate_before(self, data: Dict[str, Any]) -> bool:
        """Validate that data is in V1.0 format."""
        # For V1.0, we just need it to be a dict and not already have metadata
        # This allows migration of any V1.0 data, including default/empty data
        return isinstance(data, dict) and "metadata" not in data
    
    def validate_after(self, data: Dict[str, Any]) -> bool:
        """Validate that data is in V1.1 format."""
        # Check for required V1.1 fields
        return (
            "metadata" in data and
            "created_at" in data["metadata"] and
            "migration_history" in data["metadata"]
        )
    
    def migrate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the migration."""
        migrated_data = data.copy()
        
        # Add metadata section if not present
        if "metadata" not in migrated_data:
            migrated_data["metadata"] = {}
        
        # Set created timestamp (use last_update_timestamp if available)
        if "created_at" not in migrated_data["metadata"]:
            if "last_update_timestamp" in data:
                migrated_data["metadata"]["created_at"] = data["last_update_timestamp"]
            else:
                # Use a default timestamp if no existing timestamp
                from datetime import datetime
                migrated_data["metadata"]["created_at"] = datetime.now().isoformat()
        
        # Initialize migration history
        if "migration_history" not in migrated_data["metadata"]:
            migrated_data["metadata"]["migration_history"] = []
        
        # Ensure date fields are in ISO format (if they aren't already)
        if "last_scrape_date" in migrated_data:
            scrape_date = migrated_data["last_scrape_date"]
            if isinstance(scrape_date, str) and len(scrape_date) == 10:
                # Convert YYYY-MM-DD to ISO format with time
                migrated_data["last_scrape_date"] = f"{scrape_date}T00:00:00"
        
        if "last_daily_reset" in migrated_data:
            reset_date = migrated_data["last_daily_reset"]
            if isinstance(reset_date, str) and len(reset_date) == 10:
                # Convert YYYY-MM-DD to ISO format with time
                migrated_data["last_daily_reset"] = f"{reset_date}T00:00:00"
        
        return migrated_data