import os
import logging
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class ImageEnhancer:
    """Simple image enhancer using Gemini."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-3-pro-image-preview"
    
    def enhance_image(self, image_path: str, filename: str, change_intensity: str = "moderate", detail_level: str = "moderate") -> Tuple[str, Dict]:
        """Enhance image using Gemini.
        
        Args:
            image_path: Path to the image file
            filename: Original filename
            change_intensity: "minimal" or "extensive" - how much to change the photo
            detail_level: "minimal" or "extensive" - how many details to add
        """
        # Load image
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to bytes
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=95)
        buffer.seek(0)
        image_bytes = buffer.read()
        
        # Build prompt based on user preferences
        prompt = self._build_enhancement_prompt(change_intensity, detail_level)
        
        # Send to Gemini
        logger.info(f"Sending image to Gemini: {filename}")
        logger.info(f"Enhancement settings: change_intensity={change_intensity}, detail_level={detail_level}")
        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    prompt,
                    image_part
                ]
            )
            
            # Get response - check for image data first
            response_text = ""
            enhanced_image = None
            reason = ""
            
            if hasattr(response, 'parts'):
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Gemini returned an enhanced image
                        logger.info("Gemini returned enhanced image data")
                        try:
                            image_data = part.inline_data.data
                            enhanced_image = Image.open(BytesIO(image_data))
                            if enhanced_image.mode != 'RGB':
                                enhanced_image = enhanced_image.convert('RGB')
                            reason = "Gemini returned enhanced image"
                        except Exception as e:
                            reason = f"Gemini returned image data but failed to process: {str(e)}"
                    elif hasattr(part, 'text') and part.text:
                        response_text += part.text
            elif hasattr(response, 'text'):
                response_text = response.text
            
            # Determine reason if no image returned
            if not enhanced_image:
                if response_text:
                    reason = f"Gemini returned text response instead of image: {response_text[:100]}"
                else:
                    reason = "Gemini returned empty response - model may not support image generation/enhancement"
            
            logger.info(f"Gemini response: {response_text if response_text else '(no text response)'}")
            logger.info(f"Reason: {reason}")
        except Exception as e:
            logger.error(f"Error calling Gemini: {e}", exc_info=True)
            response_text = f"Error: {str(e)}"
            enhanced_image = None
            reason = f"Error calling Gemini API: {str(e)}"
        
        # Use Gemini's enhanced image if available, otherwise return original with reason
        if enhanced_image:
            final_image = enhanced_image
            logger.info("Using Gemini's enhanced image")
        else:
            final_image = image
            logger.warning(f"No enhanced image from Gemini. Reason: {reason}")
        
        # Save image
        enhanced_filename = f"enhanced_{filename.rsplit('.', 1)[0]}.jpg"
        enhanced_path = os.path.join('enhanced', enhanced_filename)
        final_image.save(enhanced_path, 'JPEG', quality=95)
        
        return enhanced_path, {
            "response": response_text,
            "enhanced_by_gemini": enhanced_image is not None,
            "reason": reason if not enhanced_image else "Successfully enhanced by Gemini",
            "change_intensity": change_intensity,
            "detail_level": detail_level
        }
    
    def _build_enhancement_prompt(self, change_intensity: str, detail_level: str) -> str:
        """Build enhancement prompt based on user preferences."""
        base_prompt = "Make this photo better for Airbnb and Booking.com listings."
        
        # Change intensity instructions
        if change_intensity == "minimal":
            intensity_instruction = "Make MINIMAL changes - only subtle improvements. Keep the photo very close to the original. Preserve the original look and feel as much as possible."
        elif change_intensity == "extensive":
            intensity_instruction = "Make EXTENSIVE improvements - significantly enhance the photo. Apply substantial enhancements to lighting, colors, and overall quality."
        else:  # moderate (default)
            intensity_instruction = "Make MODERATE improvements - enhance the photo noticeably but keep it natural and authentic."
        
        # Detail level instructions
        if detail_level == "minimal":
            detail_instruction = "Do NOT add many details. Keep it simple and natural. Avoid adding objects, decorations, or elements that weren't in the original photo."
        elif detail_level == "extensive":
            detail_instruction = "You can ADD MORE DETAILS to enhance the photo - add subtle decorative elements, improve textures, enhance small details that make the space more appealing."
        else:  # moderate (default)
            detail_instruction = "Add MODERATE details - enhance existing elements naturally without adding many new objects. You can add also such details that mainly used during photoshoot."
        
        prompt = f"{base_prompt} {intensity_instruction} {detail_instruction} The result should look professional and appealing for rental listings while maintaining authenticity."
        
        return prompt
