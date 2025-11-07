<!--
Sync Impact Report:
- Version change: [UNVERSIONED] → 1.0.0
- Modified principles: All principles newly defined for MVP academic project
- Added sections: Core Principles (5 principles), Development Constraints, Workflow Requirements, Governance
- Removed sections: None (initial constitution)
- Templates requiring updates:
  ✅ plan-template.md - Constitution Check references this file
  ✅ spec-template.md - Test requirements aligned (tests optional)
  ✅ tasks-template.md - Test tasks marked as optional, aligns with no TDD requirement
- Follow-up TODOs: None
-->

# Abnormal Prediction in Chest X-Ray Constitution

## Core Principles

### I. MVP Academic Simplicity

This is an academic MVP project. Code MUST be straightforward and maintainable but does NOT require production-grade standards. Focus on demonstrable functionality and clear logic over enterprise patterns. Keep implementations concise while ensuring correctness and future maintainability.

**Rationale**: Academic projects prioritize learning, experimentation, and demonstration over production hardening. Overengineering reduces velocity and obscures learning outcomes.

### II. No Test-Driven Development

Testing is NOT required. Code can be written and validated through manual execution and logging. Unit tests, integration tests, and test frameworks are explicitly excluded from this project scope.

**Rationale**: MVP academic projects focus on proof-of-concept and rapid iteration. The overhead of maintaining test suites is not justified for a local-only demonstration project.

### III. Minimal Documentation Standards

Pre-commit hooks, comprehensive inline documentation, function annotations (type hints beyond basic clarity), and extensive API documentation are NOT required. Code should be self-explanatory through clear naming and structure.

**Rationale**: Documentation overhead slows development velocity in academic contexts. Code readability through good practices (clear names, logical structure) provides sufficient understanding for small-scale projects.

### IV. Comprehensive Logging

Detailed logging MUST be implemented for all major workflow steps. Logs MUST capture key decision points, data transformations, model operations, and error conditions. Logging serves as the primary mechanism for understanding system behavior and debugging.

**Rationale**: Without automated tests, comprehensive logging becomes critical for validation, debugging, and demonstrating correct execution flow.

### V. Implementation Summaries

After implementing new logic or code changes, a summary MUST be provided that includes:
- What was implemented (components, functions, logic)
- How to verify the implementation (manual steps, expected outputs)
- Any assumptions or limitations

**Rationale**: Explicit verification instructions ensure correctness and provide clear handoff documentation for academic review or future development.

## Development Constraints

### Local Deployment Only

All development, execution, and deployment MUST target local environments. No cloud infrastructure, containerization for deployment, or CI/CD pipelines are required.

**Rationale**: Academic projects run in controlled local environments. Infrastructure complexity is unnecessary overhead.

### Technology Stack

- **Language**: Python 3.12+
- **Deployment**: Local machine execution
- **Dependencies**: Minimal, declared in `pyproject.toml`
- **Storage**: Local filesystem (no external databases unless explicitly required)

### Code Quality Without Overhead

Code MUST be:
- Easy to understand (clear variable/function names, logical organization)
- Concise (avoid unnecessary abstraction)
- Functional (correct outputs, efficient execution)
- Maintainable (structured to allow future modifications)

Code does NOT need:
- Type annotations on every function
- Docstrings for obvious functions
- Complex design patterns (e.g., repository pattern, factories unless truly needed)
- Pre-commit hooks or linters (optional, not enforced)

## Workflow Requirements

### Development Cycle

1. **Plan**: Understand requirement and approach
2. **Implement**: Write clear, functional code with logging
3. **Log**: Ensure key steps produce informative logs
4. **Summarize**: Document what was built and how to verify
5. **Verify**: Manually test using provided verification steps

### Logging Standards

Logs MUST include:
- Timestamp and log level
- Component/module identifier
- Action or event description
- Relevant data (input shapes, key values, paths)
- Error messages with context
- Show color coding if console supports it

Use Python's `logging` module with appropriate levels (DEBUG, INFO, WARNING, ERROR).

### Verification Process

Every implementation MUST include verification guidance:
- **Setup steps**: Any prerequisites or data preparation
- **Execution command**: Exact command to run
- **Expected outputs**: Console output, log messages, file artifacts
- **Success indicators**: How to confirm correct behavior

## Governance

### Constitution Authority

This constitution defines the development standards for the Abnormal Prediction in Chest X-Ray project. All development decisions should align with these principles.

### Amendments

Amendments may be made when:
- Project scope changes (e.g., transitions from academic to production)
- New requirements emerge (e.g., collaboration needs mandate testing)
- Standards prove insufficient (e.g., logging inadequate for debugging)

Amendments MUST update this document and increment the version following semantic versioning.

### Versioning Policy

- **MAJOR**: Fundamental principle changes (e.g., TDD becomes mandatory)
- **MINOR**: New principles or sections added
- **PATCH**: Clarifications or wording improvements

### Compliance

Development MUST adhere to:
1. **Simplicity**: Reject unnecessary complexity
2. **Logging**: Comprehensive operational visibility
3. **Verification**: Clear manual testing paths
4. **Maintainability**: Code remains understandable and modifiable

Violations require explicit justification documented in implementation plans.

**Version**: 1.0.0 | **Ratified**: 2025-11-07 | **Last Amended**: 2025-11-07
