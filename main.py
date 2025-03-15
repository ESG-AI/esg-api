from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
import uvicorn
from dotenv import load_dotenv
from pydantic import BaseModel
import google.generativeai as genai
from typing import List
from pypdf import PdfReader

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

class AnalyzeRequest(BaseModel):
    text: str

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Hello, ESG Scoring API is running!"}
# add a comment
@app.post("/upload/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    uploaded_files = []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        uploaded_files.append(file.filename)

    return {"uploaded_files": uploaded_files, "message": "Files uploaded successfully!"}

@app.post("/analyze/")
async def analyze_text(request: AnalyzeRequest):
    """Send text to Gemini AI for ESG analysis."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(request.text)
        return {"analysis": response.text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)