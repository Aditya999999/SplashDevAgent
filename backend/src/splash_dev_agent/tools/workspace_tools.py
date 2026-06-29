import os
import subprocess
from typing import Dict, Any, List

try:
    from mcp import FastMCP
    mcp = FastMCP("Splash Workspace Server")
except ImportError:
    # Fallback mock for environments without FastMCP installed
    class MockMCP:
        def tool(self):
            def decorator(func):
                return func
            return decorator
    mcp = MockMCP()

@mcp.tool()
async def read_workspace_file(path: str) -> str:
    """Read contents of a file in the workspace directory. Path must be relative to current workspace."""
    safe_path = os.path.abspath(path)
    if not os.path.exists(safe_path):
        return f"Error: File {path} does not exist."
    with open(safe_path, "r", encoding="utf-8") as f:
        return f.read()

@mcp.tool()
async def write_workspace_file(path: str, content: str) -> str:
    """Write/overwrite content to a file in the workspace directory."""
    safe_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(safe_path), exist_ok=True)
    with open(safe_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Success: File {path} has been written."

@mcp.tool()
async def run_compilation_or_test(command: str) -> Dict[str, Any]:
    """Execute a shell command/test suite within the workspace safely."""
    try:
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "status": "success" if process.returncode == 0 else "failed",
            "stdout": process.stdout,
            "stderr": process.stderr,
            "exit_code": process.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Command execution timed out after 30 seconds."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool()
async def get_workspace_diff() -> str:
    """Get the current unstaged changes via git diff."""
    try:
        process = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if not process.stdout.strip():
            return "No local modifications discovered."
        return process.stdout
    except Exception as e:
        return f"Error executing git diff: {str(e)}"
