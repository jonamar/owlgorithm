#!/usr/bin/env python3
"""
Enhanced Scraper with Retry Logic and Graceful Degradation
Wraps the existing scraper with intelligent retry, fallback mechanisms, and error recovery.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from .retry_handler import RetryHandler, RetryConfig, ErrorType
from .duome_raw_scraper import fetch_duome_data_with_update
# NOTE: fetch_duome_data (HTTP fallback) removed - it only returns stale cached data
# See: https://github.com/user/repo/issues/XXX for details on data freshness testing
from ..data.data_manager import DataManager, DataAccessError
from ..notifiers.pushover_notifier import PushoverNotifier
from config import app_config as cfg


class ScrapingError(Exception):
    """Raised when scraping operations fail."""
    pass


class GracefulDegradationMode:
    """Configuration for graceful degradation behavior."""
    
    def __init__(self):
        self.use_cached_data = True
        self.max_cache_age_hours = 24
        self.send_failure_notifications = True
        self.minimum_data_quality = 0.7  # Minimum quality score to accept data
        
    def should_use_cache(self, cache_age_hours: float) -> bool:
        """Determine if cached data should be used based on age."""
        return self.use_cached_data and cache_age_hours <= self.max_cache_age_hours


class EnhancedScraper:
    """
    Enhanced scraper with retry logic, graceful degradation, and error recovery.
    
    Provides intelligent scraping with automatic fallbacks and comprehensive
    error handling to ensure maximum reliability.
    """
    
    def __init__(self, 
                 retry_config: Optional[RetryConfig] = None,
                 degradation_mode: Optional[GracefulDegradationMode] = None):
        """
        Initialize enhanced scraper.
        
        Args:
            retry_config: Configuration for retry behavior
            degradation_mode: Configuration for graceful degradation
        """
        self.retry_handler = RetryHandler(retry_config or RetryConfig(
            max_attempts=5,
            initial_delay=1.0,
            max_delay=300.0,
            circuit_breaker_threshold=3
        ))
        
        self.degradation_mode = degradation_mode or GracefulDegradationMode()
        self.data_manager = DataManager()
        self.logger = logging.getLogger(__name__)
        
        # Initialize notification handler
        try:
            self.notifier = PushoverNotifier()
        except Exception as e:
            self.logger.warning(f"Failed to initialize notifier: {e}")
            self.notifier = None
    
    def scrape_with_retry(self, username: str = None) -> Dict[str, Any]:
        """
        Scrape data with intelligent retry and fallback logic.
        
        Args:
            username: Username to scrape (defaults to configured username)
            
        Returns:
            Scraped data dictionary
            
        Raises:
            ScrapingError: If all scraping and fallback methods fail
        """
        username = username or cfg.USERNAME
        self.logger.info(f"Starting enhanced scraping for user: {username}")
        
        # Try primary scraping method with retry
        try:
            data = self.retry_handler.execute_with_retry(
                lambda: self._scrape_primary_method(username),
                operation_name=f"scrape_primary_{username}"
            )
            
            self.logger.info("Primary scraping succeeded")
            
            # Validate data quality
            if self._validate_data_quality(data):
                # Save successful scrape
                self._save_scrape_data(data, username)
                return data
            else:
                self.logger.warning("Primary scrape data quality insufficient, trying fallback")
                
        except Exception as e:
            self.logger.error(f"Primary scraping failed after retries: {e}")
            
        # HTTP fallback method REMOVED - it only returns stale cached data
        # Testing confirmed that duome.eu serves stale data unless the "aggiorna" 
        # update button is clicked via browser automation. HTTP requests bypass this
        # mechanism and return outdated session data, making them useless for real-time tracking.
        self.logger.warning("Primary scraping failed, only cached data fallback available")
        
        # Try cached data fallback
        cached_data = self._try_cached_data_fallback(username)
        if cached_data:
            self.logger.info("Using cached data as fallback")
            return cached_data
        
        # All methods failed - send notification and raise error
        self._handle_persistent_failure(username)
        raise ScrapingError(f"All scraping methods failed for user {username}")
    
    def _scrape_primary_method(self, username: str) -> Dict[str, Any]:
        """
        Primary scraping method using browser automation.
        
        Args:
            username: Username to scrape
            
        Returns:
            Scraped data
            
        Raises:
            Exception: If scraping fails
        """
        self.logger.info("Attempting primary scraping method (browser automation)")
        
        # Use the existing scraper with browser automation
        page_source = fetch_duome_data_with_update(username, headless=True)
        
        if not page_source:
            raise ScrapingError("Browser automation returned no data")
        
        # Parse the page source (reuse existing parsing logic)
        from .duome_raw_scraper import parse_session_data
        data = parse_session_data(page_source)
        
        # Add username and timestamp
        data['username'] = username
        data['scraped_at'] = datetime.now().isoformat()
        
        if not data or not data.get('sessions'):
            raise ScrapingError("No session data extracted from page")
        
        return data
    
    # _scrape_fallback_method REMOVED
    # 
    # CRITICAL: HTTP-based fallback scraping does NOT work for duome.eu
    # 
    # Problem: duome.eu serves stale cached session data unless the "aggiorna" update 
    # button is clicked through browser automation. Direct HTTP requests bypass this 
    # refresh mechanism and return outdated data.
    # 
    # Evidence: Testing on 2025-06-30 confirmed that:
    # - HTTP method: Showed 6 sessions, most recent from 08:33:07
    # - Browser method: Showed 7 sessions, most recent from 09:20:12
    # - User completed lesson at ~09:20, only browser method detected it
    # 
    # Therefore: Browser automation with update button click is REQUIRED for fresh data.
    # HTTP fallbacks create false confidence while returning stale data.
    
    def _has_required_fields(self, data: Dict[str, Any]) -> Tuple[float, int]:
        """Check for essential required fields"""
        quality_score = 0.0
        checks = 0
        
        essential_fields = ['sessions', 'username', 'scraped_at']
        for field in essential_fields:
            checks += 1
            if field in data and data[field]:
                quality_score += 1.0
        
        return quality_score, checks
    
    def _validate_sessions_data(self, data: Dict[str, Any]) -> Tuple[float, int]:
        """Validate session data quality and recency"""
        quality_score = 0.0
        checks = 0
        
        if 'sessions' in data and isinstance(data['sessions'], list):
            sessions = data['sessions']
            checks += 1
            
            if len(sessions) > 0:
                quality_score += 1.0
                
                # Check for recent sessions (within last 7 days)
                recent_sessions = 0
                current_time = datetime.now()
                
                for session in sessions[:10]:  # Check first 10 sessions
                    if 'date' in session:
                        try:
                            session_date = datetime.fromisoformat(session['date'].replace('Z', '+00:00'))
                            if (current_time - session_date).days <= 7:
                                recent_sessions += 1
                        except (ValueError, AttributeError):
                            continue
                
                if recent_sessions > 0:
                    checks += 1
                    quality_score += 1.0
        
        return quality_score, checks
    
    def _validate_computed_metrics(self, data: Dict[str, Any]) -> Tuple[float, int]:
        """Validate computed metrics are present and reasonable"""
        quality_score = 0.0
        checks = 0
        
        computed_fields = ['computed_total_sessions', 'computed_lesson_count']
        for field in computed_fields:
            checks += 1
            if field in data and isinstance(data[field], (int, float)) and data[field] > 0:
                quality_score += 1.0
        
        return quality_score, checks
    
    def _validate_data_quality(self, data: Dict[str, Any]) -> bool:
        """
        Validate the quality of scraped data.
        
        Args:
            data: Scraped data to validate
            
        Returns:
            True if data quality is acceptable
        """
        if not data or not isinstance(data, dict):
            return False
        
        total_quality_score = 0.0
        total_checks = 0
        
        # Check required fields
        quality_score, checks = self._has_required_fields(data)
        total_quality_score += quality_score
        total_checks += checks
        
        # Validate sessions data
        quality_score, checks = self._validate_sessions_data(data)
        total_quality_score += quality_score
        total_checks += checks
        
        # Validate computed metrics
        quality_score, checks = self._validate_computed_metrics(data)
        total_quality_score += quality_score
        total_checks += checks
        
        final_score = total_quality_score / total_checks if total_checks > 0 else 0.0
        
        self.logger.info(f"Data quality score: {final_score:.2f} (threshold: {self.degradation_mode.minimum_data_quality})")
        
        return final_score >= self.degradation_mode.minimum_data_quality
    
    def _try_cached_data_fallback(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Try to use cached data as a fallback.
        
        Args:
            username: Username for cached data
            
        Returns:
            Cached data if suitable, None otherwise
        """
        if not self.degradation_mode.use_cached_data:
            return None
        
        try:
            # Find latest cached data
            latest_file = self.data_manager.find_latest_scrape_file(username)
            if not latest_file:
                self.logger.info("No cached data available")
                return None
            
            # Check cache age
            cache_age = time.time() - os.path.getctime(latest_file)
            cache_age_hours = cache_age / 3600
            
            if not self.degradation_mode.should_use_cache(cache_age_hours):
                self.logger.info(f"Cached data too old ({cache_age_hours:.1f} hours)")
                return None
            
            # Load and validate cached data
            cached_data = self.data_manager.load_scrape_data(latest_file)
            
            if self._validate_data_quality(cached_data):
                self.logger.info(f"Using cached data from {cache_age_hours:.1f} hours ago")
                # Mark as cached data
                cached_data['from_cache'] = True
                cached_data['cache_age_hours'] = cache_age_hours
                return cached_data
            else:
                self.logger.warning("Cached data quality insufficient")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to load cached data: {e}")
            return None
    
    def _save_scrape_data(self, data: Dict[str, Any], username: str):
        """
        Save scraped data with error handling.
        
        Args:
            data: Data to save
            username: Username for the data
        """
        try:
            saved_path = self.data_manager.save_scrape_data(data, username)
            self.logger.info(f"Saved scrape data to: {saved_path}")
            
            # Cleanup old files
            deleted_count = self.data_manager.cleanup_old_scrape_files(username, keep_count=10)
            if deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} old scrape files")
                
        except Exception as e:
            self.logger.error(f"Failed to save scrape data: {e}")
    
    def _handle_persistent_failure(self, username: str):
        """
        Handle persistent scraping failures with notifications.
        
        Args:
            username: Username that failed to scrape
        """
        if not self.degradation_mode.send_failure_notifications or not self.notifier:
            return
        
        try:
            # Get failure statistics
            stats = self.retry_handler.get_retry_statistics()
            
            message = f"🚨 Persistent scraping failure for {username}\n\n"
            message += f"• Total attempts: {stats['total_attempts']}\n"
            message += f"• Circuit breaker: {stats['circuit_breaker']['state']}\n"
            
            if stats['error_types']:
                message += f"• Error types: {', '.join(stats['error_types'].keys())}\n"
            
            message += f"\nFallback to cached data also failed. Manual intervention may be required."
            
            self.notifier.send_notification(
                message=message,
                title="Scraping System Alert",
                priority=1  # High priority
            )
            
            self.logger.info("Sent failure notification")
            
        except Exception as e:
            self.logger.error(f"Failed to send failure notification: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the enhanced scraper.
        
        Returns:
            Health status information
        """
        return {
            "retry_handler": self.retry_handler.get_retry_statistics(),
            "circuit_breaker": self.retry_handler.circuit_breaker.get_status(),
            "data_manager": self.data_manager.health_check(),
            "degradation_mode": {
                "use_cached_data": self.degradation_mode.use_cached_data,
                "max_cache_age_hours": self.degradation_mode.max_cache_age_hours,
                "minimum_data_quality": self.degradation_mode.minimum_data_quality
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_circuit_breaker(self):
        """Reset the circuit breaker and retry history."""
        self.retry_handler.reset_history()
        self.logger.info("Circuit breaker and retry history reset")


# Convenience function for easy integration
def scrape_duome_enhanced(username: str = None, 
                         retry_config: Optional[RetryConfig] = None) -> Dict[str, Any]:
    """
    Convenient function to scrape with enhanced retry and fallback logic.
    
    Args:
        username: Username to scrape (defaults to configured username)
        retry_config: Optional retry configuration
        
    Returns:
        Scraped data
    """
    scraper = EnhancedScraper(retry_config=retry_config)
    return scraper.scrape_with_retry(username)