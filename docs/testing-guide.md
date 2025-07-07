# Owlgorithm Testing Guide

**Comprehensive testing workflow for developers and AI agents**

## Overview

This guide implements the Testing Integration PRD to prevent silent E2E failures and ensure reliable automated Duolingo progress tracking. The testing strategy uses an 80-20 approach: essential smoke tests catch 80% of real-world failures in under 30 seconds.

## Quick Start

### For AI Agents and Developers
```bash
# MANDATORY before ANY commit to src/ or scripts/
make test-smoke

# Additional testing options
make test-unit      # Unit tests only
make test-all       # Complete test suite 
make coverage       # With coverage report
```

### Test Execution Times
- **Smoke tests**: < 30 seconds (target achieved: ~0.4s)
- **Unit tests**: < 60 seconds  
- **Complete suite**: < 2 minutes

## Testing Strategy

### Tier 1: Essential Smoke Tests (< 30 seconds)
**Primary goal**: Catch 80% of real-world failures before they reach production

#### Test 1: Data Processing Pipeline + Content Validation
- **Purpose**: End-to-end validation of core data processing
- **Coverage**: 
  - Calculation logic (daily progress, performance metrics, lesson counting)
  - Notification content validation (no junk values)
  - Markdown generation functionality
- **Critical validations**:
  - No "undefined", "calculating...", "NaN", or error messages in outputs
  - Numeric values are within reasonable ranges (0-1000 for lessons)
  - Core functions return expected data structures

#### Test 2: Basic Environment Validation  
- **Purpose**: Quick validation of critical dependencies
- **Coverage**:
  - Python imports work correctly
  - Configuration access functions
  - File I/O operations
  - Basic error handling
- **Critical validations**:
  - All required modules import successfully
  - Configuration values are accessible
  - File operations don't crash
  - Error handling is graceful

### Tier 2: Unit Tests
**Purpose**: Detailed validation of individual components
- Comprehensive coverage of calculation functions
- Edge case handling
- Data validation logic
- Repository operations

### Tier 3: Integration Tests (Future)
**Purpose**: Full system validation for critical releases
- Real browser automation testing
- Live notification delivery testing
- Cross-component integration validation

## When to Run Tests

### Mandatory Testing Triggers
- ✅ **ANY changes to `src/` directory**
- ✅ **ANY changes to `scripts/` directory**  
- ✅ **Before suggesting version bumps**
- ✅ **Before committing to main branch**

### Optional Testing Scenarios
- Documentation-only changes
- Configuration template updates
- README modifications

## Common Failure Scenarios

### Scenario 1: Notification Content Issues
**Symptoms**: Junk values in push notifications
**Tests**: Smoke test validates notification content
**Common causes**: 
- Calculation functions returning None/undefined
- String formatting errors
- Missing data validation

**Example failure**:
```
AssertionError: Notification contains junk value: 'undefined' in message: 
"Daily progress: undefined lessons completed"
```

**Resolution**: Check calculation functions, add proper null handling

### Scenario 2: Environment/Import Problems
**Symptoms**: ImportError or AttributeError during startup
**Tests**: Environment validation catches missing dependencies
**Common causes**:
- Missing required packages
- Configuration file issues
- Path setup problems

**Example failure**:
```
Failed: Critical import failed: cannot import name 'calculate_daily_progress'
```

**Resolution**: Verify imports, check package installation

### Scenario 3: Calculation Errors
**Symptoms**: Incorrect lesson counts or progress percentages
**Tests**: Data processing pipeline validates calculation logic
**Common causes**:
- Logic errors in metrics calculation
- Data type mismatches
- Missing edge case handling

**Example failure**:
```
AssertionError: Progress percentage should be reasonable: 150.5
```

**Resolution**: Review calculation logic, add bounds checking

### Scenario 4: File Operation Failures
**Symptoms**: Can't read/write state files or markdown
**Tests**: Environment validation checks file I/O
**Common causes**:
- Permission issues
- Missing directories
- File locking conflicts

## Test Command Reference

### Basic Commands
```bash
# Run smoke tests (< 30 seconds)
make test-smoke

# Run unit tests only
make test-unit

# Run all tests
make test-all

# Generate coverage report
make coverage

# Clean test artifacts
make clean
```

### Direct pytest Usage
```bash
# Run specific test file
python -m pytest tests/integration/test_smoke.py -v

# Run with short traceback
python -m pytest tests/integration/test_smoke.py --tb=short

# Run single test method
python -m pytest tests/integration/test_smoke.py::TestEssentialSmokeTests::test_basic_environment_validation -v
```

### Performance Testing
```bash
# Time smoke test execution
time make test-smoke

# Check if under 30 second target
make test-smoke && echo "✅ Under 30 seconds" || echo "❌ Too slow"
```

## Integration with Development Workflow

