# Plan Overview: Daily Goal Fix + Future Enhancements

## 🚨 **URGENT**: Daily Goal Notification Fix
**Problem**: Notifications show "X/1 lessons today" instead of "X/12 lessons today"
**Solution**: See `plan-urgent-fix.md` for immediate implementation

## 🔮 **FUTURE**: Enhanced Goal Tracking & Analytics  
**Enhancement**: 18-month goal tracking, burn rate analysis, data model improvements
**Solution**: See `plan-future-enhancements.md` for comprehensive roadmap

---

## 📋 Plan Split Rationale

This plan was **split into two files** to maintain clear priorities:

### `plan-urgent-fix.md` - **IMPLEMENT FIRST**
- ✅ **Same-day fix** for broken notifications  
- ✅ **Minimal risk** to existing automation
- ✅ **Clear success criteria**: "X/12 lessons today"
- ✅ **3 files changed**, focused approach

### `plan-future-enhancements.md` - **IMPLEMENT AFTER**
- 🔮 **4 major epics** for comprehensive improvements
- 🔮 **11-15 days** of development work
- 🔮 **Advanced features**: goal tracking, burn rate analysis
- 🔮 **Requires stable foundation** from urgent fix first

## 🎯 Recommended Approach

1. **Week 1**: Complete `plan-urgent-fix.md` 
   - Fix daily goal notifications immediately
   - Verify automation stability
   
2. **Week 2+**: Begin `plan-future-enhancements.md`
   - Start with Epic 1 (calculation unification)
   - Add goal tracking and analytics incrementally

This approach ensures the critical notification bug is resolved quickly while preserving the roadmap for comprehensive improvements.

---

## 📊 Quick Reference

### Current State (Broken)
- Daily goal shows "1 lesson/day" in notifications
- Complex calculation mixing historical + tracking data
- Logic duplication between notifications and markdown

### After Urgent Fix
- Daily goal shows "12 lessons/day" in notifications  
- Simple hardcoded constant, no calculation
- Stable automation, immediate problem solved

### After Future Enhancements
- 18-month goal tracking with burn rate analysis
- Single source of truth for all calculations
- Rich progress analytics and insights

**Next Step**: Implement `plan-urgent-fix.md` to resolve the notification bug immediately.