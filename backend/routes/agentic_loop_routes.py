"""
FastAPI endpoints for managing and monitoring the agentic loop
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from backend.simulation.agentic_loop import (
    AgentManager,
    PersonaAgent,
    EngagementType,
    AgentDecision,
)
from backend.models.schemas import User

router = APIRouter(prefix="/api/agents", tags=["agentic-loop"])

# Global agent manager instance
agent_manager: Optional[AgentManager] = None


def init_agent_manager(manager: AgentManager):
    """Initialize the global agent manager"""
    global agent_manager
    agent_manager = manager


# Request/Response Models
class CreateAgentRequest(BaseModel):
    """Request to create a new agent"""

    user_id: str
    user_name: str
    persona_type: str
    interests: List[str]
    expertise: List[str]
    engagement_threshold: float = 0.6
    reply_probability: float = 0.3


class AgentStatsResponse(BaseModel):
    """Agent statistics"""

    user_id: str
    user_name: str
    total_engagements: int
    engagement_counts: dict
    average_confidence: float
    last_check: str
    interests: List[str]


class RunAgentLoopRequest(BaseModel):
    """Request to run agentic loop"""

    num_cycles: int = 1
    max_engagements_per_check: int = 5


class AgentDecisionResponse(BaseModel):
    """Decision made by an agent"""

    tweet_id: str
    agent_id: str
    decision: str
    confidence: float
    reason: str
    reply_content: Optional[str] = None


@router.post("/register")
async def register_agent(request: CreateAgentRequest) -> AgentStatsResponse:
    """
    Register a new persona agent

    Args:
        request: Agent creation request

    Returns:
        Agent statistics

    Example:
        ```
        POST /api/agents/register
        {
            "user_id": "vc-1",
            "user_name": "Venture Investor",
            "persona_type": "venture_capitalist",
            "interests": ["AI", "Startups", "Funding"],
            "expertise": ["Due diligence", "Valuation"],
            "engagement_threshold": 0.6,
            "reply_probability": 0.3
        }
        ```
    """
    if not agent_manager:
        raise HTTPException(
            status_code=503,
            detail="Agent manager not initialized",
        )

    try:
        # Create user from request
        user = User(
            id=request.user_id,
            name=request.user_name,
            persona_type=request.persona_type,
            interests=request.interests,
            expertise=request.expertise,
        )

        # Create agent
        agent = agent_manager.create_agent(
            user=user,
            engagement_threshold=request.engagement_threshold,
            reply_probability=request.reply_probability,
        )

        # Return stats
        stats = agent_manager.get_agent_stats(request.user_id)
        return AgentStatsResponse(**stats)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error registering agent: {e}")


@router.get("/list")
async def list_agents() -> List[AgentStatsResponse]:
    """
    List all registered agents

    Returns:
        List of agent statistics

    Example:
        ```
        GET /api/agents/list
        ```
    """
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")

    stats = agent_manager.get_all_stats()
    return [AgentStatsResponse(**s) for s in stats]


@router.get("/{user_id}/stats")
async def get_agent_stats(user_id: str) -> AgentStatsResponse:
    """
    Get statistics for a specific agent

    Args:
        user_id: User ID of the agent

    Returns:
        Agent statistics

    Example:
        ```
        GET /api/agents/vc-1/stats
        ```
    """
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")

    stats = agent_manager.get_agent_stats(user_id)
    if not stats:
        raise HTTPException(status_code=404, detail=f"Agent not found: {user_id}")

    return AgentStatsResponse(**stats)


@router.post("/run-loop")
async def run_agentic_loop(
    request: RunAgentLoopRequest, background_tasks: BackgroundTasks
) -> dict:
    """
    Run the agentic loop for specified cycles

    Args:
        request: Loop configuration
        background_tasks: FastAPI background tasks

    Returns:
        Status and job ID

    Example:
        ```
        POST /api/agents/run-loop
        {
            "num_cycles": 3,
            "max_engagements_per_check": 5
        }
        ```
    """
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")

    if agent_manager.is_running:
        return {"status": "already_running", "message": "Agentic loop is already running"}

    # Run loop in background
    async def run_loop():
        await agent_manager.run_agentic_loop(request.num_cycles)

    background_tasks.add_task(run_loop)

    return {
        "status": "started",
        "message": f"Agentic loop started with {request.num_cycles} cycles",
        "num_agents": len(agent_manager.agents),
    }


@router.post("/{user_id}/manual-check")
async def manual_agent_check(user_id: str) -> List[AgentDecisionResponse]:
    """
    Manually trigger a monitoring cycle for a specific agent

    Args:
        user_id: User ID of the agent

    Returns:
        List of decisions made

    Example:
        ```
        POST /api/agents/vc-1/manual-check
        ```
    """
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")

    agent = agent_manager.get_agent(user_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {user_id}")

    try:
        decisions = await agent_manager.agent_check_cycle(agent)
        return [
            AgentDecisionResponse(
                tweet_id=d.tweet_id,
                agent_id=d.agent_id,
                decision=d.decision.value,
                confidence=d.confidence,
                reason=d.reason,
                reply_content=d.reply_content,
            )
            for d in decisions
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running agent check: {e}",
        )


@router.delete("/{user_id}/reset")
async def reset_agent_history(user_id: str) -> dict:
    """
    Reset engagement history for an agent

    Args:
        user_id: User ID of the agent

    Returns:
        Status confirmation

    Example:
        ```
        DELETE /api/agents/vc-1/reset
        ```
    """
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")

    if agent_manager.reset_agent_history(user_id):
        return {"status": "success", "message": f"History reset for agent {user_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"Agent not found: {user_id}")


@router.get("/{user_id}/history")
async def get_agent_history(user_id: str, limit: int = 20) -> List[AgentDecisionResponse]:
    """
    Get recent engagement history for an agent

    Args:
        user_id: User ID of the agent
        limit: Max number of decisions to return

    Returns:
        List of recent decisions

    Example:
        ```
        GET /api/agents/vc-1/history?limit=10
        ```
    """
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")

    agent = agent_manager.get_agent(user_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {user_id}")

    # Get recent history
    history = agent.engagement_history[-limit:]
    return [
        AgentDecisionResponse(
            tweet_id=d.tweet_id,
            agent_id=d.agent_id,
            decision=d.decision.value,
            confidence=d.confidence,
            reason=d.reason,
            reply_content=d.reply_content,
        )
        for d in history
    ]


@router.get("/stats/summary")
async def get_loop_summary() -> dict:
    """
    Get summary statistics for all agents

    Returns:
        Summary statistics

    Example:
        ```
        GET /api/agents/stats/summary
        ```
    """
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")

    all_stats = agent_manager.get_all_stats()
    total_engagements = sum(s["total_engagements"] for s in all_stats)

    engagement_breakdown = {"like": 0, "reply": 0, "retweet": 0, "bookmark": 0}
    for stats in all_stats:
        for key, count in stats["engagement_counts"].items():
            engagement_breakdown[key] += count

    avg_confidence = (
        sum(s["average_confidence"] for s in all_stats) / len(all_stats)
        if all_stats
        else 0
    )

    return {
        "total_agents": len(all_stats),
        "total_engagements": total_engagements,
        "engagement_breakdown": engagement_breakdown,
        "average_confidence": round(avg_confidence, 3),
        "is_running": agent_manager.is_running,
        "agents": all_stats,
    }
