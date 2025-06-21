# Notification Redesign Implementation Plan

## Overview
Redesigning notifications to be time-contextual with lesson-focused messaging:
- Morning: Goal setting
- Midday/Evening: Progress updates  
- Night: Daily recap

## Phase 1: Analysis & Planning
- [x] Review current notification system
- [x] Design new notification strategy
- [x] Create implementation plan
- [x] Analyze current code dependencies
- [x] Identify files that need modification

### Files to Modify:
- `src/notifiers/pushover_notifier.py` - Time-based notification templates
- `src/core/daily_tracker.py` - Daily lesson tracking & time detection
- `config/app_config.py` - New config if needed
- State file format updates for daily tracking

## Phase 2: Core Infrastructure Changes

### 2.1 Daily Lesson Tracking
- [x] Add daily lesson counter to state file
- [x] Implement daily reset logic (midnight boundary)
- [x] Add helper functions for daily lesson calculations
- [x] Test daily tracking logic

### 2.2 Time-Based Notification Logic
- [x] Create time-aware notification dispatcher
- [x] Add schedule type detection (morning/midday/evening/night)
- [x] Implement different notification triggers per time slot
- [x] Add priority level logic per schedule

### 2.3 Notification Content Updates
- [x] Create morning notification template (goal setting)
- [x] Create midday notification template (progress check)
- [x] Create evening notification template (final push)
- [x] Create night notification template (daily recap)
- [x] Update notification method signatures

## Phase 3: Integration & Logic

### 3.1 Daily Goal Calculation
- [x] Implement dynamic daily lesson goal calculation
- [x] Add progress percentage calculations
- [x] Create ahead/behind/on-track status detection
- [x] Add trajectory calculations for messaging

### 3.2 Smart Notification Logic
- [x] Morning: Always send goal-setting message
- [x] Midday: Send only if activity detected OR behind
- [x] Evening: Send only if activity detected OR behind goal
- [x] Night: Always send recap
- [x] Implement activity detection logic

### 3.3 Message Content Logic
- [x] Dynamic messaging based on progress status
- [x] Celebration messages for goal achievement
- [x] Motivational messages when behind
- [x] Streak status integration
- [x] Unit completion integration (secondary)

## Phase 4: Testing & Refinement

### 4.1 Unit Testing
- [x] Test daily lesson tracking
- [x] Test time-based logic
- [x] Test notification content generation
- [ ] Test edge cases (no activity, over-achievement)

### 4.2 Integration Testing
- [ ] Test full workflow with mock data
- [ ] Test cron job integration
- [ ] Verify state persistence
- [ ] Test notification delivery

### 4.3 Refinement
- [ ] Adjust messaging tone
- [ ] Fine-tune timing triggers
- [ ] Optimize notification frequency
- [ ] Clean up old code

## Phase 5: Deployment
- [ ] Update cron job configuration if needed
- [ ] Deploy to production
- [ ] Monitor first day of notifications
- [ ] Collect feedback and iterate

## Implementation Notes
- Keep it simple - don't over-engineer
- Focus on lessons as primary metric
- Units are secondary for trajectory only
- Commit at each major phase completion
- Ask for help if stuck

## Commit Strategy
- `notification redesign 1.1 - analysis and planning complete`
- `notification redesign 1.2 - daily lesson tracking implemented`  
- `notification redesign 1.3 - time-based notification logic added`
- `notification redesign 1.4 - notification content updated`
- `notification redesign 1.5 - integration complete`
- `notification redesign 1.6 - testing and refinement done`
- `notification redesign 1.7 - deployment complete` 