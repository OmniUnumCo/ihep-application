"""
IHEP Agent Swarm - FastAPI Entry Point

Main application entry point for the IHEP development swarm.

Usage:
    python main.py                    # Start API server
    python main.py --init-teams       # Initialize swarm with all teams
    python main.py --execute-blocking # Execute blocking missions immediately

Author: Jason M Jarmacz | jason@ihep.app
Co-Author: Claude by Anthropic
"""

import argparse
import sys
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger

from .orchestration import SwarmOrchestrator
from .communication import C2Router
from .config.models import TeamEnum, PriorityEnum


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class CreateMissionRequest(BaseModel):
    template_name: Optional[str] = None
    objective: Optional[str] = None
    team: Optional[str] = None
    priority: str = "routine"
    constraints: Optional[Dict[str, Any]] = None


class ExecuteMissionRequest(BaseModel):
    mission_id: str


# =============================================================================
# GLOBAL STATE
# =============================================================================

orchestrator: Optional[SwarmOrchestrator] = None
c2_router: Optional[C2Router] = None


# =============================================================================
# SECURITY HELPERS
# =============================================================================

# Safe error messages that can be exposed to clients
_SAFE_ERROR_MESSAGES = {
    "invalid_team": "Invalid team specified",
    "invalid_priority": "Invalid priority level",
    "mission_not_found": "Mission not found",
    "execution_failed": "Mission execution failed",
    "invalid_request": "Invalid request parameters",
}


def _sanitize_error_for_response(error: str) -> str:
    """
    Sanitize error messages before exposing to clients.

    Security: Internal error details may expose system architecture or
    implementation details. Only return safe, predefined messages.
    """
    error_lower = error.lower()

    # Map common errors to safe messages
    if "team" in error_lower:
        return _SAFE_ERROR_MESSAGES["invalid_team"]
    if "priority" in error_lower:
        return _SAFE_ERROR_MESSAGES["invalid_priority"]
    if "not found" in error_lower:
        return _SAFE_ERROR_MESSAGES["mission_not_found"]
    if "failed" in error_lower or "error" in error_lower:
        return _SAFE_ERROR_MESSAGES["execution_failed"]

    # Default safe message
    return _SAFE_ERROR_MESSAGES["invalid_request"]


# =============================================================================
# LIFESPAN MANAGEMENT
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global orchestrator, c2_router

    logger.info("Starting IHEP Agent Swarm...")

    # Initialize orchestrator
    orchestrator = SwarmOrchestrator(auto_init=True)
    c2_router = C2Router(orchestrator.agent_factory)

    logger.info("Swarm initialized and ready")

    yield

    logger.info("Shutting down IHEP Agent Swarm...")


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="IHEP Agent Swarm",
    description="Healthcare-adapted agent swarm for IHEP platform development",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# HEALTH & STATUS ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint with swarm info"""
    return {
        "name": "IHEP Agent Swarm",
        "version": "1.0.0",
        "status": "active" if orchestrator else "initializing",
        "endpoints": {
            "status": "/status",
            "teams": "/teams",
            "missions": "/missions",
            "create_mission": "/missions/create",
            "execute_mission": "/missions/execute",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "swarm_active": orchestrator is not None}


@app.get("/status")
async def get_status():
    """Get full swarm status"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Swarm not initialized")
    return orchestrator.get_swarm_status()


# =============================================================================
# TEAM ENDPOINTS
# =============================================================================

@app.get("/teams")
async def list_teams():
    """List all development teams"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Swarm not initialized")

    stats = orchestrator.agent_factory.get_stats()
    return stats["teams"]


@app.get("/teams/{team_type}")
async def get_team(team_type: str):
    """Get specific team details"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Swarm not initialized")

    try:
        team_enum = TeamEnum(team_type)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Team not found: {team_type}")

    team = orchestrator.agent_factory.get_team(team_enum)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team not found: {team_type}")

    agents = orchestrator.agent_factory.get_team_agents(team)
    return {
        "id": team.id,
        "name": team.name,
        "type": team.team_type.value,
        "status": team.status.value,
        "current_mission": team.current_mission,
        "missions_completed": team.missions_completed,
        "agents": {
            role.value: {
                "id": agent.agent_id,
                "name": agent.name,
                "rank": agent.rank.value,
                "status": agent.status.value,
            } if agent else None
            for role, agent in agents.items()
        },
    }


# =============================================================================
# MISSION ENDPOINTS
# =============================================================================

@app.get("/missions")
async def list_missions():
    """List all missions"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Swarm not initialized")

    return orchestrator.get_all_mission_statuses()


