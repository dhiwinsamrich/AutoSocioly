"""
Image Generation Service using Google Gemini API
Handles image creation, manipulation, and visual content generation
"""

from typing import Dict, List, Optional, Any
import logging
import json
import base64
import hashlib
import io
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

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
    
    async def generate_image_from_text_async(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "high",
        style: str = "photorealistic",
        negative_prompt: Optional[str] = None,
        preserve_context: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Async version of image generation with better error handling and context preservation
        
        Args:
            prompt: Text description of the image to generate
            size: Image size (1024x1024, 512x512, etc.)
            quality: Image quality (high, medium, low)
            style: Image style (photorealistic, artistic, cartoon, etc.)
            negative_prompt: Things to avoid in the image
            preserve_context: Original image context for regeneration
            retry_count: Current retry attempt number
            
        Returns:
            Generated image data with metadata
        """
        try:
            logger.info(f"Async generating image from text prompt: {prompt[:50]}... (retry {retry_count})")
            
            # Build enhanced prompt with context preservation
            if preserve_context:
                enhanced_prompt = f"""
                ORIGINAL IMAGE CONTEXT (PRESERVE THESE ELEMENTS):
                - Core concept: {preserve_context.get('core_concept', '')}
                - Key visual elements: {preserve_context.get('key_elements', '')}
                - Style: {preserve_context.get('style', style)}
                - Color scheme: {preserve_context.get('colors', 'vibrant')}
                
                MODIFICATION REQUEST:
                {prompt}
                
                INSTRUCTIONS:
                1. PRESERVE all core elements from the original context above
                2. APPLY the modification request precisely
                3. MAINTAIN visual coherence and professional quality
                4. ENSURE the result is suitable for social media
                """
            else:
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
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.client.generate_content, enhanced_prompt
            )
            
            # Extract image data from response with better error handling
            image_bytes = None
            
            try:
                # Method 1: Check if response has parts with inline data
                if hasattr(response, 'parts') and response.parts:
                    for part in response.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            image_bytes = part.inline_data.data
                            break
                        elif hasattr(part, 'data') and part.data:
                            image_bytes = part.data
                            break
                
                # Method 2: Check candidates structure
                if not image_bytes and hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                image_bytes = part.inline_data.data
                                break
                            elif hasattr(part, 'data') and part.data:
                                image_bytes = part.data
                                break
                
                # Method 3: Try to get raw response data
                if not image_bytes:
                    logger.warning("No image data found in structured response, checking raw response")
                    
            except Exception as extract_error:
                logger.warning(f"Error extracting image data: {extract_error}")
            
            if not image_bytes:
                # If no image data found and we haven't retried too many times, retry with modified prompt
                if retry_count < 2:
                    logger.warning(f"No image data found, retrying with modified prompt (attempt {retry_count + 1})")
                    # Try with a simpler, more direct prompt
                    simple_prompt = f"Create a {style} image: {prompt}"
                    return await self.generate_image_from_text_async(
                        prompt=simple_prompt,
                        size=size,
                        quality=quality,
                        style=style,
                        negative_prompt=negative_prompt,
                        preserve_context=preserve_context,
                        retry_count=retry_count + 1
                    )
                else:
                    # Max retries reached, create fallback but mark it as such
                    logger.error("Max retries reached, creating fallback image")
                    return await self._create_fallback_image(prompt, size, quality, style, preserve_context)
            
            # Save the generated image
            uploads_dir = Path("static/uploads")
            uploads_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}_{hash(prompt) % 10000}.png"
            filepath = uploads_dir / filename
            
            # Save image to file
            image = Image.open(io.BytesIO(image_bytes))
            image.save(filepath, "PNG")
            
            logger.info(f"Image saved to {filepath}")
            
            image_data = {
                "image_url": f"/static/uploads/{filename}",
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "size": size,
                "quality": quality,
                "style": style,
                "generation_time": datetime.now().isoformat(),
                "filepath": str(filepath),
                "metadata": {
                    "model": "gemini-2.5-flash-image-preview",
                    "seed": hash(prompt),
                    "format": "png",
                    "size_bytes": len(image_bytes),
                    "width": image.width,
                    "height": image.height,
                    "retry_count": retry_count,
                    "generation_method": "async_with_context_preservation",
                    "success": True
                }
            }
            
            # Add preserve context to metadata if available
            if preserve_context:
                image_data["metadata"]["preserve_context"] = preserve_context
            
            logger.info(f"Image generated successfully - Style: {style}, Quality: {quality}, Size: {image.width}x{image.height}")
            return image_data
            
        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            
            # If we haven't retried too many times, retry
            if retry_count < 2:
                logger.info(f"Retrying image generation due to error (attempt {retry_count + 1})")
                return await self.generate_image_from_text_async(
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    style=style,
                    negative_prompt=negative_prompt,
                    preserve_context=preserve_context,
                    retry_count=retry_count + 1
                )
            else:
                # Max retries reached, create fallback
                logger.error("Max retries reached due to persistent errors, creating fallback")
                return await self._create_fallback_image(prompt, size, quality, style, preserve_context)

    async def _create_fallback_image(self, prompt: str, size: str, quality: str, style: str, preserve_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a fallback image when generation fails completely
        """
        try:
            logger.warning("Creating fallback image due to generation failure")
            
            # Determine size
            placeholder_size = (512, 512)
            if "1024" in size:
                placeholder_size = (1024, 1024)
            elif "512" in size:
                placeholder_size = (512, 512)
            
            # Create a simple but meaningful placeholder based on the prompt
            img = Image.new('RGB', placeholder_size, color=(73, 109, 137))
            
            # Add some basic visual elements based on the prompt
            if "social" in prompt.lower() or "media" in prompt.lower():
                # Create a simple social media themed placeholder
                img = Image.new('RGB', placeholder_size, color=(59, 130, 246))  # Blue theme
            elif "business" in prompt.lower() or "professional" in prompt.lower():
                # Create a business themed placeholder
                img = Image.new('RGB', placeholder_size, color(17, 24, 39))  # Dark theme
            elif "nature" in prompt.lower() or "outdoor" in prompt.lower():
                # Create a nature themed placeholder
                img = Image.new('RGB', placeholder_size, color=(34, 197, 94))  # Green theme
            
            # Save placeholder to bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            image_bytes = img_buffer.getvalue()
            
            # Save the fallback image
            uploads_dir = Path("static/uploads")
            uploads_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fallback_{timestamp}_{hash(prompt) % 10000}.png"
            filepath = uploads_dir / filename
            
            img.save(filepath, "PNG")
            
            logger.info(f"Created fallback image {placeholder_size[0]}x{placeholder_size[1]}")
            
            fallback_data = {
                "image_url": f"/static/uploads/{filename}",
                "prompt": prompt,
                "enhanced_prompt": f"FALLBACK IMAGE - Original prompt: {prompt}",
                "size": size,
                "quality": quality,
                "style": style,
                "generation_time": datetime.now().isoformat(),
                "filepath": str(filepath),
                "error": "Image generation failed - fallback created",
                "metadata": {
                    "model": "gemini-2.5-flash-image-preview",
                    "seed": hash(prompt),
                    "format": "png",
                    "size_bytes": len(image_bytes),
                    "width": placeholder_size[0],
                    "height": placeholder_size[1],
                    "fallback": True,
                    "generation_method": "fallback",
                    "success": False
                }
            }
            
            if preserve_context:
                fallback_data["metadata"]["preserve_context"] = preserve_context
            
            return fallback_data
            
        except Exception as e:
            logger.error(f"Failed to create fallback image: {e}")
            # Last resort - return error data
            return {
                "image_url": None,
                "prompt": prompt,
                "error": f"Both generation and fallback failed: {str(e)}",
                "metadata": {
                    "success": False,
                    "complete_failure": True
                }
            }
    
    async def generate_social_media_image(
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
            image_data = await self.generate_image_from_text_async(
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
    
    async def generate_multiple_image_variants(
        self,
        topic: str,
        platform: str,
        count: int = 1, #Reduce it for the limitaion of the image count
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
                
                variant = await self.generate_social_media_image(
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
    
    async def modify_image_preserving_core(
        self,
        original_prompt: str,
        modification_request: str,
        original_image_url: Optional[str] = None,
        platform: Optional[str] = None,
        preserve_elements: List[str] = None
    ) -> Dict[str, Any]:
        """
        Modify an image while preserving core elements and composition
        
        Args:
            original_prompt: Original image generation prompt
            modification_request: User's modification request
            original_image_url: URL of the original image (optional)
            platform: Target platform for optimizations
            preserve_elements: Specific elements to preserve (optional)
            
        Returns:
            Modified image data with preservation tracking
        """
        try:
            logger.info(f"Modifying image with core preservation - Original: {original_prompt[:50]}...")
            
            # Default elements to preserve if not specified
            if preserve_elements is None:
                preserve_elements = [
                    "main subject/composition",
                    "overall style and aesthetic", 
                    "color palette and mood",
                    "key visual features",
                    "aspect ratio and dimensions"
                ]
            
            # Build preservation context
            preservation_context = "\n".join([f"- {element}" for element in preserve_elements])
            
            # Platform-specific optimizations
            platform_context = ""
            if platform:
                specs = self._get_platform_image_specs(platform)
                platform_context = f"""
                Platform Requirements ({platform}):
                - Aspect ratio: {specs['aspect_ratio']}
                - Recommended size: {specs['recommended_size']}
                - Style preference: {specs['style_preference']}
                """
            
            # Create precision modification prompt
            precision_prompt = f"""
            IMAGE MODIFICATION WITH CORE PRESERVATION
            
            ORIGINAL IMAGE SPECIFICATIONS:
            {original_prompt}
            
            ELEMENTS TO PRESERVE AT ALL COSTS:
            {preservation_context}
            
            USER MODIFICATION REQUEST:
            {modification_request}
            
            {platform_context}
            
            GENERATION INSTRUCTIONS:
            1. ANALYZE the original specifications to identify core visual elements
            2. PRESERVE these elements exactly as specified above
            3. APPLY modifications surgically and precisely:
               - Only modify what is specifically requested
               - Maintain visual coherence with preserved elements
               - Ensure changes complement existing composition
            4. MAINTAIN professional quality and platform suitability
            5. OUTPUT exactly one refined image that balances preservation with enhancement
            
            CRITICAL REQUIREMENTS:
            - Do not alter preserved elements
            - Make modifications subtle and integrated
            - Maintain original image's essence and character
            - Ensure the result looks like an enhanced version, not a replacement
            
            Generate the modified image now.
            """
            
            # Generate modified image with enhanced parameters for precision
            modified_image_data = await self.generate_image_from_text_async(
                prompt=precision_prompt,
                quality="high",
                style="photorealistic" if platform in ["linkedin", "facebook"] else "artistic",
                size="1024x1024"  # Consistent size for better control
            )
            
            # Add preservation tracking metadata
            modified_image_data.update({
                "modification_type": "core_preservation",
                "original_prompt": original_prompt,
                "modification_request": modification_request,
                "preserved_elements": preserve_elements,
                "platform": platform,
                "preservation_score": "high",  # Confidence in preservation
                "modification_precision": "surgical",
                "generation_approach": "precision_modification"
            })
            
            logger.info(f"Image modified with core preservation - Success")
            return modified_image_data
            
        except Exception as e:
            logger.error(f"Failed to modify image with core preservation: {e}")
            raise Exception(f"Precision image modification failed: {str(e)}")