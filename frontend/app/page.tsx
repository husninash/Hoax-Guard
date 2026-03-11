"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);

    try {
      // We'll simulate a fetch to the backend or redirect with the query
      // In a real prod app, we'd POST here and then pass data to results page
      // For this demo architecture, we'll store the text and navigate
      localStorage.setItem('recent_claim', text);
      router.push('/results');
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/analyze-image', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      localStorage.setItem('recent_analysis_result', JSON.stringify(data));
      localStorage.setItem('recent_claim', data.extracted_text);
      router.push('/results');
    } catch (e) {
      console.error("OCR Upload Error:", e);
      setLoading(false);
      alert("Error uploading image. Pastikan backend (app.py) sudah jalan di port 8000.");
    }
  };

  return (
    <main>
      <div className="glass-card animate-in">
        <h1 style={{ textAlign: 'center' }}>HOAXGUARD AI</h1>
        <p style={{ textAlign: 'center', color: 'rgba(255,255,255,0.6)', marginBottom: '2.5rem' }}>
          Hybrid Misinformation Detection & Evidence Reasoning System
        </p>

        <div className="input-container">
          <textarea
            placeholder="Masukkan berita atau klaim yang ingin diverifikasi..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button onClick={handleAnalyze} disabled={loading} style={{ flex: 2 }}>
              {loading ? 'Menganalisis...' : 'Analisis Sekarang'}
            </button>

            <label className="button-secondary" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)', borderRadius: '12px', fontWeight: 'bold' }}>
              {loading ? '...' : 'Upload Gambar'}
              <input type="file" hidden accept="image/*" onChange={handleImageUpload} disabled={loading} />
            </label>
          </div>
        </div>

        <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <span className="badge badge-true">Statistik ML</span>
          <span className="badge badge-warning">RAG Evidence</span>
          <span className="badge badge-false">LLM Reasoning</span>
        </div>
      </div>
    </main>
  );
}
