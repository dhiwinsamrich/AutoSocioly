from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import os
import json
import re
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
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict]:
        """
        Extract JSON from response text, handling various formats
        """
        try:
            # First, try direct JSON parsing
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON within code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON without code blocks
        json_match = re.search(r'(\{.*?\})', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _get_response_text(self, response) -> str:
        """
        Extract text from Gemini response, handling different response formats
        """
        try:
            if hasattr(response, 'parts') and response.parts:
                return response.parts[0].text
            elif hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
        except Exception as e:
            logger.error(f"Failed to extract response text: {e}")
            return ""
    
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
            
            IMPORTANT: Return ONLY valid JSON in this exact format:
            {{
                "content": "The generated post content",
                "hashtags": ["list", "of", "hashtags"],
                "call_to_action": "engaging call to action",
                "engagement_score": "high"
            }}
            
            Do not include any text before or after the JSON. Only return the JSON object.
            """
            
            response = self.client.generate_content(prompt)
            response_text = self._get_response_text(response)
            
            # Try to extract JSON from response
            content_data = self._extract_json_from_response(response_text)
            
            if content_data is None:
                # Enhanced fallback - try to parse the response manually
                logger.warning(f"JSON parsing failed, attempting manual parsing for {platform}")
                content_data = self._create_fallback_content(response_text, topic, platform, tone, include_hashtags)
            
            # Validate and clean the content
            content_data = self._validate_and_clean_content(content_data, max_length, include_hashtags)
            
            logger.info(f"Generated content for {platform}: {len(content_data['content'])} characters")
            return content_data
            
        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            raise Exception(f"Content generation failed: {str(e)}")
    
    def _create_fallback_content(self, response_text: str, topic: str, platform: str, tone: str, include_hashtags: bool) -> Dict[str, Any]:
        """
        Create fallback content when JSON parsing fails
        """
        # Clean the response text
        content = response_text.strip()
        
        # Extract hashtags if present
        hashtags = []
        if include_hashtags:
            hashtag_pattern = r'#(\w+)'
            hashtags = re.findall(hashtag_pattern, content)
            # Remove hashtags from main content
            content = re.sub(r'#\w+\s*', '', content).strip()
        
        # Generate some basic hashtags if none found and needed
        if include_hashtags and not hashtags:
            hashtags = self._generate_basic_hashtags(topic, platform)
        
        return {
            "content": content,
            "hashtags": hashtags[:10],  # Limit to 10 hashtags
            "call_to_action": self._generate_basic_cta(platform),
            "engagement_score": "medium"
        }
    
    def _generate_basic_hashtags(self, topic: str, platform: str) -> List[str]:
        """
        Generate basic hashtags when AI response doesn't include them
        """
        # Basic hashtag generation based on topic keywords
        words = topic.lower().split()
        hashtags = []
        
        # Add topic-based hashtags
        for word in words:
            if len(word) > 3 and word.isalpha():
                hashtags.append(word)
        
        # Add platform-appropriate hashtags
        platform_hashtags = {
            "twitter": ["trending", "viral", "follow"],
            "instagram": ["instagood", "photooftheday", "love"],
            "linkedin": ["business", "professional", "career"],
            "facebook": ["community", "share", "connect"],
            "reddit": ["discussion", "community"],
            "pinterest": ["inspiration", "ideas", "discover"]
        }
        
        hashtags.extend(platform_hashtags.get(platform, ["content", "social"]))
        
        return hashtags[:8]  # Return max 8 hashtags
    
    def _generate_basic_cta(self, platform: str) -> str:
        """
        Generate basic call-to-action based on platform
        """
        ctas = {
            "twitter": "What do you think? Share your thoughts!",
            "instagram": "Double tap if you agree! 💖",
            "linkedin": "What's your experience with this?",
            "facebook": "Let us know in the comments!",
            "reddit": "What are your thoughts on this?",
            "pinterest": "Save this for later!"
        }
        
        return ctas.get(platform, "Let us know what you think!")
    
    def _validate_and_clean_content(self, content_data: Dict[str, Any], max_length: int, include_hashtags: bool) -> Dict[str, Any]:
        """
        Validate and clean the content data
        """
        # Ensure required fields exist
        if "content" not in content_data:
            content_data["content"] = "Content generation error. Please try again."
        
        if "hashtags" not in content_data:
            content_data["hashtags"] = []
        
        if "call_to_action" not in content_data:
            content_data["call_to_action"] = "Engage with this content!"
        
        if "engagement_score" not in content_data:
            content_data["engagement_score"] = "medium"
        
        # Validate content length
        if len(content_data["content"]) > max_length:
            logger.warning(f"Generated content exceeds max length ({len(content_data['content'])} > {max_length})")
            content_data["content"] = content_data["content"][:max_length-3] + "..."
        
        # Clean hashtags
        if isinstance(content_data["hashtags"], list):
            content_data["hashtags"] = [tag.strip().replace('#', '') for tag in content_data["hashtags"] if tag.strip()]
        else:
            content_data["hashtags"] = []
        
        # Remove hashtags if not requested
        if not include_hashtags:
            content_data["hashtags"] = []
        
        # Add character count
        content_data["character_count"] = len(content_data["content"])
        
        return content_data
    
    def generate_image_ideas(self, topic: str, count: int = 5, image_context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate image ideas for a topic
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
            
            IMPORTANT: Return ONLY valid JSON in this exact format:
            {{
                "ideas": [
                    {{
                        "title": "Image idea title",
                        "description": "Detailed visual description",
                        "colors": ["primary", "colors"],
                        "style": "photographic",
                        "text_overlay": "suggested text if any",
                        "mood": "overall mood/atmosphere"
                    }}
                ]
            }}
            
            Do not include any text before or after the JSON.
            """
            
            response = self.client.generate_content(prompt)
            response_text = self._get_response_text(response)
            
            # Try to extract JSON from response
            ideas_data = self._extract_json_from_response(response_text)
            
            if ideas_data and "ideas" in ideas_data:
                ideas = ideas_data["ideas"]
                logger.info(f"Generated {len(ideas)} image ideas")
                return ideas
            else:
                # Fallback
                logger.warning("Failed to parse image ideas JSON, using enhanced fallback")
                return self._create_fallback_image_ideas(response_text, topic, count)
                
        except Exception as e:
            logger.error(f"Failed to generate image ideas: {e}")
            return self._create_fallback_image_ideas("", topic, count)
    
    def _create_fallback_image_ideas(self, response_text: str, topic: str, count: int) -> List[Dict[str, Any]]:
        """
        Create fallback image ideas when JSON parsing fails
        """
        ideas = []
        
        # Split response into lines and try to extract ideas
        lines = response_text.split('\n')
        current_idea = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to identify different parts of an idea
            if any(keyword in line.lower() for keyword in ['idea', 'concept', 'title']):
                if current_idea:
                    ideas.append(current_idea)
                    current_idea = {}
                current_idea["title"] = line
                current_idea["description"] = response_text[:200] + "..."
                current_idea["colors"] = ["vibrant", "engaging"]
                current_idea["style"] = "mixed"
                current_idea["text_overlay"] = ""
                current_idea["mood"] = "engaging"
        
        if current_idea:
            ideas.append(current_idea)
        
        # If we still don't have enough ideas, generate basic ones
        while len(ideas) < count:
            ideas.append({
                "title": f"Creative visualization {len(ideas) + 1}",
                "description": f"A creative visual representation of {topic}",
                "colors": ["vibrant", "professional"],
                "style": "modern",
                "text_overlay": topic,
                "mood": "engaging"
            })
        
        return ideas[:count]
    
    def analyze_content_performance(self, content: str, platform: str) -> Dict[str, Any]:
        """
        Analyze content for predicted performance
        """
        try:
            logger.info(f"Analyzing content performance for {platform}")
            
            prompt = f"""
            Analyze this content for predicted performance on {platform}:
            
            Content: {content}
            
            IMPORTANT: Return ONLY valid JSON in this exact format:
            {{
                "engagement_score": "high",
                "strengths": ["list of content strengths"],
                "weaknesses": ["list of content weaknesses"],
                "improvements": ["suggested improvements"],
                "best_posting_time": "suggested posting time",
                "target_audience": "primary audience description",
                "viral_potential": "high"
            }}
            
            Do not include any text before or after the JSON.
            """
            
            response = self.client.generate_content(prompt)
            response_text = self._get_response_text(response)
            
            # Try to extract JSON from response
            analysis = self._extract_json_from_response(response_text)
            
            if analysis:
                logger.info(f"Content analysis completed: {analysis.get('engagement_score', 'unknown')} engagement")
                return analysis
            else:
                # Enhanced fallback
                logger.warning("Failed to parse performance analysis JSON, using enhanced fallback")
                return self._create_fallback_analysis(content, platform)
                
        except Exception as e:
            logger.error(f"Failed to analyze content performance: {e}")
            return self._create_fallback_analysis(content, platform)
    
    def _create_fallback_analysis(self, content: str, platform: str) -> Dict[str, Any]:
        """
        Create fallback analysis when JSON parsing fails
        """
        # Basic content analysis
        word_count = len(content.split())
        has_question = '?' in content
        has_hashtags = '#' in content
        has_exclamation = '!' in content
        
        # Determine engagement score based on content features
        engagement_score = "medium"
        if has_question and has_exclamation and word_count > 10:
            engagement_score = "high"
        elif word_count < 5:
            engagement_score = "low"
        
        # Platform-specific analysis
        platform_analysis = {
            "twitter": {
                "best_posting_time": "9-10 AM or 7-9 PM",
                "target_audience": "General Twitter users, trending topic followers"
            },
            "instagram": {
                "best_posting_time": "11 AM - 1 PM or 7-9 PM",
                "target_audience": "Visual content consumers, younger demographics"
            },
            "linkedin": {
                "best_posting_time": "8-10 AM or 5-6 PM on weekdays",
                "target_audience": "Business professionals, industry experts"
            },
            "facebook": {
                "best_posting_time": "1-3 PM or 7-9 PM",
                "target_audience": "Diverse age groups, community members"
            }
        }
        
        platform_info = platform_analysis.get(platform, {
            "best_posting_time": "varies by platform",
            "target_audience": "general social media users"
        })
        
        return {
            "engagement_score": engagement_score,
            "strengths": self._analyze_content_strengths(content, has_question, has_hashtags, has_exclamation),
            "weaknesses": self._analyze_content_weaknesses(content, word_count),
            "improvements": self._suggest_improvements(content, platform),
            "best_posting_time": platform_info["best_posting_time"],
            "target_audience": platform_info["target_audience"],
            "viral_potential": engagement_score
        }
    
    def _analyze_content_strengths(self, content: str, has_question: bool, has_hashtags: bool, has_exclamation: bool) -> List[str]:
        """Analyze content strengths"""
        strengths = []
        
        if has_question:
            strengths.append("Includes engaging questions")
        if has_hashtags:
            strengths.append("Uses relevant hashtags")
        if has_exclamation:
            strengths.append("Has energetic tone")
        if len(content) > 50:
            strengths.append("Provides detailed information")
        
        if not strengths:
            strengths.append("Clear and direct message")
            
        return strengths
    
    def _analyze_content_weaknesses(self, content: str, word_count: int) -> List[str]:
        """Analyze content weaknesses"""
        weaknesses = []
        
        if word_count < 5:
            weaknesses.append("Very short content")
        if not any(char in content for char in '!?'):
            weaknesses.append("Could be more engaging")
        if '#' not in content:
            weaknesses.append("Missing hashtags for discovery")
        
        if not weaknesses:
            weaknesses.append("Could benefit from more specific call-to-action")
            
        return weaknesses
    
    def _suggest_improvements(self, content: str, platform: str) -> List[str]:
        """Suggest content improvements"""
        improvements = []
        
        if '?' not in content:
            improvements.append("Add a question to encourage engagement")
        if '#' not in content:
            improvements.append("Include relevant hashtags")
        if platform == "instagram" and len(content) < 100:
            improvements.append("Consider adding more descriptive content")
        if platform == "twitter" and len(content) > 240:
            improvements.append("Shorten content for better readability")
            
        if not improvements:
            improvements.append("Content looks good as is")
            
        return improvements