# 🛡️ HoaxGuard AI — Hybrid Hoax Detection System

Sistem deteksi hoax berbasis **Hybrid AI** yang menggabungkan **Classical Machine Learning** dan **Large Language Model (LLM)** untuk analisis klaim/berita secara mendalam.

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────┐
│                  Frontend (Next.js)              │
│            http://localhost:3000                 │
└─────────────────┬───────────────────────────────┘
                  │ POST /analyze
┌─────────────────▼───────────────────────────────┐
│              Backend (FastAPI)                    │
│            http://localhost:8000                  │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │ ML Layer (50%)                           │    │
│  │  ├─ Linear SVM (Best Hoax)    → 20%      │    │
│  │  ├─ Naive Bayes               → 15%      │    │
│  │  └─ Logistic Regression       → 15%      │    │
│  ├──────────────────────────────────────────┤    │
│  │ LLM Layer (50%)                          │    │
│  │  ├─ Gemini 2.0 Flash (Primary)           │    │
│  │  └─ OpenAI GPT-4o (Fallback)             │    │
│  ├──────────────────────────────────────────┤    │
│  │ RAG Layer                                │    │
│  │  ├─ Supabase Vector DB                   │    │
│  │  └─ DuckDuckGo / Tavily Search           │    │
│  ├──────────────────────────────────────────┤    │
│  │ Fusion Engine                            │    │
│  │  Final Score = ML(50%) + LLM(50%)        │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
```

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/husninash/Hoax-Guard.git
cd Hoax-Guard
```

### 2. Setup Backend
```bash
# Copy environment template & isi API keys
cp backend/.env.example backend/.env

# Install dependencies
pip install -r backend/requirements.txt

# Jalankan server
cd .. && python backend/app.py
# Server berjalan di http://localhost:8000
```

### 3. Setup Frontend
```bash
cd frontend
npm install
npm run dev
# Frontend berjalan di http://localhost:3000
```

### 4. Buka Browser
Akses **http://localhost:3000**, masukkan klaim, dan lihat hasil analisis!

## 📊 Weighted Ensemble Model

| Model | Tipe | Bobot |
|-------|------|-------|
| Linear SVM | Classical ML | 20% |
| Naive Bayes | Classical ML | 15% |
| Logistic Regression | Classical ML | 15% |
| Gemini 2.0 / GPT-4o | LLM Reasoning | 50% |

## 🔑 Environment Variables

Buat file `backend/.env` berdasarkan `backend/.env.example`:

| Variable | Deskripsi |
|----------|-----------|
| `OPENAI_API_KEY` | API key OpenAI (fallback LLM) |
| `GEMINI_API_KEY` | API key Google Gemini (primary LLM) |
| `SUPABASE_URL` | URL Supabase project |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key Supabase |
| `TAVILY_API_KEY` | API key Tavily Search |

## 📁 Struktur Proyek

```
Hoax-Guard/
├── backend/
│   ├── app.py                 # FastAPI server
│   ├── core/
│   │   ├── ml_layer.py        # Ensemble ML (SVM, NB, LR)
│   │   ├── llm_layer.py       # Gemini + OpenAI
│   │   ├── fusion.py          # Weighted fusion engine
│   │   ├── rag_layer.py       # Evidence retrieval
│   │   ├── ocr_layer.py       # Image text extraction
│   │   └── search_engine.py   # Web search
│   ├── models/                # Pre-trained ML models
│   ├── .env.example           # Template environment
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Homepage
│   │   ├── results/page.tsx   # Results with ML breakdown
│   │   ├── globals.css        # Styling
│   │   └── layout.tsx         # Layout
│   └── package.json
└── README.md
```

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, scikit-learn, joblib
- **Frontend**: Next.js 16, TypeScript, React
- **AI/ML**: Linear SVM, Naive Bayes, Logistic Regression, TF-IDF
- **LLM**: Google Gemini 2.0 Flash, OpenAI GPT-4o
- **Database**: Supabase (PostgreSQL + Vector)
- **Search**: DuckDuckGo, Tavily API
