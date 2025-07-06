#!/usr/bin/env python3
"""
Cross-Platform Automation Setup for Owlgorithm
==============================================

Sets up automated Duolingo progress tracking across platforms:
- macOS: Uses cron (replacing complex launchd setup)
- Linux: Uses cron 
- WSL: Uses cron with Windows integration

Based on current working launchd pattern:
- Runs every 30 minutes from 6:00am to 11:30pm + midnight
- Uses scripts/daily_update.py as entry point
- Handles path setup and logging automatically
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

# Setup project paths - must be done before other imports
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from config import app_config as cfg


class AutomationSetup:
    """Cross-platform automation setup for Owlgorithm."""
    
    def __init__(self):
        """Initialize automation setup with platform detection."""
        self.platform = platform.system().lower()
        self.project_root = Path(project_root)
        self.python_path = sys.executable
        self.entry_script = self.project_root / "scripts" / "daily_update.py"
        
        # Detect environment details
        self.is_wsl = self._detect_wsl()
        self.cron_available = self._check_cron_available()
        
    def _detect_wsl(self) -> bool:
        """Detect if running in Windows Subsystem for Linux."""
        try:
            with open('/proc/version', 'r') as f:
                return 'Microsoft' in f.read()
        except FileNotFoundError:
            return False
    
    def _check_cron_available(self) -> bool:
        """Check if cron is available on the system."""
        return shutil.which('crontab') is not None
    
    def _get_platform_name(self) -> str:
        """Get human-readable platform name."""
        if self.is_wsl:
            return "Windows Subsystem for Linux (WSL)"
        elif self.platform == 'darwin':
            return "macOS"
        elif self.platform == 'linux':
            return "Linux"
        else:
            return f"Unknown ({self.platform})"
    
    def _generate_cron_entry(self) -> str:
        """Generate cron entry based on current working launchd pattern."""
        # Current pattern: Every 30 minutes from 6am to 11:30pm + midnight
        # Cron equivalent: */30 6-23 * * * + 0 0 * * *
        log_file = self.project_root / cfg.LOG_DIR / "automation.log"
        
        cron_command = (
            f"cd {self.project_root} && "
            f"{self.python_path} {self.entry_script} "
            f">> {log_file} 2>&1"
        )
        
        return f"*/30 6-23 * * * {cron_command}\n0 0 * * * {cron_command}"
    
    def _get_current_crontab(self) -> str:
        """Get current crontab content."""
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else ""
        except subprocess.SubprocessError:
            return ""
    
    def _crontab_has_owlgorithm(self, crontab_content: str) -> bool:
        """Check if crontab already has Owlgorithm entries."""
        return 'daily_update.py' in crontab_content or 'owlgorithm' in crontab_content.lower()
    
    def show_status(self):
        """Show current automation status."""
        print(f"🔍 Automation Setup Status")
        print(f"{'='*50}")
        print(f"Platform: {self._get_platform_name()}")
        print(f"Cron Available: {'✅ Yes' if self.cron_available else '❌ No'}")
        print(f"Project Root: {self.project_root}")
        print(f"Python Path: {self.python_path}")
        print(f"Entry Script: {self.entry_script}")
        
        if self.cron_available:
            current_crontab = self._get_current_crontab()
            has_automation = self._crontab_has_owlgorithm(current_crontab)
            print(f"Current Automation: {'✅ Active' if has_automation else '❌ Not configured'}")
            
            if has_automation:
                print(f"\n📋 Current Crontab Entries:")
                for line in current_crontab.split('\n'):
                    if line.strip() and ('daily_update.py' in line or 'owlgorithm' in line.lower()):
                        print(f"   {line}")
        print()
    
    def setup_automation(self, force: bool = False):
        """Set up automated scheduling for the current platform."""
        print(f"🚀 Setting up automation for {self._get_platform_name()}")
        print(f"{'='*60}")
        
        if not self.cron_available:
            print("❌ Error: cron is not available on this system")
            print("   Please install cron or use a different scheduling method")
            return False
        
        # Check existing automation
        current_crontab = self._get_current_crontab()
        if self._crontab_has_owlgorithm(current_crontab) and not force:
            print("⚠️  Owlgorithm automation is already configured!")
            print("   Use --force to overwrite existing configuration")
            return False
        
        # Generate new cron entries
        new_entries = self._generate_cron_entry()
        
        print(f"📝 Generated cron entries:")
        for line in new_entries.split('\n'):
            if line.strip():
                print(f"   {line}")
        print()
        
        # Show what will be added
        print(f"🔧 This will:")
        print(f"   • Run every 30 minutes from 6:00 AM to 11:30 PM")
        print(f"   • Run once at midnight (00:00)")
        print(f"   • Log to: {self.project_root / cfg.LOG_DIR / 'automation.log'}")
        print(f"   • Execute: {self.entry_script}")
        print()
        
        # Confirm before proceeding
        if not force:
            response = input("📋 Add these entries to your crontab? (y/N): ").strip().lower()
            if response != 'y':
                print("❌ Setup cancelled")
                return False
        
        # Add to crontab
        try:
            # Prepare new crontab content
            clean_crontab = self._remove_owlgorithm_entries(current_crontab)
            new_crontab = clean_crontab.rstrip() + '\n\n# Owlgorithm Duolingo Automation\n' + new_entries + '\n'
            
            # Apply new crontab
            result = subprocess.run(['crontab', '-'], input=new_crontab, text=True, capture_output=True)
            
            if result.returncode == 0:
                print("✅ Automation setup successful!")
                print(f"   📊 Status: Active (running every 30 minutes)")
                print(f"   📁 Logs: {self.project_root / cfg.LOG_DIR / 'automation.log'}")
                print(f"   🔍 Check: crontab -l | grep owlgorithm")
                return True
            else:
                print(f"❌ Failed to setup crontab: {result.stderr}")
                return False
                
        except subprocess.SubprocessError as e:
            print(f"❌ Error setting up automation: {e}")
            return False
    
    def _remove_owlgorithm_entries(self, crontab_content: str) -> str:
        """Remove existing Owlgorithm entries from crontab."""
        lines = []
        skip_next = False
        
        for line in crontab_content.split('\n'):
            if 'Owlgorithm' in line and line.strip().startswith('#'):
                skip_next = True
                continue
            if skip_next and ('daily_update.py' in line or 'owlgorithm' in line.lower()):
                continue
            skip_next = False
            lines.append(line)
        
        return '\n'.join(lines)
    
    def remove_automation(self):
        """Remove Owlgorithm automation from crontab."""
        print(f"🗑️  Removing Owlgorithm automation")
        print(f"{'='*40}")
        
        current_crontab = self._get_current_crontab()
        if not self._crontab_has_owlgorithm(current_crontab):
            print("ℹ️  No Owlgorithm automation found in crontab")
            return True
        
        try:
            clean_crontab = self._remove_owlgorithm_entries(current_crontab)
            result = subprocess.run(['crontab', '-'], input=clean_crontab, text=True, capture_output=True)
            
            if result.returncode == 0:
                print("✅ Automation removed successfully!")
                return True
            else:
                print(f"❌ Failed to remove automation: {result.stderr}")
                return False
                
        except subprocess.SubprocessError as e:
            print(f"❌ Error removing automation: {e}")
            return False
    
    def test_automation(self):
        """Test the automation setup by running manually."""
        print(f"🧪 Testing automation setup")
        print(f"{'='*30}")
        print(f"Running: {self.entry_script}")
        print()
        
        try:
            # Change to project directory and run
            os.chdir(self.project_root)
            result = subprocess.run([self.python_path, str(self.entry_script)], 
                                  capture_output=False, text=True)
            
            if result.returncode == 0:
                print("\n✅ Test successful! Automation should work correctly.")
                return True
            else:
                print(f"\n❌ Test failed with return code: {result.returncode}")
                return False
                
        except subprocess.SubprocessError as e:
            print(f"❌ Test error: {e}")
            return False


def main():
    """Main entry point for automation setup."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Cross-platform automation setup for Owlgorithm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/setup_cron.py status          # Show current status
  python scripts/setup_cron.py setup           # Setup automation
  python scripts/setup_cron.py setup --force   # Force setup (overwrite existing)
  python scripts/setup_cron.py remove          # Remove automation
  python scripts/setup_cron.py test            # Test automation manually
        """
    )
    
    parser.add_argument('action', choices=['status', 'setup', 'remove', 'test'],
                       help='Action to perform')
    parser.add_argument('--force', action='store_true',
                       help='Force setup even if automation already exists')
    
    args = parser.parse_args()
    
    # Initialize automation setup
    automation = AutomationSetup()
    
    # Execute requested action
    if args.action == 'status':
        automation.show_status()
    elif args.action == 'setup':
        success = automation.setup_automation(force=args.force)
        sys.exit(0 if success else 1)
    elif args.action == 'remove':
        success = automation.remove_automation()
        sys.exit(0 if success else 1)
    elif args.action == 'test':
        success = automation.test_automation()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 