#!/usr/bin/env python3
"""
Migration registry - imports and registers all available migrations.
"""

from .migrator import migrator
from .v1_0_to_v1_1 import V1_0_to_V1_1_Migration


def register_all_migrations():
    """Register all available migrations with the global migrator."""
    migrator.register_migration(V1_0_to_V1_1_Migration())


# Auto-register migrations when this module is imported
register_all_migrations()