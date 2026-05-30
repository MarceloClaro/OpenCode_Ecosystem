# Contributing to OpenCode Ecosystem

Thank you for your interest in contributing to the OpenCode Ecosystem! This document provides guidelines and standards for contributions.

---

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct.html). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## How to Contribute

### Reporting Issues

- **Bug reports:** Include steps to reproduce, expected behavior, actual behavior, and environment details (OS, Python version, Node.js version, OpenCode CLI version)
- **Feature requests:** Describe the use case, proposed solution, and any alternatives considered
- **Documentation improvements:** Point out specific sections that need clarification or correction

### Development Workflow

1. **Fork and clone** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-contribution
   ```
3. **Make your changes** following the coding standards below
4. **Run tests** to ensure nothing is broken
5. **Submit a pull request** with a clear description of the changes

### Pull Request Process

1. Ensure all tests pass before submitting
2. Update documentation if your changes affect public APIs, agent definitions, or configuration
3. Include a clear PR title and description explaining the motivation and approach
4. Reference any related issues
5. Maintainers will review your PR and may request changes
6. Once approved, your PR will be squashed and merged

### PR Checklist

- [ ] Tests pass (`python -m pytest tests/ -v`)
- [ ] No CJK characters in output files
- [ ] Skills respect the 2.5KB size limit (where applicable)
- [ ] Documentation updated (if applicable)
- [ ] Code follows established patterns in the module

---

## Coding Standards

### General Principles

- **Readability over cleverness** — Write code that is easy to understand
- **Type safety** — Use type hints in Python and TypeScript
- **Test coverage** — New code should include unit tests
- **Documentation** — Public functions and classes must have docstrings
- **Consistency** — Follow the patterns already established in the module you are editing

### Python

| Requirement | Standard |
|-------------|----------|
| **Minimum version** | Python 3.12+ |
| **Docstrings** | Required for all public functions and classes (Google-style preferred) |
| **Type hints** | Required for all function signatures |
| **Testing** | pytest with fixtures and mocking |
| **Linting** | ruff (configured in project) |

### TypeScript

| Requirement | Standard |
|-------------|----------|
| **Runtime** | Bun 1.3+ compatible |
| **Modules** | ESModules |
| **Style** | Follow patterns in existing `plugins/` code |

### Skills (YAML/Markdown)

- Each `SKILL.md` must have complete YAML frontmatter with `name`, `description`, `trigger`, and `version`
- Content should be concise; extended documentation goes in `references/*.md` (progressive disclosure)
- Skills should stay within the 2.5KB limit for context optimization

### Language Requirements

- **User-facing documentation and output:** Brazilian Portuguese (formal)
- **Code comments and commit messages:** English or Portuguese
- **Variable names, paths, code:** Keep in original language (typically English)
- **Zero tolerance for CJK characters** in output files — run the CJK corrector before submitting documentation

---

## Testing Requirements

- Run all existing tests before submitting:
  ```bash
  python -m pytest tests/ -v
  ```
- New features must include corresponding tests
- Bug fixes should include a regression test
- Test coverage should not decrease with your contribution
- For academic pipeline changes, run the TDD validator:
  ```bash
  # Check TDD documentation for specific validation commands
  ```

---

## Adding New Components

### Adding a New Agent

1. Create a Markdown file in `agents/` with YAML frontmatter
2. Follow the template of existing agents
3. Register with the DI Container if the agent needs ecosystem services
4. Update agent counts in documentation

### Adding a New Skill

1. Create a directory under `skills/<category>/`
2. Create `SKILL.md` with YAML frontmatter (max 2.5KB)
3. Add extended content in `references/*.md`
4. Verify file size: `wc -c SKILL.md` should be ≤ 2500

### Adding a New MCP Server

1. Configure the server in `opencode.json` under `mcpServers`
2. Implement JSON-RPC over stdio (local) or HTTP (remote)
3. MCPs initialize on first use (lazy init) — no explicit startup code needed
4. Document the new MCP in the README

---

## Questions?

Open an issue on GitHub. All contributions are welcome — from bug fixes to new features, documentation improvements, and academic use cases.

---

<div align="center">

**OpenCode Ecosystem v4.6** · Contributing Guide

</div>
