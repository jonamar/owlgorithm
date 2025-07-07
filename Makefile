# Owlgorithm Testing Integration Makefile
# Phase 0: Basic test infrastructure
# 
# This Makefile provides a unified interface for running tests
# and supports the Testing Integration PRD requirements.

.PHONY: help test-unit test-smoke test-high-value test-integration test-all clean coverage

# Default target
help:
	@echo "Owlgorithm Testing Integration"
	@echo "============================="
	@echo ""
	@echo "Available targets:"
	@echo "  help             - Show this help message"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-smoke       - Run smoke tests only (< 30 seconds)"
	@echo "  test-high-value  - Run high-value development tests"
	@echo "  test-integration - Run all integration tests (smoke + high-value)"
	@echo "  test-all         - Run all tests (unit + integration)"
	@echo "  coverage         - Run tests with coverage report"
	@echo "  clean            - Clean test artifacts"
	@echo ""
	@echo "Usage:"
	@echo "  make test-unit        # Run existing unit tests"
	@echo "  make test-smoke       # Run essential smoke tests (MANDATORY for commits)"
	@echo "  make test-high-value  # Run additional development safety tests"
	@echo "  make test-all         # Run complete test suite"
	@echo ""

# Unit tests - existing pytest setup
test-unit:
	@echo "🧪 Running unit tests..."
	python -m pytest tests/unit/ -v

# Smoke tests - essential E2E validation (< 30 seconds)
test-smoke:
	@echo "🚀 Running smoke tests..."
	@if [ ! -f tests/integration/test_smoke.py ]; then \
		echo "⚠️  Smoke tests not implemented yet. Run 'make test-unit' instead."; \
		exit 1; \
	fi
	python -m pytest tests/integration/test_smoke.py -v --tb=short

# High-value tests - additional development safety
test-high-value:
	@echo "🔧 Running high-value development tests..."
	@if [ ! -f tests/integration/test_high_value.py ]; then \
		echo "⚠️  High-value tests not implemented yet."; \
		exit 1; \
	fi
	python -m pytest tests/integration/test_high_value.py -v --tb=short

# Integration tests - smoke + high-value
test-integration: test-smoke test-high-value
	@echo "🔗 Integration tests completed"

# All tests - comprehensive test suite  
test-all: test-unit test-integration
	@echo "✅ All tests completed"

# Coverage report
coverage:
	@echo "📊 Running tests with coverage..."
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Clean test artifacts
clean:
	@echo "🧹 Cleaning test artifacts..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	@echo "✅ Test artifacts cleaned" 