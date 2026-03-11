import base64
import os
from openai import OpenAI
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(override=True)

class OCRLayer:
    def __init__(self):
        # OpenAI Setup (Fallback)
        openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        
        # Gemini Setup (Primary) - Using NEW google-genai SDK
        gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if gemini_api_key:
            self.gemini_client = genai.Client(api_key=gemini_api_key)
            self.model_id = 'gemini-2.0-flash'
        else:
            self.gemini_client = None

    def extract_text(self, image_bytes: bytes):
        """
        Menggunakan Gemini Vision (Primary - New SDK) atau GPT-4o Vision (Fallback) untuk OCR.
        """
        # 1. Coba Gemini (Primary - New SDK)
        if self.gemini_client:
            try:
                print(f"DEBUG: Menjalankan OCR menggunakan Gemini {self.model_id} (New SDK)...")
                response = self.gemini_client.models.generate_content(
                    model=self.model_id,
                    contents=[
                        "Ekstrak SEMUA teks yang terbaca dari gambar ini dalam Bahasa Indonesia. Berikan hasilnya langsung tanpa komentar.",
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                    ]
                )
                return response.text
            except Exception as e:
                print(f"DEBUG: Gemini OCR Error: {e}. Switching to OpenAI Fallback...")

        # 2. Fallback OpenAI
        if self.openai_client:
            try:
                print("DEBUG: Menjalankan OCR menggunakan OpenAI GPT-4o (Fallback)...")
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "Anda adalah ekstraktor teks OCR profesional. Tugas Anda adalah mengekstrak teks dalam Bahasa Indonesia secara akurat."
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Ekstrak teks dari gambar ini:"},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=1000
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"DEBUG: OpenAI OCR Fallback Error: {e}")

        return "Error: Gagal memproses OCR via Gemini & OpenAI."
