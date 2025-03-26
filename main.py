import shutil
from fastapi import FastAPI, File, UploadFile
import os
import uvicorn
from dotenv import load_dotenv
from pydantic import BaseModel
import google.generativeai as genai
from typing import List
from ocr_service import extract_text_from_pdf
from score_text_with_rules import score_text_with_rules
import time
import json
import re

load_dotenv()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# class AnalyzeRequest(BaseModel):
#     text: str

with open("scoring_rules.json", "r", encoding="utf-8") as f:
    scoring_rules = json.load(f)

def get_ai_explanation(text, gri_code, criteria):
    """
    Generate AI explanation with Gemini based on criteria.
    """

    criteria_prompt = "\n".join([f"Score {k}: {v}" for k, v in criteria.items()])
    prompt = f"""You are an ESG reporting analyst.
    The following combined report text comes from multiple documents submitted by one company.
    Assess the level of disclosure for GRI indicator {gri_code}.

    Combined text: "{text[:3500]}..." (trimmed for brevity)

    Scoring criteria:
    {criteria_prompt}
    
    Please assign a score (0 to 4) and explain why that score is given."""

    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        explanation = response.candidates[0].content.parts[0].text
        return explanation
    except Exception as e:
        return f"AI explanation error: {str(e)}"


# Function to split text into chunks
def chunk_text(text: str, max_chunk_size: int = 3500) -> list:
    """
    Splits text into chunks without breaking sentences, around max_chunk_size characters each.
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

    return chunks

@app.post("/process_pdfs/")
async def process_pdfs(files: List[UploadFile] = File(...)):
    start_time = time.time()

    combined_text = ""
    uploaded_filenames = []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_filenames.append(file.filename)
        
        extracted_text = extract_text_from_pdf(file_path)
        combined_text += f"\n\n##### Extracted from: {file.filename} #####\n\n" + extracted_text
    
    scoring_result = score_text_with_rules(combined_text)

    enriched_indicators = []
    for indicator in scoring_result["indicators"]:
        gri_code = indicator["GRI"]
        keywords_found = indicator["found_keywords"]
        score = indicator["score"]
        criteria = scoring_rules[gri_code]["criteria"]

        if score > 0:
            ai_explanation = get_ai_explanation(combined_text, gri_code, criteria)
        else:
            ai_explanation = f"No relevant content found for GRI {gri_code}; score 0 assigned."

        enriched_indicators.append({
            "GRI": gri_code,
            "description": indicator["description"],
            "score": score,
            "found_keywords": keywords_found,
            "criteria_explanation": criteria,
            "ai_explanation": ai_explanation
        })
        
    end_time = time.time()

    return {
        "company_files": uploaded_filenames,
        "processing_time_seconds": round(end_time - start_time, 2),
        "total_score": scoring_result["total_score"],
        "indicators": enriched_indicators
    }

    #     chunks = chunk_text(extracted_text)

    #     aggregated_scores = {}
    #     aggregated_indicators = {}
    #     for chunk in chunks:
    #         scoring_result = score_text(chunk)

    #         for pillar, score in scoring_result["score_breakdown"].items():
    #             aggregated_scores[pillar] = aggregated_scores.get(pillar, 0) + score
            

    #         for indicator in scoring_result["indicators"]:
    #             gri = indicator["GRI"]
    #             if gri not in aggregated_indicators:
    #                 aggregated_indicators[gri] = {
    #                     "description": indicator["description"],
    #                     "found": indicator["found"],
    #                     "score": indicator["score"],
    #                     "best_chunk": chunk if indicator["found"] else None
    #                 }
    #             else:
    #                 if indicator["found"]:
    #                     aggregated_indicators[gri]["found"] = True
    #                     aggregated_indicators[gri]["score"] = indicator["score"]
    #                     if aggregated_indicators[gri]["best_chunk"] is None:
    #                         aggregated_indicators[gri]["best_chunk"] = chunk
        
    #     total_score = sum(aggregated_scores.values())

    #     enriched_indicators = []
    #     for gri_code, indicator in aggregated_indicators.items():
    #         if indicator["found"]:
    #             explanation = get_ai_explanation(extracted_text, indicator["GRI"])
    #         else:
    #             explanation = "Indicator not found, no explanation needed."

    #         enriched_indicators.append({
    #             "GRI": indicator["GRI"],
    #             "description": indicator["description"],
    #             "found": indicator["found"],
    #             "score": indicator["score"],
    #             "ai_explanation": explanation
    #         })
        
    #     end_time = time.time()

    #     results.append({
    #         "filename": file.filename,
    #         "processing_time_seconds": round(end_time - start_time, 2),
    #         "total_score": scoring_result["total_score"],
    #         "pillar_breakdown": scoring_result["score_breakdown"],
    #         "indicators": enriched_indicators
    #     })

    # return {"results": results}

# @app.post("/upload_pdfs/")
# async def upload_pdfs(files: list[UploadFile] = File(...)):
#     start_time = time.time()
#     extracted_data = []

#     for file in files:
#         file_path = os.path.join(UPLOAD_DIR, file.filename)

#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         extracted_text = extract_text_from_pdf(file_path)

#         extracted_data.append({
#             "filename": file.filename,
#             "extracted_text": extracted_text
#         })

#     end_time = time.time()
#     total_time = end_time - start_time
#     return {
#         "documents": extracted_data,
#         "processing_time_seconds": total_time
#     }

# @app.post("/analyze/")
# async def analyze_text(request: AnalyzeRequest):
#     """Send text to Gemini AI for ESG analysis and return token usage."""
#     try:
#         model = genai.GenerativeModel("gemini-2.0-flash")

#         chunks = chunk_text(request.text)
#         total_tokens_used = 0
#         combined_analysis = ""
#         chunk_durations = []

#         for idx, chunk in enumerate(chunks):
#             chunk_start = time.time()
#             response = model.generate_content(chunk)
#             chunk_end = time.time()
#             duration = chunk_end - chunk_start
#             chunk_durations.append({"chunk": idx + 1, "duration": duration})

#             estimated_tokens = len(chunk) / 4
#             total_tokens_used += estimated_tokens

#             combined_analysis += f"\n\n=== Analysis for chunnk {idx + 1} ===\n{response.candidates[0].content}"

        
#         return {
#             "combined_analysis": combined_analysis.strip(),
#             "estimated_tokens_used": total_tokens_used,
#             "per_chunk_timing": chunk_durations
#         }
    
#     except Exception as e:
#         return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)