---
name: shell_execution
description: Execution guidelines for tests, compilation, linting, and running diagnostics in development workspace.
---

# Shell Execution Skill

This skill outlines strategies for running shell utilities, testing, and debugging errors.

## Best Practices
1. **Command Validation**: Scan commands to ensure no malicious loops or runaway background processes are started.
2. **Timeout Boundaries**: Hard timeout limit of 30 seconds for test compilations to preserve gateway capacity.
3. **Observation Feedback**: Capture standard errors (stderr) to feed logs directly back into execution loops.

## Integrated Tools via FastMCP
- `run_compilation_or_test(command)`: Runs tests or compiler operations.
