from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging
import asyncio
import json
from pathlib import Path
import uuid

from ..models import (
    ContentRequest, ContentResponse, PostRequest, PostResponse,
    Platform, Tone
)
from ..services.getlate_service import GetLateService
from ..services.ai_service import AIService
from ..utils.logger_config import log_social_media_action
from ..config import settings

logger = logging.getLogger(__name__)

class SocialMediaWorkflow:
    """Main workflow for social media content creation and posting"""
    
    def __init__(self):
        """Initialize workflow with services"""
        self.getlate_service = GetLateService(
            api_key=settings.GETLATE_API_KEY,
            base_url=settings.GETLATE_BASE_URL
        )
        self.ai_service = AIService()
        self.workflow_id = str(uuid.uuid4())
        self.status = "idle"
        self.current_step = None
        self.results = {}
        self.errors = []
        
        logger.info(f"Social media workflow initialized: {self.workflow_id}")
    
    async def create_content_workflow(
        self,
        topic: str,
        platforms: List[Platform],
        tone: Tone = Tone.PROFESSIONAL,
        include_images: bool = False,
        image_context: Optional[str] = None,
        generate_variants: bool = False
    ) -> ContentResponse:
        """
        Complete workflow for content creation
        
        Args:
            topic: Content topic
            platforms: Target platforms
            tone: Content tone
            include_images: Whether to include images
            image_context: Optional image context
            generate_variants: Whether to generate multiple variants
            
        Returns:
            Content response with generated content
        """
        self.status = "running"
        self.current_step = "content_generation"
        
        try:
            
            # Step 1: Generate content for each platform
            platform_content = {}
            
            for platform in platforms:
                logger.info(f"Generating content for {platform.value}")
                
                if generate_variants:
                    # Generate multiple variants for A/B testing
                    variants = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        self.ai_service.generate_multiple_variants,
                        topic, platform.value, 3, tone.value
                    )
                    platform_content[platform.value] = variants
                else:
                    # Generate single content piece
                    content_data = await asyncio.get_event_loop().run_in_executor(
                        None,
                        self.ai_service.generate_social_media_content,
                        topic, platform.value, tone.value
                    )
                    platform_content[platform.value] = [content_data]
            
            # Step 2: Generate images if requested
            image_ideas = []
            if include_images:
                logger.info("Generating image ideas")
                self.current_step = "image_generation"
                
                image_ideas = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.ai_service.generate_image_ideas,
                    topic, 3, image_context
                )
            
            # Step 3: Analyze content performance
            self.current_step = "content_analysis"
            performance_analysis = {}
            
            for platform, contents in platform_content.items():
                performance_analysis[platform] = []
                for content in contents:
                    analysis = await asyncio.get_event_loop().run_in_executor(
                        None,
                        self.ai_service.analyze_content_performance,
                        content.get("content", ""), platform
                    )
                    performance_analysis[platform].append(analysis)
            
            self.status = "completed"
            self.results = {
                "platform_content": platform_content,
                "image_ideas": image_ideas,
                "performance_analysis": performance_analysis
            }
            

            
            return ContentResponse(
                success=True,
                workflow_id=self.workflow_id,
                platform_content=platform_content,
                image_ideas=image_ideas,
                performance_analysis=performance_analysis,
                message="Content generated successfully"
            )
            
        except Exception as e:
            self.status = "failed"
            self.errors.append(str(e))
            
            logger.error(f"Content generation workflow failed: {e}")
            
            return ContentResponse(
                success=False,
                workflow_id=self.workflow_id,
                error=str(e),
                message="Content generation failed"
            )
    
    async def post_content_workflow(
        self,
        content_data: Dict[str, Any],
        platforms: List[Platform],
        schedule_time: Optional[datetime] = None,
        use_variants: bool = False
    ) -> PostResponse:
        """
        Complete workflow for posting content to social media platforms
        
        Args:
            content_data: Content data from content generation
            platforms: Target platforms
            schedule_time: Optional scheduled posting time
            use_variants: Whether to use content variants
            
        Returns:
            Post response with posting results
        """
        self.status = "running"
        self.current_step = "posting"
        
        try:
            
            # Get platform content
            platform_content = content_data.get("platform_content", {})
            posting_results = {}
            
            # Step 1: Get connected accounts
            logger.info("Getting connected accounts")
            connected_accounts = await asyncio.get_event_loop().run_in_executor(
                None, self.getlate_service.get_accounts
            )
            
            available_platforms = {acc.platform: acc for acc in connected_accounts}
            
            # Step 2: Post to each platform
            for platform in platforms:
                if platform not in available_platforms:
                    logger.warning(f"No connected account for {platform.value}")
                    posting_results[platform.value] = {
                        "success": False,
                        "error": "No connected account"
                    }
                    continue
                
                try:
                    # Select content (use first variant or random variant)
                    if platform.value in platform_content:
                        contents = platform_content[platform.value]
                        if use_variants and len(contents) > 1:
                            # Select best performing variant based on analysis
                            content = self._select_best_variant(contents, platform.value)
                        else:
                            content = contents[0] if contents else {}
                    else:
                        logger.warning(f"No content for {platform.value}")
                        continue
                    
                    # Extract content text
                    content_text = content.get("content", "")
                    
                    # Post to platform
                    logger.info(f"Posting to {platform.value}")
                    
                    if platform == Platform.FACEBOOK:
                        result = await asyncio.get_event_loop().run_in_executor(
                            None, self.getlate_service.post_to_facebook, content_text
                        )
                    
                    elif platform == Platform.INSTAGRAM:
                        # Instagram requires media
                        if "image_ideas" in content_data and content_data["image_ideas"]:
                            # Use generated image ideas (in real implementation, these would be actual images)
                            media_urls = ["https://example.com/image1.jpg"]  # Placeholder
                            result = await asyncio.get_event_loop().run_in_executor(
                                None, self.getlate_service.post_to_instagram, content_text, media_urls
                            )
                        else:
                            raise ValueError("Instagram posts require images")
                    
                    elif platform == Platform.LINKEDIN:
                        result = await asyncio.get_event_loop().run_in_executor(
                            None, self.getlate_service.post_to_linkedin, content_text
                        )
                    
                    elif platform == Platform.X:
                        result = await asyncio.get_event_loop().run_in_executor(
                            None, self.getlate_service.post_to_x, content_text
                        )
                    
                    elif platform == Platform.REDDIT:
                        # Reddit requires subreddit
                        subreddit = self._get_default_subreddit(topic=content_data.get("topic", ""))
                        result = await asyncio.get_event_loop().run_in_executor(
                            None, self.getlate_service.post_to_reddit, content_text, subreddit
                        )
                    
                    elif platform == Platform.PINTEREST:
                        # Pinterest requires board and media
                        board_id = "default_board"  # This would come from configuration
                        if "image_ideas" in content_data and content_data["image_ideas"]:
                            media_urls = ["https://example.com/image1.jpg"]  # Placeholder
                            result = await asyncio.get_event_loop().run_in_executor(
                                None, self.getlate_service.post_to_pinterest, 
                                content_text, board_id, media_urls
                            )
                        else:
                            raise ValueError("Pinterest posts require images")
                    
                    else:
                        logger.warning(f"Unsupported platform: {platform.value}")
                        continue
                    
                    posting_results[platform.value] = {
                        "success": True,
                        "post_id": result.get("id"),
                        "post_url": result.get("url"),
                        "content": content_text
                    }
                    
                    logger.info(f"Successfully posted to {platform.value}: {result.get('id')}")
                    
                except Exception as e:
                    logger.error(f"Failed to post to {platform.value}: {e}")
                    posting_results[platform.value] = {
                        "success": False,
                        "error": str(e)
                    }
            
            self.status = "completed"
            self.results = posting_results
            
            return PostResponse(
                success=True,
                workflow_id=self.workflow_id,
                posting_results=posting_results,
                message="Content posted successfully"
            )
            
        except Exception as e:
            self.status = "failed"
            self.errors.append(str(e))
            
            logger.error(f"Posting workflow failed: {e}")
            
            return PostResponse(
                success=False,
                workflow_id=self.workflow_id,
                error=str(e),
                message="Posting failed"
            )
    
    async def complete_workflow(
        self,
        topic: str,
        platforms: List[Platform],
        tone: Tone = Tone.PROFESSIONAL,
        include_images: bool = False,
        generate_variants: bool = False,
        auto_post: bool = True
    ) -> Dict[str, Any]:
        """
        Complete end-to-end workflow: content generation + posting
        
        Args:
            topic: Content topic
            platforms: Target platforms
            tone: Content tone
            include_images: Whether to include images
            generate_variants: Whether to generate variants
            auto_post: Whether to automatically post content
            
        Returns:
            Complete workflow results
        """
        try:
            logger.info(f"Starting complete workflow for topic: {topic}")
            
            # Step 1: Generate content
            content_response = await self.create_content_workflow(
                topic=topic,
                platforms=platforms,
                tone=tone,
                include_images=include_images,
                generate_variants=generate_variants
            )
            
            if not content_response.success:
                return {
                    "success": False,
                    "error": content_response.error,
                    "stage": "content_generation"
                }
            
            if not auto_post:
                return {
                    "success": True,
                    "stage": "content_generation_only",
                    "content_data": content_response.dict()
                }
            
            # Step 2: Post content
            post_response = await self.post_content_workflow(
                content_data=content_response.dict(),
                platforms=platforms,
                use_variants=generate_variants
            )
            
            return {
                "success": post_response.success,
                "stage": "complete",
                "content_data": content_response.dict(),
                "posting_results": post_response.posting_results if post_response.success else None,
                "error": post_response.error if not post_response.success else None
            }
            
        except Exception as e:
            logger.error(f"Complete workflow failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "stage": "workflow_error"
            }
    
    def _select_best_variant(self, variants: List[Dict], platform: str) -> Dict:
        """Select best content variant based on performance analysis"""
        if not variants:
            return {}
        
        # Simple selection logic - in real implementation, this would use
        # historical performance data and ML models
        best_variant = variants[0]
        highest_score = 0
        
        for variant in variants:
            # Score based on content analysis
            content = variant.get("content", "")
            score = len(content) * 0.1  # Length factor
            
            # Add engagement factors
            if "?" in content:  # Questions drive engagement
                score += 5
            if "!" in content:  # Exclamation adds energy
                score += 3
            if variant.get("hashtags"):  # Hashtags help discovery
                score += len(variant["hashtags"]) * 2
            
            if score > highest_score:
                highest_score = score
                best_variant = variant
        
        return best_variant
    
    def _get_default_subreddit(self, topic: str) -> str:
        """Get appropriate subreddit for topic"""
        # Simple mapping - in real implementation, this would use
        # topic analysis and subreddit research
        topic_lower = topic.lower()
        
        if "business" in topic_lower or "marketing" in topic_lower:
            return "r/business"
        elif "technology" in topic_lower or "tech" in topic_lower:
            return "r/technology"
        elif "design" in topic_lower or "creative" in topic_lower:
            return "r/design"
        elif "social" in topic_lower or "media" in topic_lower:
            return "r/socialmedia"
        else:
            return "r/selfpromotion"
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "current_step": self.current_step.value if self.current_step else None,
            "results": self.results,
            "errors": self.errors,
            "progress_percentage": self._calculate_progress()
        }
    
    def _calculate_progress(self) -> int:
        """Calculate workflow progress percentage"""
        if self.status == WorkflowStatus.COMPLETED:
            return 100
        elif self.status == WorkflowStatus.FAILED:
            return 0
        elif self.status == WorkflowStatus.IDLE:
            return 0
        
        # Simple progress calculation based on steps
        step_progress = {
            WorkflowStep.CONTENT_GENERATION: 30,
            WorkflowStep.IMAGE_GENERATION: 60,
            WorkflowStep.CONTENT_ANALYSIS: 80,
            WorkflowStep.POSTING: 90,
            WorkflowStep.SCHEDULING: 95
        }
        
        return step_progress.get(self.current_step, 0)