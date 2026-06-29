import os
import json
from typing import Dict, Any, List
from splash_dev_agent.agents.base import BaseAgent
from splash_dev_agent.llm.client import get_llm_client
from splash_dev_agent.tools.workspace_tools import (
    read_workspace_file,
    write_workspace_file,
    run_compilation_or_test,
    get_workspace_diff
)
from splash_dev_agent.agents.orchestrator import WorkflowOrchestrator

class DeveloperAgent(BaseAgent):
    def __init__(self):
        self.skills: Dict[str, Any] = {}
        self.memory: List[Dict[str, Any]] = []
        self.session_id: str = "default"

    @property
    def name(self) -> str:
        return "developer"

    async def initialize(self) -> None:
        print("[DeveloperAgent] Initialized.")

    async def load_memory(self, session_id: str) -> None:
        self.session_id = session_id

    async def load_skills(self, language: str) -> None:
        skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills", language)
        if os.path.exists(skills_dir):
            for file_key in ["metadata", "prompts", "templates", "workflows", "examples", "tool_mappings"]:
                path = os.path.join(skills_dir, f"{file_key}.json")
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        self.skills[file_key] = json.load(f)

    async def plan(self, user_message: str) -> str:
        return f"Developer Agent execution plan for: {user_message}"

    async def execute(self, **kwargs) -> Dict[str, Any]:
        user_message = kwargs.get("user_message", "")
        loop_mode = kwargs.get("loop_mode", "react")
        language = kwargs.get("language", "python")
        
        metadata = {
            "loop_mode": loop_mode,
            "session_id": self.session_id,
            "status": "completed"
        }
        
        # Route to multi-agent orchestrator loop if "deep" mode is requested
        if loop_mode == "deep":
            orch = WorkflowOrchestrator(session_id=self.session_id, language=language)
            res = await orch.run_workflow(user_message)
            metadata["orchestration_log"] = res.get("log", [])
            return {
                "content": f"### Deep Multi-Agent Workflow Completed\n\nPipeline steps:\n" + "\n".join([f"- {item}" for item in res.get("log", [])]),
                "metadata": metadata,
                "artifacts": {"orchestrator_results": res}
            }
        
        if loop_mode == "ralph":
            return await self._run_ralph_loop(user_message, metadata)
        else:
            return await self._run_react_loop(user_message, metadata)

    async def reflect(self) -> str:
        return "Developer agent reflect completed."

    async def validate(self) -> bool:
        return True

    async def finish(self) -> Dict[str, Any]:
        return {"status": "finished"}

    async def _run_react_loop(self, user_message: str, metadata: dict) -> Dict[str, Any]:
        llm_client = get_llm_client()
        history = [f"User: {user_message}"]
        steps = []
        
        # Max 3 turns of ReAct thought-action-observation
        for turn in range(3):
            system_prompt = (
                "You are an AI Developer executing a ReAct loop. "
                "Format your response EXACTLY as:\n"
                "Thought: <your reasoning>\n"
                "Action: <write_file path='<path>' content='<content>' | read_file path='<path>' | run_cmd cmd='<cmd>'>\n"
                "If no further action is required, output 'Final Answer: <your explanation>'"
            )
            
            prompt = "\n".join(history) + f"\nTurn {turn + 1}. Choose your next Action/Thought."
            response = await llm_client.generate_completion(prompt, system_prompt=system_prompt)
            steps.append(response)
            history.append(f"Agent: {response}")
            
            if "Final Answer:" in response or "Action:" not in response:
                break
                
            # Parse simple action execution for demonstration/test verification
            observation = "Action processed."
            if "run_cmd cmd=" in response:
                cmd = response.split("run_cmd cmd=")[1].strip("'\" \n")
                res = await run_compilation_or_test(cmd)
                observation = f"Result of command: {res}"
            elif "write_file path=" in response:
                observation = "Successfully written file."
                
            history.append(f"Observation: {observation}")
            steps.append(f"Observation: {observation}")
            
        metadata["react_steps"] = steps
        return {
            "content": f"### ReAct Execution Process Completed\n\n" + "\n\n".join(steps),
            "metadata": metadata,
            "artifacts": {"steps_count": len(steps)}
        }

    async def _run_ralph_loop(self, user_message: str, metadata: dict) -> Dict[str, Any]:
        prd_path = "prd.json"
        progress_path = "progress.txt"
        
        # Read or initialize prd.json
        prd_content = {}
        if os.path.exists(prd_path):
            try:
                prd_content = json.loads(await read_workspace_file(prd_path))
            except Exception:
                prd_content = {"requirements": []}
        else:
            prd_content = {"requirements": [user_message], "status": "Initiated"}
            await write_workspace_file(prd_path, json.dumps(prd_content, indent=2))
            
        # Get local Git diffs
        git_diff = await get_workspace_diff()
        
        # Append progress log
        progress_log = f"Attempting task step: {user_message}\nWorkspace status: {git_diff[:200]}\n"
        await write_workspace_file(progress_path, progress_log)
        
        llm_client = get_llm_client()
        prompt = (
            f"Requirements: {prd_content}\n"
            f"Current Workspace git diff:\n{git_diff}\n"
            f"Instructions: Generate a remediation recommendation report and outline the next step."
        )
        
        completion = await llm_client.generate_completion(prompt, system_prompt="You are an autonomous Ralph loop step executor.")
        
        # Update files with final step outcome
        prd_content["status"] = "Step Completed"
        await write_workspace_file(prd_path, json.dumps(prd_content, indent=2))
        
        metadata["ralph_files"] = [prd_path, progress_path]
        return {
            "content": f"### Ralph Loop Turn Completed\n\n{completion}\n\n*Progress updated in workspace files (`prd.json`, `progress.txt`)*",
            "metadata": metadata,
            "artifacts": {"prd": prd_content, "git_diff_length": len(git_diff)}
        }
