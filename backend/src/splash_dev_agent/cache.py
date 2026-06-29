import json
from typing import Optional, Any
import redis
from splash_dev_agent.config import get_settings

class RedisCache:
    def __init__(self):
        settings = get_settings()
        try:
            self.client = redis.from_url(settings.REDIS_URL, socket_timeout=2.0)
            self.client.ping()
            self.is_connected = True
        except Exception:
            self.is_connected = False
            self._mock_cache = {}

    def _get_key(self, session_id: str, agent_name: str) -> str:
        return f"agent_result:{session_id}:{agent_name}"

    async def cache_agent_result(self, session_id: str, agent_name: str, result: Any, ex: int = 3600) -> None:
        key = self._get_key(session_id, agent_name)
        serialized = json.dumps(result)
        if self.is_connected:
            try:
                self.client.set(key, serialized, ex=ex)
            except Exception:
                self._mock_cache[key] = serialized
        else:
            self._mock_cache[key] = serialized

    async def get_cached_agent_result(self, session_id: str, agent_name: str) -> Optional[Any]:
        key = self._get_key(session_id, agent_name)
        serialized = None
        if self.is_connected:
            try:
                serialized = self.client.get(key)
            except Exception:
                serialized = self._mock_cache.get(key)
        else:
            serialized = self._mock_cache.get(key)

        if serialized:
            if isinstance(serialized, bytes):
                serialized = serialized.decode('utf-8')
            return json.loads(serialized)
        return None

_cache_instance: Optional[RedisCache] = None

def get_cache() -> RedisCache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance
