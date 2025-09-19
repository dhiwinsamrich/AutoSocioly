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
from ..services.image_gen import ImageGenerationService
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
        self.image_gen_service = ImageGenerationService()
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
            generated_images = []
            if include_images:
                logger.info("Generating image ideas and actual images")
                self.current_step = "image_generation"
                
                # First generate image ideas (only 1 for single image generation)
                image_ideas = await self.ai_service.generate_image_ideas(
                    topic, 1, image_context
                )
                
                # Then generate actual images based on the ideas
                logger.info("Generating actual images from ideas")
                for i, idea in enumerate(image_ideas):
                    try:
                        image_description = idea.get("description", "")
                        if image_description:
                            # Generate image using the description
                            image_data = await self.image_gen_service.generate_image_from_text_async(
                                image_description,
                                f"{topic}_{i}"
                            )
                            if image_data and image_data.get("image_url"):
                                generated_images.append(image_data["image_url"])
                                logger.info(f"Generated image {i+1} for topic: {topic}")
                            else:
                                logger.warning(f"Failed to generate image {i+1}")
                    except Exception as e:
                        logger.error(f"Error generating image {i+1}: {e}")
                        # Continue with other images even if one fails
            
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
                "generated_images": generated_images,
                "performance_analysis": performance_analysis
            }
            

            
            return ContentResponse(
                success=True,
                workflow_id=self.workflow_id,
                platform_content=platform_content,
                image_ideas=image_ideas,
                generated_images=generated_images,
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
                platform_content={},  # Required field - empty dict for error case
                error=str(e),
                message="Content generation failed"
            )
    
    async def post_content_workflow(
        self,
        workflow_id: str,
        platforms: List[str],
        selected_variants: Optional[Dict[str, int]] = None,
        schedule_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post content to selected platforms
        
        Args:
            workflow_id: Workflow ID
            platforms: List of platforms to post to
            selected_variants: Dict mapping platform to variant index
            schedule_time: Optional schedule time
            
        Returns:
            Posting results
        """
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            if workflow['status'] != 'completed':
                raise ValueError(f"Workflow {workflow_id} is not completed")
            
            # Update workflow status
            workflow['status'] = 'publishing'
            workflow['progress'] = 80
            
            results = {}
            
            # Get linked accounts
            accounts = await self.get_linked_accounts()
            if not accounts:
                raise ValueError("No linked social media accounts found")
            
            # Post to each platform
            for platform in platforms:
                try:
                    # Get account for platform
                    account = next((acc for acc in accounts if acc['platform'] == platform), None)
                    if not account:
                        results[platform] = {"error": f"No account found for {platform}"}
                        continue
                    
                    # Select variant if specified
                    if selected_variants and platform in selected_variants:
                        variant_index = selected_variants[platform]
                        content = workflow['content']['variants'][variant_index]
                    else:
                        # Use first variant as default
                        content = workflow['content']['variants'][0]
                    
                    # Get media files if available
                    media_files = []
                    if workflow.get('images'):
                        media_files = workflow['images']
                    
                    # Post using Getlate API
                    post_result = await self.getlate_service.post_content_with_media(
                        account_id=account['id'],
                        content=content['content'],
                        media_files=media_files,
                        platform=platform,
                        scheduled_time=schedule_time,
                        hashtags=content.get('hashtags', []),
                        mentions=content.get('mentions', [])
                    )
                    
                    results[platform] = {
                        "success": True,
                        "post_id": post_result.get('id'),
                        "url": post_result.get('url'),
                        "platform_data": post_result
                    }
                    
                    logger.info(f"Successfully posted to {platform}: {post_result.get('id')}")
                    
                except Exception as e:
                    logger.error(f"Failed to post to {platform}: {e}")
                    results[platform] = {"error": str(e)}
            
            # Update workflow with results
            workflow['posting_results'] = results
            workflow['status'] = 'published'
            workflow['progress'] = 100
            workflow['completed_at'] = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            logger.error(f"Posting workflow failed: {e}")
            if workflow_id in self.workflows:
                self.workflows[workflow_id]['status'] = 'failed'
                self.workflows[workflow_id]['error'] = str(e)
            raise
    
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

    async def get_linked_accounts(self) -> List[Dict[str, Any]]:
        """
        Get all linked social media accounts
        
        Returns:
            List of linked account information
        """
        try:
            accounts = await self.getlate_service.get_accounts()
            return accounts
        except Exception as e:
            logger.error(f"Failed to get linked accounts: {e}")
            return []

    async def regenerate_image_with_prompt(self, content_id: str, new_prompt: str, preserve_context: bool = True) -> Dict[str, Any]:
        """
        Regenerate an image with a new prompt while preserving context
        
        Args:
            content_id: The content ID to regenerate image for
            new_prompt: The new image prompt
            preserve_context: Whether to preserve original context
            
        Returns:
            Dict with success status and new image data
        """
        try:
            logger.info(f"Regenerating image for content {content_id} with new prompt")
            
            # Get original content to preserve context
            original_content = None
            if preserve_context:
                original_content = self.content_manager.get_content(content_id)
            
            # Use image generation service with context preservation
            from .image_gen import ImageGenerationService
            image_service = ImageGenerationService()
            
            # Generate new image with enhanced prompt that includes context
            enhanced_prompt = new_prompt
            if original_content and preserve_context:
                context = original_content.get('context', '')
                if context:
                    enhanced_prompt = f"{new_prompt} (maintaining context: {context})"
            
            # Generate image using the async method
            image_result = await image_service.agenerate_image_from_text(
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="high",
                style="photorealistic",
                context=original_content.get('context') if original_content else None
            )
            
            if image_result and image_result.get("image_url"):
                # Update content with new image
                update_data = {
                    "image_url": image_result["image_url"],
                    "image_prompt": new_prompt,
                    "regenerated_at": datetime.now().isoformat(),
                    "regeneration_context": enhanced_prompt
                }
                
                success = self.content_manager.update_content(content_id, update_data)
                
                if success:
                    logger.info(f"Image regenerated successfully for content {content_id}")
                    return {
                        "success": True,
                        "image_url": image_result["image_url"],
                        "prompt": new_prompt,
                        "context_preserved": preserve_context
                    }
                else:
                    logger.error(f"Failed to update content {content_id} with new image")
                    return {
                        "success": False,
                        "error": "Failed to update content with new image"
                    }
            else:
                logger.error(f"Failed to generate new image for content {content_id}")
                return {
                    "success": False,
                    "error": "Failed to generate new image"
                }
                
        except Exception as e:
            logger.error(f"Error regenerating image for content {content_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def modify_image_with_feedback(self, content_id: str, feedback: str, image_url: str) -> Dict[str, Any]:
        """
        Modify an existing image based on user feedback
        
        Args:
            content_id: The content ID
            feedback: User feedback for modification
            image_url: Current image URL
            
        Returns:
            Dict with success status and modified image data
        """
        try:
            logger.info(f"Modifying image for content {content_id} based on feedback: {feedback}")
            
            # Get original content for context
            original_content = self.content_manager.get_content(content_id)
            
            # Use image generation service for modification
            from .image_gen import ImageGenerationService
            image_service = ImageGenerationService()
            
            # Modify image with feedback
            modification_result = await image_service.amodify_image(
                image_url=image_url,
                modification_prompt=feedback,
                preserve_core_elements=True,
                context=original_content.get('context') if original_content else None
            )
            
            if modification_result and modification_result.get("image_url"):
                # Update content with modified image
                update_data = {
                    "image_url": modification_result["image_url"],
                    "modification_feedback": feedback,
                    "modified_at": datetime.now().isoformat()
                }
                
                success = self.content_manager.update_content(content_id, update_data)
                
                if success:
                    logger.info(f"Image modified successfully for content {content_id}")
                    return {
                        "success": True,
                        "image_url": modification_result["image_url"],
                        "feedback": feedback
                    }
                else:
                    logger.error(f"Failed to update content {content_id} with modified image")
                    return {
                        "success": False,
                        "error": "Failed to update content with modified image"
                    }
            else:
                logger.error(f"Failed to modify image for content {content_id}")
                return {
                    "success": False,
                    "error": "Failed to modify image"
                }
                
        except Exception as e:
            logger.error(f"Error modifying image for content {content_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }