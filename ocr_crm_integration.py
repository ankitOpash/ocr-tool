from fastapi import FastAPI, UploadFile
from typing import List, Dict, Union
import os
import cv2
# from services.preprocessing import preprocess_image
from pdf2image import convert_from_path
import fitz  # PyMuPDF
import easyocr
import re
from tempfile import TemporaryDirectory
from dotenv import load_dotenv
from openai import OpenAI

# from utils.file_utils import save_uploaded_file

import json
# Initialize FastAPI app
app = FastAPI()

load_dotenv()
client = OpenAI()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("Environment variable OPENAI_API_KEY is not set.")

# Initialize EasyOCR Reader for English and Arabic
reader = easyocr.Reader(["en", "ar"])


#  **Preprocessing Function**
# def preprocess_image(image_path: str) -> str:
#     """Preprocess the image for better OCR results."""
#     image = cv2.imread(image_path)
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#     edged = cv2.Canny(blurred, 30, 150)
#     processed_path = f"{os.path.splitext(image_path)[0]}_processed.png"
#     cv2.imwrite(processed_path, edged)
#     return processed_path
def preprocess_image(image_path: str) -> str:
    """Preprocess the image for better OCR results."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    temp_path = f"{os.path.splitext(image_path)[0]}_processed.png"
    cv2.imwrite(temp_path, image)
    return temp_path

#  **Text Extraction Function**
def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image using EasyOCR."""
    processed_path = preprocess_image(image_path)
    results = reader.readtext(processed_path, detail=0, paragraph=True)
    os.remove(processed_path)
    return "\n".join(results)


# 📄 **PDF to Image Conversion**
def pdf_to_images_with_pymupdf(pdf_file: str, output_folder: str) -> List[str]:
    """Convert a PDF into a list of image file paths using PyMuPDF."""
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

def extract_with_ai(text: str) -> Dict[str, Dict[str, str]]:
    prompt = """
    You are an advanced OCR extraction agent. Your task is to extract all identifiable key-value pairs from the provided text. 

    1. Identify all fields dynamically — do not assume predefined fields.
    2. Return results in a JSON format where:
       - The key is the field name (in English if possible).
       - The value contains both English and Arabic (if both are available).
       - If only one language is present, return that.
    3. Avoid extra text, summaries, or explanations. Only return a clean JSON Format with key-value pairs strict to the requirements.

    Example output:
    {
        "Field Name 1": {
            "English": "Value in English",
            "Arabic": "Value in Arabic (if available)"
        },
        "Field Name 2": {
            "English": "Value in English",
            "Arabic": "Value in Arabic (if available)"
        }
    }

    Text to process:
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

# 🚀 **API Route**
@app.post("/extract")
async def extract_text(files: List[UploadFile]) -> Dict[str, Union[str, Dict]]:
    """Extract text and key-value pairs from uploaded PDFs or images."""
    with TemporaryDirectory() as temp_dir:
        extracted_data = {}
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            
            if file.filename.endswith(".pdf"):
                images = pdf_to_images_with_pymupdf(file_path, temp_dir)
                text = "\n".join(extract_text_from_image(img) for img in images)
            else:
                text = extract_text_from_image(file_path)
                # completion = client.chat.completions.create(
                #     model="gpt-4o",
                #     messages=[
                #         {"role": "system", "content": "Extract only key-value pairs from the given text without explanation."},
                #         {"role": "user", "content": f"{text}"}
                #     ]
                # )
            ai_response = extract_with_ai(text)
            print(text)
            print("AI response:",ai_response)
            json_file_path = f"{os.path.splitext(file.filename)[0]}_ai_response.json"   
            with open(json_file_path, 'w') as json_file:
                json.dump(ai_response, json_file)
                
            print("AI json_file_path:",json_file_path)
            extracted_data[file.filename] = {
                "text": text,
                "gpt_data": ai_response
            }
        
        return {"status": "success", "data": extracted_data}
