from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class Platform(str, Enum):
    """Supported social media platforms"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    X = "x"
    TWITTER = "twitter"
    REDDIT = "reddit"
    PINTEREST = "pinterest"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"

class Tone(str, Enum):
    """Content tone options"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FUNNY = "funny"
    INSPIRING = "inspiring"
    INFORMATIVE = "informative"
    ENGAGING = "engaging"
    FRIENDLY = "friendly"
    FORMAL = "formal"

class CaptionLength(str, Enum):
    """Caption length options"""
    VERY_SHORT = "very_short"
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

class ContentRequest(BaseModel):
    """Request model for content generation"""
    topic: str = Field(..., min_length=1, max_length=1000, description="Main topic or subject")
    platforms: List[Platform] = Field(..., min_items=1, description="Target social media platforms")
    tone: Tone = Field(default=Tone.ENGAGING, description="Content tone")
    caption_length: CaptionLength = Field(default=CaptionLength.MEDIUM, description="Caption length")
    hashtag_count: int = Field(default=10, ge=1, le=30, description="Number of hashtags")
    include_image: bool = Field(default=True, description="Generate image")
    image_context: Optional[str] = Field(None, description="Optional context for image generation")
    generate_variants: bool = Field(False, description="Whether to generate multiple content variants")
    
    @validator('platforms')
    def validate_platforms(cls, v):
        if not v:
            raise ValueError('At least one platform must be selected')
        return v
    
    @validator('hashtag_count')
    def validate_hashtag_count(cls, v):
        if v < 1 or v > 30:
            raise ValueError('Hashtag count must be between 1 and 30')
        return v

class ContentResponse(BaseModel):
    """Response model for generated content"""
    success: bool = Field(..., description="Success status")
    workflow_id: str = Field(..., description="Workflow ID")
    platform_content: Dict[str, List[Dict[str, Any]]] = Field(..., description="Generated content by platform")
    image_ideas: List[Dict[str, Any]] = Field(default=[], description="Generated image ideas")
    generated_images: List[str] = Field(default=[], description="Generated image URLs/paths")
    performance_analysis: Dict[str, List[Dict[str, Any]]] = Field(default={}, description="Content performance analysis")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PostRequest(BaseModel):
    """Request model for posting content"""
    content_id: str = Field(..., description="Content ID to post")
    platforms: List[Platform] = Field(..., min_items=1, description="Platforms to post to")
    scheduled_time: Optional[datetime] = Field(None, description="Optional scheduling time")
    
    @validator('scheduled_time')
    def validate_scheduled_time(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Scheduled time must be in the future')
        return v

class PostResult(BaseModel):
    """Result of posting to a platform"""
    platform: Platform = Field(..., description="Target platform")
    success: bool = Field(..., description="Posting success status")
    post_id: Optional[str] = Field(None, description="Platform post ID")
    post_url: Optional[str] = Field(None, description="Platform post URL")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Platform response data")

class PostResponse(BaseModel):
    """Response model for posting results"""
    content_id: str = Field(..., description="Content ID")
    results: List[PostResult] = Field(..., description="Posting results by platform")
    total_success: int = Field(..., description="Number of successful posts")
    total_failed: int = Field(..., description="Number of failed posts")
    posting_time: float = Field(..., description="Total posting time in seconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GetLateAccount(BaseModel):
    """GetLate account information"""
    id: str = Field(..., description="Account ID")
    platform: Platform = Field(..., description="Platform type")
    name: Optional[str] = Field(None, description="Account name")
    username: Optional[str] = Field(None, description="Username/handle")
    connected: bool = Field(..., description="Connection status")
    last_used: Optional[datetime] = Field(None, description="Last used timestamp")

class GetLatePostData(BaseModel):
    """GetLate API post data"""
    content: str = Field(..., description="Post content")
    platforms: List[Dict[str, Any]] = Field(..., description="Platform configurations")
    media_items: Optional[List[Dict[str, Any]]] = Field(None, description="Media items")
    schedule_at: Optional[datetime] = Field(None, description="Schedule timestamp")

class VoiceInputRequest(BaseModel):
    """Request model for voice input processing"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    language: str = Field(default="en-US", description="Language code")

class VoiceInputResponse(BaseModel):
    """Response model for voice input processing"""
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., description="Transcription confidence")
    language: str = Field(..., description="Detected language")

class ContentModificationRequest(BaseModel):
    """Request model for content modification"""
    content_id: str = Field(..., description="Content ID to modify")
    new_text_prompt: Optional[str] = Field(None, description="New text prompt")
    new_hashtag_prompt: Optional[str] = Field(None, description="New hashtag prompt")
    new_image_prompt: Optional[str] = Field(None, description="New image prompt")
    regenerate_image: bool = Field(default=False, description="Force image regeneration")
    regenerate_text: bool = Field(default=False, description="Force text regeneration")

class SystemStats(BaseModel):
    """System statistics"""
    total_posts_generated: int = Field(..., description="Total posts generated")
    total_posts_posted: int = Field(..., description="Total posts posted")
    success_rate: float = Field(..., description="Overall success rate")
    average_generation_time: float = Field(..., description="Average generation time")
    average_posting_time: float = Field(..., description="Average posting time")
    active_platforms: List[Platform] = Field(..., description="Active platforms")
    last_activity: datetime = Field(..., description="Last activity timestamp")

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Error details")
    request_id: Optional[str] = Field(None, description="Request ID for debugging")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")