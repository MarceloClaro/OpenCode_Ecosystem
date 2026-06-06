# Plan Review Checklist


### 1. Structure (Pre-validated)

> **Note:** Saved plans are structurally validated by `plan_save` before storage.
> Format compliance (YAML frontmatter, status markers, CURRENT marker, numbering) is guaranteed.
> Focus your review on the quality aspects below.

### 2. Citation Quality

| Requirement | Check |
|-------------|-------|
| Decisions reference sources | `ref:delegation-id` format used |
| No unsubstantiated claims | Architectural decisions cite research |
| Research phases show refs | Completed research tasks include citations |
| Citations are verifiable | IDs match actual delegation outputs |

**Red Flags:**
- Decisions table with empty or `-` in Source column
- Claims like "industry standard" or "best practice" without citation
- Research tasks marked complete without `→ ref:id`

### 3. Completeness

| Requirement | Check |
|-------------|-------|
| Goal is specific | Measurable outcome, not vague intent |
| Phases are logical | Sequential, with clear progression |
| Edge cases considered | Error handling, failure modes addressed |
| Notes section present | Key decisions and observations documented |
| Context & Decisions table | Captures architectural choices with rationale |

**Goal Quality Examples:**
- ❌ "Improve authentication" (vague)
- ❌ "Make it better" (unmeasurable)
- ✅ "Add JWT authentication with refresh token support" (specific)
- ✅ "Migrate user table to PostgreSQL with zero downtime" (measurable)

### 4. PLANS.md Compliance

| Requirement | Check |
|-------------|-------|
| PLANS.md exists | Active plan tracking artifact present at workspace root |
| State machine obeyed | Exactly ONE phase `[IN PROGRESS]`, exactly ONE task `← CURRENT` |
| Versioning respected | Previous PLANS.md archived before overwrite |
| Consistency with detail plan | PLANS.md condensed version matches `thoughts/plans/{name}.md` |
| Critical context current | Relevant files, blockers, and decisions reflect reality |

### 5. Actionability

| Requirement | Check |
|-------------|-------|
| Tasks are specific | Clear what file/component is affected |
| No ambiguous tasks | Avoids "investigate" or "figure out" without scope |
| Dependencies clear | Sequential tasks show logical order |
| Implementation path obvious | Developer can start without clarification |

**Actionability Examples:**
- ❌ "Set up the backend" (too vague)
- ❌ "Make it work" (no implementation path)
- ✅ "Create `src/auth/jwt.ts` with sign/verify functions" (specific file)
- ✅ "Add bcrypt password hashing to `UserService.create()`" (clear scope)

---
