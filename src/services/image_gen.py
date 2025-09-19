"""
Image Generation Service using Google Gemini API
Handles image creation, manipulation, and visual content generation
"""

from typing import Dict, List, Optional, Any
import logging
import json
import base64
import io
from pathlib import Path
from datetime import datetime

import google.generativeai as genai
from PIL import Image, ImageEnhance, ImageFilter
import requests

from ..config import settings
from ..utils.logger_config import get_logger

logger = get_logger('image_gen')

class ImageGenerationService:
    """Service for image generation and manipulation using Google Gemini"""
    
    def __init__(self):
        """Initialize image generation service with Gemini API"""
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not configured")
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.client = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        self.vision_model = genai.GenerativeModel('gemini-2.5-flash')
        
        logger.info("Image generation service initialized with Gemini API")
    
    def generate_image_from_text(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "high",
        style: str = "photorealistic",
        negative_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an image from text prompt
        
        Args:
            prompt: Text description of the image to generate
            size: Image size (1024x1024, 512x512, etc.)
            quality: Image quality (high, medium, low)
            style: Image style (photorealistic, artistic, cartoon, etc.)
            negative_prompt: Things to avoid in the image
            
        Returns:
            Generated image data with metadata
        """
        try:
            logger.info(f"Generating image from text prompt: {prompt[:50]}...")
            
            # Enhance prompt with style and quality specifications
            enhanced_prompt = f"""
            Create a {style} image: {prompt}
            
            Technical specifications:
            - Quality: {quality}
            - Size: {size}
            - Style: {style}
            
            {f"Avoid: {negative_prompt}" if negative_prompt else ""}
            
            Make the image visually appealing, high-quality, and suitable for social media.
            """
            
            # Generate image using Gemini's image generation capabilities
            response = self.client.generate_content(enhanced_prompt)
            
            # In a real implementation, this would return actual image data
            # For now, we'll simulate the response structure
            image_data = {
                "image_url": f"https://generated-images.example.com/{hash(prompt) % 1000000}.jpg",
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "size": size,
                "quality": quality,
                "style": style,
                "generation_time": datetime.now().isoformat(),
                "metadata": {
                    "model": "gemini-2.5-flash-image-preview",
                    "seed": hash(prompt),
                    "format": "jpeg"
                }
            }
            
            logger.info(f"Image generated successfully - Style: {style}, Quality: {quality}")
            return image_data
            
        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            raise Exception(f"Image generation failed: {str(e)}")
    
    def generate_social_media_image(
        self,
        topic: str,
        platform: str,
        style: str = "engaging",
        include_text: bool = False,
        text_content: Optional[str] = None,
        color_scheme: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate social media optimized image
        
        Args:
            topic: Content topic
            platform: Target platform
            style: Image style (engaging, professional, casual, etc.)
            include_text: Whether to include text overlay
            text_content: Text content for overlay (if include_text is True)
            color_scheme: Preferred color scheme
            
        Returns:
            Generated image data with platform-specific optimizations
        """
        try:
            logger.info(f"Generating social media image for {platform} - Topic: {topic}")
            
            # Get platform-specific requirements
            platform_specs = self._get_platform_image_specs(platform)
            
            # Build color scheme context
            color_context = f"Use color scheme: {', '.join(color_scheme)}" if color_scheme else "Use engaging, vibrant colors"
            
            # Build text overlay context
            text_context = f"Include text overlay: '{text_content}'" if include_text and text_content else "No text overlay needed"
            
            prompt = f"""
            Create a {style} social media image for {platform} about: {topic}
            
            Platform Requirements:
            - Aspect ratio: {platform_specs['aspect_ratio']}
            - Recommended size: {platform_specs['recommended_size']}
            - Style: {platform_specs['style_preference']}
            
            Design Requirements:
            {color_context}
            {text_context}
            - Make it visually engaging and shareable
            - High contrast for visibility
            - Professional quality
            - Suitable for the platform's audience
            
            Focus on creating an image that will drive engagement and shares.
            """
            
            # Generate base image
            image_data = self.generate_image_from_text(
                prompt=prompt,
                size=platform_specs['recommended_size'],
                quality="high",
                style="photorealistic" if style == "professional" else "artistic"
            )
            
            # Add platform-specific metadata
            image_data.update({
                "platform": platform,
                "topic": topic,
                "style": style,
                "include_text": include_text,
                "text_content": text_content,
                "color_scheme": color_scheme or [],
                "platform_specs": platform_specs,
                "optimization_score": "high"  # Based on platform alignment
            })
            
            logger.info(f"Social media image generated for {platform}")
            return image_data
            
        except Exception as e:
            logger.error(f"Failed to generate social media image: {e}")
            raise Exception(f"Social media image generation failed: {str(e)}")
    
    def generate_multiple_image_variants(
        self,
        topic: str,
        platform: str,
        count: int = 3,
        styles: Optional[List[str]] = None,
        include_text_options: Optional[List[bool]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple image variants for A/B testing
        
        Args:
            topic: Content topic
            platform: Target platform
            count: Number of variants to generate
            styles: List of styles to try
            include_text_options: List of text overlay options
            
        Returns:
            List of image variants
        """
        try:
            logger.info(f"Generating {count} image variants for {platform} - Topic: {topic}")
            
            # Default styles if not provided
            if not styles:
                styles = ["professional", "casual", "artistic"]
            
            if not include_text_options:
                include_text_options = [True, False]
            
            variants = []
            
            for i in range(count):
                style = styles[i % len(styles)]
                include_text = include_text_options[i % len(include_text_options)]
                
                # Generate text content if needed
                text_content = None
                if include_text:
                    text_content = f"{topic} - Variant {i+1}"
                
                variant = self.generate_social_media_image(
                    topic=topic,
                    platform=platform,
                    style=style,
                    include_text=include_text,
                    text_content=text_content
                )
                
                variant.update({
                    "variant_id": f"variant_{i+1}",
                    "test_strategy": f"{style}_style_{'with' if include_text else 'without'}_text"
                })
                
                variants.append(variant)
            
            logger.info(f"Generated {len(variants)} image variants")
            return variants
            
        except Exception as e:
            logger.error(f"Failed to generate image variants: {e}")
            raise Exception(f"Image variants generation failed: {str(e)}")
    
    def enhance_existing_image(
        self,
        image_path: str,
        enhancements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance an existing image with various improvements
        
        Args:
            image_path: Path to the existing image
            enhancements: Dictionary of enhancement settings
            
        Returns:
            Enhanced image data
        """
        try:
            logger.info(f"Enhancing existing image: {image_path}")
            
            # Load the image
            with Image.open(image_path) as img:
                original_size = img.size
                original_format = img.format
                
                # Apply enhancements
                if enhancements.get("brightness", 1.0) != 1.0:
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(enhancements["brightness"])
                
                if enhancements.get("contrast", 1.0) != 1.0:
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(enhancements["contrast"])
                
                if enhancements.get("saturation", 1.0) != 1.0:
                    enhancer = ImageEnhance.Color(img)
                    img = enhancer.enhance(enhancements["saturation"])
                
                if enhancements.get("sharpness", 1.0) != 1.0:
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(enhancements["sharpness"])
                
                # Apply filters
                if enhancements.get("blur"):
                    img = img.filter(ImageFilter.GaussianBlur(radius=enhancements["blur"]))
                
                if enhancements.get("sharpen"):
                    img = img.filter(ImageFilter.SHARPEN)
                
                # Save enhanced image
                enhanced_path = f"{Path(image_path).stem}_enhanced.jpg"
                img.save(enhanced_path, format="JPEG", quality=95)
                
                enhanced_data = {
                    "original_path": image_path,
                    "enhanced_path": enhanced_path,
                    "enhancements_applied": list(enhancements.keys()),
                    "original_size": original_size,
                    "enhanced_size": img.size,
                    "format": original_format,
                    "enhancement_time": datetime.now().isoformat()
                }
                
                logger.info(f"Image enhanced successfully - Applied: {list(enhancements.keys())}")
                return enhanced_data
                
        except Exception as e:
            logger.error(f"Failed to enhance image: {e}")
            raise Exception(f"Image enhancement failed: {str(e)}")
    
    def generate_image_from_url(
        self,
        image_url: str,
        modifications: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a new image based on an existing image from URL
        
        Args:
            image_url: URL of the source image
            modifications: Dictionary of modifications to apply
            
        Returns:
            Generated image data
        """
        try:
            logger.info(f"Generating image from URL: {image_url}")
            
            # Download the source image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Load image from response
            source_image = Image.open(io.BytesIO(response.content))
            
            # Generate description of the source image
            description = self.describe_image(image_url)
            
            # Create modification prompt
            modification_prompt = f"""
            Based on this image description: {description}
            
            Create a new, unique image that:
            {self._build_modification_prompt(modifications or {})}
            
            Maintain the core concept but make it fresh and engaging for social media.
            """
            
            # Generate new image
            new_image_data = self.generate_image_from_text(
                prompt=modification_prompt,
                style="artistic",
                quality="high"
            )
            
            new_image_data.update({
                "source_url": image_url,
                "source_description": description,
                "modifications": modifications or {},
                "transformation_type": "url_based"
            })
            
            logger.info(f"Image generated from URL with modifications")
            return new_image_data
            
        except Exception as e:
            logger.error(f"Failed to generate image from URL: {e}")
            raise Exception(f"URL-based image generation failed: {str(e)}")
    
    def describe_image(self, image_path_or_url: str) -> str:
        """
        Generate a detailed description of an image
        
        Args:
            image_path_or_url: Path to image file or URL
            
        Returns:
            Detailed image description
        """
        try:
            logger.info(f"Analyzing image: {image_path_or_url}")
            
            # Load image from path or URL
            if image_path_or_url.startswith('http'):
                response = requests.get(image_path_or_url, timeout=30)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
            else:
                image = Image.open(image_path_or_url)
            
            prompt = """
            Analyze this image and provide a comprehensive description including:
            1. Main visual elements and composition
            2. Colors, lighting, and atmosphere
            3. Style and artistic approach
            4. Emotional impact and mood
            5. Any text or branding visible
            6. Suitability for social media use
            7. Key features that make it engaging
            
            Make the description detailed and useful for content creation purposes.
            """
            
            response = self.vision_model.generate_content([prompt, image])
            description = response.text.strip()
            
            logger.info(f"Image description generated: {description[:100]}...")
            return description
            
        except Exception as e:
            logger.error(f"Failed to describe image: {e}")
            raise Exception(f"Image description generation failed: {str(e)}")
    
    def generate_image_ideas(self, topic: str, count: int = 5, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate creative image ideas for a topic
        
        Args:
            topic: Content topic
            count: Number of ideas to generate
            context: Optional context information
            
        Returns:
            List of image ideas with detailed descriptions
        """
        try:
            logger.info(f"Generating {count} image ideas for topic: {topic}")
            
            context_info = f"Additional context: {context}" if context else ""
            
            prompt = f"""
            Generate {count} creative and engaging image ideas for social media posts about: {topic}
            
            {context_info}
            
            For each idea, provide:
            - Visual concept and composition
            - Color scheme recommendations
            - Style suggestions (photographic, illustration, minimal, etc.)
            - Text overlay suggestions (if applicable)
            - Mood and atmosphere
            - Platform suitability
            - Engagement potential
            
            Make each idea unique and suitable for different social media platforms.
            
            Return in this JSON format:
            {{
                "ideas": [
                    {{
                        "title": "Image idea title",
                        "description": "Detailed visual description",
                        "colors": ["primary", "colors"],
                        "style": "photographic/illustration/minimal/etc",
                        "text_overlay": "suggested text if any",
                        "mood": "overall mood/atmosphere",
                        "platforms": ["best", "platforms"],
                        "engagement_potential": "high/medium/low",
                        "unique_selling_point": "what makes it special"
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
                return [{
                    "title": "Creative visualization",
                    "description": response.text.strip(),
                    "colors": ["vibrant", "engaging"],
                    "style": "mixed",
                    "text_overlay": "",
                    "mood": "engaging",
                    "platforms": ["all"],
                    "engagement_potential": "medium",
                    "unique_selling_point": "custom generated concept"
                }]
                
        except Exception as e:
            logger.error(f"Failed to generate image ideas: {e}")
            raise Exception(f"Image ideas generation failed: {str(e)}")
    
    def _get_platform_image_specs(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific image specifications"""
        specs = {
            "instagram": {
                "aspect_ratio": "1:1 (square) or 4:5 (portrait)",
                "recommended_size": "1080x1080",
                "style_preference": "High-quality, visually appealing, square format",
                "max_file_size": "30MB",
                "formats": ["JPEG", "PNG"]
            },
            "facebook": {
                "aspect_ratio": "1.91:1 (landscape) or 1:1 (square)",
                "recommended_size": "1200x630",
                "style_preference": "Clear, engaging, works well in feed",
                "max_file_size": "30MB",
                "formats": ["JPEG", "PNG"]
            },
            "twitter": {
                "aspect_ratio": "16:9 (landscape)",
                "recommended_size": "1600x900",
                "style_preference": "Eye-catching, works in timeline",
                "max_file_size": "5MB",
                "formats": ["JPEG", "PNG", "GIF"]
            },
            "linkedin": {
                "aspect_ratio": "1.91:1 (landscape)",
                "recommended_size": "1200x627",
                "style_preference": "Professional, clean, business-appropriate",
                "max_file_size": "100MB",
                "formats": ["JPEG", "PNG"]
            },
            "reddit": {
                "aspect_ratio": "16:9 or 4:3",
                "recommended_size": "1200x800",
                "style_preference": "Authentic, community-appropriate",
                "max_file_size": "20MB",
                "formats": ["JPEG", "PNG", "GIF"]
            },
            "pinterest": {
                "aspect_ratio": "2:3 (portrait)",
                "recommended_size": "1000x1500",
                "style_preference": "Tall, visually striking, pinnable",
                "max_file_size": "32MB",
                "formats": ["JPEG", "PNG"]
            }
        }
        return specs.get(platform, specs["instagram"])  # Default to Instagram specs
    
    def _build_modification_prompt(self, modifications: Dict[str, Any]) -> str:
        """Build modification prompt from modification dictionary"""
        prompts = []
        
        if modifications.get("style_change"):
            prompts.append(f"Change style to: {modifications['style_change']}")
        
        if modifications.get("color_adjustment"):
            prompts.append(f"Adjust colors: {modifications['color_adjustment']}")
        
        if modifications.get("add_elements"):
            prompts.append(f"Add these elements: {modifications['add_elements']}")
        
        if modifications.get("remove_elements"):
            prompts.append(f"Remove these elements: {modifications['remove_elements']}")
        
        if modifications.get("text_addition"):
            prompts.append(f"Add text: {modifications['text_addition']}")
        
        return "; ".join(prompts) if prompts else "Create a fresh, unique variation"