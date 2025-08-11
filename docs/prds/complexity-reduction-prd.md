# Complexity Reduction PRD - Strategic Technical Debt Management

**Project**: Owlgorithm Complexity Reduction Initiative  
**Document Version**: 1.1  
**Date**: January 2025  
**Status**: Ready for Implementation

## 🎯 Problem Statement

### Current Technical Debt Assessment
- **High-complexity functions**: 17 functions with CCN > 10 (unchanged count)
- **Critical complexity hotspots**: 2 functions with CCN ≥ 30 remain the top risks
- **New/raised hotspots**: `core/daily_tracker.py::main` (now CCN 16), `core/metrics_calculator.py::{calculate_performance_metrics (18), get_tracked_unit_progress (15)}`
- **Concentrated complexity**: Majority remains in scraping; some growth in core flow/orchestration

### Latest Complexity Audit Results (current)
```
🔍 Overall: GOOD; focused refactors recommended
📊 Blocks analyzed: 226
🧮 Average complexity: A (3.99)
✅ Maintainability: All files A-grade
⚠️ Warnings (examples):
  - scrapers/duome_raw_scraper.py::parse_session_data  CCN 39
  - scrapers/duome_raw_scraper.py::calculate_recent_lessons_per_unit  CCN 31
  - scrapers/duome_raw_scraper.py::scrape_duome  CCN 18
  - core/metrics_calculator.py::{calculate_performance_metrics 18, get_tracked_unit_progress 15}
  - core/daily_tracker.py::main  CCN 16
  - core/markdown_updater.py::update_markdown_file  CCN 15
  - scrapers/enhanced_scraper.py::_validate_data_quality  CCN 19
```

### Guiding Principles (Scope Guardrails)
- **Boring, obvious, simple**: Prefer tiny, local refactors over architectural changes
- **Healthy modularity without over-engineering**: Extract small helpers within the same file
- **No speculative complexity**: Avoid new packages/patterns unless clearly necessary
- **Behavior-preserving refactors**: Zero functional changes; improve structure only

## 📊 Success Metrics (Primary KPI = Cyclomatic Complexity)

### Primary KPIs
- **Function-level CCN reductions:**
  - `parse_session_data` 39 → ≤ 12
  - `calculate_recent_lessons_per_unit` 31 → ≤ 10
  - `_validate_data_quality` 19 → ≤ 10
  - `scrape_duome` 18 → ≤ 12
  - `core/daily_tracker.py::main` 16 → ≤ 12
  - `core/metrics_calculator.py::calculate_performance_metrics` 18 → ≤ 12
  - `core/metrics_calculator.py::get_tracked_unit_progress` 15 → ≤ 10
  - `core/markdown_updater.py::update_markdown_file` 15 → ≤ 9
- **No new functions above CCN 12** in PRs touching targeted files
- **Average codebase complexity** stays A and does not regress

### Secondary KPIs
- Reduced conditional depth via guard clauses and early returns
- Fewer nested loops by splitting into linear, focused helpers
- Improved readability measured by smaller function lengths (target: ≤ 60 LOC for helpers)

## 🏗️ Refactor Approach (Minimalist)

- **Local, in-file extractions**: Private helpers (`_helper_name`) colocated with callers
- **Guard clauses**: Replace nested conditionals with early returns
- **Straight-line steps**: Sequence transformations into named steps (one responsibility each)
- **Naming over comments**: Clear function names to reduce need for heavy comments
- **Tiny PRs**: 1-2 functions per PR to keep risk low and reviews fast
- **No new directories/patterns**: Avoid Strategy/Builder/Factory unless a future need is proven

## 📋 Requirements Specification

### R1: Critical Functions (Phase 1)
- `scrapers/duome_raw_scraper.py::parse_session_data` (39 → ≤ 12)
  - Extract 4-6 tiny helpers: `_parse_lessons`, `_parse_units`, `_parse_progress`, `_normalize_fields`, `_validate_required_keys`
  - Flatten if/elif ladders using guard clauses and simple dispatch maps where obvious
- `scrapers/duome_raw_scraper.py::calculate_recent_lessons_per_unit` (31 → ≤ 10)
  - Split into: `_group_by_unit`, `_summarize_unit`, `_aggregate_recent_window`
  - Ensure each helper has ≤ 2 nested levels

### R2: High Value Core Paths (Phase 1.5)
- `core/metrics_calculator.py::calculate_performance_metrics` (18 → ≤ 12)
  - Extract: `_compute_daily`, `_compute_projection`, `_compute_completion_stats`
- `core/metrics_calculator.py::get_tracked_unit_progress` (15 → ≤ 10)
  - Extract: `_select_tracked_units`, `_derive_progress_row`, `_accumulate_totals`
- `core/daily_tracker.py::main` (16 → ≤ 12)
  - Extract straight-line steps: `_load_state`, `_maybe_reset_daily`, `_run_scrape`, `_update_metrics`, `_maybe_notify`, `_save_and_exit`

### R3: Medium Priority (Phase 2)
- `scrapers/enhanced_scraper.py::_validate_data_quality` (19 → ≤ 10)
  - Extract simple rule-check helpers like `_has_required_fields`, `_within_expected_ranges`, `_no_duplicate_sessions`
- `core/markdown_updater.py::update_markdown_file` (15 → ≤ 9)
  - Extract formatting helpers: `_render_header`, `_render_stats_section`, `_write_if_changed`

### R4: Safety and Validation
- Behavior must remain identical; add/adjust unit tests only when splitting makes testing easier
- Keep helpers private and colocated; avoid cross-file dependencies
- Prefer linear data transformations over clever abstractions

## 🔧 Implementation Plan (Small, Safe, Fast)

### Phase 1 (2-3 days, boring refactors)
1. `parse_session_data` → iterative extractions until CCN ≤ 12
2. `calculate_recent_lessons_per_unit` → split path; target CCN ≤ 10

### Phase 1.5 (1-2 days)
3. `metrics_calculator` pair (18 and 15) → extract 2-3 helpers each
4. `core/daily_tracker.py::main` → linearize into 5-6 obvious steps

### Phase 2 (2-3 days)
5. `_validate_data_quality` → carve out simple validators
6. `update_markdown_file` → format helpers; add write-on-change

### Tooling (No new infra required)
- Optional local checks before PR:
  - `radon cc src/ -a --total-average`
  - `lizard src/ --CCN 10 | head -n 60`
- No CI gate changes required for this initiative

## 📊 Risk & Mitigation
- **Regression risk**: Keep changes small; run `make test-smoke` per edit; favor pure helpers
- **Readability risk**: Name helpers for intent; keep each ≤ 60 LOC
- **Scope creep**: No new modules/patterns unless post-Phase 2 need is proven

## 🚀 Business Value
- Faster, safer edits in complex scraping areas
- Lower onboarding overhead; more obvious code paths
- Measurable CCN reductions without architectural churn

## 📈 Success Criteria
- Primary KPI targets achieved per function listed in R1–R3
- No new function introduced with CCN > 12 in touched files
- Tests pass (`make test-smoke`), no behavior change reported
- Average complexity stays A; hotspot list reduced on `lizard` warnings

---

This revision aligns with “boring, obvious, simple, healthily modular” goals by favoring within-file extractions, guard clauses, and linearized flows. It sets concrete CCN targets and avoids introducing speculative complexity or new architecture. 