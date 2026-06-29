---
name: git_operations
description: Track modifications, view version control logs, and inspect active repo diff states.
---

# Git Operations Skill

This skill governs the developer agent's interactions with Git.

## Best Practices
1. **Incremental Diff Tracking**: Inspect active diffs before and after edits to confirm correctness.
2. **Deterministic Checks**: Check `git status` output to determine clean workspace baselines.

## Integrated Tools via FastMCP
- `get_workspace_diff()`: Extracts active unstaged changes to track progress.
