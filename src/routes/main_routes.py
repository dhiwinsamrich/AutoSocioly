from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uuid
from datetime import datetime
import asyncio

from ..models import ContentRequest, PostRequest
from ..services import APIService
from ..utils.logger_config import get_logger

logger = get_logger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Global workflow storage (in production, use Redis)
active_workflows = {}

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main page"""
    logger.info("Rendering home page")
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/create-content")
async def create_content_api(
    topic: str = Form(...),
    platforms: list = Form([]),
    tone: str = Form("professional"),
    include_image: bool = Form(False),
    voice_input: str = Form(None),
    caption_length: str = Form("medium"),
    hashtag_count: int = Form(10),
    image_context: str = Form(None),
    generate_variants: bool = Form(False)
):
    """Create social media content"""
    try:
        # Generate unique workflow ID
        workflow_id = str(uuid.uuid4())
        
        # Prepare content request
        content_request = ContentRequest(
            topic=topic,
            platforms=platforms if platforms else ["twitter", "linkedin"],
            tone=tone,
            include_image=include_image,
            caption_length=caption_length,
            hashtag_count=hashtag_count,
            image_context=image_context,
        generate_variants=generate_variants
        )
        
        logger.info(f"Creating content for workflow {workflow_id}", extra={
            "workflow_id": workflow_id,
            "topic": topic,
            "platforms": platforms,
            "tone": tone,
        })
        
        # Initialize API service
        api_service = APIService()
        
        # Start content creation workflow
        result = await api_service.create_content(content_request)
        
        # Extract content data from the result
        content_data = result.get("data", {})
        platform_content = content_data.get("platform_content", {})
        image_ideas = content_data.get("image_ideas", [])
        performance_analysis = content_data.get("performance_analysis", {})
        
        # Extract first image URL from image ideas
        first_image_url = None
        if image_ideas:
            first_image_url = image_ideas[0].get("description", "") if isinstance(image_ideas[0], dict) else str(image_ideas[0])
        
        # Store workflow info
        active_workflows[workflow_id] = {
            "id": workflow_id,
            "status": "content_created",
            "created_at": datetime.now(),
            "topic": topic,
            "platforms": platforms,
            "tone": tone,
            "content": platform_content,
            "image_url": first_image_url,
            "analytics": performance_analysis
        }
        
        logger.info(f"Content created successfully for workflow {workflow_id}")
        
        return JSONResponse({
            "success": True,
            "workflow_id": workflow_id,
            "content": platform_content,
            "image_url": first_image_url,
            "analytics": performance_analysis,
            "message": "Content created successfully!"
        })
        
    except Exception as e:
        logger.error(f"Error creating content: {str(e)}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e),
            "message": "Failed to create content"
        }, status_code=500)

@router.post("/publish-content")
async def publish_content_api(
    workflow_id: str = Form(...),
    selected_variants: dict = Form({})
):
    """Publish content to social media platforms"""
    try:
        logger.info(f"Publishing content for workflow {workflow_id}")
        
        # Check if workflow exists
        if workflow_id not in active_workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Prepare publish request
        publish_request = PostRequest(
            content_id=workflow_id,
            platforms=list(selected_variants.keys()) if selected_variants else []
        )
        
        # Initialize API service
        api_service = APIService()
        
        # Publish content
        result = await api_service.publish_content(publish_request)
        
        # Update workflow status
        active_workflows[workflow_id]["status"] = "published"
        active_workflows[workflow_id]["published_at"] = datetime.now()
        active_workflows[workflow_id]["publish_results"] = result.get("results", {})
        
        logger.info(f"Content published successfully for workflow {workflow_id}")
        
        return JSONResponse({
            "success": True,
            "workflow_id": workflow_id,
            "results": result.get("results", {}),
            "message": "Content published successfully!"
        })
        
    except Exception as e:
        logger.error(f"Error publishing content: {str(e)}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e),
            "message": "Failed to publish content"
        }, status_code=500)

@router.get("/workflow-status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get workflow status"""
    try:
        logger.info(f"Getting status for workflow {workflow_id}")
        
        # Initialize API service
        api_service = APIService()
        
        # Get workflow status
        status = await api_service.get_workflow_status(workflow_id)
        
        # Update local storage if workflow exists
        if workflow_id in active_workflows:
            active_workflows[workflow_id]["status"] = status.get("status", "unknown")
        
        return JSONResponse({
            "success": True,
            "workflow_id": workflow_id,
            "status": status
        })
        
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e),
            "message": "Failed to get workflow status"
        }, status_code=500)

@router.get("/accounts")
async def get_accounts():
    """Get connected social media accounts"""
    try:
        logger.info("Getting social media accounts")
        
        # Initialize API service
        api_service = APIService()
        
        # Get accounts
        accounts = await api_service.get_platform_accounts()
        
        return JSONResponse({
            "success": True,
            "accounts": accounts
        })
        
    except Exception as e:
        logger.error(f"Error getting accounts: {str(e)}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e),
            "message": "Failed to get accounts"
        }, status_code=500)

@router.post("/optimize-content")
async def optimize_content_api(
    content: str = Form(...),
    platform: str = Form(...),
    analytics_data: dict = Form({})
):
    """Optimize content based on analytics"""
    try:
        logger.info(f"Optimizing content for platform {platform}")
        
        # Initialize API service
        api_service = APIService()
        
        # Optimize content
        result = await api_service.optimize_content(content, platform, analytics_data)
        
        return JSONResponse({
            "success": True,
            "optimized_content": result.get("optimized_content", content),
            "suggestions": result.get("suggestions", []),
            "message": "Content optimized successfully!"
        })
        
    except Exception as e:
        logger.error(f"Error optimizing content: {str(e)}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e),
            "message": "Failed to optimize content"
        }, status_code=500)

@router.get("/analytics")
async def get_analytics():
    """Get system analytics"""
    try:
        logger.info("Getting system analytics")
        
        # Initialize API service
        api_service = APIService()
        
        # Get analytics
        analytics = await api_service.get_analytics()
        
        return JSONResponse({
            "success": True,
            "analytics": analytics
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e),
            "message": "Failed to get analytics"
        }, status_code=500)

@router.delete("/cleanup-workflows")
async def cleanup_workflows():
    """Clean up completed workflows"""
    try:
        logger.info("Cleaning up workflows")
        
        # Initialize API service
        api_service = APIService()
        
        # Clean up workflows
        result = await api_service.cleanup_workflows()
        
        # Clean up local storage
        global active_workflows
        completed_workflows = [
            wf_id for wf_id, wf_data in active_workflows.items()
            if wf_data.get("status") == "published"
        ]
        
        for wf_id in completed_workflows:
            del active_workflows[wf_id]
        
        return JSONResponse({
            "success": True,
            "cleaned_count": len(completed_workflows),
            "message": f"Cleaned up {len(completed_workflows)} workflows"
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up workflows: {str(e)}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e),
            "message": "Failed to cleanup workflows"
        }, status_code=500)