"""
User Workflow Service - Implements the complete user flow:
User Input → Parse & Analyze → Generate Content → User Confirmation → Post/Modify → Final Post
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import logging
import asyncio
from pathlib import Path

from ..models import ContentRequest, Platform, Tone
from ..services.text_gen import TextGenerationService
from ..services.image_gen import ImageGenerationService
from ..services.poster_service import PosterService
from ..services.getlate_service import GetLateService
from ..config import settings
from ..utils.logger_config import get_logger
from ..utils.ngrok_manager import get_ngrok_manager

logger = get_logger('user_workflow')

class UserWorkflowService:
    """Service that implements the complete user confirmation workflow"""
    
    def __init__(self):
        """Initialize user workflow service"""
        self.text_gen = TextGenerationService()
        self.image_gen = ImageGenerationService()
        self.getlate_service = GetLateService(
            api_key=settings.GETLATE_API_KEY,
            base_url=settings.GETLATE_BASE_URL
        )
        self.poster_service = PosterService(self.getlate_service)
        self.ngrok_manager = get_ngrok_manager()
        self.active_sessions = {}  # Store user sessions
        logger.info("User workflow service initialized")
    
    async def process_user_input(
        self, 
        user_input: str, 
        platforms: List[str],
        tone: str = "professional",
        include_image: bool = True
    ) -> Dict[str, Any]:
        """
        Process user input and generate initial content
        
        Args:
            user_input: Raw user input text
            platforms: Target social media platforms
            tone: Content tone
            include_image: Whether to include image generation
            
        Returns:
            Initial content package for user review
        """
        start_time = datetime.now()
        workflow_logger = get_logger('workflow')
        session_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Processing user input for session {session_id}")
            workflow_logger.info(
                f"WORKFLOW START: Session {session_id}",
                extra={
                    'session_id': session_id,
                    'action': 'workflow_start',
                    'user_input': user_input,
                    'platforms': platforms,
                    'tone': tone,
                    'include_image': include_image,
                    'timestamp': start_time.isoformat()
                }
            )
            
            # Step 1: Parse and analyze user input using Gemini
            logger.info(f"Analyzing user input: '{user_input[:100]}...'")
            analysis_start = datetime.now()
            analysis = await self._analyze_user_input(user_input)
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            
            workflow_logger.info(
                f"Input analysis completed in {analysis_duration:.2f}s",
                extra={
                    'session_id': session_id,
                    'action': 'input_analysis',
                    'duration': analysis_duration,
                    'analysis_result': analysis
                }
            )
            
            # Step 2: Generate content based on analysis
            content_start = datetime.now()
            logger.info(f"Generating content package for platforms: {platforms}")
            content_package = await self._generate_content_package(
                topic=analysis.get("topic", user_input),
                platforms=platforms,
                tone=tone,
                include_image=include_image,
                hashtags_count=analysis.get("hashtags_count", 10)
            )
            content_duration = (datetime.now() - content_start).total_seconds()
            
            workflow_logger.info(
                f"Content package generated in {content_duration:.2f}s",
                extra={
                    'session_id': session_id,
                    'action': 'content_generation',
                    'duration': content_duration,
                    'platforms': platforms,
                    'topic': analysis.get("topic", user_input),
                    'tone': tone,
                    'image_count': len(content_package.get("images", [])),
                    'has_platform_content': bool(content_package.get("platform_content"))
                }
            )
            
            # Step 3: Store session for user confirmation
            self.active_sessions[session_id] = {
                "session_id": session_id,
                "user_input": user_input,
                "analysis": analysis,
                "content_package": content_package,
                "status": "awaiting_confirmation",
                "created_at": datetime.now(),
                "modification_history": []
            }
            
            # Step 4: Make images publicly available if generated
            if include_image and content_package.get("images"):
                logger.info(f"Making {len(content_package['images'])} images public using ngrok")
                ngrok_start = datetime.now()
                public_images = await self._make_images_public(content_package["images"])
                content_package["public_images"] = public_images
                ngrok_duration = (datetime.now() - ngrok_start).total_seconds()
                
                workflow_logger.info(
                    f"Images made public in {ngrok_duration:.2f}s",
                    extra={
                        'session_id': session_id,
                        'action': 'ngrok_public_urls',
                        'duration': ngrok_duration,
                        'original_count': len(content_package["images"]),
                        'public_count': len(public_images),
                        'success_rate': len(public_images) / len(content_package["images"]) if content_package["images"] else 0
                    }
                )
            
            total_duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Initial content generated for session {session_id} in {total_duration:.2f}s")
            workflow_logger.info(
                f"WORKFLOW STEP COMPLETE: Content generation",
                extra={
                    'session_id': session_id,
                    'action': 'content_generation_complete',
                    'total_duration': total_duration,
                    'status': 'awaiting_confirmation',
                    'public_images_count': len(content_package.get("public_images", [])),
                    'platforms_ready': platforms
                }
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "status": "awaiting_confirmation",
                "analysis": analysis,
                "content": content_package,
                "message": "Content generated successfully. Please review and confirm."
            }
            
        except Exception as e:
            total_duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Failed to process user input: {e}")
            workflow_logger.error(
                f"WORKFLOW ERROR: Content generation failed",
                extra={
                    'session_id': session_id,
                    'action': 'workflow_error',
                    'duration': total_duration,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'user_input': user_input,
                    'platforms': platforms,
                    'tone': tone,
                    'include_image': include_image
                }
            )
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "message": "Failed to process user input"
            }
    
    async def confirm_and_post(self, session_id: str, user_confirmation: bool = True, 
                               modifications: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Confirm and post content to social media platforms
        
        Args:
            session_id: Session ID for tracking
            user_confirmation: Whether user confirmed to post
            modifications: Optional modifications to content
            
        Returns:
            Posting results
        """
        start_time = datetime.now()
        workflow_logger = get_logger('workflow')
        
        try:
            # Retrieve session data
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                logger.error(f"Session {session_id} not found")
                workflow_logger.error(
                    f"WORKFLOW ERROR: Session not found",
                    extra={
                        'session_id': session_id,
                        'action': 'session_retrieval_error',
                        'error': 'Session not found'
                    }
                )
                return {"success": False, "error": "Session not found"}
            
            if not user_confirmation:
                # User cancelled posting
                session_data["status"] = "cancelled"
                logger.info(f"Posting cancelled by user for session {session_id}")
                workflow_logger.info(
                    f"WORKFLOW CANCELLED: User cancelled posting",
                    extra={
                        'session_id': session_id,
                        'action': 'user_cancelled',
                        'status': 'cancelled',
                        'timestamp': datetime.now().isoformat()
                    }
                )
                return {"success": True, "status": "cancelled", "message": "Posting cancelled by user"}
            
            # Apply modifications if provided
            if modifications:
                logger.info(f"Applying modifications for session {session_id}")
                modification_start = datetime.now()
                await self._apply_modifications(session_data, modifications)
                modification_duration = (datetime.now() - modification_start).total_seconds()
                
                workflow_logger.info(
                    f"Modifications applied in {modification_duration:.2f}s",
                    extra={
                        'session_id': session_id,
                        'action': 'content_modification',
                        'duration': modification_duration,
                        'modifications_applied': list(modifications.keys()) if modifications else []
                    }
                )
            
            # Post to platforms
            logger.info(f"Posting content for session {session_id}")
            posting_start = datetime.now()
            posting_results = await self._post_content_to_platforms(
                content_package=session_data["content_package"],
                platforms=list(session_data["content_package"]["platform_content"].keys())
            )
            posting_duration = (datetime.now() - posting_start).total_seconds()
            
            # Calculate posting statistics
            successful_posts = sum(1 for result in posting_results.values() if result.get("success"))
            total_platforms = len(posting_results)
            success_rate = successful_posts / total_platforms if total_platforms > 0 else 0
            
            workflow_logger.info(
                f"Posting completed in {posting_duration:.2f}s",
                extra={
                    'session_id': session_id,
                    'action': 'platform_posting',
                    'duration': posting_duration,
                    'total_platforms': total_platforms,
                    'successful_posts': successful_posts,
                    'failed_posts': total_platforms - successful_posts,
                    'success_rate': success_rate,
                    'platform_results': {platform: result.get("success", False) for platform, result in posting_results.items()}
                }
            )
            
            # Update session status
            session_data["status"] = "posted"
            session_data["posting_results"] = posting_results
            session_data["posted_at"] = datetime.now()
            
            total_duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Content posted successfully for session {session_id}")
            workflow_logger.info(
                f"WORKFLOW COMPLETE: Content posted successfully",
                extra={
                    'session_id': session_id,
                    'action': 'workflow_complete',
                    'total_duration': total_duration,
                    'status': 'posted',
                    'successful_platforms': successful_posts,
                    'total_platforms': total_platforms,
                    'success_rate': success_rate,
                    'posting_results': posting_results
                }
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "status": "posted",
                "results": posting_results,
                "message": f"Content posted successfully to {successful_posts}/{total_platforms} platforms"
            }
            
        except Exception as e:
            total_duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Failed to handle confirmation: {e}")
            workflow_logger.error(
                f"WORKFLOW ERROR: Posting failed",
                extra={
                    'session_id': session_id,
                    'action': 'posting_error',
                    'duration': total_duration,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'user_confirmation': user_confirmation,
                    'modifications_provided': bool(modifications)
                }
            )
            return {"success": False, "error": str(e)}
    
    async def modify_content(
        self, 
        session_id: str,
        text_prompt: Optional[str] = None,
        hashtag_prompt: Optional[str] = None,
        image_prompt: Optional[str] = None,
        regenerate_image: bool = False,
        regenerate_text: bool = False
    ) -> Dict[str, Any]:
        """
        Modify content based on user feedback
        
        Args:
            session_id: User session ID
            text_prompt: Instructions for text modification
            hashtag_prompt: Instructions for hashtag modification
            image_prompt: Instructions for image modification
            regenerate_image: Force image regeneration
            regenerate_text: Force text regeneration
            
        Returns:
            Modified content package
        """
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": "Session not found"}
            
            session = self.active_sessions[session_id]
            
            logger.info(f"Modifying content for session {session_id}")
            
            # Track modification history
            modification = {
                "timestamp": datetime.now(),
                "text_prompt": text_prompt,
                "hashtag_prompt": hashtag_prompt,
                "image_prompt": image_prompt,
                "regenerate_image": regenerate_image,
                "regenerate_text": regenerate_text
            }
            session["modification_history"].append(modification)
            
            # Apply modifications
            if text_prompt or hashtag_prompt or regenerate_text:
                await self._modify_text_content(session, text_prompt, hashtag_prompt, regenerate_text)
            
            if image_prompt or regenerate_image:
                await self._modify_image_content(session, image_prompt, regenerate_image)
            
            # Update session status
            session["status"] = "awaiting_confirmation"
            session["last_modified"] = datetime.now()
            
            # Make images public again if modified
            if session["content_package"].get("images"):
                public_images = await self._make_images_public(session["content_package"]["images"])
                session["content_package"]["public_images"] = public_images
            
            logger.info(f"Content modified for session {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "status": "awaiting_confirmation",
                "content": session["content_package"],
                "modification_history": session["modification_history"],
                "message": "Content modified successfully. Please review and confirm."
            }
            
        except Exception as e:
            logger.error(f"Failed to modify content: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input using Gemini"""
        try:
            # Use text generation service to analyze input
            analysis_prompt = f"""
            Analyze this user input for social media content creation:
            "{user_input}"
            
            Extract:
            1. Main topic/theme
            2. Target audience
            3. Suggested tone
            4. Key points to include
            5. Number of hashtags recommended (1-15)
            6. Whether an image would enhance the content (yes/no)
            7. Platform-specific considerations
            
            Return as JSON with keys: topic, audience, tone, key_points, hashtags_count, needs_image, platform_notes
            """
            
            # This would use the text generation service for analysis
            # For now, return a basic analysis
            return {
                "topic": user_input,
                "audience": "general social media users",
                "tone": "engaging",
                "key_points": [user_input],
                "hashtags_count": 10,
                "needs_image": True,
                "platform_notes": "Adapt content for each platform's style"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze user input: {e}")
            # Fallback to basic analysis
            return {
                "topic": user_input,
                "audience": "general",
                "tone": "professional",
                "key_points": [user_input],
                "hashtags_count": 10,
                "needs_image": True,
                "platform_notes": ""
            }
    
    async def _generate_content_package(
        self,
        topic: str,
        platforms: List[str],
        tone: str,
        include_image: bool,
        hashtags_count: int
    ) -> Dict[str, Any]:
        """Generate complete content package"""
        
        platform_content = {}
        images = []
        
        # Generate content for each platform
        for platform in platforms:
            # Generate text content
            text_content = self.text_gen.generate_caption_and_hashtags(
                topic=topic,
                platform=platform,
                tone=tone,
                include_hashtags=True
            )
            
            platform_content[platform] = {
                "caption": text_content["caption"],
                "hashtags": text_content["hashtags"],
                "call_to_action": text_content.get("call_to_action", ""),
                "engagement_score": text_content.get("engagement_score", "medium"),
                "character_count": text_content.get("character_count", 0)
            }
        
        # Generate images if requested
        if include_image:
            try:
                # Generate image ideas first
                image_ideas = self.image_gen.generate_image_ideas(
                    topic=topic,
                    count=1
                )
                
                # Generate actual image using first idea
                if image_ideas:
                    main_image = await self.image_gen.generate_social_media_image(
                        topic=topic,
                        platform=platforms[0],  # Use first platform
                        style="engaging"
                    )
                    images.append(main_image)
                    
            except Exception as e:
                logger.warning(f"Image generation failed: {e}")
                images = []
        
        return {
            "platform_content": platform_content,
            "images": images,
            "topic": topic,
            "tone": tone,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _make_images_public(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Make images publicly available using ngrok"""
        public_images = []
        
        for image in images:
            try:
                # Get image path from image data
                image_path = image.get("image_path") or image.get("local_path") or image.get("filepath")
                
                if image_path and Path(image_path).exists():
                    # Create public URL using ngrok
                    public_url = self.ngrok_manager.create_public_url(image_path)
                    
                    public_image = image.copy()
                    public_image["public_url"] = public_url
                    public_image["accessible"] = True
                    
                    public_images.append(public_image)
                else:
                    logger.warning(f"Image file not found: {image_path}")
                    
            except Exception as e:
                logger.error(f"Failed to make image public: {e}")
                
        return public_images
    
    async def _modify_text_content(
        self, 
        session: Dict[str, Any],
        text_prompt: Optional[str],
        hashtag_prompt: Optional[str],
        regenerate_text: bool
    ):
        """Modify text content based on user feedback"""
        try:
            content_package = session["content_package"]
            
            for platform, content in content_package["platform_content"].items():
                if text_prompt or regenerate_text:
                    # Generate new caption based on modification prompt
                    new_caption = self.text_gen.generate_caption_and_hashtags(
                        topic=text_prompt or session["user_input"],
                        platform=platform,
                        tone=session["content_package"]["tone"],
                        context=text_prompt
                    )
                    
                    content["caption"] = new_caption["caption"]
                    content["character_count"] = new_caption["character_count"]
                
                if hashtag_prompt:
                    # Generate new hashtags based on modification prompt
                    new_hashtags = self.text_gen.generate_hashtags_only(
                        topic=hashtag_prompt,
                        platform=platform,
                        count=len(content["hashtags"])
                    )
                    
                    content["hashtags"] = new_hashtags
                
                # Update engagement score
                content["engagement_score"] = "high"  # Could be recalculated
                
        except Exception as e:
            logger.error(f"Failed to modify text content: {e}")
            raise
    
    async def _modify_image_content(
        self, 
        session: Dict[str, Any],
        image_prompt: Optional[str],
        regenerate_image: bool
    ):
        """Modify image content based on user feedback"""
        try:
            content_package = session["content_package"]
            
            if regenerate_image and image_prompt:
                # Generate completely new image
                new_image = await self.image_gen.generate_social_media_image(
                    topic=image_prompt,
                    platform=list(content_package["platform_content"].keys())[0],
                    style="modified"
                )
                
                content_package["images"] = [new_image]
                
            elif image_prompt:
                # Modify existing image based on prompt
                # This would require image editing capabilities
                logger.info(f"Image modification requested: {image_prompt}")
                
                # For now, generate a new image with the modification prompt
                modified_image = await self.image_gen.generate_social_media_image(
                    topic=f"{session['user_input']} - {image_prompt}",
                    platform=list(content_package["platform_content"].keys())[0],
                    style="modified"
                )
                
                content_package["images"] = [modified_image]
                
        except Exception as e:
            logger.error(f"Failed to modify image content: {e}")
            raise
    
    async def _post_content_to_platforms(
        self,
        content_package: Dict[str, Any],
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Post content to social media platforms"""
        
        posting_results = {}
        
        try:
            for platform in platforms:
                platform_content = content_package["platform_content"][platform]
                
                # Prepare content for posting
                post_content = f"{platform_content['caption']}\n\n"
                post_content += " ".join([f"#{tag}" for tag in platform_content['hashtags']])
                
                # Add image if available
                media_urls = []
                if content_package.get("public_images"):
                    media_urls = [img.get("public_url") for img in content_package["public_images"]]
                
                try:
                    # Post using poster service
                    poster = self.poster_service.get_poster(platform)
                    result = await poster.post_content(
                        content=post_content,
                        media_urls=media_urls
                    )
                    
                    posting_results[platform] = {
                        "success": True,
                        "post_id": result.get("post_id"),
                        "post_url": result.get("post_url"),
                        "message": "Posted successfully"
                    }
                    
                except Exception as e:
                    logger.error(f"Failed to post to {platform}: {e}")
                    posting_results[platform] = {
                        "success": False,
                        "error": str(e),
                        "message": f"Failed to post to {platform}"
                    }
            
            return posting_results
            
        except Exception as e:
            logger.error(f"Failed to post content: {e}")
            raise
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current session status"""
        return self.active_sessions.get(session_id)
    
    def cleanup_session(self, session_id: str):
        """Clean up completed session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Cleaned up session {session_id}")
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        return [
            {
                "session_id": sid,
                "status": session["status"],
                "topic": session["content_package"]["topic"],
                "created_at": session["created_at"],
                "last_modified": session.get("last_modified")
            }
            for sid, session in self.active_sessions.items()
        ]