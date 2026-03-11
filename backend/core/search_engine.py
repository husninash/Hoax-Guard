import os
import warnings
from duckduckgo_search import DDGS
from tavily import TavilyClient

# Suppress annoying DDGS rename warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

class SearchEngine:
    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        if self.tavily_key:
            self.tavily = TavilyClient(api_key=self.tavily_key)
        else:
            self.tavily = None

    def search_news(self, query: str, max_results: int = 3):
        """
        Melakukan pencarian berita real-time.
        Prioritas: Tavily (Professional), Fallback: DuckDuckGo (Gratis).
        """
        results = []
        
        # 1. Coba pakai Tavily (Lebih akurat & profesional)
        if self.tavily:
            try:
                print(f"DEBUG: Mencari berita via Tavily AI untuk: {query}")
                search_result = self.tavily.search(
                    query=query, 
                    search_depth="advanced", 
                    max_results=max_results,
                    include_domains=["detik.com", "kompas.com", "tempo.co", "liputan6.com", "cnnindonesia.com", "turnbackhoax.id"]
                )
                
                for r in search_result.get('results', []):
                    results.append({
                        "title": r.get('title'),
                        "content": r.get('content'),
                        "url": r.get('url'),
                        "source": self._extract_source(r.get('url'))
                    })
                
                if results:
                    return results
            except Exception as e:
                print(f"DEBUG: Tavily search error: {e}. Falling back to DuckDuckGo.")

        # 2. Fallback ke DuckDuckGo jika Tavily gagal atau tidak ada API Key
        try:
            print(f"DEBUG: Menjalankan DuckDuckGo News fallback untuk: {query}")
            with DDGS() as ddgs:
                clean_query = query.strip()[:100]
                ddgs_gen = ddgs.news(
                    keywords=clean_query, 
                    region='id-id', 
                    safesearch='off', 
                    max_results=max_results
                )
                
                for r in ddgs_gen:
                    results.append({
                        "title": r.get('title'),
                        "content": r.get('body'),
                        "url": r.get('url'),
                        "source": r.get('source') or self._extract_source(r.get('url'))
                    })
            return results
        except Exception as e:
            print(f"DEBUG: DuckDuckGo search error: {e}")
            return []

    def _extract_source(self, url):
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain.replace('www.', '')
        except:
            return "Sumber Berita"

if __name__ == "__main__":
    # Test internal
    engine = SearchEngine()
    res = engine.search_news("Berita terbaru Gibran")
    print(f"Found {len(res)} results.")
