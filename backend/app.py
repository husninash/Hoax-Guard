from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from dotenv import load_dotenv

# Specific imports
from core.ml_layer import MLLayer
from core.rag_layer import RAGLayer
from core.llm_layer import LLMLayer
from core.fusion import FusionEngine
from core.ocr_layer import OCRLayer

# Force reload environment variables
load_dotenv(override=True)

app = FastAPI(title="HoaxGuard AI API")

# Enable CORS - Broad for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize layers globally
print("DEBUG: Initializing Backend Layers...")
try:
    ml_layer = MLLayer()
    rag_layer = RAGLayer()
    llm_layer = LLMLayer()
    fusion_engine = FusionEngine()
    ocr_layer = OCRLayer()
    print("DEBUG: All layers initialized successfully.")
except Exception as e:
    print(f"CRITICAL: Engine initialization failed: {e}")

class AnalysisRequest(BaseModel):
    text: str

class AnalysisResult(BaseModel):
    claim: str
    ml_score: float
    ml_breakdown: Optional[dict] = None
    llm_analysis: dict
    fusion_result: dict
    evidence: List[dict]

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "components": {
            "ML": ml_layer.model is not None,
            "RAG": rag_layer.supabase is not None,
            "LLM": getattr(llm_layer, 'gemini_client', None) is not None or getattr(llm_layer, 'openai_client', None) is not None,
            "OCR": getattr(ocr_layer, 'gemini_client', None) is not None or getattr(ocr_layer, 'openai_client', None) is not None
        }
    }

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_text(request: AnalysisRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="Empty text")

    print(f"DEBUG: Analyzing claim: {request.text[:100]}...")
    
    # Layer 1: ML Score
    ml_prob, ml_breakdown = ml_layer.predict(request.text)
    
    # Layer 2: RAG Evidence
    evidence = rag_layer.retrieve_evidence(request.text)
    
    # Layer 3: LLM Reasoning
    llm_result = llm_layer.analyze_claim(request.text, ml_prob, evidence)
    
    # Fusion Scoring
    llm_prob = llm_result.get("llm_probability_false", 0.5)
    fusion_res = fusion_engine.calculate_final_score(ml_prob, llm_prob)
    
    return {
        "claim": request.text,
        "ml_score": ml_prob,
        "ml_breakdown": ml_breakdown,
        "llm_analysis": llm_result,
        "fusion_result": fusion_res,
        "evidence": evidence
    }

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    
    print(f"DEBUG: Processing image OCR for file: {file.filename}")
    image_bytes = await file.read()
    
    # 1. OCR Extraction (Gemini/OpenAI)
    extracted_text = ocr_layer.extract_text(image_bytes)
    
    if not extracted_text or "Error" in extracted_text:
         print(f"DEBUG: OCR failed or empty. Result: {extracted_text}")
         raise HTTPException(status_code=500, detail=f"OCR failed: {extracted_text}")
    
    print(f"DEBUG: OCR extracted text: {extracted_text[:150]}...")
    
    # 2. Pipeline on Extracted Text
    ml_score, ml_breakdown = ml_layer.predict(extracted_text)
    evidence = rag_layer.retrieve_evidence(extracted_text)
    llm_analysis = llm_layer.analyze_claim(extracted_text, ml_score, evidence)
    
    # 3. Fusion Scoring
    llm_prob = llm_analysis.get("llm_probability_false", 0.5)
    fusion_result = fusion_engine.calculate_final_score(ml_score, llm_prob)

    # Return structure compatible with frontend results page
    return {
        "extracted_text": extracted_text,
        "ml_score": ml_score,
        "ml_breakdown": ml_breakdown,
        "evidence": evidence,
        "llm_analysis": llm_analysis,
        "fusion_result": fusion_result
    }

if __name__ == "__main__":
    # Use standard port 8000 for local testing
    uvicorn.run(app, host="0.0.0.0", port=8000)
