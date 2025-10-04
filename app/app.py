"""FastAPI application for Versailles visit planning agent."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import sys
from typing import Optional

# Add parent directory to path
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../agents'))
sys.path.append(os.path.abspath('/Users/sarah/Desktop/les_4_MousquetAIres/'))
sys.path.append(os.path.abspath('/Users/sarah/Desktop/les_4_MousquetAIres/agents'))

from agents.langgraph_flow import run_graph
from agents.agent_multistep import reset_session

from llm.reservation_memory import ReservationPlan, ReservationState
from memory.memory import load_session, save_session

app = FastAPI(
    title="Versailles Visit Planning Agent",
    description="AI agent to help plan visits to Château de Versailles",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's message")
    session_id: str = Field(default="default_session", description="Session identifier")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Agent's response")
    session_id: str = Field(..., description="Session identifier")


class SessionRequest(BaseModel):
    """Request model for session operations."""
    session_id: str = Field(..., description="Session identifier")


class ReservationResponse(BaseModel):
    """Response model for reservation status."""
    session_id: str
    reservation_plan: ReservationPlan
    completion_percentage: float
    is_complete: bool
    missing_slots: list


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Versailles Visit Planning Agent API",
        "version": "1.0.0",
        "description": "AI agent to help plan visits to Château de Versailles",
        "endpoints": {
            "POST /chat": "Send a message to the agent",
            "GET /session/{session_id}": "Get session information",
            "DELETE /session/{session_id}": "Reset a session",
            "GET /reservation/{session_id}": "Get reservation status",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Versailles Visit Planning Agent"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the agent and get a response.
    
    Args:
        request: Chat request with message and session_id
        
    Returns:
        Agent's response
    """
    try:
        # Run the LangGraph flow
        response = run_graph(
            input_text=request.message,
            session_id=request.session_id
        )
        
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Get session information.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session data
    """
    try:
        session_data = load_session(session_id)
        
        return {
            "session_id": session_id,
            "chat_history": session_data.get("chat_history", ""),
            "has_history": bool(session_data.get("chat_history"))
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving session: {str(e)}"
        )


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Reset a session (clear conversation history).
    
    Args:
        session_id: Session identifier
        
    Returns:
        Confirmation message
    """
    try:
        reset_session(session_id)
        
        return {
            "message": f"Session {session_id} reset successfully",
            "session_id": session_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting session: {str(e)}"
        )


@app.get("/reservation/{session_id}", response_model=ReservationResponse)
async def get_reservation_status(session_id: str):
    """
    Get the current reservation status for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Reservation plan and status
    """
    try:
        session_data = load_session(session_id)
        
        # Extract reservation data if available
        reservation_data = session_data.get("reservation_plan", {})
        
        # Create ReservationPlan instance
        reservation_plan = ReservationPlan(**reservation_data) if reservation_data else ReservationPlan()
        
        return ReservationResponse(
            session_id=session_id,
            reservation_plan=reservation_plan,
            completion_percentage=reservation_plan.get_completion_percentage(),
            is_complete=reservation_plan.is_complete(),
            missing_slots=reservation_plan.get_missing_slots()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving reservation status: {str(e)}"
        )


@app.post("/reservation/{session_id}")
async def update_reservation(session_id: str, reservation: ReservationPlan):
    """
    Update reservation plan for a session.
    
    Args:
        session_id: Session identifier
        reservation: Updated reservation plan
        
    Returns:
        Updated reservation status
    """
    try:
        session_data = load_session(session_id)
        
        # Update timestamp
        reservation.update_timestamp()
        
        # Save reservation plan
        session_data["reservation_plan"] = reservation.dict()
        save_session(session_id, session_data)
        
        return {
            "message": "Reservation updated successfully",
            "session_id": session_id,
            "reservation_plan": reservation,
            "completion_percentage": reservation.get_completion_percentage(),
            "is_complete": reservation.is_complete()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating reservation: {str(e)}"
        )


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("=" * 70)
    print("🏰 Versailles Visit Planning Agent API")
    print("=" * 70)
    print("✓ FastAPI server started")
    print("✓ Agent initialized")
    print("✓ Ready to accept requests")
    print("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Shutting down Versailles Visit Planning Agent API...")


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug
    )
