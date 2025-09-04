# Agentic Refactoring Guide

## Core Principle

**Good refactoring for AI agents = SUBTRACTION of complexity, not addition of "helpful" systems.**

Agents get lost in complex codebases, but the solution isn't building frameworks—it's making code **boring and predictable**.

## When to Refactor vs When to Leave Alone

### ✅ Refactor When:
- **Functions >50 lines** → Agents lose context
- **Files >500 lines** → Too much to scan at once  
- **Duplicate code exists** → Agents update one copy, miss others
- **File names don't match contents** → Agents look in wrong places
- **Import depth >3 levels** (`../../../`) → Agents get lost in hierarchy
- **Dead code exists** → Confuses agents about what's actually used

### ❌ Leave Alone When:
- **It works and agents can navigate it** → Don't fix what isn't broken
- **You want to "make it more flexible"** → Flexibility = unpredictability for agents
- **You're tempted to "future-proof"** → Solve today's problems, not tomorrow's
- **It's "not following best practices"** → Agent-friendly > academically correct

## The Five Critical Tests

### 1. The "Grep Test"
**Can an agent find what it needs with simple search?**

✅ **Good:** `grep "generateResume"` → finds one clear function  
❌ **Bad:** `grep "generate"` → finds 15 wrapper methods and interfaces

### 2. The "Obvious Location Test" 
**Is there only one obvious place to put new code?**

✅ **Good:** Theme changes go in `theme.ts`  
❌ **Bad:** Theme changes could go in `config/`, `styles/`, `theme/`, or `design-system/`

### 3. The "15-Minute Human Test"
**Can a human understand the change in 15 minutes?**

✅ **Good:** "Moved user validation logic from controller to service"  
❌ **Bad:** "Implemented abstract factory pattern with dependency injection for service creation"

### 4. The "Agent Onboarding Test"
**Can you explain the codebase to an agent in 3 sentences?**

✅ **Good:** "Generate resumes with `generateResume()`. Analyze keywords with `analyzeKeywords()`. Services are in the `services/` folder."  
❌ **Bad:** "First understand the service registry, then the dependency injection container, then the abstract factory pattern..."

### 5. The "Rollback Test"
**Can you undo the change in 5 minutes?**

✅ **Good:** Delete a file, update 2 imports  
❌ **Bad:** Remove framework, update 20 files, reconfigure build system

## What Good vs Bad Looks Like

### File Organization

✅ **Agent-Friendly (Flat & Obvious):**
```
services/
├── hiring-evaluation.ts      # Does hiring evaluation
├── keyword-analysis.ts       # Analyzes keywords  
├── document-generation.ts    # Generates documents
└── vale-linting.ts          # Lints with Vale
```

❌ **Agent-Confusing (Deep & Abstract):**
```
src/
├── core/
│   ├── services/
│   │   ├── providers/
│   │   │   ├── implementations/
│   │   │   │   ├── hiring/
│   │   │   │   │   └── evaluation-service-impl.ts
│   │   │   └── abstractions/
│   │   │       └── base-service-provider.ts
│   │   └── factories/
│   │       └── service-factory.ts
```

### Function Design

✅ **Agent-Friendly (Specific & Predictable):**
```typescript
export function generateResume(candidateData: CandidateData): ResumeDocument {
  // Agent knows exactly what this does
}

export function analyzeKeywords(jobText: string): KeywordAnalysis {
  // Agent can predict the behavior
}
```

❌ **Agent-Confusing (Generic & Flexible):**
```typescript
export function process<T>(data: T, config: ProcessConfig): ProcessResult<T> {
  // Agent has no idea what this actually does
}

class ServiceFactory {
  createService(type: string): BaseService {
    // Agent can't predict what gets returned
  }
}
```

### Import Patterns

✅ **Agent-Friendly (Direct & Clear):**
```typescript
import { generateResume } from '../services/document-generation';
import { analyzeKeywords } from '../services/keyword-analysis';
import { evaluateCandidate } from '../services/hiring-evaluation';
```

❌ **Agent-Confusing (Indirect & Abstract):**
```typescript
import { ServiceRegistry } from '../core/registry';
import { ServiceFactory } from '../core/factory';

const registry = ServiceRegistry.getInstance();
const service = registry.get('documentGeneration');
```

## Practical Refactoring Patterns

### Pattern 1: Extract Long Functions
**When:** Function >50 lines  
**How:** Break into smaller, named functions in same file

```typescript
// Before: 80-line function agents can't track
function processApplication(data: ApplicationData) {
  // ... 80 lines of mixed logic
}

// After: Clear, trackable steps
function processApplication(data: ApplicationData) {
  const validated = validateApplicationData(data);
  const keywords = extractKeywords(validated);
  const resume = generateResume(validated, keywords);
  return resume;
}

function validateApplicationData(data: ApplicationData) { /* ... */ }
function extractKeywords(data: ApplicationData) { /* ... */ }
function generateResume(data: ApplicationData, keywords: Keywords) { /* ... */ }
```

### Pattern 2: Delete Dead Code
**When:** Files/functions not used anywhere  
**How:** Search for references, delete if none found

```bash
# Find if function is used anywhere
grep -r "functionName" .

# If no results (except definition), delete it
```

### Pattern 3: Consolidate Duplicates
**When:** Same logic in multiple places  
**How:** Extract to single location, import from there

```typescript
// Before: Duplicated in 3 files
function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

// After: Single location
// utils/date-formatting.ts
export function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}
```

### Pattern 4: Flatten Deep Hierarchies
**When:** More than 3 levels of nesting  
**How:** Move files up, use clear naming

```typescript
// Before: src/core/services/implementations/hiring/evaluation/runner.ts
// After: services/hiring-evaluation.ts
```

### Pattern 5: Make Names Obvious
**When:** File/function names don't indicate purpose  
**How:** Rename to match actual function

```typescript
// Before: Confusing names
utils.ts              // What utils?
processor.js          // Processes what?  
manager.ts           // Manages what?

// After: Obvious names
date-formatting.ts    // Formats dates
resume-generator.ts   // Generates resumes
keyword-analyzer.ts   // Analyzes keywords
```

## Red Flags That Signal Over-Engineering

### 🚨 Immediate Stop Signals:
- Creating interfaces for things that will never be swapped
- Building "reusable" components for single use cases
- Adding configuration for things that never change
- Creating abstractions to "future-proof" the code
- Building frameworks when simple functions would work

### 🚨 Language Red Flags:
- "This will make it easier to..."
- "We need this for consistency..."
- "This follows best practices..."
- "Let's make this more flexible..."
- "We should abstract this..."

## The Meta-Rule

> **If your refactoring makes the code harder for a new agent to understand, you're going in the wrong direction.**

**Test:** After refactoring, could you drop a fresh agent into the codebase and have it successfully complete a task in the area you just changed?

If yes → Good refactoring  
If no → Over-engineering

## Quick Decision Framework

When considering any code change, ask:

1. **Am I solving a real problem that exists today?** (Not future problems)
2. **Am I making the code more predictable?** (Not more flexible)
3. **Am I removing complexity?** (Not adding helpful systems)
4. **Can I explain this change in one sentence?** (Not a paragraph)
5. **Would this help an agent understand the code faster?** (Not impress other engineers)

If any answer is "No" → Stop and find a simpler approach.

---

**Remember:** The best code is boring, obvious, and predictable. Agents (and humans) love boring code.

 