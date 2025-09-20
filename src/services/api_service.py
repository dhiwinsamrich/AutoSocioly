from typing import Dict, List, Optional, Any
import logging
import json
import asyncio
from datetime import datetime
import uuid
from typing import Dict, Any, List, Optional

from ..models import ContentRequest, PostRequest, Platform, Tone
from ..services.workflow_service import SocialMediaWorkflow
from ..utils.logger_config import log_api_call, get_logger

logger = get_logger('api_service')

class APIService:
    """Service for handling API requests and orchestrating workflows"""
    
    def __init__(self):
        """Initialize API service"""
        self.active_workflows: Dict[str, SocialMediaWorkflow] = {}
        logger.info("API service initialized")
    
    async def create_content(self, request: ContentRequest) -> Dict[str, Any]:
        """
        Create social media content
        
        Args:
            request: Content creation request
            
        Returns:
            Content creation results
        """
        workflow_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting content creation workflow: {workflow_id}")
            
            # Create workflow instance
            workflow = SocialMediaWorkflow()
            self.active_workflows[workflow_id] = workflow
            
            # Execute content creation workflow
            result = await workflow.create_content_workflow(
                topic=request.topic,
                platforms=request.platforms,
                tone=request.tone,
                include_images=request.include_image,
                image_context=request.image_context,
                generate_variants=request.generate_variants
            )
            
            # Clean up workflow
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            # Log API call
            log_api_call(
                logger_name='api.content',
                method='POST',
                endpoint='/api/content',
                status_code=200 if result.success else 400,
                duration=0,  # Will be calculated by middleware
                request_data=request.dict(),
                response_data=result.dict()
            )
            
            if result.success:
                logger.info(f"Content created successfully: {workflow_id}")
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "data": result.dict(),
                    "message": "Content generated successfully"
                }
            else:
                logger.error(f"Content creation failed: {result.error}")
                return {
                    "success": False,
                    "workflow_id": workflow_id,
                    "error": result.error,
                    "message": "Content generation failed"
                }
                
        except Exception as e:
            logger.error(f"Content creation error: {e}")
            
            # Clean up workflow
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e),
                "message": "Internal server error"
            }
    
    async def post_content(self, content_data: Dict[str, Any], platforms: List[Platform], schedule_time: Optional[datetime] = None, use_variants: bool = False) -> Dict[str, Any]:
        """
        Post content to social media platforms
        
        Args:
            content_data: Content data from content generation
            platforms: List of platforms to post to
            schedule_time: Optional scheduled posting time
            use_variants: Whether to use content variants
            
        Returns:
            Posting results
        """
        workflow_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting posting workflow: {workflow_id}")
            
            # Create workflow instance
            workflow = SocialMediaWorkflow()
            self.active_workflows[workflow_id] = workflow
            
            # Extract scheduling information from content_data
            scheduling_params = {}
            if 'publishNow' in content_data:
                scheduling_params['publish_now'] = content_data['publishNow']
            if 'scheduledFor' in content_data:
                scheduling_params['scheduled_for'] = content_data['scheduledFor']
            
            # Execute posting workflow
            result = await workflow.post_content_workflow(
                content_data=content_data,
                platforms=platforms,
                schedule_time=schedule_time,
                use_variants=use_variants,
                **scheduling_params
            )
            
            # Clean up workflow
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            # Log API call
            log_api_call(
                logger_name='api.post',
                method='POST',
                endpoint='/api/post',
                status_code=200,
                duration=0,
                request_data={"content_id": content_data.get("workflow_id", ""), "platforms": [p.value for p in platforms]},
                response_data=result
            )
            
            # Check if posting was successful - result is a PostResponse object from workflow service
            logger.info(f"Post response: total_success={result.total_success}, total_failed={result.total_failed}, results={len(result.results) if hasattr(result, 'results') else 0}")
            
            if result.total_success > 0:
                logger.info(f"Content posted successfully: {workflow_id}")
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "data": result.dict() if hasattr(result, 'dict') else result,
                    "message": "Content posted successfully"
                }
            else:
                # Extract error messages from failed results
                failed_results = [r for r in result.results if not r.success] if hasattr(result, 'results') else []
                error_msg = failed_results[0].error_message if failed_results else "Unknown posting error"
                logger.error(f"Posting failed: {error_msg}, failed_results={len(failed_results)}, total_failed={result.total_failed}")
                return {
                    "success": False,
                    "workflow_id": workflow_id,
                    "error": error_msg,
                    "message": "Posting failed"
                }
                
        except Exception as e:
            logger.error(f"Posting error: {e}")
            
            # Clean up workflow
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e),
                "message": "Internal server error"
            }
    
    async def complete_workflow(self, request: ContentRequest) -> Dict[str, Any]:
        """
        Complete workflow: content generation + posting
        
        Args:
            request: Content creation request
            
        Returns:
            Complete workflow results
        """
        workflow_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting complete workflow: {workflow_id}")
            
            # Create workflow instance
            workflow = SocialMediaWorkflow()
            self.active_workflows[workflow_id] = workflow
            
            # Execute complete workflow
            result = await workflow.complete_workflow(
                topic=request.topic,
                platforms=request.platforms,
                tone=request.tone,
                include_images=request.include_image,
                generate_variants=request.generate_variants,
                auto_post=True
            )
            
            # Clean up workflow
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            # Log API call
            log_api_call(
                logger_name='api.complete',
                method='POST',
                endpoint='/api/complete',
                status_code=200 if result["success"] else 400,
                duration=0,
                request_data=request.dict(),
                response_data=result
            )
            
            if result["success"]:
                logger.info(f"Complete workflow successful: {workflow_id}")
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "data": result,
                    "message": "Complete workflow successful"
                }
            else:
                logger.error(f"Complete workflow failed: {result['error']}")
                return {
                    "success": False,
                    "workflow_id": workflow_id,
                    "error": result["error"],
                    "message": f"Workflow failed at stage: {result.get('stage', 'unknown')}"
                }
                
        except Exception as e:
            logger.error(f"Complete workflow error: {e}")
            
            # Clean up workflow
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e),
                "message": "Internal server error"
            }
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow status
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow status
        """
        try:
            if workflow_id not in self.active_workflows:
                return {
                    "success": False,
                    "error": "Workflow not found or completed",
                    "message": "Workflow not found"
                }
            
            workflow = self.active_workflows[workflow_id]
            status = workflow.get_workflow_status()
            
            log_api_call(
                logger_name='api.status',
                method='GET',
                endpoint=f'/api/workflow/{workflow_id}/status',
                status_code=200,
                duration=0
            )
            
            return {
                "success": True,
                "data": status,
                "message": "Workflow status retrieved"
            }
            
        except Exception as e:
            logger.error(f"Get workflow status error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get workflow status"
            }
    
    async def get_platform_accounts(self) -> Dict[str, Any]:
        """
        Get connected platform accounts
        
        Returns:
            Connected accounts information
        """
        try:
            logger.info("Getting platform accounts")
            
            # Initialize GetLate service directly
            from ..services.getlate_service import GetLateService
            from ..config import settings
            
            logger.info(f"Using GetLate API key: {settings.GETLATE_API_KEY[:10]}...")
            logger.info(f"Using GetLate base URL: {settings.GETLATE_BASE_URL}")
            
            getlate_service = GetLateService(
                api_key=settings.GETLATE_API_KEY,
                base_url=settings.GETLATE_BASE_URL
            )
            
            logger.info("GetLate service initialized, calling get_accounts...")
            
            # Get accounts from GetLate service (run in executor since it's not async)
            accounts = await asyncio.get_event_loop().run_in_executor(
                None, getlate_service.get_accounts
            )
            
            logger.info(f"Retrieved {len(accounts)} accounts from GetLate")
            
            # Format accounts data
            accounts_data = []
            for account in accounts:
                accounts_data.append({
                    "id": account.id,
                    "platform": account.platform.value,
                    "name": account.name,
                    "username": account.username,
                    "connected": account.connected,
                    "last_used": account.last_used.isoformat() if account.last_used else None
                })
            
            log_api_call(
                logger_name='api.accounts',
                method='GET',
                endpoint='/api/accounts',
                status_code=200,
                duration=0
            )
            
            logger.info(f"Retrieved {len(accounts_data)} accounts")
            return {
                "success": True,
                "data": {"accounts": accounts_data},
                "message": "Accounts retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Get accounts error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get accounts"
            }
    
    async def analyze_content(self, content: str, platform: Platform) -> Dict[str, Any]:
        """
        Analyze content for platform optimization
        
        Args:
            content: Content to analyze
            platform: Target platform
            
        Returns:
            Content analysis results
        """
        try:
            logger.info(f"Analyzing content for {platform.value}")
            
            # Create temporary workflow to access AI service
            workflow = SocialMediaWorkflow()
            analysis = await asyncio.get_event_loop().run_in_executor(
                None, workflow.ai_service.analyze_content_performance, content, platform.value
            )
            
            log_api_call(
                logger_name='api.analyze',
                method='POST',
                endpoint='/api/analyze',
                status_code=200,
                duration=0,
                request_data={"content": content, "platform": platform.value},
                response_data=analysis
            )
            
            return {
                "success": True,
                "data": analysis,
                "message": "Content analyzed successfully"
            }
            
        except Exception as e:
            logger.error(f"Content analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Content analysis failed"
            }
    
    async def optimize_content(self, content: str, platform: Platform) -> Dict[str, Any]:
        """
        Optimize content for specific platform
        
        Args:
            content: Content to optimize
            platform: Target platform
            
        Returns:
            Optimized content
        """
        try:
            logger.info(f"Optimizing content for {platform.value}")
            
            # Create temporary workflow to access AI service
            workflow = SocialMediaWorkflow()
            optimized_content = await asyncio.get_event_loop().run_in_executor(
                None, workflow.ai_service.optimize_content_for_platform, content, platform.value
            )
            
            log_api_call(
                logger_name='api.optimize',
                method='POST',
                endpoint='/api/optimize',
                status_code=200,
                duration=0,
                request_data={"content": content, "platform": platform.value},
                response_data={"optimized_content": optimized_content}
            )
            
            return {
                "success": True,
                "data": {"optimized_content": optimized_content},
                "message": "Content optimized successfully"
            }
            
        except Exception as e:
            logger.error(f"Content optimization error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Content optimization failed"
            }
    
    def cleanup_completed_workflows(self):
        """Clean up completed workflows from memory"""
        try:
            completed_workflows = []
            
            for workflow_id, workflow in self.active_workflows.items():
                if workflow.status.value in ["completed", "failed"]:
                    completed_workflows.append(workflow_id)
            
            for workflow_id in completed_workflows:
                del self.active_workflows[workflow_id]
            
            logger.info(f"Cleaned up {len(completed_workflows)} completed workflows")
            
        except Exception as e:
            logger.error(f"Workflow cleanup error: {e}")
    
    def get_service_health(self) -> Dict[str, Any]:
        """
        Get service health status
        
        Returns:
            Health status information
        """
        try:
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "active_workflows": len(self.active_workflows),
                "services": {
                    "api_service": True,
                    "workflow_service": True
                }
            }
            
            # Check if any workflows are stuck
            stuck_workflows = 0
            for workflow in self.active_workflows.values():
                if workflow.status.value == "running" and workflow.current_step:
                    # Simple timeout check (would be more sophisticated in production)
                    stuck_workflows += 1
            
            health_data["stuck_workflows"] = stuck_workflows
            
            if stuck_workflows > 5:  # Threshold for concern
                health_data["status"] = "degraded"
                health_data["warnings"] = [f"{stuck_workflows} workflows may be stuck"]
            
            return health_data
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_analytics(self) -> Dict[str, Any]:
        """
        Get system analytics and statistics
        
        Returns:
            Analytics data
        """
        try:
            logger.info("Getting system analytics")
            
            # Get service health data
            health_data = self.get_service_health()
            
            # Create analytics response
            analytics_data = {
                "system_health": health_data,
                "total_workflows": len(self.active_workflows),
                "platforms_supported": ["twitter", "linkedin", "facebook", "instagram"],
                "service_status": {
                    "api_service": "running",
                    "workflow_service": "running",
                    "ai_service": "running",
                    "getlate_service": "running"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            log_api_call(
                logger_name='api.analytics',
                method='GET',
                endpoint='/api/analytics',
                status_code=200,
                duration=0
            )
            
            return {
                "success": True,
                "data": analytics_data,
                "message": "Analytics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Get analytics error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get analytics"
            }