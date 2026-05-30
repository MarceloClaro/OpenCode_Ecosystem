# The 4 Review Layers


### Layer 1: Correctness
- Logic errors and edge cases
- Error handling completeness
- Type safety and null checks
- Algorithm correctness
- Off-by-one errors

### Layer 2: Security
- No hardcoded secrets or API keys
- Input validation and sanitization
- Injection vulnerability prevention (SQL, XSS, command)
- Authentication and authorization checks
- Sensitive data not logged
- OWASP Top 10 awareness

### Layer 3: Performance
- No N+1 query patterns
- Appropriate caching strategies
- No unnecessary re-renders (React/frontend)
- Lazy loading where appropriate
- Memory leak prevention
- Algorithmic complexity concerns

### Layer 4: Style & Maintainability
- Adherence to project conventions (check AGENTS.md)
- Code duplication (DRY violations)
- Complexity management (cyclomatic complexity)
- Documentation completeness
- Test coverage gaps
