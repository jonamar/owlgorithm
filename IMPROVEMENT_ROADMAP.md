# Owlgorithm Improvement Roadmap

*A structured plan to enhance maintainability, reliability, and extensibility*

## 📋 Context & Motivation

Based on comprehensive codebase audit (June 2025), Owlgorithm demonstrates solid engineering fundamentals but suffers from common maintainability challenges:

- **615-line daily_tracker.py** handling multiple responsibilities 
- **Complex session parsing** with nested loops and fragile logic
- **Manual JSON operations** without atomic writes or corruption recovery
- **No automated testing** infrastructure for validation
- **Fragile DOM parsing** susceptible to duome.eu site changes

This roadmap addresses these issues through focused, incremental improvements that preserve existing functionality while building toward a more maintainable architecture.

## 🎯 Implementation Strategy

### Core Philosophy: "Working Replacements, Not Theoretical Improvements"

**Lesson from notification debugging saga**: Never replace fragile-but-working code with theoretically-robust code that doesn't actually work.

- **Phase-based approach**: Complete one category before moving to next
- **Working replacement strategy**: Each change must work equivalently to what it replaces
- **No backwards compatibility**: Single user means we can move forward and replace deprecated code
- **Immediate validation**: Test replacement works before removing original
- **Rollback readiness**: Each phase has a rollback plan if issues arise

### Git Workflow

- **Feature branches**: `feature/phase-1a-refactor-core`, `feature/phase-2a-atomic-ops`, etc.
- **Frequent commits**: Commit working increments, not just completed features
- **Commit message pattern**: `[Phase-Task] Brief description - working/tested/complete`
- **Branch strategy**: 
  - `main` - always working production code
  - `feature/phase-X` - development branch for each phase
  - Merge only after validation that replacement works
- **Validation gates**: Each merge requires:
  - [ ] Manual test of core functionality (scrape → process → notify)
  - [ ] No regression in daily operations
  - [ ] Rollback plan documented

### Git Commands Reference
```bash
# Start Phase 1A
git checkout main
git checkout -b feature/phase-1a-refactor-core
git commit -m "[Phase-1A] Backup original daily_tracker.py - working"

# Frequent commits during development
git add src/core/metrics_calculator.py
git commit -m "[Phase-1A] Extract metrics_calculator.py - tested"
git add tests/test_metrics_calculator.py  
git commit -m "[Phase-1A] Add tests for metrics_calculator - all passing"

# Before merge validation
python scripts/daily_update.py  # Must work identically
git checkout main
git merge feature/phase-1a-refactor-core

# Emergency rollback if needed
git revert HEAD  # Or restore daily_tracker_original.py
```

---

## Phase 1: Code Organization & Maintainability 🏗️

*Foundation improvements for easier development and debugging*

### Priority 1A: Refactor Core Module (HIGH)
- [ ] **1.1** Extract `src/core/orchestrator.py` from daily_tracker.py
  - [ ] Move main workflow coordination logic
  - [ ] Keep dependencies minimal (config, logging, state management)
  - [ ] Test equivalent functionality to current main()
- [ ] **1.2** Create `src/core/metrics_calculator.py`
  - [ ] Extract `calculate_performance_metrics()`
  - [ ] Extract `calculate_unit_completion_metrics()`  
  - [ ] Extract `calculate_daily_progress()`
  - [ ] Add input validation for all functions
- [ ] **1.3** Create `src/core/markdown_updater.py`
  - [ ] Extract `update_markdown_file()` (146 lines)
  - [ ] Centralize regex patterns as constants
  - [ ] Add markdown template validation
  - [ ] Test against existing personal-math.md
- [ ] **1.4** Slim down daily_tracker.py
  - [ ] Keep only orchestration imports and main()
  - [ ] Verify all functionality preserved
  - [ ] Update CLAUDE.md documentation

### Priority 1B: Testing Infrastructure (HIGH)
- [ ] **1.5** Set up testing framework
  - [ ] Install pytest and testing dependencies
  - [ ] Create `tests/` directory structure
  - [ ] Add `conftest.py` with common fixtures
- [ ] **1.6** Unit tests for core components
  - [ ] Test metrics_calculator functions with sample data
  - [ ] Test markdown_updater regex patterns
  - [ ] Test session parsing with mock JSON data
  - [ ] Achieve >80% code coverage for core modules
- [ ] **1.7** Integration tests
  - [ ] Mock duome.eu responses for scraper tests
  - [ ] End-to-end workflow test (scrape → process → notify)
  - [ ] Test error handling paths

### Priority 1C: Logging Framework (MEDIUM)
- [ ] **1.8** Implement structured logging
  - [ ] Replace print statements with logging calls
  - [ ] Add log levels (DEBUG/INFO/WARN/ERROR)
  - [ ] Configure file rotation in logs/ directory
- [ ] **1.9** Add error tracking
  - [ ] Centralized exception handling
  - [ ] Error context and stack traces
  - [ ] Performance timing logs

---

## Phase 2: Data Reliability & State Management 💾

*Robust data handling and state consistency*

### Priority 2A: Atomic Operations (HIGH)
- [ ] **2.1** Create `src/data/repository.py`
  - [ ] Abstract JSON file operations
  - [ ] Implement atomic write operations (temp file → rename)
  - [ ] Add file locking for concurrent access
- [ ] **2.2** State validation and recovery
  - [ ] Validate state.json schema on load
  - [ ] Automatic backup before state updates
  - [ ] Corruption detection and recovery mechanisms
- [ ] **2.3** Replace existing state operations
  - [ ] Update daily_tracker to use repository
  - [ ] Test state consistency across failures
  - [ ] Remove old JSON handling code after validation

