import datetime
from typing import List, Dict, Any, Optional
import pymongo
from splash_dev_agent.config import get_settings

class SessionHistoryManager:
    def __init__(self):
        settings = get_settings()
        try:
            self.client = pymongo.MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=2000)
            self.db = self.client.get_default_database()
            self.conversations = self.db["conversations"]
            # Trigger quick check
            self.client.server_info()
            self.is_connected = True
        except Exception:
            # Fallback to local in-memory dict for mock/development environment resilience
            self.is_connected = False
            self._mock_db: Dict[str, Dict[str, Any]] = {}

    async def save_message(self, session_id: str, user_id: str, workspace_id: str, role: str, content: str, framework_metadata: Optional[dict] = None) -> None:
        message_doc = {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.utcnow()
        }
        if framework_metadata:
            message_doc["framework_metadata"] = framework_metadata

        if self.is_connected:
            self.conversations.update_one(
                {"session_id": session_id, "user_id": user_id, "workspace_id": workspace_id},
                {"$push": {"messages": message_doc}},
                upsert=True
            )
        else:
            if session_id not in self._mock_db:
                self._mock_db[session_id] = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "workspace_id": workspace_id,
                    "messages": []
                }
            self._mock_db[session_id]["messages"].append(message_doc)

    async def load_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        if self.is_connected:
            return self.conversations.find_one({"session_id": session_id})
        return self._mock_db.get(session_id)

# Singleton helper instance
_db_manager: Optional[SessionHistoryManager] = None

def get_db_manager() -> SessionHistoryManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = SessionHistoryManager()
    return _db_manager
