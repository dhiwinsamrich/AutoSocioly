"""
User Workflow API Routes - Implements the complete user flow with confirmation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import logging
from fastapi.responses import HTMLResponse

from ..services.user_workflow_service import UserWorkflowService
from ..models import Platform, Tone
from ..utils.logger_config import get_logger
from ..utils.ngrok_manager import get_ngrok_manager

logger = get_logger('user_workflow_routes')

router = APIRouter(prefix="/user-workflow", tags=["User Workflow"])

# Initialize service
workflow_service = UserWorkflowService()

# Request/Response Models
class UserInputRequest(BaseModel):
    user_input: str
    platforms: List[str]
    tone: str = "professional"
    include_image: bool = True

class ContentConfirmationRequest(BaseModel):
    session_id: str
    confirmed: bool = True
    text_modification: Optional[str] = None
    hashtag_modification: Optional[str] = None
    image_modification: Optional[str] = None
    regenerate_image: bool = False
    regenerate_text: bool = False

class WorkflowStatusResponse(BaseModel):
    success: bool
    session_id: str
    status: str
    message: str
    content: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    modification_history: Optional[List[Dict[str, Any]]] = None

@router.post("/create-content", response_model=WorkflowStatusResponse)
async def create_user_content(request: UserInputRequest):
    """
    Create content from user input
    User Input → Parse & Analyze → Generate Content → Return for Review
    """
    try:
        logger.info(f"Received user input: {request.user_input[:50]}...")
        
        result = await workflow_service.process_user_input(
            user_input=request.user_input,
            platforms=request.platforms,
            tone=request.tone,
            include_image=request.include_image
        )
        
        if result["success"]:
            return WorkflowStatusResponse(
                success=True,
                session_id=result["session_id"],
                status=result["status"],
                message=result["message"],
                content=result["content"],
                analysis=result["analysis"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Failed to create user content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm-content", response_model=WorkflowStatusResponse)
async def confirm_user_content(request: ContentConfirmationRequest):
    """
    Handle user confirmation or modification request
    If confirmed: Post to platforms
    If not confirmed: Return modification request
    """
    try:
        logger.info(f"Processing confirmation for session: {request.session_id}")
        
        if request.confirmed:
            # User confirmed - post content
            result = await workflow_service.confirm_and_post(
                session_id=request.session_id,
                user_confirmation=True
            )
            
            if result["success"]:
                # Clean up session after successful posting
                workflow_service.cleanup_session(request.session_id)
                
                return WorkflowStatusResponse(
                    success=True,
                    session_id=result["session_id"],
                    status=result["status"],
                    message=result["message"]
                )
            else:
                raise HTTPException(status_code=500, detail=result["message"])
                
        else:
            # User wants modifications
            result = await workflow_service.modify_content(
                session_id=request.session_id,
                text_prompt=request.text_modification,
                hashtag_prompt=request.hashtag_modification,
                image_prompt=request.image_modification,
                regenerate_image=request.regenerate_image,
                regenerate_text=request.regenerate_text
            )
            
            if result["success"]:
                return WorkflowStatusResponse(
                    success=True,
                    session_id=result["session_id"],
                    status=result["status"],
                    message=result["message"],
                    content=result["content"],
                    modification_history=result["modification_history"]
                )
            else:
                raise HTTPException(status_code=500, detail=result["message"])
                
    except Exception as e:
        logger.error(f"Failed to confirm content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/modify-content", response_model=WorkflowStatusResponse)
async def modify_user_content(request: ContentConfirmationRequest):
    """
    Modify content based on user feedback
    """
    try:
        logger.info(f"Processing modification for session: {request.session_id}")
        
        result = await workflow_service.modify_content(
            session_id=request.session_id,
            text_prompt=request.text_modification,
            hashtag_prompt=request.hashtag_modification,
            image_prompt=request.image_modification,
            regenerate_image=request.regenerate_image,
            regenerate_text=request.regenerate_text
        )
        
        if result["success"]:
            return WorkflowStatusResponse(
                success=True,
                session_id=result["session_id"],
                status=result["status"],
                message=result["message"],
                content=result["content"],
                modification_history=result["modification_history"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Failed to modify content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """
    Get current session status and content
    """
    try:
        session = workflow_service.get_session_status(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session_id": session_id,
            "status": session["status"],
            "topic": session["content_package"]["topic"],
            "created_at": session["created_at"],
            "last_modified": session.get("last_modified"),
            "content": session["content_package"],
            "modification_history": session["modification_history"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-sessions")
async def get_active_sessions():
    """
    Get all active user sessions
    """
    try:
        sessions = workflow_service.get_all_sessions()
        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        }
    except Exception as e:
        logger.error(f"Failed to get active sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ngrok-status")
async def get_ngrok_status():
    """
    Get ngrok tunnel status and information
    """
    try:
        ngrok_manager = get_ngrok_manager()
        tunnel_info = ngrok_manager.get_tunnel_info()
        
        return {
            "success": True,
            "ngrok_status": tunnel_info
        }
    except Exception as e:
        logger.error(f"Failed to get ngrok status: {e}")
        return {
            "success": False,
            "error": str(e),
            "ngrok_status": {
                "ngrok_running": False,
                "error": str(e),
                "active_mappings": {}
            }
        }

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a user session
    """
    try:
        workflow_service.cleanup_session(session_id)
        
        return {
            "success": True,
            "message": "Session deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional utility endpoints
@router.post("/quick-post")
async def quick_post(request: UserInputRequest, background_tasks: BackgroundTasks):
    """
    Quick post without user confirmation (for testing)
    """
    try:
        logger.info(f"Quick posting user input: {request.user_input[:50]}...")
        
        # Create content
        result = await workflow_service.process_user_input(
            user_input=request.user_input,
            platforms=request.platforms,
            tone=request.tone,
            include_image=request.include_image
        )
        
        if result["success"]:
            # Auto-confirm and post
            confirm_result = await workflow_service.confirm_and_post(
                session_id=result["session_id"],
                user_confirmation=True
            )
            
            if confirm_result["success"]:
                workflow_service.cleanup_session(result["session_id"])
                
                return {
                    "success": True,
                    "session_id": result["session_id"],
                    "status": "posted",
                    "message": "Content posted successfully!",
                    "results": confirm_result["results"]
                }
            else:
                raise HTTPException(status_code=500, detail=confirm_result["message"])
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Failed to quick post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check for the user workflow service
    """
    try:
        return {
            "success": True,
            "service": "user_workflow",
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# HTML Interface endpoint
@router.get("/workflow", response_class=HTMLResponse)
async def workflow_interface(request: Request):
    """
    Serve the user workflow HTML interface
    """
    try:
        with open("templates/user_workflow.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        logger.error(f"Failed to serve workflow interface: {e}")
        raise HTTPException(status_code=500, detail=str(e))