from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uuid
from datetime import datetime
import asyncio

from ..models import ContentRequest, PostRequest
from ..services import APIService
from ..services.ai_service import AIService
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
    request: Request,
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
        generated_images = content_data.get("generated_images", [])
        performance_analysis = content_data.get("performance_analysis", {})
        
        # Use the first generated image URL if available, otherwise fall back to image ideas
        first_image_url = None
        if generated_images:
            first_image_url = generated_images[0]  # Use the first actual generated image
        elif image_ideas:
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
            "original_image_url": first_image_url,  # Store original image separately
            "generated_images": generated_images,  # Store all generated images
            "analytics": performance_analysis
        }
        
        logger.info(f"Content created successfully for workflow {workflow_id}")
        
        # Store enhanced prompt if available
        enhanced_prompt = content_data.get("enhanced_prompt", topic)
        
        # Redirect to review page with all the data
        return templates.TemplateResponse("review.html", {
            "request": request,
            "workflow_id": workflow_id,
            "topic": topic,
            "platforms": platforms,
            "tone": tone,
            "content": platform_content,
            "image_url": first_image_url,
            "generated_images": generated_images,
            "enhanced_prompt": enhanced_prompt,
            "analytics": performance_analysis
        })
        
    except Exception as e:
        logger.error(f"Error creating content: {str(e)}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e),
            "message": "Failed to create content"
        }, status_code=500)

@router.post("/edit-content")
async def edit_content_api(
    workflow_id: str = Form(...),
    platform: str = Form(...),
    content_type: str = Form(...),  # 'caption' or 'hashtags'
    new_content: str = Form(...)
):
    """Edit content (caption or hashtags) for a specific platform"""
    try:
        logger.info(f"Editing {content_type} for workflow {workflow_id}, platform {platform}")
        
        # Check if workflow exists
        if workflow_id not in active_workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Initialize AI service for content generation
        ai_service = AIService()
        
        # Get current content
        workflow_data = active_workflows[workflow_id]
        current_content = workflow_data["content"].get(platform, {})
        
        if content_type == "caption":
            # Generate new caption based on user input
            enhanced_prompt = f"""
            Original topic: {workflow_data['topic']}
            Platform: {platform}
            Current caption: {current_content.get('caption', '')}
            User request: {new_content}
            
            Please generate a new caption based on the user's requirements.
            Keep the same tone ({workflow_data['tone']}) and optimize for {platform}.
            """
            
            new_caption = await ai_service.generate_content(enhanced_prompt, platform)
            
            # Update content
            current_content["caption"] = new_caption
            current_content["character_count"] = len(new_caption)
            
        elif content_type == "hashtags":
            # Generate new hashtags based on user input
            enhanced_prompt = f"""
            Original topic: {workflow_data['topic']}
            Platform: {platform}
            Current hashtags: {current_content.get('hashtags', [])}
            User request: {new_content}
            
            Please generate new hashtags based on the user's requirements.
            Provide {workflow_data.get('hashtag_count', 10)} relevant hashtags for {platform}.
            Return only the hashtags as a comma-separated list.
            """
            
            hashtag_response = await ai_service.generate_content(enhanced_prompt, platform)
            new_hashtags = [tag.strip() for tag in hashtag_response.split(',') if tag.strip()]
            
            # Update content
            current_content["hashtags"] = new_hashtags
        
        # Update workflow data
        workflow_data["content"][platform] = current_content
        
        logger.info(f"Successfully edited {content_type} for workflow {workflow_id}")
        
        return JSONResponse({
            "success": True,
            "message": f"{content_type.capitalize()} updated successfully!",
            "updated_content": current_content
        })
        
    except Exception as e:
        logger.error(f"Error editing content: {str(e)}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e),
            "message": f"Failed to edit {content_type}"
        }, status_code=500)

@router.post("/regenerate-image")
async def regenerate_image_api(request: Request):
    """
    Regenerate a single image based on user prompt and original image context
    """
    try:
        data = await request.json()
        workflow_id = data.get("workflow_id")
        prompt = data.get("prompt")
        original_image_url = data.get("original_image_url")
        preserve_context = data.get("preserve_context", True)
        
        if not workflow_id or not prompt:
            raise HTTPException(status_code=400, detail="Workflow ID and prompt are required")
        
        # Check if workflow exists
        if workflow_id not in active_workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Get current workflow data
        workflow_data = active_workflows[workflow_id]
        
        # Use the workflow service to regenerate image with context preservation
        from ..services.workflow_service import SocialMediaWorkflow
        workflow = SocialMediaWorkflow()
        
        result = await workflow.regenerate_image_with_prompt(
            content_id=workflow_id,
            new_prompt=prompt,
            preserve_context=preserve_context
        )
        
        if result['success']:
            # Update workflow with new image
            workflow_data["image_url"] = result['image_url']
            workflow_data["last_regenerated_at"] = datetime.now()
            
            # Initialize regeneration history if not exists
            if "regeneration_history" not in workflow_data:
                workflow_data["regeneration_history"] = []
            
            # Add to regeneration history
            workflow_data["regeneration_history"].append({
                "prompt": prompt,
                "previous_image_url": workflow_data.get("image_url"),
                "new_image_url": result['image_url'],
                "regenerated_at": datetime.now()
            })
            
            return JSONResponse({
                "success": True,
                "image_url": result['image_url'],
                "original_image_url": workflow_data.get("original_image_url"),
                "context_preserved": result.get('context_preserved', False),
                "message": "Image regenerated successfully"
            })
        else:
            raise HTTPException(status_code=500, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to regenerate image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to regenerate image: {str(e)}")

@router.post("/modify-image")
async def modify_image_api(request: Request):
    """
    Modify an existing image based on user feedback
    """
    try:
        data = await request.json()
        workflow_id = data.get("workflow_id")
        feedback = data.get("feedback")
        image_url = data.get("image_url")
        
        if not workflow_id or not feedback or not image_url:
            raise HTTPException(status_code=400, detail="Workflow ID, feedback, and image_url are required")
        
        # Check if workflow exists
        if workflow_id not in active_workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Use the workflow service to modify image
        from ..services.workflow_service import SocialMediaWorkflow
        workflow = SocialMediaWorkflow()
        
        result = await workflow.modify_image_with_feedback(
            content_id=workflow_id,
            feedback=feedback,
            image_url=image_url
        )
        
        if result['success']:
            # Update workflow with new image
            workflow_data = active_workflows[workflow_id]
            workflow_data["image_url"] = result['image_url']
            
            return JSONResponse({
                "success": True,
                "image_url": result['image_url'],
                "feedback": result['feedback'],
                "message": "Image modified successfully"
            })
        else:
            raise HTTPException(status_code=500, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to modify image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to modify image: {str(e)}")

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
        accounts_result = await api_service.get_platform_accounts()
        
        return JSONResponse(accounts_result)
        
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