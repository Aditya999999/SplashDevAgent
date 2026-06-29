import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from splash_dev_agent.config import get_settings

PUBLIC_PATHS = {"/health", "/api/status", "/mcp/status", "/docs", "/openapi.json"}

def verify_jwt_token(token: str) -> dict:
    settings = get_settings()
    try:
        # Decode the token using the secret and algorithm
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        raise ValueError(f"Invalid authentication token: {str(e)}")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exemption list check
        path = request.url.path
        if path in PUBLIC_PATHS or any(path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        # Token extraction
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        
        if not token:
            token = request.headers.get("X-Auth-Token")
            
        if not token:
            token = request.cookies.get("authToken")

        if not token:
            return JSONResponse(
                status_code=401,
                content={"status": "error", "message": "Missing authentication credentials"}
            )

        try:
            claims = verify_jwt_token(token)
            request.state.jwt_claims = claims
        except ValueError as e:
            return JSONResponse(
                status_code=401,
                content={"status": "error", "message": str(e)}
            )

        return await call_next(request)
