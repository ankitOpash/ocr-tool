# OCR System for ID Cards and Reports

This system provides a comprehensive OCR solution for processing ID cards and reports, with support for multiple languages and document types.

## Features

- Document classification and type detection
- ID card front/back detection and processing
- Structured data extraction from reports
- Multilingual support (Arabic and English)
- Data validation and cleaning
- Continuous learning capabilities

## Requirements

- Python 3.8+
- OpenCV
- Tesseract OCR
- TensorFlow
- Additional dependencies in requirements.txt

## Installation

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Tesseract OCR:
   - For Ubuntu/Debian:
     ```bash
     sudo apt-get install tesseract-ocr
     sudo apt-get install tesseract-ocr-ara  # For Arabic support
     ```
   - For macOS:
     ```bash
     brew install tesseract
     brew install tesseract-lang  # For additional languages
     ```

## Usage

```python
from src.main import OCRPipeline

# Initialize the pipeline
pipeline = OCRPipeline()

# Process a document
result = pipeline.process_document('path/to/document.jpg')
print(result)
```

## Project Structure

- `src/`
  - `main.py` - Main application entry point
  - `document_classifier.py` - Document classification module
  - `ocr_engine.py` - Core OCR functionality
  - `image_preprocessor.py` - Image preprocessing utilities
  - `data_validator.py` - Data validation and cleaning
  - `config.py` - Configuration settings
  - `training/` - Model training utilities

## Training

To train the document classifier:

```python
from src.training.model_trainer import ModelTrainer

trainer = ModelTrainer('path/to/training/data')
trainer.train()
trainer.save_model('path/to/save/model')
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request


python -m venv venv
source venv/bin/activate
uvicorn main:app --reload