---
name: filesystem_access
description: Guideline for developer agent filesystem operations, editing, and workspace manipulation.
---

# Filesystem Access Skill

This skill governs how the agent interacts with workspace files securely and efficiently.

## Best Practices
1. **Scope Checking**: Always ensure target paths reside within the defined workspace directories.
2. **Atomic Writes**: Write small, target changes instead of replacing large files.
3. **Encoding**: Enforce UTF-8 encoding across all reads and writes.

## Integrated Tools via FastMCP
- `read_workspace_file(path)`: Retrieves file text.
- `write_workspace_file(path, content)`: Creates or replaces target content.
