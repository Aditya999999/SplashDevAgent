from fastapi import APIRouter, Depends, Request, HTTPException
from splash_dev_agent.schemas.messages import SendMessageRequest, SendMessageResponse
from splash_dev_agent.database import get_db_manager, SessionHistoryManager
from splash_dev_agent.cache import get_cache, RedisCache
from splash_dev_agent.agents.developer_agent import DeveloperAgent

router = APIRouter()

@router.post("/messages", response_model=SendMessageResponse)
async def send_message(
    body: SendMessageRequest,
    request: Request,
    db: SessionHistoryManager = Depends(get_db_manager),
    cache: RedisCache = Depends(get_cache)
):
    # Retrieve claims injected by AuthMiddleware
    jwt_claims = getattr(request.state, "jwt_claims", None)
    if not jwt_claims:
        raise HTTPException(status_code=401, detail="Authentication failed or credentials missing")

    # 1. Volatile Cache Lookup
    cached_result = await cache.get_cached_agent_result(body.conversation_id, "developer")
    if cached_result:
        return SendMessageResponse(
            status="success",
            role="assistant",
            content=cached_result.get("content", ""),
            metadata=cached_result.get("metadata"),
            artifacts=cached_result.get("artifacts")
        )

    # 2. Inbound Interaction Preservation (Save user message)
    await db.save_message(
        session_id=body.conversation_id,
        user_id=body.user_id,
        workspace_id=body.workspace_id,
        role="user",
        content=body.user_message
    )

    # 3. Agent Processing execution
    agent = DeveloperAgent()
    try:
        await agent.initialize()
        await agent.load_memory(body.conversation_id)
        await agent.load_skills("python")
        
        result = await agent.execute(
            user_message=body.user_message,
            loop_mode=body.loop_mode,
            conversation_id=body.conversation_id,
            workspace_id=body.workspace_id
        )
    except Exception as e:
        return SendMessageResponse(
            status="error",
            content=f"An execution exception occurred: {str(e)}"
        )

    # 4. Outbound Interaction Preservation (Save agent message)
    await db.save_message(
        session_id=body.conversation_id,
        user_id=body.user_id,
        workspace_id=body.workspace_id,
        role="assistant",
        content=result.get("content", ""),
        framework_metadata=result.get("metadata")
    )

    # 5. Cache response to volatile cache
    await cache.cache_agent_result(body.conversation_id, "developer", result)

    return SendMessageResponse(
        status="success",
        role="assistant",
        content=result.get("content", ""),
        metadata=result.get("metadata"),
        artifacts=result.get("artifacts")
    )
