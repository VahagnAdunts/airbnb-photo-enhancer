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
    
    def convert_to_night(self, image_path: str, filename: str) -> Tuple[str, Dict]:
        """Convert a day photo to a night photo using Gemini.
        
        Args:
            image_path: Path to the image file
            filename: Original filename
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
        
        # Build night conversion prompt
        prompt = self._build_night_conversion_prompt()
        
        # Send to Gemini
        logger.info(f"Converting image to night: {filename}")
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
            converted_image = None
            reason = ""
            
            if hasattr(response, 'parts'):
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Gemini returned a converted image
                        logger.info("Gemini returned night-converted image data")
                        try:
                            image_data = part.inline_data.data
                            converted_image = Image.open(BytesIO(image_data))
                            if converted_image.mode != 'RGB':
                                converted_image = converted_image.convert('RGB')
                            reason = "Gemini returned night-converted image"
                        except Exception as e:
                            reason = f"Gemini returned image data but failed to process: {str(e)}"
                    elif hasattr(part, 'text') and part.text:
                        response_text += part.text
            elif hasattr(response, 'text'):
                response_text = response.text
            
            # Determine reason if no image returned
            if not converted_image:
                if response_text:
                    reason = f"Gemini returned text response instead of image: {response_text[:100]}"
                else:
                    reason = "Gemini returned empty response - model may not support image generation/enhancement"
            
            logger.info(f"Gemini response: {response_text if response_text else '(no text response)'}")
            logger.info(f"Reason: {reason}")
        except Exception as e:
            logger.error(f"Error calling Gemini: {e}", exc_info=True)
            response_text = f"Error: {str(e)}"
            converted_image = None
            reason = f"Error calling Gemini API: {str(e)}"
        
        # Use Gemini's converted image if available, otherwise return original with reason
        if converted_image:
            final_image = converted_image
            logger.info("Using Gemini's night-converted image")
        else:
            final_image = image
            logger.warning(f"No night-converted image from Gemini. Reason: {reason}")
        
        # Save image
        night_filename = f"night_{filename.rsplit('.', 1)[0]}.jpg"
        night_path = os.path.join('enhanced', night_filename)
        final_image.save(night_path, 'JPEG', quality=95)
        
        return night_path, {
            "response": response_text,
            "converted_by_gemini": converted_image is not None,
            "reason": reason if not converted_image else "Successfully converted to night by Gemini",
            "conversion_type": "night_conversion"
        }
    
    def _build_night_conversion_prompt(self) -> str:
        """Build night conversion prompt for converting day photos to night photos."""
        prompt = """Convert this day photo into a realistic night photo. The transformation should be natural and professional.

CRITICAL REQUIREMENTS:
1. OUTSIDE/EXTERIOR: Make all visible outside areas completely dark (night time). This includes:
   - Windows should show dark night sky (no daylight visible)
   - Balconies, terraces, and outdoor spaces should be dark
   - Any visible landscape, buildings, or sky outside should appear as nighttime
   - Add subtle ambient city lights or stars in the night sky if visible through windows

2. INDOOR LIGHTING: Turn on all lights in the room:
   - If there are ceiling lights, chandeliers, or overhead fixtures, make them ON and glowing
   - Table lamps, floor lamps, and desk lamps should be ON with warm, inviting light
   - Under-cabinet lighting in kitchens should be ON
   - Any decorative lighting should be illuminated
   - Light fixtures should emit warm, cozy light that creates a welcoming atmosphere
   - Add realistic light glow and shadows from the turned-on lights

3. ATMOSPHERE & MOOD:
   - Create a cozy, warm, and inviting nighttime atmosphere
   - The interior should feel lived-in and comfortable
   - Maintain natural color balance - warm tones from artificial lighting
   - Add subtle warmth to the overall color temperature (warmer than daylight)

4. DETAILS:
   - Preserve all furniture, decor, and room elements exactly as they are
   - Do not add or remove objects
   - Maintain the same composition and perspective
   - Keep the photo looking realistic and authentic
   - The result should look like a professional nighttime real estate or Airbnb photo

5. QUALITY:
   - The final image should be high quality and professional
   - Suitable for Airbnb, Booking.com, and real estate listings
   - Should look like it was taken during a professional nighttime photoshoot

Transform this day photo into a beautiful, realistic night photo that showcases the space in its best nighttime lighting."""
        
        return prompt
    
    def _build_enhancement_prompt(self, change_intensity: str, detail_level: str) -> str:
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
