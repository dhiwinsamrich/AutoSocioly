from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import os
import json
from pathlib import Path

import google.generativeai as genai
from PIL import Image
import io
import base64

from ..config import settings
from ..utils.logger_config import get_logger

logger = get_logger('ai_service')

class AIService:
    """Service for AI-powered content generation using Google Gemini"""
    
    def __init__(self):
        """Initialize AI service with Gemini API"""
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not configured")
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.client = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        self.vision_model = genai.GenerativeModel('gemini-2.5-flash')
        
        logger.info("AI service initialized with Gemini API")
    
    def generate_social_media_content(
        self, 
        topic: str, 
        platform: str, 
        tone: str = "professional",
        max_length: int = 280,
        include_hashtags: bool = True,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate social media content for a specific platform
        
        Args:
            topic: Content topic
            platform: Target platform (facebook, instagram, twitter, linkedin, etc.)
            tone: Content tone (professional, casual, funny, etc.)
            max_length: Maximum character length
            include_hashtags: Whether to include hashtags
            context: Optional context information
            
        Returns:
            Generated content with metadata
        """
        try:
            logger.info(f"Generating {platform} content for topic: {topic}")
            
            # Platform-specific prompts
            platform_prompts = {
                "facebook": "Facebook posts should be engaging, conversational, and encourage interaction. Use a friendly tone.",
                "instagram": "Instagram captions should be visually descriptive, use relevant hashtags, and include calls-to-action for engagement.",
                "twitter": "Twitter posts should be concise, punchy, and use trending hashtags when relevant. Include a hook.",
                "linkedin": "LinkedIn posts should be professional, insightful, and provide value to business professionals. Use industry terminology.",
                "reddit": "Reddit posts should be authentic, community-focused, and follow subreddit rules. Be helpful and informative.",
                "pinterest": "Pinterest descriptions should be keyword-rich, inspiring, and help users discover your content through search."
            }
            
            platform_guidelines = platform_prompts.get(platform, "Create engaging social media content.")
            
            prompt = f"""
            Generate a {tone} social media post for {platform} about: {topic}
            
            Guidelines:
            {platform_guidelines}
            
            Requirements:
            - Maximum {max_length} characters
            - {tone} tone
            - {"Include relevant hashtags" if include_hashtags else "Do not include hashtags"}
            - Make it engaging and shareable
            {"- Context: " + context if context else ""}
            
            Return the response in this JSON format:
            {{
                "content": "The generated post content",
                "hashtags": ["list", "of", "hashtags"],
                "call_to_action": "engaging call to action",
                "engagement_score": "estimated engagement level (high/medium/low)"
            }}
            """
            
            response = self.client.generate_content(prompt)
            
            try:
                # Parse JSON response
                content_data = json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                content_data = {
                    "content": response.text.strip(),
                    "hashtags": [],
                    "call_to_action": "",
                    "engagement_score": "medium"
                }
            
            # Validate content length
            if len(content_data["content"]) > max_length:
                logger.warning(f"Generated content exceeds max length ({len(content_data['content'])} > {max_length})")
                content_data["content"] = content_data["content"][:max_length-3] + "..."
            
            logger.info(f"Generated content for {platform}: {len(content_data['content'])} characters")
            return content_data
            
        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            raise Exception(f"Content generation failed: {str(e)}")
    
    def generate_multiple_variants(
        self,
        topic: str,
        platform: str,
        count: int = 3,
        tone: str = "professional",
        max_length: int = 280
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple content variants for A/B testing
        
        Args:
            topic: Content topic
            platform: Target platform
            count: Number of variants to generate
            tone: Content tone
            max_length: Maximum character length
            
        Returns:
            List of content variants
        """
        try:
            logger.info(f"Generating {count} variants for {platform} about {topic}")
            
            prompt = f"""
            Generate {count} different {tone} social media posts for {platform} about: {topic}
            
            Each post should be unique in approach and style.
            Maximum {max_length} characters each.
            
            Return the response in this JSON format:
            {{
                "variants": [
                    {{
                        "content": "Post content 1",
                        "hashtags": ["hashtag1", "hashtag2"],
                        "approach": "description of the approach used",
                        "target_audience": "intended audience"
                    }},
                    {{
                        "content": "Post content 2",
                        "hashtags": ["hashtag1", "hashtag2"],
                        "approach": "description of the approach used",
                        "target_audience": "intended audience"
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
                    if len(variant["content"]) <= max_length:
                        cleaned_variants.append(variant)
                    else:
                        variant["content"] = variant["content"][:max_length-3] + "..."
                        cleaned_variants.append(variant)
                
                logger.info(f"Generated {len(cleaned_variants)} variants")
                return cleaned_variants
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse variants JSON, using fallback")
                return [{"content": response.text.strip(), "hashtags": [], "approach": "single post", "target_audience": "general"}]
                
        except Exception as e:
            logger.error(f"Failed to generate variants: {e}")
            raise Exception(f"Variants generation failed: {str(e)}")
    
    def generate_image_description(self, image_path: str) -> str:
        """
        Generate description for an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Image description
        """
        try:
            logger.info(f"Generating description for image: {image_path}")
            
            image = Image.open(image_path)
            
            prompt = """
            Analyze this image and provide a detailed description that would be suitable for:
            1. Social media alt text
            2. Image caption
            3. SEO purposes
            
            Include key visual elements, colors, mood, and any text visible in the image.
            Make the description engaging and informative.
            """
            
            response = self.vision_model.generate_content([prompt, image])
            description = response.text.strip()
            
            logger.info(f"Generated image description: {description[:100]}...")
            return description
            
        except Exception as e:
            logger.error(f"Failed to generate image description: {e}")
            raise Exception(f"Image description generation failed: {str(e)}")
    
    def generate_image_ideas(self, topic: str, count: int = 5, image_context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate image ideas for a topic
        
        Args:
            topic: Content topic
            count: Number of image ideas
            
        Returns:
            List of image ideas with descriptions
        """
        try:
            logger.info(f"Generating {count} image ideas for topic: {topic}")
            
            prompt = f"""
            Generate {count} creative image ideas for social media posts about: {topic}
            
            Each idea should include:
            - Visual concept
            - Color scheme suggestions
            - Style recommendations
            - Text overlay suggestions (if any)
            - Mood/atmosphere
            
            {f"Additional context: {image_context}" if image_context else ""}
            
            Return in this JSON format:
            {{
                "ideas": [
                    {{
                        "title": "Image idea title",
                        "description": "Detailed visual description",
                        "colors": ["primary colors"],
                        "style": "photographic/illustration/minimal/etc",
                        "text_overlay": "suggested text if any",
                        "mood": "overall mood/atmosphere"
                    }}
                ]
            }}
            """
            
            response = self.client.generate_content(prompt)
            
            try:
                ideas_data = json.loads(response.text)
                ideas = ideas_data.get("ideas", [])
                logger.info(f"Generated {len(ideas)} image ideas")
                return ideas
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse image ideas JSON, using fallback")
                return [{"title": "Creative visualization", "description": response.text.strip(), "colors": ["various"], "style": "mixed", "text_overlay": "", "mood": "engaging"}]
                
        except Exception as e:
            logger.error(f"Failed to generate image ideas: {e}")
            raise Exception(f"Image ideas generation failed: {str(e)}")
    
    def optimize_content_for_platform(self, content: str, platform: str) -> str:
        """
        Optimize existing content for a specific platform
        
        Args:
            content: Original content
            platform: Target platform
            
        Returns:
            Optimized content
        """
        try:
            logger.info(f"Optimizing content for {platform}")
            
            platform_limits = {
                "twitter": 280,
                "facebook": 2000,
                "instagram": 2200,
                "linkedin": 3000,
                "reddit": 40000,
                "pinterest": 500
            }
            
            max_length = platform_limits.get(platform, 2000)
            
            prompt = f"""
            Optimize this content for {platform}:
            
            Original content:
            {content}
            
            Platform-specific requirements:
            - Maximum {max_length} characters
            - Use appropriate tone and style for {platform}
            - Include relevant hashtags if appropriate
            - Make it more engaging for the platform's audience
            - Add appropriate calls-to-action
            
            Return only the optimized content.
            """
            
            response = self.client.generate_content(prompt)
            optimized_content = response.text.strip()
            
            # Ensure length limit
            if len(optimized_content) > max_length:
                optimized_content = optimized_content[:max_length-3] + "..."
            
            logger.info(f"Optimized content for {platform}: {len(optimized_content)} characters")
            return optimized_content
            
        except Exception as e:
            logger.error(f"Failed to optimize content: {e}")
            raise Exception(f"Content optimization failed: {str(e)}")
    
    def extract_keywords(self, text: str, count: int = 10) -> List[str]:
        """
        Extract relevant keywords from text
        
        Args:
            text: Input text
            count: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        try:
            logger.info(f"Extracting {count} keywords from text")
            
            prompt = f"""
            Extract {count} relevant keywords from this text:
            
            {text}
            
            Focus on:
            - Main topics and themes
            - Industry-specific terms
            - Action words
            - Hashtag-worthy keywords
            
            Return only the keywords as a comma-separated list, nothing else.
            """
            
            response = self.client.generate_content(prompt)
            keywords = [kw.strip() for kw in response.text.strip().split(',') if kw.strip()]
            
            logger.info(f"Extracted {len(keywords)} keywords")
            return keywords[:count]
            
        except Exception as e:
            logger.error(f"Failed to extract keywords: {e}")
            raise Exception(f"Keyword extraction failed: {str(e)}")
    
    def analyze_content_performance(self, content: str, platform: str) -> Dict[str, Any]:
        """
        Analyze content for predicted performance
        
        Args:
            content: Content to analyze
            platform: Target platform
            
        Returns:
            Performance analysis
        """
        try:
            logger.info(f"Analyzing content performance for {platform}")
            
            prompt = f"""
            Analyze this content for predicted performance on {platform}:
            
            Content: {content}
            
            Provide analysis in this JSON format:
            {{
                "engagement_score": "high/medium/low",
                "strengths": ["list of content strengths"],
                "weaknesses": ["list of content weaknesses"],
                "improvements": ["suggested improvements"],
                "best_posting_time": "suggested posting time",
                "target_audience": "primary audience description",
                "viral_potential": "high/medium/low"
            }}
            """
            
            response = self.client.generate_content(prompt)
            
            try:
                analysis = json.loads(response.text)
                logger.info(f"Content analysis completed: {analysis.get('engagement_score', 'unknown')} engagement")
                return analysis
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse performance analysis JSON")
                return {
                    "engagement_score": "medium",
                    "strengths": ["content provided"],
                    "weaknesses": ["analysis unavailable"],
                    "improvements": ["manual review recommended"],
                    "best_posting_time": "varies",
                    "target_audience": "general",
                    "viral_potential": "medium"
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze content performance: {e}")
            raise Exception(f"Content performance analysis failed: {str(e)}")