from contextlib import asynccontextmanager
from fastapi import FastAPI
from splash_dev_agent.middleware.auth import AuthMiddleware
from splash_dev_agent.routers import messages
from splash_dev_agent.tools.workspace_tools import mcp

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Orchestrate startup events for both FastAPI & FastMCP sub-apps here
    print("[Lifespan] Starting Splash Financial Developer Agent services...")
    yield
    # Shutdown: Clean up database connections/resource pools
    print("[Lifespan] Stopping services and cleaning up database connections...")

app = FastAPI(
    title="Splash Financial Developer Agent API",
    description="Microservices API gateway for autonomous developer agents",
    version="1.0.0",
    lifespan=lifespan
)

# Mount security validation middleware
app.add_middleware(AuthMiddleware)

# Include core messaging REST routes
app.include_router(messages.router, prefix="/api", tags=["Messages"])

# Mount FastMCP server as an ASGI sub-application
# Handles custom tools under sub-path `/mcp`
try:
    mcp_asgi = mcp.http_app()
    app.mount("/mcp", mcp_asgi)
except AttributeError:
    # Handle environment mockup fallbacks if http_app helper is absent
    @app.get("/mcp/status")
    async def mcp_status():
        return {"status": "running", "mode": "mocked"}
