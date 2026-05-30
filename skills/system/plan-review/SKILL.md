---
name: plan-review
description: "Criteria for reviewing implementation plans against quality standards"
user-invocable: true
license: MIT
compatibility: OpenCode, Claude Code, Cursor, Gemini CLI
metadata:
  author: OpenCode Ecosystem
  version: "2.1.0"
  openclaw:
        emoji: "📋"
    homepage: https://github.com/anomalyco/opencode
allowed-tools: Read Edit Write Glob Grep Bash Task SequentialThinking AskUserQuestion
---

# Plan Review

## TL;DR  
Systematic plan review focused on 3 quality categories: Citation Quality, Completeness, and Actionability. Structure is pre-validated by `plan_save`—focus on whether the plan provides actionable implementation guidance.

## When to Use

- When reviewing implementation plans before execution
- When auditing plan quality after creation
- When verifying plans meet documentation standards
- As part of the plan validation workflow

---


## Quick Reference Files

| File | Content |
|------|---------|
| `reference/plan-review-checklist.md` | Plan Review Checklist |
| `reference/severity-classification.md` | Severity Classification |
| `reference/output-format.md` | Output Format |
| `reference/what-not-to-do.md` | What NOT to Do |
| `reference/adherence-checklist.md` | Adherence Checklist |
