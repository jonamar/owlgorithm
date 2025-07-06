# Contributing to Owlgorithm

This document defines the development workflow and versioning philosophy for Owlgorithm. **AI agents should follow these guidelines when suggesting changes, commits, and version bumps.**

## 🎯 **Core Philosophy: User Impact Threshold**

**Version when users would care, not by calendar or commit count.**

### **The "Would I Update?" Test**
Before suggesting a version bump, ask:
> "If I were a user of this project, would I bother updating to get these changes?"

- **Yes, definitely** → MINOR or MAJOR bump
- **Yes, if it's easy** → PATCH bump  
- **Meh, not really** → Keep working, don't version yet

## 📋 **Version Bump Decision Framework**

### **✅ DO Version When:**
- Completed a user-facing feature (however small)
- Fixed a bug that impacts user experience
- Made setup/configuration easier  
- Added documentation that changes user workflow
- Accumulated 3-5+ small improvements that add up
- About to start risky work (lock in current stable state)
- Made a breaking change (immediate MAJOR bump)

### **❌ DON'T Version For:**
- Internal refactoring with no user impact
- Work-in-progress commits
- Dependency updates (unless user-visible)
- Code style/formatting changes
- Comment typo fixes
- Single-line bug fixes in development

## 🔄 **Commit and Version Workflow**

### **1. Atomic Commits (Always)**
```bash
# Good: One logical change per commit
feat(notifiers): add email backend interface
fix: handle edge case when sessions list is empty
docs: clarify Python version requirements

# Bad: Multiple unrelated changes
feat: add email, fix scraper, update docs, refactor utils
```

### **2. Feature Branch vs Direct-to-Main**

**Feature Branches (for larger/riskier work):**
```bash
git checkout -b feat/email-notifications
# Multiple related commits
git commit -m "feat(notifiers): add email backend"
git commit -m "feat(notifiers): implement SMTP client"  
git commit -m "test: add email notification tests"
# Merge when complete
git checkout main && git merge feat/email-notifications
```

**Direct-to-Main (for small improvements):**
```bash
# Small atomic commits as ideas arise
git commit -m "fix: improve error message for missing geckodriver"
git commit -m "docs: add M1 Mac troubleshooting notes"
```

### **3. Version Bump Commits (Separate & Clear)**
```bash
# When accumulated enough user value:
echo "1.3.0" > VERSION
# Update CHANGELOG.md with user-focused entries
git add VERSION CHANGELOG.md
git commit -m "chore: bump version to 1.3.0 - email notifications

### Added
- Email notifications as Pushover alternative
- SMTP configuration with validation

New users can now use email if Pushover isn't available."
```

## 📝 **Changelog Guidelines for AI Agents**

### **Focus on User Impact, Not Implementation**
```markdown
# Good (user-focused):
### Added
- Email notifications as Pushover alternative
- Dry-run mode for testing changes safely

### Fixed  
- Scraper crash when Duolingo has no recent sessions
- Setup script now works on M1 Macs

# Bad (implementation-focused):
### Added
- SMTP client class with TLS support
- --dry-run flag in ArgumentParser

### Fixed
- IndexError in session list processing
- Architecture detection in brew installation
```

### **Changelog Entry Template**
```markdown
## [X.Y.Z] - YYYY-MM-DD

### 🎉 What's New
**[Feature Name]**: [Why users care]
- [Specific user benefit]
- [Another user benefit]

### 🐛 What's Fixed
**[Problem Area]**: [What was broken and why it matters]

### 🛠️ For Developers (optional)
- [Internal improvements worth noting]
```

## 🤖 **AI Agent Decision Tree**

When suggesting commits and versions, follow this logic:

### **For Commits:**
1. **Is this one logical change?** → Good for atomic commit
2. **Does this change user-facing behavior?** → Note for potential version bump
3. **Does this break existing functionality?** → Requires immediate MAJOR version bump
4. **Is this work-in-progress?** → Don't suggest version bump yet

### **For Version Bumps:**
1. **Check recent commits** → Any user-facing changes since last version?
2. **Apply "Would I Update?" test** → Is there enough value?
3. **Classify impact:**
   - Breaking changes → MAJOR
   - New features → MINOR  
   - Bug fixes/improvements → PATCH
4. **If yes to step 2** → Suggest version bump with user-focused changelog

### **For Changelog Entries:**
1. **Group by user impact** → What problems does this solve?
2. **Lead with benefits** → Why users should care
3. **Use plain language** → Avoid technical jargon
4. **Include context** → Help users understand when they'd want this

## 🔍 **Quality Gates**

### **Before Suggesting Version Bump:**
- [ ] Can I explain why users would want this version in one sentence?
- [ ] Does the changelog read like "user benefits" not "code changes"?
- [ ] Are breaking changes clearly highlighted with migration notes?
- [ ] Has the system been tested end-to-end recently?

### **Commit Message Quality:**
- [ ] Uses conventional commit format (`feat:`, `fix:`, `docs:`, etc.)
- [ ] Describes the change, not the implementation
- [ ] Could be understood by someone who didn't write the code
- [ ] Is specific enough to be useful in git history

## 📊 **Version Number Guidelines**

### **MAJOR (X.0.0) - Breaking Changes**
- Configuration file format changes
- API changes that break existing usage
- Removal of features or commands
- Changes that require user action to upgrade

### **MINOR (x.Y.0) - New Features**
- New notification backends
- New command-line options
- Enhanced functionality
- New configuration options (backward compatible)

### **PATCH (x.y.Z) - Fixes & Improvements**
- Bug fixes
- Documentation improvements
- Small usability enhancements
- Dependency updates (when user-visible)

## 🎯 **Examples for Owlgorithm Context**

### **PATCH Example (1.3.1):**
```bash
# Recent commits:
- fix: better error message when geckodriver missing
- docs: add troubleshooting for M1 Macs
- feat: add --quiet flag for cron usage

# User impact: "Makes setup easier and debugging clearer"
# Version: PATCH (small improvements)
```

### **MINOR Example (1.4.0):**
```bash
# Recent commits:
- feat: add weekly progress summaries
- feat: implement streak tracking  
- test: add streak calculation tests

# User impact: "New insights into learning patterns"
# Version: MINOR (new feature complete)
```

### **MAJOR Example (2.0.0):**
```bash
# Recent commits:
- feat!: migrate from launchd to cron scheduling
- docs: add migration guide from 1.x

# User impact: "Cross-platform support but requires setup changes"
# Version: MAJOR (breaking change)
```

## 🚀 **Workflow Summary for AI Agents**

1. **Make atomic commits** with clear conventional commit messages
2. **Track user-facing changes** as you work
3. **Suggest version bumps** when accumulated changes pass "Would I Update?" test
4. **Write user-focused changelogs** that explain benefits, not implementation
5. **Test thoroughly** before version bumps
6. **Document breaking changes** clearly with migration guidance

This approach maintains quality while staying flexible and user-focused. 