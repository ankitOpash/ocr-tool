import os
import cv2
import pytesseract
from pytesseract import Output
from pdf2image import convert_from_path
from fastapi import FastAPI, UploadFile, Form
from pydantic import BaseModel
from typing import List, Dict, Union
from langdetect import detect

# Initialize FastAPI app
app = FastAPI()

# Configuration for Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract"

# Models
class ExtractedData(BaseModel):
    document_type: str
    data: Dict[str, Union[str, List[str]]]

# Functions

def preprocess_image(image_path: str) -> str:
    """Preprocess the image for better OCR results."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    temp_path = f"{os.path.splitext(image_path)[0]}_processed.png"
    cv2.imwrite(temp_path, image)
    return temp_path

def extract_text_from_image(image_path: str, lang: str = "eng") -> str:
    """Extract text from an image using Tesseract."""
    processed_path = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_path, lang=lang)
    os.remove(processed_path)  # Clean up processed image
    return text

def pdf_to_images(pdf_file: str) -> List[str]:
    """Convert PDF pages to images."""
    images = convert_from_path(pdf_file)
    image_paths = []
    for i, image in enumerate(images):
        temp_path = f"{os.path.splitext(pdf_file)[0]}_page_{i}.png"
        image.save(temp_path, "PNG")
        image_paths.append(temp_path)
    return image_paths

def detect_language(text: str) -> str:
    """Detect the language of the text."""
    return detect(text)

@app.post("/upload")
async def upload_document(file: UploadFile):
    """Endpoint to upload and process a document."""
    file_path = f"./temp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Determine if the file is an image or a PDF
    if file.filename.endswith(".pdf"):
        image_paths = pdf_to_images(file_path)
    else:
        image_paths = [file_path]

    # Perform OCR
    extracted_texts = []
    for image_path in image_paths:
        lang = detect_language(extract_text_from_image(image_path))
        extracted_texts.append(extract_text_from_image(image_path, lang=lang))
        os.remove(image_path)  # Clean up temp images

    os.remove(file_path)  # Clean up uploaded file

    return {"texts": extracted_texts}

@app.post("/extract")
async def extract_data(file: UploadFile, document_type: str = Form(...)) -> ExtractedData:
    """Extract specific data from a document based on its type."""
    file_path = f"./temp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    if file.filename.endswith(".pdf"):
        image_paths = pdf_to_images(file_path)
    else:
        image_paths = [file_path]

    extracted_data = {}
    for image_path in image_paths:
        lang = detect_language(extract_text_from_image(image_path))
        text = extract_text_from_image(image_path, lang=lang)

        # Map text to fields based on document_type
        if document_type == "id_card":
            extracted_data = parse_id_card(text)
        elif document_type == "report":
            extracted_data = parse_report(text)

        os.remove(image_path)

    os.remove(file_path)

    return ExtractedData(document_type=document_type, data=extracted_data)

def parse_id_card(text: str) -> Dict[str, str]:
    """Extract specific fields from ID card text."""
    # Example extraction logic
    lines = text.splitlines()
    fields = {}
    for line in lines:
        if "Name:" in line:
            fields["Name"] = line.split(":")[1].strip()
        if "DOB:" in line:
            fields["Date of Birth"] = line.split(":")[1].strip()
    return fields

def parse_report(text: str) -> Dict[str, str]:
    """Extract specific fields from report text."""
    # Example extraction logic
    fields = {}
    if "Report ID" in text:
        fields["Report ID"] = text.split("Report ID:")[1].split()[0]
    return fields

# To run: `uvicorn ocr_crm_integration:app --reload`
# Ensure the "temp" directory exists before running the server.
