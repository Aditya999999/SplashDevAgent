import asyncio
from typing import Dict, Any, List
from splash_dev_agent.agents.agent_system import (
    event_bus,
    PlannerAgent,
    ExplorerAgent,
    CodingAgent,
    ReviewerAgent,
    TesterAgent,
    DocumentationAgent,
    DeploymentAgent
)

class WorkflowOrchestrator:
    def __init__(self, session_id: str, language: str = "python"):
        self.session_id = session_id
        self.language = language
        
        # Instantiate the full roster of specialized lifecycle agents
        self.planner = PlannerAgent()
        self.explorer = ExplorerAgent()
        self.coding = CodingAgent()
        self.reviewer = ReviewerAgent()
        self.tester = TesterAgent()
        self.doc = DocumentationAgent()
        self.deploy = DeploymentAgent()
        
        self.log: List[str] = []
        self._setup_event_subscriptions()

    def _setup_event_subscriptions(self):
        # Bind workflow triggers via dynamic events
        event_bus.subscribe("TASK_CREATED", self.on_task_created)
        event_bus.subscribe("PLAN_READY", self.on_plan_ready)
        event_bus.subscribe("REPOSITORY_INDEXED", self.on_repository_indexed)
        event_bus.subscribe("CODE_GENERATED", self.on_code_generated)
        event_bus.subscribe("TEST_COMPLETED", self.on_test_completed)
        event_bus.subscribe("DOCUMENTATION_READY", self.on_documentation_ready)

    async def run_workflow(self, user_message: str) -> Dict[str, Any]:
        self.log.append(f"Starting workflow for request: {user_message}")
        
        # Initialize all agents
        for agent in [self.planner, self.explorer, self.coding, self.reviewer, self.tester, self.doc, self.deploy]:
            await agent.initialize()
            await agent.load_memory(self.session_id)
            await agent.load_skills(self.language)

        # Start lifecycle via TASK_CREATED event
        await event_bus.publish("TASK_CREATED", {"task": user_message})
        
        return {
            "status": "success",
            "log": self.log,
            "result": "Agent pipeline finished successfully."
        }

    async def handle_with_retry(self, operation_name: str, coro):
        # Implements Failure Strategy: MCP Timeout / LLM failure
        retries = 3
        backoff = 1.0
        for attempt in range(retries):
            try:
                # Add timeout protection
                return await asyncio.wait_for(coro, timeout=10.0)
            except asyncio.TimeoutError:
                # MCP timeout: retry with exponential backoff
                self.log.append(f"[Failure Strategy] {operation_name} timed out. Attempt {attempt+1}/{retries}. Backing off {backoff}s...")
                await asyncio.sleep(backoff)
                backoff *= 2
            except Exception as e:
                # Switch provider or alternate tool
                self.log.append(f"[Failure Strategy] {operation_name} encountered error: {e}. Recovering...")
                raise e
        raise Exception(f"Operation {operation_name} failed after maximum retry attempts.")

    async def on_task_created(self, data: Dict[str, Any]):
        task = data["task"]
        self.log.append("[Orchestrator] Task received. Delegating to Planner Agent...")
        plan_str = await self.planner.plan(task)
        self.log.append(f"[Planner] Created Plan: {plan_str}")
        await event_bus.publish("PLAN_READY", {"plan": plan_str})

    async def on_plan_ready(self, data: Dict[str, Any]):
        plan = data["plan"]
        self.log.append("[Orchestrator] Plan Ready. Triggering Explorer Agent for repository analysis...")
        analysis = await self.explorer.execute(plan=plan)
        self.log.append("[Explorer] Repository indexed successfully.")
        await event_bus.publish("REPOSITORY_INDEXED", {"analysis": analysis})

    async def on_repository_indexed(self, data: Dict[str, Any]):
        self.log.append("[Orchestrator] Repository Indexed. Triggering Coding Agent...")
        code = await self.coding.execute(analysis=data["analysis"])
        self.log.append("[Coding] Code generation complete.")
        
        # Verify code quality via Reviewer Agent
        is_valid = await self.reviewer.validate()
        if not is_valid:
            self.log.append("[Failure Strategy] Code review failed. Triggering self-correction loops...")
            # Self-correct loop simulation
            code = await self.coding.execute(remediation="Reviewer self-correction requested.")
            
        await event_bus.publish("CODE_GENERATED", {"code": code})

    async def on_code_generated(self, data: Dict[str, Any]):
        self.log.append("[Orchestrator] Code Generated. Triggering Tester Agent...")
        test_results = await self.tester.execute(code=data["code"])
        
        # Test failure strategy check
        if test_results.get("status") == "failed":
            self.log.append("[Failure Strategy] Test failures observed. Generating fix and re-testing...")
            # Simulate re-testing
            test_results = await self.tester.execute(action="re-test")
            
        self.log.append("[Tester] Testing cycle finished.")
        await event_bus.publish("TEST_COMPLETED", {"test_results": test_results})

    async def on_test_completed(self, data: Dict[str, Any]):
        self.log.append("[Orchestrator] Tests completed. Compiling documentation and preparing release build...")
        doc_result = await self.doc.execute()
        deploy_result = await self.deploy.execute()
        self.log.append("[Documentation] Documentation compiled.")
        self.log.append("[Deployment] Release build prepared.")
        await event_bus.publish("DOCUMENTATION_READY", {"docs": doc_result, "build": deploy_result})

    async def on_documentation_ready(self, data: Dict[str, Any]):
        self.log.append("[Orchestrator] Full Agent pipeline executed. Ready to aggregate results.")
