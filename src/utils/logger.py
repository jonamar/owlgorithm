#!/usr/bin/env python3
"""
Comprehensive Logging Infrastructure
Provides timestamped, categorized logging for debugging automation failures.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from config import app_config as cfg

class OWLLogger:
    """Centralized logging for Owlgorithm with automation-specific features."""
    
    def __init__(self, name="owlgorithm", run_type="unknown"):
        """
        Initialize logger with run type identification.
        
        Args:
            name: Logger name
            run_type: 'manual', 'automated', or 'test'
        """
        self.name = name
        self.run_type = run_type
        self.start_time = datetime.now()
        self.logger = logging.getLogger(name)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_logging()
        
        # Log run identification
        self.info(f"=== {run_type.upper()} RUN STARTED ===")
        self.info(f"Timestamp: {self.start_time.isoformat()}")
        self.info(f"PID: {os.getpid()}")
        self.info(f"Environment: {dict(os.environ)}")
        
    def _setup_logging(self):
        """Configure logging handlers and formatters."""
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory
        log_dir = Path(cfg.LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        
        # Detailed formatter with execution context
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler - separate files per run type
        log_file = log_dir / f"{self.name}_{self.run_type}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler for real-time feedback
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Also write to main tracker.log for compatibility
        main_log = log_dir / "tracker.log"
        main_handler = logging.FileHandler(main_log)
        main_handler.setLevel(logging.INFO)
        main_handler.setFormatter(formatter)
        self.logger.addHandler(main_handler)
    
    def debug(self, msg, **kwargs):
        """Debug level logging with optional context."""
        self._log_with_context(logging.DEBUG, msg, **kwargs)
    
    def info(self, msg, **kwargs):
        """Info level logging with optional context."""
        self._log_with_context(logging.INFO, msg, **kwargs)
        
    def warning(self, msg, **kwargs):
        """Warning level logging with optional context."""
        self._log_with_context(logging.WARNING, msg, **kwargs)
        
    def error(self, msg, **kwargs):
        """Error level logging with optional context."""
        self._log_with_context(logging.ERROR, msg, **kwargs)
        
    def critical(self, msg, **kwargs):
        """Critical level logging with optional context."""
        self._log_with_context(logging.CRITICAL, msg, **kwargs)
    
    def _log_with_context(self, level, msg, **kwargs):
        """Log message with additional context if provided."""
        if kwargs:
            context_str = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            msg = f"{msg} | Context: {context_str}"
        self.logger.log(level, msg)
    
    def execution_step(self, step_name, **context):
        """Log execution step with timing."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.info(f"STEP: {step_name}", elapsed_seconds=elapsed, **context)
    
    def state_change(self, component, old_value, new_value, **context):
        """Log state changes for audit trail."""
        self.info(f"STATE_CHANGE: {component}", 
                 old_value=old_value, new_value=new_value, **context)
    
    def external_call(self, service, action, success=None, **context):
        """Log external service calls (scraper, notifications, etc)."""
        status = "SUCCESS" if success else "FAILED" if success is False else "ATTEMPTED"
        self.info(f"EXTERNAL_CALL: {service}.{action} - {status}", **context)
    
    def performance_timing(self, operation, duration_seconds, **context):
        """Log performance timing information."""
        self.info(f"TIMING: {operation}", duration_seconds=duration_seconds, **context)
    
    def run_summary(self, success=True, **context):
        """Log run completion summary."""
        total_time = (datetime.now() - self.start_time).total_seconds()
        status = "SUCCESS" if success else "FAILED"
        self.info(f"=== {self.run_type.upper()} RUN {status} ===", 
                 total_duration_seconds=total_time, **context)

def get_logger(run_type="manual"):
    """
    Get logger instance with automatic run type detection.
    
    Args:
        run_type: Override run type detection
    """
    # Auto-detect run type based on environment
    if run_type == "manual":
        # Check if running from terminal vs launchd
        if os.getenv('TERM') is None and os.getenv('SSH_CLIENT') is None:
            run_type = "automated"
    
    return OWLLogger(run_type=run_type)