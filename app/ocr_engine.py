"""Main OCR engine module."""
import pytesseract
import cv2
import numpy as np
from langdetect import detect
import arabic_reshaper
from bidi.algorithm import get_display

class OCREngine:
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        
    def extract_text(self, image, lang='en'):
        """Extract text from image with language support."""
        preprocessed = self.preprocessor.preprocess(image)
        
        # Configure Tesseract for the specific language
        config = f'--psm 6 -l {lang}'
        text = pytesseract.image_to_string(preprocessed, config=config)
        
        # Handle Arabic text if needed
        if lang == 'ara':
            text = self._process_arabic_text(text)
            
        return text
    
    def extract_structured_data(self, image, doc_type, template):
        """Extract structured data based on document type and template."""
        data = {}
        for field, coords in template.items():
            roi = self._extract_roi(image, coords)
            text = self.extract_text(roi)
            data[field] = self._validate_field(field, text)
        return data
    
    def _process_arabic_text(self, text):
        """Process Arabic text for correct display and handling."""
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    
    def _extract_roi(self, image, coords):
        """Extract region of interest from image."""
        h, w = image.shape[:2]
        x1, y1, x2, y2 = [int(c * w) if i % 2 == 0 else int(c * h) 
                         for i, c in enumerate(coords)]
        return image[y1:y2, x1:x2]
    
    def _validate_field(self, field_name, text):
        """Validate extracted field data."""
        # Implement field-specific validation rules
        return text.strip()