### Priority 2B: Schema Versioning (MEDIUM)
- [ ] **2.4** Add version tracking
  - [ ] Add `"schema_version": "1.0"` to all JSON files
  - [ ] Create migration framework in `src/data/migrations/`
  - [ ] Test version detection and handling
- [ ] **2.5** Schema evolution framework
  - [ ] V1.0 → V1.1 example migration
  - [ ] One-time migration on startup if needed
  - [ ] Migration testing with sample data

### Priority 2C: Data Access Layer (LOW)
- [ ] **2.6** Centralize data operations
  - [ ] Abstract file path management
  - [ ] Consistent error handling patterns
  - [ ] Prepare for future database migration

---

## Phase 3: Scraping Resilience & Error Recovery 🛡️

*Robust scraping that adapts to failures and site changes*

### Priority 3A: Retry Logic (HIGH)
- [ ] **3.1** Implement intelligent retry
  - [ ] Exponential backoff for network failures
  - [ ] Different retry strategies by error type
  - [ ] Maximum retry limits and circuit breaker
- [ ] **3.2** Enhanced error recovery
  - [ ] Graceful degradation when automation fails
  - [ ] Fallback to cached data when appropriate
  - [ ] User notification for persistent failures

### Priority 3B: Scraping Strategy Abstraction (MEDIUM)
- [ ] **3.3** Create strategy framework
  - [ ] `src/scrapers/strategies/` directory
  - [ ] Base strategy interface
  - [ ] Firefox automation strategy
  - [ ] HTTP fallback strategy
- [ ] **3.4** Strategy selection logic
  - [ ] Automatic strategy choice based on success rates
  - [ ] Strategy health monitoring
  - [ ] Easy addition of new strategies

### Priority 3C: Robust DOM Parsing (MEDIUM)
- [ ] **3.5** Multiple selector strategies
  - [ ] Primary and fallback CSS selectors
  - [ ] Content-based parsing for critical data
  - [ ] Validation of parsed data quality
- [ ] **3.6** Site change adaptation
  - [ ] Flexible parsing rules
  - [ ] Automatic fallback detection
  - [ ] Monitoring for parsing failures

---

## 📝 Implementation Notes

### Completed Items
*Track lessons learned and important decisions made during implementation*

*None yet - will be populated as work progresses*

### Current Blockers
*Issues preventing progress on specific tasks*

*None identified*

### Architecture Decisions
*Record significant design choices and rationale*

*Will be populated during implementation*

### Rollback Plans & Validation Gates

**Phase 1 Rollback**: 
- Keep original daily_tracker.py as daily_tracker_original.py until Phase 1 complete
- Validation: New modules must produce identical outputs to original
- Rollback trigger: Any regression in daily operations

**Phase 2 Rollback**:
- Keep backup of tracker_state.json before atomic operations
- Validation: State operations must not corrupt data
- Rollback trigger: Any data loss or corruption

**Phase 3 Rollback**:
- Keep current scraper as fallback if new strategies fail
- Validation: Scraping success rate must not decrease
- Rollback trigger: <90% scraping success rate

### Validation Checklist (Before Each Merge)
- [ ] **Manual smoke test**: Run `python scripts/daily_update.py` successfully
- [ ] **Output comparison**: New code produces same results as original
- [ ] **Error handling**: Graceful failure under expected error conditions
- [ ] **Performance**: No significant slowdown in execution time
- [ ] **State consistency**: No corruption of tracker_state.json or data files

---

## 🎯 Best Practices & Learnings

### Code Organization
- **Single Responsibility**: Each module should have one clear purpose
- **Dependency Injection**: Pass dependencies rather than importing globally
- **Error Boundaries**: Fail fast with clear error messages
- **Working First**: Replacement must work before removing original
- **Immediate Validation**: Test each change against real data immediately

### Testing Strategy
- **Working Replacement Test**: New code must handle your actual data correctly
- **Test Pyramid**: Unit tests (fast) → Integration tests (medium) → E2E tests (slow)
- **Mock External Dependencies**: duome.eu, filesystem, network calls
- **Test Error Paths**: Don't just test happy path scenarios
- **Real Data Validation**: Every change tested against actual duome.eu data

### Data Management
- **Atomic Operations**: Always use temp files + rename for updates
- **Schema Evolution**: Version all data formats from day one
- **Validation First**: Validate inputs before processing

### Error Handling
- **Retry with Backoff**: Network operations should retry intelligently
- **Graceful Degradation**: Continue operation when non-critical components fail
- **User Communication**: Inform user of failures and recovery actions

### Scraping Resilience
- **Multiple Strategies**: Don't depend on single parsing approach
- **Change Detection**: Monitor for site changes that break parsing
- **Respectful Scraping**: Include delays and respect robots.txt

---

## 🚀 Getting Started

### Phase 1 Kickoff Checklist
- [ ] **Document current behavior**: Record exactly what daily_tracker.py does today
- [ ] **Backup working system**: Full repo backup + test current functionality
- [ ] **Create feature branch**: `git checkout -b feature/phase-1a-refactor-core`
- [ ] **Establish validation baseline**: Run current system, record outputs
- [ ] **Install testing framework**: pytest, coverage tools
- [ ] **Define "working" criteria**: What must work before we merge each change

### Success Metrics
- **Code Maintainability**: Reduce largest file from 615 → <200 lines
- **Test Coverage**: Achieve >80% coverage for core logic
- **Error Recovery**: Zero data corruption events
- **Scraping Reliability**: >95% successful scrape rate
- **Zero Regressions**: No functionality lost during refactoring
- **Working Replacements**: Every change works with real data before merge

---

*Last Updated: June 28, 2025*  
*Next Review: After Phase 1 completion*