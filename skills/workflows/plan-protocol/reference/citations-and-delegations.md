# Citations & Delegations


### Where Citations Come From

Citations reference delegation research. The flow is:

1. You delegate research: `delegate` to `researcher` or `explore`
2. Delegation completes with a readable ID (e.g., `swift-amber-falcon`)
3. You cite that research in the plan: `ref:swift-amber-falcon`

### When to Cite

| Situation | Action |
|-----------|--------|
| Architectural decision based on research | Add to Context & Decisions table |
| Task informed by research | Append `→ ref:id` to task line |
| Implementation detail from research | Inline citation in Notes |

### How to Find Delegation IDs

- Use `delegation_list()` to see all delegations
- Use `delegation_read("id")` to verify content before citing

### ❌ NEVER

- Make up delegation IDs
- Cite without actually reading the delegation
- Skip citations for research-based decisions

---
