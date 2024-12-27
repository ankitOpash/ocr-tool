import os
import cv2
from pdf2image import convert_from_path
from fastapi import FastAPI, UploadFile
from typing import List, Dict, Union
import easyocr
import fitz  # PyMuPDF

# Initialize FastAPI app
app = FastAPI()

# Initialize EasyOCR Reader
reader = easyocr.Reader(["en", "ar"])  # Add 'ar' for Arabic support

# Functions

def preprocess_image(image_path: str) -> str:
    """Preprocess the image for better OCR results."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    temp_path = f"{os.path.splitext(image_path)[0]}_processed.png"
    cv2.imwrite(temp_path, image)
    return temp_path

def extract_text_from_image(image_path: str, lang: str = "en") -> str:
    """Extract text from an image using EasyOCR."""
    processed_path = preprocess_image(image_path)
    results = reader.readtext(processed_path, detail=0, paragraph=True)
    os.remove(processed_path)  # Clean up processed image
    return "\n".join(results)

def pdf_to_images(pdf_file: str, output_folder: str = "./temp") -> List[str]:
    """Convert a PDF into a list of image file paths."""
    images = convert_from_path(pdf_file, fmt="png", output_folder=output_folder)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i + 1}.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)
    return image_paths

def pdf_to_images_with_pymupdf(pdf_file: str, output_folder: str = "./temp") -> List[str]:
    """Convert a PDF into a list of image file paths using PyMuPDF."""
    os.makedirs(output_folder, exist_ok=True)
    pdf_document = fitz.open(pdf_file)
    image_paths = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        image_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        pix.save(image_path)
        image_paths.append(image_path)
    pdf_document.close()
    return image_paths

def pdf_to_text(pdf_file: str) -> str:
    """Extract text from a PDF by converting pages to images and running OCR."""
    temp_folder = "./temp/pdf_pages"
    os.makedirs(temp_folder, exist_ok=True)
    images = pdf_to_images(pdf_file, temp_folder)
    text = ""
    for image_path in images:
        text += extract_text_from_image(image_path)
        if os.path.exists(image_path):  # Clean up each processed image
            os.remove(image_path)
    os.rmdir(temp_folder)  # Remove temp folder
    return text

def extract_key_value_pairs(text: str) -> Dict[str, str]:
    """Extract key-value pairs from the text."""
    lines = text.splitlines()
    key_value_pairs = {}
    for line in lines:
        if "=" in line:
            parts = line.split("=", 1)
            key = parts[0].strip()
            value = parts[1].strip()
            key_value_pairs[key] = value
    return key_value_pairs

@app.post("/extract")
async def extract_text(files: List[UploadFile]) -> Dict[str, Union[str, Dict[str, str]]]:
    """Endpoint to upload and extract text as key-value pairs from images or PDFs."""
    # Ensure temp directory exists
    os.makedirs("./temp", exist_ok=True)

    extracted_data = {}
    extracted_text = {}  # Initialize a dictionary to store the extracted text
    for file in files:
        file_path = f"./temp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Determine if the file is an image or a PDF
        if file.filename.endswith(".pdf"):
            text = pdf_to_images_with_pymupdf(file_path)
            key_value_pairs = extract_key_value_pairs(text)
            extracted_text[file.filename] = text  # Store the extracted text
            extracted_data.update(key_value_pairs)
        else:
            image_path = file_path
            text = extract_text_from_image(image_path)
            key_value_pairs = extract_key_value_pairs(text)
            extracted_text[file.filename] = text  # Store the extracted text
            extracted_data.update(key_value_pairs)

        if os.path.exists(file_path):  # Check if the file exists before deleting
            os.remove(file_path)  # Clean up uploaded file

    return {"status": "success", "data": extracted_data, "text": extracted_text}

# To run: `uvicorn script_name:app --reload`
