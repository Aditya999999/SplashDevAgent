from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """System-wide unique identifier for the agent."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialise agent dependencies and states."""
        pass

    @abstractmethod
    async def load_memory(self, session_id: str) -> None:
        """Retrieve previous conversational context from persistence stores."""
        pass

    @abstractmethod
    async def load_skills(self, language: str) -> None:
        """Dynamically load metadata, prompts, templates, and mappings for target language."""
        pass

    @abstractmethod
    async def plan(self, user_message: str) -> str:
        """Decompose requirements or build local execution step patterns."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Perform tool actions and log outcomes."""
        pass

    @abstractmethod
    async def reflect(self) -> str:
        """Evaluate action outcomes against plan goals."""
        pass

    @abstractmethod
    async def validate(self) -> bool:
        """Check outputs for syntax correctness or design compliance."""
        pass

    @abstractmethod
    async def finish(self) -> Dict[str, Any]:
        """Wrap and aggregate final output returns."""
        pass
