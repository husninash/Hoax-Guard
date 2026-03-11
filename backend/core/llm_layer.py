import os
import json
from openai import OpenAI
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(override=True)

class LLMLayer:
    def __init__(self):
        # OpenAI Setup (Fallback)
        openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        
        # Gemini Setup (Primary) - Using NEW google-genai SDK
        gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if gemini_api_key:
            # Use 'v1' instead of default if needed, or just standard string
            self.gemini_client = genai.Client(api_key=gemini_api_key)
            self.model_id = 'gemini-2.0-flash'
        else:
            self.gemini_client = None

    def analyze_claim(self, claim: str, ml_probability: float, evidence: list):
        evidence_text = "\n".join([f"- {doc.get('content', '')} (Source: {doc.get('source', 'Unknown')})" for doc in evidence])
        
        prompt = f"""
        Analisislah klaim berikut untuk mendeteksi potensi hoax atau misinformasi dalam Bahasa Indonesia.
        
        KLAIM: {claim}
        
        PROBABILITAS DETEKSI ML (HOAX): {ml_probability:.2f}
        
        BUKTI YANG DITEMUKAN:
        {evidence_text if evidence_text else "Tidak ditemukan bukti spesifik."}
        
        Berikan analisis lengkap dalam format JSON dengan kunci sebagai berikut:
        - claim_summary: Ringkasan singkat klaim dalam Bahasa Indonesia.
        - analysis_steps: Langkah-langkah penalaran (list) dalam Bahasa Indonesia.
        - evidence_summary: Ringkasan bagaimana bukti mendukung atau menyangkal klaim dalam Bahasa Indonesia.
        - llm_probability_false: Estimasi probabilitas bahwa klaim ini SALAH (0.0 hingga 1.0).
        - verdict: Salah satu dari [HOAX, BUKAN HOAX].
        - reasoning: Penjelasan mendalam mengenai kesimpulan akhir dalam Bahasa Indonesia.
        """

        # 1. Coba pakai Gemini (Primary - New SDK)
        if self.gemini_client:
            try:
                print(f"DEBUG: Menganalisis klaim menggunakan Gemini ({self.model_id})...")
                response = self.gemini_client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                return json.loads(response.text)
            except Exception as e:
                print(f"DEBUG: Gemini Error: {e}. Switching to OpenAI Fallback...")

        # 2. Fallback ke OpenAI
        if self.openai_client:
            try:
                print("DEBUG: Menganalisis klaim menggunakan OpenAI (Fallback)...")
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Anda adalah ahli pemeriksa fakta (fact-checker) Indonesia yang sangat teliti. Anda harus menjawab SELALU dalam Bahasa Indonesia dan hanya memberikan output dalam format JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"DEBUG: OpenAI Fallback Error: {e}")

        # 3. Final Fallback (Empty Result)
        return {
            "verdict": "Internal Error",
            "llm_probability_false": 0.5,
            "reasoning": "Gagal menghubungi AI Service (Gemini & OpenAI)."
        }
