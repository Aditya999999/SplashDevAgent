# Filesystem Access Skill

This skill governs how the agent interacts with workspace files securely and efficiently.

## Best Practices
1. **Scope Checking**: Always ensure target paths reside within the defined workspace directories.
2. **Atomic Writes**: Write small, target changes instead of replacing large files.
3. **Encoding**: Enforce UTF-8 encoding across all reads and writes.
