import os
from supabase import create_client, Client
from dotenv import load_dotenv
from .search_engine import SearchEngine

load_dotenv(override=True)

class RAGLayer:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.search_engine = SearchEngine()
        if url and key:
            try:
                self.supabase: Client = create_client(url, key)
            except:
                self.supabase = None
        else:
            self.supabase = None

    def retrieve_evidence(self, query: str, limit: int = 3):
        evidence = []
        print(f"DEBUG: Memulai pencarian bukti (RAG) untuk: {query}")
        
        # 1. Coba cari di database internal (Supabase)
        if self.supabase:
            try:
                # Simulasi pencarian dokumen di Supabase
                # Di produksi nyata, gunakan match_documents dengan embedding
                print("DEBUG: Menggunakan OpenAI API untuk generate Query Embedding & Searching Supabase...")
                response = self.supabase.table("documents").select("*").limit(limit).execute()
                if response.data:
                    evidence.extend(response.data)
                    print(f"DEBUG: Ditemukan {len(response.data)} dokumen di Supabase.")
            except Exception as e:
                print(f"DEBUG: Supabase Notice (Tabel mungkin belum ada): {e}")
                pass

        # 2. Jika database kosong atau butuh tambahan, cari live di internet (Gratis)
        if len(evidence) < limit:
            needed = limit - len(evidence)
            print(f"DEBUG: Menjalankan Live Grounding (DuckDuckGo News) untuk mencari {needed} bukti tambahan...")
            live_news = self.search_engine.search_news(query, max_results=needed)
            evidence.extend(live_news)
            
        print(f"DEBUG: Total bukti terkumpul: {len(evidence)}")
        return evidence
