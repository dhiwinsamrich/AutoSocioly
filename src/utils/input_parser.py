import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Fetch the API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_ID = "gemini-2.5-flash"

# Check if the Gemini API Key is provided
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the Gemini client
client = genai.GenerativeModel(model_name=MODEL_ID)


def parse_user_input(user_input):
    """
    Parse user input to extract topic, platforms, tone, caption length, and hashtag count using Gemini.
    
    Args:
        user_input (str): The raw user input from the index page
        
    Returns:
        dict: Parsed components including topic, platforms, tone, caption_length, hashtag_count
    """
    system_prompt = """
    You are an AI assistant that analyzes user input for social media post generation and extracts key components.
    
    From the user's input, identify and extract:
    1. MAIN TOPIC: The core subject matter they want to post about (enhance and elaborate this for better content generation)
    2. PLATFORMS: Any mentioned social media platforms (instagram, linkedin, x, twitter, facebook)
    3. TONE: The desired tone (professional, casual, humorous, inspirational, promotional, informative, engaging)
    4. CAPTION_LENGTH: Desired caption length (short, medium, long, very_short)
    5. HASHTAG_COUNT: Number of hashtags requested (extract number if mentioned)
    
    IMPORTANT INSTRUCTIONS:
    - For MAIN TOPIC: Don't just extract it - ENHANCE and ELABORATE it into a more detailed, engaging prompt that would work well for both text and image generation
    - If platforms are mentioned, extract them as a list
    - If no platforms mentioned, return empty list []
    - If no tone mentioned, default to "engaging"
    - If no caption length mentioned, default to "medium"
    - If no hashtag count mentioned, default to 10
    - For hashtag count, look for phrases like "5 hashtags", "ten hashtags", "few hashtags" (interpret "few" as 5)
    
    Return ONLY a valid JSON object with these exact keys:
    {
        "enhanced_topic": "detailed and enhanced version of the topic",
        "original_topic": "original topic as mentioned by user",
        "platforms": ["platform1", "platform2"],
        "tone": "tone_value",
        "caption_length": "length_value",
        "hashtag_count": number
    }
    
    Examples:
    - Input: "Create a post about AI for LinkedIn in professional tone"
    - Output: {"enhanced_topic": "Artificial Intelligence revolution in modern business: exploring how AI technologies are transforming industries, improving efficiency, and creating new opportunities for professionals and organizations", "original_topic": "AI", "platforms": ["linkedin"], "tone": "professional", "caption_length": "medium", "hashtag_count": 10}
    
    - Input: "Funny cat videos for Instagram and Facebook with 8 hashtags"
    - Output: {"enhanced_topic": "Hilarious cat behaviors and adorable feline antics that make our days brighter: exploring the amusing world of cats, their quirky personalities, playful moments, and the joy they bring to our lives", "original_topic": "cats", "platforms": ["instagram", "facebook"], "tone": "humorous", "caption_length": "medium", "hashtag_count": 8}
    """
    
    prompt = f"{system_prompt}\n\nUser Input: {user_input}\n\nJSON Response:"
    
    logger.info(f"Parsing user input with Gemini: {user_input}")
    
    try:
        response = client.generate_content(prompt)
        
        if response.candidates and response.candidates[0].content.parts:
            parsed_json_str = response.candidates[0].content.parts[0].text.strip()
            logger.debug(f"Raw JSON string from Gemini: {parsed_json_str}")
            
            # Clean up the JSON string if it contains markdown or extra text
            if parsed_json_str.startswith("```json"):
                parsed_json_str = parsed_json_str[7:]
            if parsed_json_str.endswith("```"):
                parsed_json_str = parsed_json_str[:-3]
            parsed_json_str = parsed_json_str.strip()
            
            try:
                parsed_data = json.loads(parsed_json_str)
                logger.info(f"Successfully parsed user input: {parsed_data}")
                
                # Validate and set defaults
                result = {
                    "enhanced_topic": parsed_data.get("enhanced_topic", user_input),
                    "original_topic": parsed_data.get("original_topic", user_input),
                    "platforms": parsed_data.get("platforms", []),
                    "tone": parsed_data.get("tone", "engaging"),
                    "caption_length": parsed_data.get("caption_length", "medium"),
                    "hashtag_count": parsed_data.get("hashtag_count", 10)
                }
                
                # Ensure platforms are lowercase
                result["platforms"] = [platform.lower() for platform in result["platforms"]]
                
                # Convert 'twitter' to 'x'
                if 'twitter' in result["platforms"]:
                    result["platforms"] = ['x' if p == 'twitter' else p for p in result["platforms"]]
                
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Problematic JSON string: {parsed_json_str}")
                return get_default_parsed_data(user_input)
        else:
            logger.warning("Could not parse user input with Gemini. Using defaults.")
            return get_default_parsed_data(user_input)
            
    except Exception as e:
        logger.error(f"Error parsing user input with Gemini: {e}")
        return get_default_parsed_data(user_input)


def get_default_parsed_data(user_input):
    """
    Return default parsed data when Gemini parsing fails.
    """
    return {
        "enhanced_topic": user_input,
        "original_topic": user_input,
        "platforms": [],
        "tone": "engaging",
        "caption_length": "medium",
        "hashtag_count": 10
    }


def enhance_topic_for_generation(topic, tone="engaging"):
    """
    Further enhance the topic specifically for content generation.
    
    Args:
        topic (str): The topic to enhance
        tone (str): The desired tone
        
    Returns:
        str: Enhanced topic for content generation
    """
    system_prompt = f"""
    You are an AI assistant that enhances topics for social media content generation.
    
    Take the provided topic and create a more detailed, descriptive prompt that will work well for:
    1. Text/caption generation
    2. Image generation
    3. Hashtag generation
    
    The tone should be: {tone}
    
    Make the enhanced topic:
    - More descriptive and specific
    - Include relevant context and angles
    - Suitable for creating engaging social media content
    - Rich enough to inspire both visual and textual content
    
    Return only the enhanced topic, nothing else.
    """
    
    prompt = f"{system_prompt}\n\nOriginal Topic: {topic}\n\nEnhanced Topic:"
    
    try:
        response = client.generate_content(prompt)
        
        if response.candidates and response.candidates[0].content.parts:
            enhanced_topic = response.candidates[0].content.parts[0].text.strip()
            logger.debug(f"Enhanced topic: {enhanced_topic}")
            return enhanced_topic
        else:
            logger.warning(f"Could not enhance topic '{topic}'. Using original topic.")
            return topic
            
    except Exception as e:
        logger.error(f"Error enhancing topic '{topic}': {e}")
        return topic