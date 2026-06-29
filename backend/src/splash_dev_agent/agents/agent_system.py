import os
import json
import asyncio
from typing import Dict, Any, List, Callable, Awaitable
from splash_dev_agent.agents.base import BaseAgent
from splash_dev_agent.llm.client import get_llm_client

# --- Event-Driven Communication Infrastructure ---
class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[Dict[str, Any]], Awaitable[None]]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    async def publish(self, event_type: str, data: Dict[str, Any]):
        print(f"[EventBus] Publishing Event: {event_type} - {list(data.keys())}")
        if event_type in self._listeners:
            tasks = [cb(data) for cb in self._listeners[event_type]]
            await asyncio.gather(*tasks)

event_bus = EventBus()

# --- Specialized Agent Implementations conforming to BaseAgent contract ---

class GenericAgent(BaseAgent):
    def __init__(self, name: str):
        self._name = name
        self.skills: Dict[str, Any] = {}
        self.memory: List[Dict[str, Any]] = []
        self.current_task: Optional[str] = None
        self.llm_client = get_llm_client()

    @property
    def name(self) -> str:
        return self._name

    async def initialize(self) -> None:
        print(f"[{self.name}] Initialized.")

    async def load_memory(self, session_id: str) -> None:
        # Load from in-memory or generic schema
        self.memory.append({"role": "system", "content": f"Loaded context for session {session_id}"})

    async def load_skills(self, language: str) -> None:
        # Dynamically load skill package files: Select Skill -> Load Metadata -> Load Instructions -> etc.
        skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills", language)
        if os.path.exists(skills_dir):
            try:
                for file_key in ["metadata", "prompts", "templates", "workflows", "examples", "tool_mappings"]:
                    path = os.path.join(skills_dir, f"{file_key}.json")
                    if os.path.exists(path):
                        with open(path, "r", encoding="utf-8") as f:
                            self.skills[file_key] = json.load(f)
                print(f"[{self.name}] Successfully loaded skills package for: {language}")
            except Exception as e:
                print(f"[{self.name}] Skill loading failure: {e}")
        else:
            print(f"[{self.name}] Skill package directory not found: {skills_dir}")

    async def plan(self, user_message: str) -> str:
        self.current_task = user_message
        return f"Decomposed task for {self.name}: {user_message}"

    async def execute(self, **kwargs) -> Dict[str, Any]:
        prompt = f"Agent {self.name} processing task: {self.current_task}. Context: {kwargs}"
        system_instruction = self.skills.get("prompts", {}).get("system_instruction", "You are an expert software developer.")
        
        response = await self.llm_client.generate_completion(prompt, system_prompt=system_instruction)
        return {"content": response, "status": "completed"}

    async def reflect(self) -> str:
        return f"Reflected on {self.name} execution success."

    async def validate(self) -> bool:
        return True

    async def finish(self) -> Dict[str, Any]:
        return {"agent": self.name, "status": "finished"}

# --- Specific Agent Classes with Custom Responsibilities ---

class PlannerAgent(GenericAgent):
    def __init__(self):
        super().__init__("planner")

class ExplorerAgent(GenericAgent):
    def __init__(self):
        super().__init__("explorer")

class CodingAgent(GenericAgent):
    def __init__(self):
        super().__init__("coding")

class ReviewerAgent(GenericAgent):
    def __init__(self):
        super().__init__("reviewer")

class TesterAgent(GenericAgent):
    def __init__(self):
        super().__init__("tester")

class DocumentationAgent(GenericAgent):
    def __init__(self):
        super().__init__("documentation")

class DeploymentAgent(GenericAgent):
    def __init__(self):
        super().__init__("deployment")
