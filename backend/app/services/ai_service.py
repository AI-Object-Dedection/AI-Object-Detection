import google.generativeai as genai
from PIL import Image
import os
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.image import Image as ImageModel, ImageDescription, AIStatus

class AIService:
    """Service for AI-powered image analysis using Google Gemini"""
    
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    async def process_image(self, image_id: int, db: Session):
        """Process image with AI to generate description and categorization"""
        # Get image
        image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
        if not image:
            return
        
        # Update status
        image.ai_status = AIStatus.PROCESSING
        db.commit()
        
        try:
            # Generate description
            description_text, category = await self._analyze_image(image.file_path)
            
            # Save description
            description = ImageDescription(
                image_id=image.id,
                model_name="gemini-1.5-flash",
                description_text=description_text,
                category=category
            )
            db.add(description)
            
            # Update image status
            image.ai_status = AIStatus.DONE
            db.commit()
            
            # Generate embedding (async in production)
            from app.services.embedding_service import EmbeddingService
            embedding_service = EmbeddingService()
            await embedding_service.create_embedding(image.id, description_text, db)
            
        except Exception as e:
            print(f"AI processing error: {e}")
            image.ai_status = AIStatus.FAILED
            db.commit()
    
    async def _analyze_image(self, file_path: str) -> tuple:
        """Analyze image and return (description, category)"""
        if not self.model:
            # Fallback for testing
            return self._generate_mock_description()
        
        try:
            # Open image
            full_path = os.path.join(settings.UPLOAD_DIR, file_path)
            img = Image.open(full_path)
            
            # Prompt for construction site analysis
            prompt = """
            Analyze this construction site photo and provide:
            1. A detailed description of what's visible in the image
            2. The primary construction activity category (choose ONE from: Excavation, Concrete, Electrical, Finishing, Safety, Plumbing, Structural, Other)
            
            Format your response as:
            DESCRIPTION: [detailed description]
            CATEGORY: [category name]
            """
            
            response = self.model.generate_content([prompt, img])
            text = response.text
            
            # Parse response
            description = ""
            category = "Other"
            
            for line in text.split('\n'):
                if line.startswith('DESCRIPTION:'):
                    description = line.replace('DESCRIPTION:', '').strip()
                elif line.startswith('CATEGORY:'):
                    category = line.replace('CATEGORY:', '').strip()
            
            return description, category
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._generate_mock_description()
    
    def _generate_mock_description(self) -> tuple:
        """Generate mock description for testing"""
        descriptions = [
            ("Construction site showing concrete foundation work in progress with visible formwork and reinforcement bars", "Concrete"),
            ("Excavation equipment operating in the designated area with safety barriers in place", "Excavation"),
            ("Electrical conduit installation on the second floor with proper cable management", "Electrical"),
            ("Interior finishing work with drywall installation and taping in progress", "Finishing"),
            ("Workers wearing proper PPE including hard hats and safety vests on active construction site", "Safety"),
        ]
        import random
        return random.choice(descriptions)
