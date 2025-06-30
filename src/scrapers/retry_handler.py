#!/usr/bin/env python3
"""
Retry Handler for Scraping Operations
Provides intelligent retry logic with exponential backoff and circuit breaker functionality.
"""

import time
import logging
import random
from typing import Callable, Any, Optional, Dict, List, Type
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta


class ErrorType(Enum):
    """Classification of error types for different retry strategies."""
    NETWORK = "network"
    TIMEOUT = "timeout"
    BROWSER = "browser"
    PARSING = "parsing"
    RATE_LIMIT = "rate_limit"
    SERVER_ERROR = "server_error"
    UNKNOWN = "unknown"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 300.0  # 5 minutes


@dataclass
class RetryAttempt:
    """Information about a retry attempt."""
    attempt_number: int
    error_type: ErrorType
    error_message: str
    delay: float
    timestamp: datetime


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests due to failures
    HALF_OPEN = "half_open"  # Testing if service has recovered


class CircuitBreaker:
    """
    Circuit breaker implementation to prevent cascade failures.
    
    Tracks failure rates and temporarily blocks requests when failure
    threshold is exceeded, allowing the service time to recover.
    """
    
    def __init__(self, config: RetryConfig):
        """Initialize circuit breaker with configuration."""
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        
    def can_execute(self) -> bool:
        """Check if operation can be executed based on circuit breaker state."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            # Check if timeout has passed to transition to half-open
            if (self.last_failure_time and 
                datetime.now() - self.last_failure_time > timedelta(seconds=self.config.circuit_breaker_timeout)):
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    def record_success(self):
        """Record a successful operation."""
        self.failure_count = 0
        self.last_success_time = datetime.now()
        self.state = CircuitBreakerState.CLOSED
    
    def record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.config.circuit_breaker_threshold:
            self.state = CircuitBreakerState.OPEN
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Failed during test, go back to open
            self.state = CircuitBreakerState.OPEN
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
            "can_execute": self.can_execute()
        }


class RetryHandler:
    """
    Intelligent retry handler with exponential backoff and error-specific strategies.
    
    Provides flexible retry logic that adapts to different types of errors
    and includes circuit breaker functionality to prevent cascade failures.
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """
        Initialize retry handler.
        
        Args:
            config: Retry configuration (uses defaults if not provided)
        """
        self.config = config or RetryConfig()
        self.circuit_breaker = CircuitBreaker(self.config)
        self.logger = logging.getLogger(__name__)
        self.retry_history: List[RetryAttempt] = []
        
        # Error type mappings for classification
        self.error_mappings = {
            # Network errors
            "ConnectionError": ErrorType.NETWORK,
            "ConnectTimeout": ErrorType.NETWORK,
            "ReadTimeout": ErrorType.TIMEOUT,
            "TimeoutException": ErrorType.TIMEOUT,
            "URLError": ErrorType.NETWORK,
            "HTTPError": ErrorType.NETWORK,
            
            # Browser automation errors
            "WebDriverException": ErrorType.BROWSER,
            "NoSuchElementException": ErrorType.BROWSER,
            "ElementNotInteractableException": ErrorType.BROWSER,
            "ElementClickInterceptedException": ErrorType.BROWSER,
            "StaleElementReferenceException": ErrorType.BROWSER,
            
            # Server errors
            "500": ErrorType.SERVER_ERROR,
            "502": ErrorType.SERVER_ERROR,
            "503": ErrorType.SERVER_ERROR,
            "504": ErrorType.SERVER_ERROR,
            
            # Rate limiting
            "429": ErrorType.RATE_LIMIT,
            "rate limit": ErrorType.RATE_LIMIT,
            "too many requests": ErrorType.RATE_LIMIT,
        }
    
    def classify_error(self, exception: Exception) -> ErrorType:
        """
        Classify an error to determine the appropriate retry strategy.
        
        Args:
            exception: The exception to classify
            
        Returns:
            ErrorType classification
        """
        error_str = str(exception).lower()
        exception_name = type(exception).__name__
        
        # Check exception type first
        if exception_name in self.error_mappings:
            return self.error_mappings[exception_name]
        
        # Check error message content
        for pattern, error_type in self.error_mappings.items():
            if pattern.lower() in error_str:
                return error_type
        
        return ErrorType.UNKNOWN
    
    def get_error_specific_config(self, error_type: ErrorType) -> RetryConfig:
        """
        Get error-specific retry configuration.
        
        Args:
            error_type: Type of error that occurred
            
        Returns:
            Adjusted retry configuration for the error type
        """
        config = RetryConfig(
            max_attempts=self.config.max_attempts,
            initial_delay=self.config.initial_delay,
            max_delay=self.config.max_delay,
            exponential_base=self.config.exponential_base,
            jitter=self.config.jitter,
            circuit_breaker_threshold=self.config.circuit_breaker_threshold,
            circuit_breaker_timeout=self.config.circuit_breaker_timeout
        )
        
        # Adjust config based on error type
        if error_type == ErrorType.RATE_LIMIT:
            # Be more aggressive with rate limit errors
            config.initial_delay = 5.0
            config.max_delay = 300.0
            config.exponential_base = 3.0
        elif error_type == ErrorType.NETWORK:
            # Standard backoff for network issues
            config.initial_delay = 2.0
            config.max_delay = 120.0
        elif error_type == ErrorType.TIMEOUT:
            # Shorter delays for timeouts
            config.initial_delay = 1.0
            config.max_delay = 30.0
        elif error_type == ErrorType.BROWSER:
            # Quick retries for browser automation issues
            config.initial_delay = 0.5
            config.max_delay = 10.0
            config.exponential_base = 1.5
        elif error_type == ErrorType.SERVER_ERROR:
            # Longer delays for server issues
            config.initial_delay = 10.0
            config.max_delay = 600.0
        
        return config
    
    def calculate_delay(self, attempt: int, error_type: ErrorType) -> float:
        """
        Calculate delay before next retry attempt.
        
        Args:
            attempt: Current attempt number (0-based)
            error_type: Type of error that occurred
            
        Returns:
            Delay in seconds
        """
        config = self.get_error_specific_config(error_type)
        
        # Calculate exponential backoff
        delay = config.initial_delay * (config.exponential_base ** attempt)
        delay = min(delay, config.max_delay)
        
        # Add jitter to prevent thundering herd
        if config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            jitter = random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay + jitter)
        
        return delay
    
    def execute_with_retry(self, 
                          operation: Callable[[], Any], 
                          operation_name: str = "operation",
                          custom_config: Optional[RetryConfig] = None) -> Any:
        """
        Execute an operation with intelligent retry logic.
        
        Args:
            operation: Function to execute
            operation_name: Name for logging purposes
            custom_config: Override retry configuration for this operation
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: Last exception if all retries failed
        """
        config = custom_config or self.config
        last_exception = None
        
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            self.logger.warning(f"Circuit breaker is OPEN, blocking {operation_name}")
            raise Exception(f"Circuit breaker is open. Service unavailable. "
                          f"Last failure: {self.circuit_breaker.last_failure_time}")
        
        for attempt in range(config.max_attempts):
            try:
                self.logger.info(f"Executing {operation_name} (attempt {attempt + 1}/{config.max_attempts})")
                result = operation()
                
                # Success - record and return
                self.circuit_breaker.record_success()
                self.logger.info(f"{operation_name} succeeded on attempt {attempt + 1}")
                return result
                
            except Exception as e:
                last_exception = e
                error_type = self.classify_error(e)
                
                self.logger.warning(f"{operation_name} failed on attempt {attempt + 1}: {e} "
                                  f"(classified as {error_type.value})")
                
                # Record retry attempt
                delay = self.calculate_delay(attempt, error_type) if attempt < config.max_attempts - 1 else 0
                retry_attempt = RetryAttempt(
                    attempt_number=attempt + 1,
                    error_type=error_type,
                    error_message=str(e),
                    delay=delay,
                    timestamp=datetime.now()
                )
                self.retry_history.append(retry_attempt)
                
                # If this is the last attempt, don't wait
                if attempt == config.max_attempts - 1:
                    break
                
                # Wait before retry
                if delay > 0:
                    self.logger.info(f"Waiting {delay:.2f} seconds before retry...")
                    time.sleep(delay)
        
        # All retries failed
        self.circuit_breaker.record_failure()
        self.logger.error(f"{operation_name} failed after {config.max_attempts} attempts")
        
        if last_exception:
            raise last_exception
        else:
            raise Exception(f"{operation_name} failed after {config.max_attempts} attempts")
    
    def get_retry_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about retry attempts.
        
        Returns:
            Dictionary with retry statistics
        """
        if not self.retry_history:
            return {"total_attempts": 0, "error_types": {}, "average_delay": 0}
        
        error_counts = {}
        total_delay = 0
        
        for attempt in self.retry_history:
            error_type = attempt.error_type.value
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
            total_delay += attempt.delay
        
        return {
            "total_attempts": len(self.retry_history),
            "error_types": error_counts,
            "average_delay": total_delay / len(self.retry_history) if self.retry_history else 0,
            "circuit_breaker": self.circuit_breaker.get_status(),
            "recent_attempts": [
                {
                    "attempt": a.attempt_number,
                    "error_type": a.error_type.value,
                    "error": a.error_message,
                    "delay": a.delay,
                    "timestamp": a.timestamp.isoformat()
                } for a in self.retry_history[-10:]  # Last 10 attempts
            ]
        }
    
    def reset_history(self):
        """Reset retry history and circuit breaker state."""
        self.retry_history.clear()
        self.circuit_breaker = CircuitBreaker(self.config)
        self.logger.info("Retry handler reset")