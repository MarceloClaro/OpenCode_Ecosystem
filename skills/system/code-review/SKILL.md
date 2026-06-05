---
name: code-review
description: "Metodologia abrangente de revisao de codigo com classificacao de gravidade e limites de confianca"
user-invocable: true
license: MIT
compatibility: OpenCode, Claude Code, Cursor, Gemini CLI
metadata:
  author: OpenCode Ecosystem
  version: "2.1.0"
  openclaw:
        emoji: "🔍"
    homepage: https://github.com/anomalyco/opencode
allowed-tools: Read Edit Write Glob Grep Bash Diff Eslint
---

# Code Review

## TL;DR  
Systematic code review across 4 layers with severity classification. Only report findings with ≥80% confidence. Include file:line references for all issues.

## When to Use

- Before reporting implementation completion
- When explicitly asked to review code
- When using the `/review` command
- As an independent audit after code changes


## Quick Reference Files

| File | Content |
|------|---------|
| `reference/review-layers.md` | The 4 Review Layers |
| `reference/severity-classification.md` | Severity Classification |
| `reference/confidence-threshold.md` | Confidence Threshold |
| `reference/review-process.md` | Review Process |
| `reference/output-format.md` | Output Format |
| `reference/what-not-to-do.md` | What NOT to Do |
| `reference/adherence-checklist.md` | Adherence Checklist |
