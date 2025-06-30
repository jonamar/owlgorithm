#!/usr/bin/env python3
"""
Tests for Retry Handler
Tests intelligent retry logic, exponential backoff, and circuit breaker functionality.
"""

import pytest
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.scrapers.retry_handler import (
    RetryHandler, RetryConfig, ErrorType, CircuitBreaker,
    CircuitBreakerState, RetryAttempt
)


class TestErrorClassification:
    """Test error classification functionality."""
    
    @pytest.fixture
    def retry_handler(self):
        """Create retry handler for testing."""
        return RetryHandler()
    
    def test_network_error_classification(self, retry_handler):
        """Test classification of network errors."""
        # Create mock exception types
        class ConnectionError(Exception):
            pass
        
        class URLError(Exception):
            pass
        
        # Test by exception type
        error = ConnectionError("Connection failed")
        assert retry_handler.classify_error(error) == ErrorType.NETWORK
        
        # Test by message content
        error = Exception("URLError: connection failed")
        assert retry_handler.classify_error(error) == ErrorType.NETWORK
    
    def test_timeout_error_classification(self, retry_handler):
        """Test classification of timeout errors."""
        class TimeoutException(Exception):
            pass
        
        error = TimeoutException("operation timed out")
        assert retry_handler.classify_error(error) == ErrorType.TIMEOUT
    
    def test_browser_error_classification(self, retry_handler):
        """Test classification of browser automation errors."""
        class NoSuchElementException(Exception):
            pass
        
        error = NoSuchElementException("element not found")
        assert retry_handler.classify_error(error) == ErrorType.BROWSER
    
    def test_rate_limit_classification(self, retry_handler):
        """Test classification of rate limit errors."""
        error = Exception("429 Too Many Requests")
        assert retry_handler.classify_error(error) == ErrorType.RATE_LIMIT
        
        error = Exception("rate limit exceeded")
        assert retry_handler.classify_error(error) == ErrorType.RATE_LIMIT
    
    def test_server_error_classification(self, retry_handler):
        """Test classification of server errors."""
        error = Exception("500 Internal Server Error")
        assert retry_handler.classify_error(error) == ErrorType.SERVER_ERROR
        
        error = Exception("503 Service Unavailable")
        assert retry_handler.classify_error(error) == ErrorType.SERVER_ERROR
    
    def test_unknown_error_classification(self, retry_handler):
        """Test classification of unknown errors."""
        error = Exception("Some unknown error")
        assert retry_handler.classify_error(error) == ErrorType.UNKNOWN


