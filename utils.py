import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
import os
import shutil
from fastapi import UploadFile
# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 

# C:\Program Files\Tesseract-OCR# Update as needed

def extract_text_from_image(image_path: str) -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

def extract_text_from_pdf(pdf_path: str) -> str:
    pages = convert_from_path(pdf_path)
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text

# def extract_key_value_pairs(text: str) -> dict:
#     data = {}
#     name_match = re.search(r'Name:\s*(.+)', text, re.IGNORECASE)
#     id_match = re.search(r'ID:\s*(\d+)', text, re.IGNORECASE)
#     if name_match:
#         data['name'] = name_match.group(1).strip()
#     if id_match:
#         data['id'] = id_match.group(1).strip()
#     return data
def extract_key_value_pairs(text: str) -> dict:
    """
    Extracts specific key-value pairs from the text based on predefined patterns.
    Fields: Name, Date of Birth, Nationality, Issuing Date, Expiry Date, ID Number, License No.
    """
    data = {}

    # Define regex patterns for each field
    patterns = {
        "Name": r"Name:\s*(.+)",
        "Date of Birth": r"(Date of Birth|DOB):\s*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})",
        "Nationality": r"Nationality:\s*(.+)",
        "Issuing Date": r"(Issuing Date|Issue Date):\s*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})",
        "Expiry Date": r"(Expiry Date|Exp Date):\s*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})",
        "ID Number": r"(ID Number|ID No):\s*(\w+)",
        "License No": r"(License No|License Number):\s*(\w+)",
        "Phone": r"(?i)\bphone:\s*(\+?\d{1,4}?[-. ]?(\(?\d{1,3}?\)?[-. ]?\d{1,4}[-. ]?\d{1,9}))",
        "Email": r"(?i)\nEmall:\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
    }

    # Search text using patterns
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = match.group(1).strip() if key != "Date of Birth" else match.group(2).strip()

    return data