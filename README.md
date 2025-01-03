# OCR System for ID Cards and Reports




python -m venv venv
pip install -r requirements.txt
venv\Scripts\activate
uvicorn main:app --reload

uvicorn ocr_crm_integration:app --reload