class TestRetryDelay:
    """Test retry delay calculation."""
    
    @pytest.fixture
    def retry_handler(self):
        """Create retry handler for testing."""
        config = RetryConfig(
            initial_delay=1.0,
            max_delay=60.0,
            exponential_base=2.0,
            jitter=False  # Disable jitter for predictable testing
        )
        return RetryHandler(config)
    
    def test_exponential_backoff(self, retry_handler):
        """Test exponential backoff calculation."""
        # Test basic exponential progression for network errors (initial_delay = 2.0)
        assert retry_handler.calculate_delay(0, ErrorType.NETWORK) == 2.0
        assert retry_handler.calculate_delay(1, ErrorType.NETWORK) == 4.0
        assert retry_handler.calculate_delay(2, ErrorType.NETWORK) == 8.0
        assert retry_handler.calculate_delay(3, ErrorType.NETWORK) == 16.0
    
    def test_max_delay_cap(self, retry_handler):
        """Test that delay is capped at max_delay."""
        # High attempt number should be capped at network-specific max_delay (120.0)
        delay = retry_handler.calculate_delay(10, ErrorType.NETWORK)
        assert delay == 120.0  # network-specific max_delay
    
    def test_error_specific_delays(self, retry_handler):
        """Test that different error types have different delay strategies."""
        # Rate limit errors should have longer delays
        rate_limit_delay = retry_handler.calculate_delay(0, ErrorType.RATE_LIMIT)
        network_delay = retry_handler.calculate_delay(0, ErrorType.NETWORK)
        
        assert rate_limit_delay > network_delay
        
        # Browser errors should have shorter delays
        browser_delay = retry_handler.calculate_delay(0, ErrorType.BROWSER)
        assert browser_delay < network_delay
    
    def test_jitter_randomization(self):
        """Test that jitter adds randomization to delays."""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            jitter=True
        )
        retry_handler = RetryHandler(config)
        
        # Calculate delays multiple times - should vary due to jitter
        # For NETWORK errors, the initial delay is actually 2.0, and attempt 1 gives 4.0
        delays = [retry_handler.calculate_delay(1, ErrorType.NETWORK) for _ in range(10)]
        
        # Should not all be exactly the same
        assert len(set(delays)) > 1
        
        # Should all be reasonably close to expected value (4.0 for network errors)
        # Allow wider range due to jitter (10% of 4.0 = 0.4)
        for delay in delays:
            assert 3.0 <= delay <= 5.0


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker for testing."""
        config = RetryConfig(
            circuit_breaker_threshold=3,
            circuit_breaker_timeout=1.0  # 1 second for testing
        )
        return CircuitBreaker(config)
    
    def test_initial_state(self, circuit_breaker):
        """Test circuit breaker initial state."""
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.can_execute() is True
        assert circuit_breaker.failure_count == 0
    
    def test_success_recording(self, circuit_breaker):
        """Test recording successful operations."""
        circuit_breaker.record_success()
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.last_success_time is not None
    
    def test_failure_threshold(self, circuit_breaker):
        """Test circuit breaker opening at failure threshold."""
        # Record failures up to threshold
        for i in range(2):
            circuit_breaker.record_failure()
            assert circuit_breaker.state == CircuitBreakerState.CLOSED
            assert circuit_breaker.can_execute() is True
        
        # Threshold failure should open circuit
        circuit_breaker.record_failure()
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        assert circuit_breaker.can_execute() is False
    
    def test_timeout_recovery(self, circuit_breaker):
        """Test circuit breaker recovery after timeout."""
        # Open the circuit
        for i in range(3):
            circuit_breaker.record_failure()
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        assert circuit_breaker.can_execute() is False
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Should transition to half-open
        assert circuit_breaker.can_execute() is True
        assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN
    
    def test_half_open_success(self, circuit_breaker):
        """Test successful operation in half-open state."""
        # Open circuit and wait for timeout
        for i in range(3):
            circuit_breaker.record_failure()
        time.sleep(1.1)
        circuit_breaker.can_execute()  # Triggers transition to half-open
        
        # Record success in half-open state
        circuit_breaker.record_success()
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.failure_count == 0
    
    def test_half_open_failure(self, circuit_breaker):
        """Test failed operation in half-open state."""
        # Open circuit and wait for timeout
        for i in range(3):
            circuit_breaker.record_failure()
        time.sleep(1.1)
        circuit_breaker.can_execute()  # Triggers transition to half-open
        
        # Record failure in half-open state
        circuit_breaker.record_failure()
        assert circuit_breaker.state == CircuitBreakerState.OPEN
    
    def test_status_reporting(self, circuit_breaker):
        """Test circuit breaker status reporting."""
        status = circuit_breaker.get_status()
        
        assert "state" in status
        assert "failure_count" in status
        assert "can_execute" in status
        assert status["state"] == "closed"
        assert status["failure_count"] == 0
        assert status["can_execute"] is True


class TestRetryExecution:
    """Test retry execution logic."""
    
    @pytest.fixture
    def retry_handler(self):
        """Create retry handler for testing."""
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.01,  # Very short delays for testing
            exponential_base=2.0,
            jitter=False
        )
        return RetryHandler(config)
    
    def test_successful_operation(self, retry_handler):
        """Test operation that succeeds on first try."""
        mock_operation = Mock(return_value="success")
        
        result = retry_handler.execute_with_retry(mock_operation, "test_op")
        
        assert result == "success"
        assert mock_operation.call_count == 1
        assert len(retry_handler.retry_history) == 0
    
    def test_operation_succeeds_after_retries(self, retry_handler):
        """Test operation that succeeds after some failures."""
        mock_operation = Mock()
        mock_operation.side_effect = [
            Exception("First failure"),
            Exception("Second failure"),
            "success"  # Succeeds on third try
        ]
        
        result = retry_handler.execute_with_retry(mock_operation, "test_op")
        
        assert result == "success"
        assert mock_operation.call_count == 3
        assert len(retry_handler.retry_history) == 2  # Two failed attempts recorded
    
    def test_operation_fails_all_retries(self, retry_handler):
        """Test operation that fails all retry attempts."""
        mock_operation = Mock(side_effect=Exception("Always fails"))
        
        with pytest.raises(Exception) as exc_info:
            retry_handler.execute_with_retry(mock_operation, "test_op")
        
        assert "Always fails" in str(exc_info.value)
        assert mock_operation.call_count == 3  # max_attempts
        assert len(retry_handler.retry_history) == 3
    
    def test_circuit_breaker_integration(self, retry_handler):
        """Test that circuit breaker blocks operations when open."""
        # Trigger circuit breaker by recording failures
        for i in range(5):  # Exceed threshold
            retry_handler.circuit_breaker.record_failure()
        
        mock_operation = Mock(return_value="success")
        
        with pytest.raises(Exception) as exc_info:
            retry_handler.execute_with_retry(mock_operation, "test_op")
        
        assert "Circuit breaker is open" in str(exc_info.value)
        assert mock_operation.call_count == 0  # Should not be called
    
    def test_custom_config_override(self, retry_handler):
        """Test using custom configuration for specific operations."""
        custom_config = RetryConfig(max_attempts=1)  # Only one attempt
        mock_operation = Mock(side_effect=Exception("Fails"))
        
        with pytest.raises(Exception):
            retry_handler.execute_with_retry(
                mock_operation, 
                "test_op", 
                custom_config=custom_config
            )
        
        assert mock_operation.call_count == 1  # Only one attempt due to custom config
    
    def test_retry_delay_timing(self, retry_handler):
        """Test that retry delays are actually applied."""
        # Use slightly longer delay for this test
        config = RetryConfig(
            max_attempts=2,
            initial_delay=0.1,
            jitter=False
        )
        handler = RetryHandler(config)
        
        mock_operation = Mock(side_effect=[Exception("Fail"), "success"])
        
        start_time = time.time()
        result = handler.execute_with_retry(mock_operation, "test_op")
        end_time = time.time()
        
        assert result == "success"
        # Should have taken at least the delay time
        assert end_time - start_time >= 0.1


class TestRetryStatistics:
    """Test retry statistics and monitoring."""
    
    @pytest.fixture
    def retry_handler(self):
        """Create retry handler for testing."""
        return RetryHandler()
    
    def test_empty_statistics(self, retry_handler):
        """Test statistics when no retries have occurred."""
        stats = retry_handler.get_retry_statistics()
        
        assert stats["total_attempts"] == 0
        assert stats["error_types"] == {}
        assert stats["average_delay"] == 0
    
    def test_retry_statistics_collection(self, retry_handler):
        """Test collection of retry statistics."""
        # Manually add some retry attempts
        retry_handler.retry_history = [
            RetryAttempt(1, ErrorType.NETWORK, "Network error", 1.0, datetime.now()),
            RetryAttempt(2, ErrorType.NETWORK, "Another network error", 2.0, datetime.now()),
            RetryAttempt(1, ErrorType.TIMEOUT, "Timeout error", 1.5, datetime.now()),
        ]
        
        stats = retry_handler.get_retry_statistics()
        
        assert stats["total_attempts"] == 3
        assert stats["error_types"]["network"] == 2
        assert stats["error_types"]["timeout"] == 1
        assert stats["average_delay"] == (1.0 + 2.0 + 1.5) / 3
        assert "circuit_breaker" in stats
        assert "recent_attempts" in stats
    
    def test_history_reset(self, retry_handler):
        """Test resetting retry history."""
        # Add some history
        retry_handler.retry_history = [
            RetryAttempt(1, ErrorType.NETWORK, "Error", 1.0, datetime.now())
        ]
        retry_handler.circuit_breaker.record_failure()
        
        # Reset
        retry_handler.reset_history()
        
        assert len(retry_handler.retry_history) == 0
        assert retry_handler.circuit_breaker.failure_count == 0
        assert retry_handler.circuit_breaker.state == CircuitBreakerState.CLOSED


class TestIntegration:
    """Integration tests for retry handler."""
    
    def test_real_world_scenario(self):
        """Test a realistic retry scenario."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=0.01,
            circuit_breaker_threshold=3
        )
        retry_handler = RetryHandler(config)
        
        # Simulate an operation that fails a few times then succeeds
        call_count = 0
        def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                if call_count == 1:
                    raise Exception("ConnectionError: network issue")
                elif call_count == 2:
                    raise Exception("TimeoutException: timed out")
                else:
                    raise Exception("500 Internal Server Error")
            return f"Success after {call_count} attempts"
        
        result = retry_handler.execute_with_retry(flaky_operation, "flaky_op")
        
        assert result == "Success after 4 attempts"
        assert len(retry_handler.retry_history) == 3
        
        # Check statistics
        stats = retry_handler.get_retry_statistics()
        assert stats["total_attempts"] == 3
        assert "network" in stats["error_types"]
        assert "timeout" in stats["error_types"]
        assert "server_error" in stats["error_types"]


if __name__ == "__main__":
    pytest.main([__file__])