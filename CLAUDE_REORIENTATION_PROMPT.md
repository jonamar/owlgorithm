# Claude Code Reorientation Prompt

**Use this prompt when starting Claude Code in the new ~/Development/owlgorithm/ directory:**

---

I just migrated my Owlgorithm project from ~/Documents/owlgorithm/ to ~/Development/owlgorithm/ to solve chronic automation failures. The project is a Python-based Duolingo progress tracker with automated notifications.

**CURRENT STATUS:**
- ✅ Phase 1 refactoring complete (615→335 lines, -45% reduction)  
- ✅ Comprehensive test suite (29 tests, 99% coverage)
- ✅ Migration from Documents folder complete (just finished)
- ❌ Automation still broken - need to update runner script paths
- **GOAL**: Get 5 consecutive automated notifications working

**ROOT CAUSE IDENTIFIED:** macOS security blocks launchd access to ~/Documents/ folder (exit code 78: "Operation not permitted"). Migration to ~/Development/ should solve this.

**IMMEDIATE NEXT STEPS:**
1. Update `/Users/jonamar/bin/owlgorithm-daily-runner` paths from Documents to Development
2. Test manual execution from new location
3. Test runner script from new location  
4. Reload launchd job and test automation
5. Monitor for first successful automated notification (breakthrough!)

**SUCCESS CRITERIA:** 5 consecutive automated notifications working perfectly

**KEY FILES:**
- Main tracker: `src/core/daily_tracker.py`
- Runner script: `/Users/jonamar/bin/owlgorithm-daily-runner` (needs path updates)
- LaunchAgent: `~/Library/LaunchAgents/com.owlgorithm.duolingo.plist`
- Migration plans: `SAFE_MIGRATION_PLAN.md`, `CLAUDE.md`

Please help me complete the post-migration steps to fix the automation that's been broken for months. Manual execution works perfectly - this is purely an environment/path issue now.

---

**Copy this prompt when starting Claude Code in ~/Development/owlgorithm/**