### Standard Development Cycle
```bash
# 1. Make changes to core functionality
vim src/core/metrics_calculator.py

# 2. MANDATORY: Run smoke tests
make test-smoke
# Expected output: ✅ 2 passed in 0.43s

# 3. If tests pass, proceed with commit
git add src/core/metrics_calculator.py
git commit -m "fix(core): improve daily goal calculation

- Fixed edge case when no previous data exists
- Smoke tests: ✅ Passed (0.43s)
- Maintains backward compatibility"

# 4. Consider version bump if user-facing change
echo "2.0.1" > VERSION
git add VERSION docs/changelog.md
git commit -m "chore: bump version to 2.0.1 - calculation accuracy fix"
```

### AI Agent Workflow Integration
```bash
# AI agents MUST follow this pattern:

# Before ANY commit to src/ or scripts/:
make test-smoke

# Report results in commit message:
git commit -m "feat(notifier): add email fallback support

- Added SMTP client for email notifications
- Graceful fallback when Pushover unavailable  
- Smoke tests: ✅ Passed (0.38s)
- Ready for user testing"
```

### Failure Recovery Workflow
```bash
# If tests fail:
make test-smoke
# ❌ FAILED tests/integration/test_smoke.py - calculation error

# 1. DO NOT COMMIT - fix the issue first
# 2. Debug the specific failure
python -m pytest tests/integration/test_smoke.py::TestEssentialSmokeTests::test_data_processing_pipeline_with_content_validation -v

# 3. Fix the underlying issue
vim src/core/metrics_calculator.py

# 4. Re-run tests until they pass
make test-smoke
# ✅ 2 passed in 0.41s

# 5. Now safe to commit
git commit -m "fix(core): resolve calculation edge case

- Fixed division by zero in progress calculation
- Added bounds checking for percentage values
- Smoke tests: ✅ Passed (0.41s)"
```

## Production Pipeline Validation

### Isolation Guarantees
- **Separate test data**: Tests use fixtures, not production files
- **Temporary directories**: No interference with real state files  
- **Mocked external calls**: No real browser automation or API calls
- **Configuration overrides**: Tests use test-specific config values

### Production Safety Checks
```bash
# Verify tests don't affect production
ls data/          # Should not contain test files
cat tracker_state.json  # Should not be modified by tests

# Check automation is still working
python scripts/setup_cron.py status
python scripts/daily_update.py --username USERNAME
```

## Test Data and Fixtures

### Realistic Test Data
- `tests/fixtures/sample_scrape_data.json`: Realistic session data from production
- `tests/fixtures/sample_state_data.json`: Realistic tracker state
- Data includes multiple units, various session types, realistic XP values

### Fixture Maintenance
```bash
# Update fixtures with new production patterns (when needed)
cp data/latest_scrape.json tests/fixtures/sample_scrape_data.json
# Sanitize username and sensitive data
vim tests/fixtures/sample_scrape_data.json
```

## Performance Monitoring

### Target Metrics
- **Smoke tests**: < 30 seconds (currently ~0.4s ✅)
- **Unit tests**: < 60 seconds (currently ~48s ✅)
- **Coverage generation**: < 2 minutes

### Performance Validation
```bash
# Check smoke test performance
time make test-smoke
# Should complete in under 30 seconds

# Profile slow tests if needed
python -m pytest tests/integration/test_smoke.py --durations=10
```

## Troubleshooting

### Common Issues and Solutions

#### "Tests not found" error
```bash
# Solution: Ensure you're in project root
cd /path/to/owlgorithm
make test-smoke
```

#### Import errors in tests
```bash
# Solution: Check Python path and virtual environment
python -c "import src.core.metrics_calculator"
source duolingo_env/bin/activate  # If using virtual environment
```

#### "Permission denied" during testing
```bash
# Solution: Check file permissions
chmod +x scripts/daily_update.py
```

#### Tests pass locally but fail in automation
```bash
# Solution: Check environment differences
make test-smoke 2>&1 | tee test_output.log
# Review log for environment-specific issues
```

## Future Enhancements

### Tier 2 Integration Tests (Optional Future Work)
- **Scraper failure fallback**: Test graceful handling of browser automation failures
- **State corruption recovery**: Test recovery from corrupted state files
- **Cross-component integration**: Verify data flows correctly between modules

### Tier 3 E2E Validation (Optional Future Work)  
- **Real browser automation**: Test actual Firefox/geckodriver functionality
- **Live notification delivery**: Test real Pushover API integration

### Monitoring and Alerting (Future)
- **Test failure notifications**: Alert on repeated test failures
- **Performance regression detection**: Monitor test execution time trends
- **Production correlation**: Track test coverage vs production issues

## References

- **Testing Integration PRD**: `docs/prds/testing-integration-prd.md`
- **Test Implementation**: `tests/integration/test_smoke.py`
- **Makefile**: Root directory `Makefile`
- **CLAUDE.md**: Testing requirements section

---

**Remember**: Testing is not optional—it's mandatory for maintaining system reliability. Users depend on accurate daily notifications, and a failed test indicates a potential silent failure in production that could affect the user experience. 