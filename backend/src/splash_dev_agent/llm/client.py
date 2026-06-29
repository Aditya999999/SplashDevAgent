import os
from typing import List, Dict, Any, Optional
from splash_dev_agent.config import get_settings

class LLMClient:
    def __init__(self):
        self.settings = get_settings()
        self.provider = self.settings.LLM_PROVIDER
        
        # Initialize Anthropic SDK if active
        self.anthropic_client = None
        if self.provider == "anthropic":
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=self.settings.ANTHROPIC_API_KEY)
            except Exception:
                pass

        # Initialize OpenAI SDK if active
        self.openai_client = None
        if self.provider == "openai":
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=self.settings.OPENAI_API_KEY)
            except Exception:
                pass

    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        # Context compaction check - truncate prompt middle if it exceeds limit
        max_prompt_chars = 60000
        if len(prompt) > max_prompt_chars:
            half = max_prompt_chars // 2
            prompt = prompt[:half] + "\n... [Context truncated to prevent token blowup] ...\n" + prompt[-half:]

        # OpenAI Execution Path
        if self.provider == "openai":
            if self.openai_client:
                try:
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})
                    
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    return response.choices[0].message.content or ""
                except Exception as e:
                    return f"Error executing OpenAI call: {str(e)}"
            return f"Mock OpenAI Completion for: {prompt[:100]}..."

        # Anthropic Execution Path
        elif self.provider == "anthropic":
            if self.anthropic_client:
                try:
                    messages = [{"role": "user", "content": prompt}]
                    extra_headers = {"anthropic-beta": "prompt-caching-2024-07-31"}
                    
                    # Call Anthropic API
                    response = self.anthropic_client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        messages=messages,
                        system=system_prompt if system_prompt else "",
                        max_tokens=max_tokens,
                        temperature=temperature,
                        extra_headers=extra_headers
                    )
                    # Handle message block types
                    return response.content[0].text if response.content else ""
                except Exception as e:
                    return f"Error executing Anthropic call: {str(e)}"
            return f"Mock Anthropic Completion for: {prompt[:100]}..."

        return f"Unsupported provider: {self.provider}"

# Singleton client getter
_llm_client_instance: Optional[LLMClient] = None

def get_llm_client() -> LLMClient:
    global _llm_client_instance
    if _llm_client_instance is None:
        _llm_client_instance = LLMClient()
    return _llm_client_instance
