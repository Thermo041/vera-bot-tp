"""
Vera Bot - FastAPI Application
"""
import os
import time
from datetime import datetime
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

from .storage import store
from .composer import compose_message, handle_reply

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Vera Bot", version="1.0.0")

# Track uptime
START_TIME = time.time()

# Conversation history storage
conversations: Dict[str, List[Dict[str, Any]]] = {}


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ContextRequest(BaseModel):
    scope: str
    context_id: str
    version: int
    payload: Dict[str, Any]
    delivered_at: str


class TickRequest(BaseModel):
    now: str
    available_triggers: List[str] = []


class ReplyRequest(BaseModel):
    conversation_id: str
    merchant_id: Optional[str] = None
    customer_id: Optional[str] = None
    from_role: str
    message: str
    received_at: str
    turn_number: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/v1/healthz")
async def healthz():
    """Health check endpoint"""
    uptime = int(time.time() - START_TIME)
    counts = store.count_by_scope()
    
    return {
        "status": "ok",
        "uptime_seconds": uptime,
        "contexts_loaded": counts
    }


@app.get("/v1/metadata")
async def metadata():
    """Bot metadata endpoint"""
    return {
        "team_name": os.getenv("TEAM_NAME", "Team TP"),
        "team_members": [os.getenv("TEAM_MEMBERS", "Your Name")],
        "model": "groq/llama-3.1-70b-versatile",
        "approach": "LLM-based composer with context-aware prompting and trigger-specific templates",
        "contact_email": "team@example.com",
        "version": os.getenv("BOT_VERSION", "1.0.0"),
        "submitted_at": "2026-04-26T08:00:00Z"
    }


@app.post("/v1/context")
async def push_context(req: ContextRequest):
    """Receive and store context"""
    
    accepted, reason, current_version = store.store(
        req.scope, 
        req.context_id, 
        req.version, 
        req.payload
    )
    
    if not accepted:
        return {
            "accepted": False,
            "reason": reason,
            "current_version": current_version
        }
    
    return {
        "accepted": True,
        "ack_id": f"ack_{req.context_id}_v{req.version}",
        "stored_at": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/v1/tick")
async def tick(req: TickRequest):
    """Process tick and generate actions"""
    
    actions = []
    
    # Process each available trigger
    for trigger_id in req.available_triggers[:10]:  # Limit to 10 per tick
        
        # Compose message for this trigger
        action = compose_message(trigger_id)
        
        if action:
            actions.append(action)
            
            # Initialize conversation history
            conv_id = action["conversation_id"]
            if conv_id not in conversations:
                conversations[conv_id] = []
            
            conversations[conv_id].append({
                "from": "vera",
                "body": action["body"],
                "ts": req.now
            })
    
    return {"actions": actions}


@app.post("/v1/reply")
async def reply(req: ReplyRequest):
    """Handle merchant/customer reply"""
    
    # Get conversation history
    conv_history = conversations.get(req.conversation_id, [])
    
    # Add merchant message to history
    conv_history.append({
        "from": req.from_role,
        "body": req.message,
        "ts": req.received_at
    })
    
    # Handle reply
    response = handle_reply(
        req.conversation_id,
        req.merchant_id or "",
        req.message,
        conv_history
    )
    
    # If sending, add to history
    if response.get("action") == "send":
        conv_history.append({
            "from": "vera",
            "body": response.get("body", ""),
            "ts": datetime.utcnow().isoformat() + "Z"
        })
    
    # Update conversation history
    conversations[req.conversation_id] = conv_history
    
    return response


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Vera Bot",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "GET /v1/healthz",
            "GET /v1/metadata",
            "POST /v1/context",
            "POST /v1/tick",
            "POST /v1/reply"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
