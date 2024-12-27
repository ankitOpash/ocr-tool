"""Main application entry point."""
import cv2
from app.document_classifier import DocumentClassifier
from app.ocr_engine import OCREngine
from app.data_validator import DataValidator
from app.config import *
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

class OCRPipeline:
    def __init__(self):
        self.classifier = DocumentClassifier()
        self.OCREngine = OCREngine()
        self.validator = DataValidator()
    
    def process_document(self, image_path):
        """Process a document through the OCR pipeline."""
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not load image")
        
        # Classify document
        doc_type = self.classifier.classify_document(image)
        
        # Extract data based on document type
        if doc_type['type'] == DOCUMENT_TYPES['ID_CARD']:
            return self._process_id_card(image, doc_type['subtype'])
        elif doc_type['type'] == DOCUMENT_TYPES['REPORT']:
            return self._process_report(image, doc_type['subtype'])
        else:
            raise ValueError("Unknown document type")
    
    def _process_id_card(self, image, card_type):
        """Process ID card specific logic."""
        # Detect and separate front/back if needed
        sides = self.classifier.detect_id_card_sides(image)
        
        data = {}
        for side, img in sides.items():
            template = FIELD_COORDINATES['ID_CARD'][card_type][side]
            side_data = self.OCREngine.extract_structured_data(
                img, 'ID_CARD', template)
            data.update(side_data)
        
        return self._validate_data(data)
    
    def _process_report(self, image, report_type):
        """Process report specific logic."""
        template = FIELD_COORDINATES['REPORT'][report_type]
        data = self.OCREngine.extract_structured_data(
            image, 'REPORT', template)
        return self._validate_data(data)
    
    def _validate_data(self, data):
        """Validate extracted data."""
        validated_data = {}
        for field, value in data.items():
            if self.validator.validate_field(field, value):
                validated_data[field] = self.validator.clean_text(value)
        return validated_data

def main():
    pipeline = OCRPipeline()
    
    # Example usage
    try:
        result = pipeline.process_document('/image_2024_12_27T07_10_31_664Z.png')
        print("Extracted Data:", result)
    except Exception as e:
        print(f"Error processing document: {str(e)}")

if __name__ == "__main__":
    main()