@app.get("/missions/templates")
async def list_mission_templates():
    """List available mission templates"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Swarm not initialized")

    return {
        "templates": orchestrator.mission_planner.get_available_templates()
    }


@app.post("/missions/create")
async def create_mission(request: CreateMissionRequest):
    """Create a new mission"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Swarm not initialized")

    try:
        team_enum = None
        if request.team:
            team_enum = TeamEnum(request.team)

        priority = PriorityEnum(request.priority)

        mission = orchestrator.create_mission(
            template_name=request.template_name,
            objective=request.objective,
            team=team_enum,
            priority=priority,
            constraints=request.constraints,
        )

        return {
            "mission_id": mission.id,
            "name": mission.name,
            "status": mission.status.value,
            "tasks": len(mission.tasks),
        }

    except ValueError as e:
        # Security: Sanitize error message before exposing to client
        logger.warning("Mission creation failed: %s", str(e))
        raise HTTPException(status_code=400, detail=_sanitize_error_for_response(str(e)))


@app.post("/missions/execute")
async def execute_mission(request: ExecuteMissionRequest):
    """Execute a mission"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Swarm not initialized")

    result = orchestrator.execute_mission(request.mission_id)

    if "error" in result:
        # Security: Sanitize error message before exposing to client
        logger.warning("Mission execution failed: %s", result.get("error", "unknown"))
        raise HTTPException(
            status_code=400,
            detail=_sanitize_error_for_response(result.get("error", ""))
        )

    return result


@app.post("/missions/assign-all")
async def assign_all_missions():
    """Assign initial missions to all teams"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Swarm not initialized")

    assignments = orchestrator.assign_initial_missions()
    return {
        "assignments": {
            team.value: mission_id
            for team, mission_id in assignments.items()
        }
    }


@app.post("/missions/execute-all")
async def execute_all_missions():
    """Execute all active missions"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Swarm not initialized")

    results = orchestrator.execute_all_missions()
    return {"results": results}


@app.get("/missions/{mission_id}")
async def get_mission(mission_id: str):
    """Get mission status"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Swarm not initialized")

    status = orchestrator.get_mission_status(mission_id)
    if "error" in status:
        # Security: Sanitize error message before exposing to client
        logger.debug("Mission status lookup failed for %s: %s", mission_id, status.get("error"))
        raise HTTPException(
            status_code=404,
            detail=_sanitize_error_for_response(status.get("error", ""))
        )

    return status


# =============================================================================
# COMMUNICATION ENDPOINTS
# =============================================================================

@app.get("/comms/stats")
async def get_communication_stats():
    """Get communication statistics"""
    if not c2_router:
        raise HTTPException(status_code=503, detail="C2 router not initialized")

    return c2_router.get_communication_stats()


@app.get("/comms/casreps")
async def get_recent_casreps(limit: int = 10):
    """Get recent casualty reports"""
    if not c2_router:
        raise HTTPException(status_code=503, detail="C2 router not initialized")

    casreps = c2_router.get_recent_casreps(limit)
    return {
        "count": len(casreps),
        "casreps": [
            {
                "id": c.id,
                "agent_id": c.agent_id,
                "failure_type": c.failure_type,
                "error_message": c.error_message[:200],
                "task_id": c.task_id,
                "reported_at": c.reported_at.isoformat(),
            }
            for c in casreps
        ],
    }


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(description="IHEP Agent Swarm")
    parser.add_argument(
        "--init-teams",
        action="store_true",
        help="Initialize swarm with all teams",
    )
    parser.add_argument(
        "--execute-blocking",
        action="store_true",
        help="Execute blocking missions (Three.js, Database)",
    )
    parser.add_argument(
        "--execute-all",
        action="store_true",
        help="Execute all initial missions",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind to",
    )

    args = parser.parse_args()

    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO")

    # Initialize swarm for CLI operations
    global orchestrator, c2_router
    orchestrator = SwarmOrchestrator(auto_init=True)
    c2_router = C2Router(orchestrator.agent_factory)

    if args.init_teams:
        logger.info("Teams initialized")
        stats = orchestrator.agent_factory.get_stats()
        logger.info(f"Total agents: {stats['total_agents']}")
        logger.info(f"Total teams: {stats['total_teams']}")
        for team_name, team_info in stats["teams"].items():
            logger.info(f"  {team_name}: {team_info['agent_count']} agents")

    if args.execute_blocking:
        logger.info("Executing blocking missions...")
        # Create and execute Three.js fix
        m1 = orchestrator.create_mission(template_name="fix_threejs")
        r1 = orchestrator.execute_mission(m1.id)
        logger.info(f"Three.js mission: {'SUCCESS' if r1.get('success') else 'FAILED'}")

        # Create and execute database integration
        m2 = orchestrator.create_mission(template_name="database_integration")
        r2 = orchestrator.execute_mission(m2.id)
        logger.info(f"Database mission: {'SUCCESS' if r2.get('success') else 'FAILED'}")

    if args.execute_all:
        logger.info("Assigning and executing all initial missions...")
        orchestrator.assign_initial_missions()
        results = orchestrator.execute_all_missions()
        for mission_id, result in results.items():
            success = result.get("success", False)
            name = result.get("mission_name", mission_id)
            logger.info(f"  {name}: {'SUCCESS' if success else 'FAILED'}")

    # If no CLI action, start the API server
    if not any([args.init_teams, args.execute_blocking, args.execute_all]):
        import uvicorn
        logger.info(f"Starting API server on {args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
