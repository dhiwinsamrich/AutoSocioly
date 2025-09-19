"""
Text Generation Service using Google Gemini API
Handles caption generation, hashtag creation, and text-based content optimization
"""

from typing import Dict, List, Optional, Any
import logging
import json
from datetime import datetime

import google.generativeai as genai

from ..config import settings
from ..utils.logger_config import get_logger

logger = get_logger('text_gen')

class TextGenerationService:
    """Service for text-based content generation using Google Gemini"""
    
    def __init__(self):
        """Initialize text generation service with Gemini API"""
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not configured")
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.client = genai.GenerativeModel('gemini-2.5-flash')
        
        logger.info("Text generation service initialized with Gemini API")
    
    def generate_caption_and_hashtags(
        self, 
        topic: str, 
        platform: str, 
        tone: str = "professional",
        max_length: int = 280,
        include_hashtags: bool = True,
        context: Optional[str] = None,
        target_audience: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate social media caption and hashtags for a specific platform
        
        Args:
            topic: Content topic
            platform: Target platform (facebook, instagram, twitter, linkedin, etc.)
            tone: Content tone (professional, casual, funny, etc.)
            max_length: Maximum character length
            include_hashtags: Whether to include hashtags
            context: Optional context information
            target_audience: Specific audience to target
            
        Returns:
            Generated caption and hashtags with metadata
        """
        try:
            logger.info(f"Generating caption and hashtags for {platform} - Topic: {topic}")
            
            # Platform-specific guidelines
            platform_guidelines = self._get_platform_guidelines(platform)
            
            # Build audience context
            audience_context = f"Target audience: {target_audience}" if target_audience else ""
            
            prompt = f"""
            Create an engaging social media caption and relevant hashtags for {platform} about: {topic}
            
            Platform Guidelines:
            {platform_guidelines}
            
            Requirements:
            - Tone: {tone}
            - Maximum length: {max_length} characters (caption only)
            - Include relevant hashtags: {include_hashtags}
            - Make it engaging and shareable
            - Include a compelling call-to-action
            {audience_context}
            {"Context: " + context if context else ""}
            
            Return the response in this JSON format:
            {{
                "caption": "The generated caption text",
                "hashtags": ["list", "of", "relevant", "hashtags"],
                "call_to_action": "engaging call to action",
                "engagement_score": "high/medium/low",
                "character_count": number,
                "key_themes": ["main", "themes", "mentioned"]
            }}
            """
            
            response = self.client.generate_content(prompt)
            
            try:
                # Parse JSON response
                content_data = json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                content_data = {
                    "caption": response.text.strip(),
                    "hashtags": self._extract_hashtags_from_text(response.text),
                    "call_to_action": "Check it out!",
                    "engagement_score": "medium",
                    "character_count": len(response.text.strip()),
                    "key_themes": [topic.lower()]
                }
            
            # Validate caption length
            if len(content_data["caption"]) > max_length:
                logger.warning(f"Generated caption exceeds max length ({len(content_data['caption'])} > {max_length})")
                content_data["caption"] = content_data["caption"][:max_length-3] + "..."
                content_data["character_count"] = len(content_data["caption"])
            
            # Ensure hashtags are properly formatted
            content_data["hashtags"] = [tag.strip().replace('#', '') for tag in content_data["hashtags"]]
            
            logger.info(f"Generated caption: {len(content_data['caption'])} characters, {len(content_data['hashtags'])} hashtags")
            return content_data
            
        except Exception as e:
            logger.error(f"Failed to generate caption and hashtags: {e}")
            raise Exception(f"Caption generation failed: {str(e)}")
    
    def generate_multiple_caption_variants(
        self,
        topic: str,
        platform: str,
        count: int = 3,
        tone: str = "professional",
        max_length: int = 280,
        include_hashtags: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple caption variants for A/B testing
        
        Args:
            topic: Content topic
            platform: Target platform
            count: Number of variants to generate
            tone: Content tone
            max_length: Maximum character length
            include_hashtags: Whether to include hashtags
            
        Returns:
            List of caption variants
        """
        try:
            logger.info(f"Generating {count} caption variants for {platform} - Topic: {topic}")
            
            platform_guidelines = self._get_platform_guidelines(platform)
            
            prompt = f"""
            Create {count} different {tone} social media captions for {platform} about: {topic}
            
            Platform Guidelines:
            {platform_guidelines}
            
            Each caption should be unique in:
            - Opening hook/approach
            - Call-to-action style
            - Hashtag strategy
            - Emotional appeal
            - Writing style (question, statement, story, etc.)
            
            Requirements for each:
            - Maximum {max_length} characters
            - Include relevant hashtags: {include_hashtags}
            - Engaging and shareable
            - Clear call-to-action
            
            Return in this JSON format:
            {{
                "variants": [
                    {{
                        "caption": "Caption text 1",
                        "hashtags": ["hashtag1", "hashtag2"],
                        "call_to_action": "CTA style 1",
                        "approach": "question/story/statement/etc",
                        "target_audience": "specific audience",
                        "engagement_score": "high/medium/low"
                    }}
                ]
            }}
            """
            
            response = self.client.generate_content(prompt)
            
            try:
                variants_data = json.loads(response.text)
                variants = variants_data.get("variants", [])
                
                # Validate and clean variants
                cleaned_variants = []
                for variant in variants:
                    # Ensure caption length
                    if len(variant["caption"]) > max_length:
                        variant["caption"] = variant["caption"][:max_length-3] + "..."
                    
                    # Clean hashtags
                    variant["hashtags"] = [tag.strip().replace('#', '') for tag in variant["hashtags"]]
                    cleaned_variants.append(variant)
                
                logger.info(f"Generated {len(cleaned_variants)} caption variants")
                return cleaned_variants
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse variants JSON, using fallback")
                return [{
                    "caption": response.text.strip(),
                    "hashtags": self._extract_hashtags_from_text(response.text),
                    "call_to_action": "Check it out!",
                    "approach": "single post",
                    "target_audience": "general",
                    "engagement_score": "medium"
                }]
                
        except Exception as e:
            logger.error(f"Failed to generate caption variants: {e}")
            raise Exception(f"Caption variants generation failed: {str(e)}")
    
    def generate_hashtags_only(
        self,
        topic: str,
        platform: str,
        count: int = 10,
        include_branded: bool = False,
        include_trending: bool = False
    ) -> List[str]:
        """
        Generate only hashtags for a given topic and platform
        
        Args:
            topic: Content topic
            platform: Target platform
            count: Number of hashtags to generate
            include_branded: Whether to include branded hashtags
            include_trending: Whether to include trending hashtags
            
        Returns:
            List of hashtags
        """
        try:
            logger.info(f"Generating {count} hashtags for {platform} - Topic: {topic}")
            
            platform_hashtag_guidelines = self._get_hashtag_guidelines(platform)
            
            branded_context = "Include 2-3 relevant branded hashtags" if include_branded else ""
            trending_context = "Include 1-2 trending hashtags if relevant" if include_trending else ""
            
            prompt = f"""
            Generate {count} relevant hashtags for {platform} about: {topic}
            
            Platform Hashtag Guidelines:
            {platform_hashtag_guidelines}
            
            Requirements:
            - Mix of popular and niche hashtags
            - Relevant to the topic
            - High engagement potential
            - No spaces or special characters (except letters and numbers)
            {branded_context}
            {trending_context}
            
            Return only the hashtags as a JSON array, nothing else:
            ["hashtag1", "hashtag2", "hashtag3", ...]
            """
            
            response = self.client.generate_content(prompt)
            
            try:
                hashtags = json.loads(response.text)
                # Clean hashtags
                hashtags = [tag.strip().replace('#', '').lower() for tag in hashtags if tag.strip()]
                
                logger.info(f"Generated {len(hashtags)} hashtags")
                return hashtags[:count]
                
            except json.JSONDecodeError:
                # Fallback: extract hashtags from text
                hashtags = self._extract_hashtags_from_text(response.text)
                logger.info(f"Generated {len(hashtags)} hashtags (fallback)")
                return hashtags[:count]
                
        except Exception as e:
            logger.error(f"Failed to generate hashtags: {e}")
            raise Exception(f"Hashtag generation failed: {str(e)}")
    
    def optimize_caption_for_platform(
        self, 
        caption: str, 
        platform: str,
        max_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Optimize existing caption for a specific platform
        
        Args:
            caption: Original caption
            platform: Target platform
            max_length: Optional maximum length override
            
        Returns:
            Optimized caption with analysis
        """
        try:
            logger.info(f"Optimizing caption for {platform}")
            
            platform_limits = self._get_platform_character_limits()
            max_length = max_length or platform_limits.get(platform, 2000)
            
            platform_guidelines = self._get_platform_guidelines(platform)
            
            prompt = f"""
            Optimize this caption for {platform}:
            
            Original caption:
            {caption}
            
            Platform Guidelines:
            {platform_guidelines}
            
            Optimization requirements:
            - Maximum {max_length} characters
            - Use appropriate tone and style for {platform}
            - Add relevant hashtags if appropriate
            - Make it more engaging for the platform's audience
            - Improve call-to-action if present
            - Maintain the original message/intent
            
            Return in this JSON format:
            {{
                "optimized_caption": "The optimized caption",
                "hashtags_added": ["new", "hashtags"],
                "changes_made": ["list", "of", "changes"],
                "character_count": number,
                "engagement_improvement": "high/medium/low",
                "optimization_notes": "explanation of changes"
            }}
            """
            
            response = self.client.generate_content(prompt)
            
            try:
                optimization_data = json.loads(response.text)
                
                # Ensure length limit
                if len(optimization_data["optimized_caption"]) > max_length:
                    optimization_data["optimized_caption"] = optimization_data["optimized_caption"][:max_length-3] + "..."
                    optimization_data["character_count"] = len(optimization_data["optimized_caption"])
                
                logger.info(f"Caption optimized for {platform}")
                return optimization_data
                
            except json.JSONDecodeError:
                # Fallback
                logger.warning("Failed to parse optimization JSON, using fallback")
                return {
                    "optimized_caption": caption[:max_length],
                    "hashtags_added": [],
                    "changes_made": ["length adjusted"],
                    "character_count": len(caption[:max_length]),
                    "engagement_improvement": "medium",
                    "optimization_notes": "Basic length optimization applied"
                }
                
        except Exception as e:
            logger.error(f"Failed to optimize caption: {e}")
            raise Exception(f"Caption optimization failed: {str(e)}")
    
    def _get_platform_guidelines(self, platform: str) -> str:
        """Get platform-specific content guidelines"""
        guidelines = {
            "facebook": "Facebook posts should be engaging, conversational, and encourage interaction. Use a friendly, approachable tone. Include visual descriptions and questions to drive engagement.",
            "instagram": "Instagram captions should be visually descriptive, use relevant hashtags (5-15), include calls-to-action, and tell a story. Use emojis strategically.",
            "twitter": "Twitter posts should be concise, punchy, and use trending hashtags (2-3). Include a strong hook, be timely, and encourage retweets.",
            "linkedin": "LinkedIn posts should be professional, insightful, and provide value to business professionals. Use industry terminology, share expertise, and encourage meaningful discussion.",
            "reddit": "Reddit posts should be authentic, community-focused, and follow subreddit rules. Be helpful, informative, and avoid overt self-promotion.",
            "pinterest": "Pinterest descriptions should be keyword-rich, inspiring, and help users discover content through search. Use descriptive language and relevant keywords."
        }
        return guidelines.get(platform, "Create engaging social media content.")
    
    def _get_hashtag_guidelines(self, platform: str) -> str:
        """Get platform-specific hashtag guidelines"""
        guidelines = {
            "facebook": "Use 2-3 relevant hashtags. Focus on branded and community hashtags.",
            "instagram": "Use 5-15 hashtags. Mix popular, niche, and branded hashtags. Place at end of caption.",
            "twitter": "Use 2-3 hashtags. Focus on trending and conversation hashtags. Integrate naturally.",
            "linkedin": "Use 3-5 professional hashtags. Focus on industry, company, and topic hashtags.",
            "reddit": "Hashtags not commonly used. Focus on community-specific tags if any.",
            "pinterest": "Use 3-8 descriptive hashtags. Focus on search-friendly keywords."
        }
        return guidelines.get(platform, "Use relevant hashtags strategically.")
    
    def _get_platform_character_limits(self) -> Dict[str, int]:
        """Get platform character limits"""
        return {
            "twitter": 280,
            "facebook": 2000,
            "instagram": 2200,
            "linkedin": 3000,
            "reddit": 40000,
            "pinterest": 500
        }
    
    def _extract_hashtags_from_text(self, text: str) -> List[str]:
        """Extract hashtags from text using simple parsing"""
        import re
        hashtags = re.findall(r'#\w+', text)
        return [tag.replace('#', '').lower() for tag in hashtags]