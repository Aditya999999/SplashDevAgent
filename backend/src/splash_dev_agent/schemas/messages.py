from pydantic import BaseModel, Field
from typing import Optional, List, Any

class SendMessageRequest(BaseModel):
    user_id: str
    user_message: str
    conversation_id: str
    workspace_id: str
    loop_mode: Optional[str] = "react"  # "react", "ralph", "deep"
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None

class SendMessageResponse(BaseModel):
    status: str = Field(..., description='Must be success, error, or processing')
    role: str = "assistant"
    content: str
    metadata: Optional[dict] = None
    artifacts: Optional[Any] = None
