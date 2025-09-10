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
        self.entry_script = self.project_root / "scripts" / "send_simple_notification.py"
        
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
        """Generate cron entries for simple reminder window (08:30–12:00)."""
        # Desired times: 08:30, 09:00, 09:30, 10:00, 10:30, 11:00, 11:30, 12:00
        log_file = self.project_root / cfg.LOG_DIR / "automation.log"
        
        # Add essential environment variables for cron
        # Include PATH for homebrew and pyenv, plus other essentials
        env_setup = (
            f"export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH && "
            f"export HOME={os.path.expanduser('~')} && "
        )
        
        cron_command = (
            f"{env_setup}"
            f"cd {self.project_root} && "
            f"{self.python_path} {self.entry_script} "
            f">> {log_file} 2>&1"
        )
        # Build specific cron lines for the window
        lines = [
            f"30 8 * * * {cron_command}",      # 08:30
            f"0,30 9-11 * * * {cron_command}", # 09:00, 09:30, 10:00, 10:30, 11:00, 11:30
            f"0 12 * * * {cron_command}",      # 12:00
        ]
        return "\n".join(lines)
    
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
    
    def show_platform_instructions(self):
        """Show platform-specific setup instructions and requirements."""
        print(f"🔧 Platform-Specific Setup Instructions")
        print(f"{'='*60}")
        print(f"Detected Platform: {self._get_platform_name()}")
        print()
        
        if self.platform == 'darwin':  # macOS
            print("📱 macOS Setup:")
            print("  • Cron is available by default")
            print("  • No additional setup required")
            print("  • System will handle scheduling automatically")
            print("  • Use 'crontab -l' to view active schedules")
            print()
            print("💡 macOS Tips:")
            print("  • Cron runs in background even when not logged in")
            print("  • Check logs in ~/Library/Logs/ if issues occur")
            print("  • Terminal may need Full Disk Access for some operations")
            
        elif self.platform == 'linux' and not self.is_wsl:  # Native Linux
            print("🐧 Linux Setup:")
            print("  • Cron should be available by default")
            print("  • If not installed: sudo apt-get install cron (Ubuntu/Debian)")
            print("  • Or: sudo yum install cronie (CentOS/RHEL)")
            print("  • Service management: sudo systemctl start crond")
            print()
            print("💡 Linux Tips:")
            print("  • Check if cron service is running: systemctl status crond")
            print("  • View system logs: journalctl -u crond")
            print("  • User crontab doesn't require sudo")
            
        elif self.is_wsl:  # Windows Subsystem for Linux
            print("🪟 WSL (Windows Subsystem for Linux) Setup:")
            print("  • Cron is available but may need manual start")
            print("  • Start cron service: sudo service cron start")
            print("  • Auto-start: Add to ~/.bashrc or ~/.zshrc:")
            print("    sudo service cron start 2>/dev/null")
            print()
            print("💡 WSL Tips:")
            print("  • Cron only runs while WSL is active")
            print("  • Consider Windows Task Scheduler for always-on automation")
            print("  • Test with: sudo service cron status")
            
        else:
            print("❓ Unknown Platform:")
            print("  • Manual setup may be required")
            print("  • Check if cron/crontab is available")
            print("  • Consult your system documentation")
            
        print()
        print("🔍 Common Commands:")
        print("  • View current crontab: crontab -l")
        print("  • Edit crontab manually: crontab -e")
        print("  • Test cron works: echo '* * * * * echo \"test\" >> /tmp/crontest' | crontab -")
        print("  • Remove test: crontab -r")
        print()
    
    def check_system_requirements(self):
        """Check system requirements and provide detailed status."""
        print(f"🔍 System Requirements Check")
        print(f"{'='*50}")
        
        requirements = []
        
        # Check Python
        python_version = sys.version_info
        python_ok = python_version >= (3, 8)
        requirements.append({
            'name': 'Python Version',
            'status': '✅ OK' if python_ok else '❌ FAIL',
            'details': f"{python_version.major}.{python_version.minor}.{python_version.micro}",
            'required': '>= 3.8'
        })
        
        # Check cron availability
        cron_ok = self.cron_available
        requirements.append({
            'name': 'Cron System',
            'status': '✅ OK' if cron_ok else '❌ MISSING',
            'details': 'Available' if cron_ok else 'Not found',
            'required': 'crontab command'
        })
        
        # Check project files
        entry_exists = self.entry_script.exists()
        requirements.append({
            'name': 'Entry Script',
            'status': '✅ OK' if entry_exists else '❌ MISSING',
            'details': str(self.entry_script),
            'required': 'scripts/daily_update.py'
        })
        
        # Check config file
        config_exists = (self.project_root / "config" / "app_config.py").exists()
        requirements.append({
            'name': 'Configuration',
            'status': '✅ OK' if config_exists else '❌ MISSING',
            'details': 'config/app_config.py',
            'required': 'Personal config file'
        })
        
        # Check log directory
        log_dir = self.project_root / cfg.LOG_DIR
        log_dir_exists = log_dir.exists()
        requirements.append({
            'name': 'Log Directory',
            'status': '✅ OK' if log_dir_exists else '⚠️ MISSING',
            'details': str(log_dir),
            'required': 'Will be created automatically'
        })
        
        # Display results
        for req in requirements:
            print(f"  {req['name']:<20} {req['status']:<10} {req['details']}")
            if req['status'].startswith('❌'):
                print(f"    ↳ Required: {req['required']}")
        
        print()
        
        # Overall status
        critical_fails = [r for r in requirements if r['status'].startswith('❌') and 'MISSING' in r['status']]
        if critical_fails:
            print("❌ Setup Requirements Not Met:")
            for fail in critical_fails:
                print(f"  • {fail['name']}: {fail['required']}")
            print()
            return False
        else:
            print("✅ All Requirements Met - Ready for automation setup!")
            print()
            return True
    
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
        print(f"   • Run every 30 minutes from 08:30 to 12:00 (08:30, 09:00, 09:30, 10:00, 10:30, 11:00, 11:30, 12:00)")
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
  python scripts/setup_cron.py check           # Check system requirements
  python scripts/setup_cron.py help            # Show platform-specific instructions
        """
    )
    
    parser.add_argument('action', choices=['status', 'setup', 'remove', 'test', 'check', 'help'],
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
    elif args.action == 'check':
        success = automation.check_system_requirements()
        sys.exit(0 if success else 1)
    elif args.action == 'help':
        automation.show_platform_instructions()


if __name__ == '__main__':
    main() 