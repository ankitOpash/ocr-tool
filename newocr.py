from fastapi import FastAPI, File, UploadFile, HTTPException
from utils import extract_text_from_image, extract_text_from_pdf, extract_key_value_pairs
import os
import shutil
from typing import List, Dict, Union

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    responses = []
    for file in files:
        # Save uploaded file to disk
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Determine file type and process
        try:
            if file.filename.endswith(".pdf"):
                text = extract_text_from_pdf(file_path)
            else:
                text = extract_text_from_image(file_path)
            
            # Extract structured data
            structured_data = extract_key_value_pairs(text)
            
            # Cleanup uploaded file
            os.remove(file_path)

            responses.append({
                "success": True,
                "text": text,
                "structured_data": structured_data
            })
        except Exception as e:
            # Cleanup on error
            if os.path.exists(file_path):
                os.remove(file_path)
            responses.append({
                "success": False,
                "error": str(e)
            })

    return responses

@app.get("/")
async def root():
    return {"message": "Welcome to the OCR API"}
