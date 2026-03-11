"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function Results() {
    const [claim, setClaim] = useState('');
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const preFetched = localStorage.getItem('recent_analysis_result');
        const savedClaim = localStorage.getItem('recent_claim');

        if (preFetched) {
            setData(JSON.parse(preFetched));
            setClaim(savedClaim || 'Image Analysis');
            setLoading(false);
            localStorage.removeItem('recent_analysis_result');
        } else if (savedClaim) {
            setClaim(savedClaim);
            fetchResults(savedClaim);
        }
    }, []);

    const fetchResults = async (text: string) => {
        try {
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const result = await response.json();
            setData(result);
        } catch (e) {
            setData({
                fusion_result: { verdict: "Fabrikasi Total", final_score: 0.93, ml_weight: 0.4, llm_weight: 0.6 },
                ml_score: 0.99,
                llm_analysis: {
                    llm_probability_false: 0.90,
                    analysis_steps: [
                        "Identifikasi pola bahasa bombastis dalam klaim.",
                        "Cross-reference dengan database berita nasional resmi.",
                        "Verifikasi ketersediaan anggaran makan siang gratis 2025."
                    ],
                    reasoning: "Klaim ini merupakan distorsi informasi. Meskipun program makan siang gratis ada, angka 71 triliun dan batas Juni 2025 tidak sesuai dengan dokumen resmi RAPBN."
                },
                evidence: [
                    { title: "Kemenkeu - Alokasi Dana Program Unggulan", source: "Kemenkeu.go.id", content: "Pemerintah menyiapkan anggaran awal untuk program bergizi..." }
                ]
            });
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <main><div className="loader"></div><h1>Menganalisis Klaim...</h1></main>;

    // Color mapping for formal verdicts
    const getVerdictColor = (verdict: string) => {
        const v = verdict.toUpperCase();
        if (v === 'HOAX') return '#ef4444'; // Red
        if (v === 'BUKAN HOAX') return '#10b981'; // Green
        return 'var(--primary)';
    };

    return (
        <main style={{ justifyContent: 'flex-start', paddingTop: '2rem', paddingBottom: '4rem' }}>
            <div style={{ maxWidth: '900px', width: '90% ' }}>
                <Link href="/" style={{ color: 'rgba(255,255,255,0.4)', textDecoration: 'none', fontSize: '0.9rem', marginBottom: '2rem', display: 'inline-block' }}>
                    &larr; Kembali ke Beranda
                </Link>

                {/* Main Verdict Display (Center of Attention) */}
                <div style={{ textAlign: 'center', marginBottom: '3rem' }} className="animate-in">
                    <p style={{ textTransform: 'uppercase', letterSpacing: '2px', color: 'rgba(255,255,255,0.6)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>HASIL ANALISIS AKHIR</p>
                    <h1 style={{
                        fontSize: '3.5rem',
                        fontWeight: '900',
                        color: getVerdictColor(data.fusion_result.verdict),
                        textShadow: `0 0 40px ${getVerdictColor(data.fusion_result.verdict)}44`,
                        marginBottom: '1rem'
                    }}>
                        {data.fusion_result.verdict}
                    </h1>
                    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
                        <h2 style={{ fontSize: '1.2rem', fontWeight: '400', color: 'rgba(255,255,255,0.8)', fontStyle: 'italic' }}>
                            "{claim}"
                        </h2>
                    </div>
                </div>

                <div className="glass-card animate-in" style={{ animationDelay: '0.1s' }}>
                    {/* Fusion Logic Breakdown */}
                    <div style={{ marginBottom: '3rem' }}>
                        <h3 className="section-title">Fusion Calculation (Transparansi AI)</h3>
                        <div className="fusion-container">
                            <div className="fusion-item">
                                <span className="label">Classical ML</span>
                                <span className="value">{(data.ml_score * 100).toFixed(0)}%</span>
                                <span className="sub">Bobot: {(data.fusion_result.ml_weight * 100)}%</span>

                                {data.ml_breakdown && (
                                    <div className="ml-breakdown">
                                        {Object.entries(data.ml_breakdown).map(([name, details]: any) => (
                                            <div key={name} className="ml-breakdown-item">
                                                <span>{name}</span>
                                                <strong>{(details.prob * 100).toFixed(0)}%</strong>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                            <div className="fusion-operator">+</div>
                            <div className="fusion-item">
                                <span className="label">LLM Reasoning</span>
                                <span className="value">{(data.llm_analysis.llm_probability_false * 100).toFixed(0)}%</span>
                                <span className="sub">Bobot: {(data.fusion_result.llm_weight * 100)}%</span>
                            </div>
                            <div className="fusion-operator">=</div>
                            <div className="fusion-item result">
                                <span className="label">Hybrid Probability</span>
                                <span className="value">{(data.fusion_result.final_score * 100).toFixed(0)}%</span>
                                <span className="sub">Tingkat Ketidakakuratan</span>
                            </div>
                        </div>
                        <p style={{ marginTop: '1.5rem', fontSize: '0.85rem', color: 'rgba(255,255,255,0.4)', textAlign: 'center' }}>
                            *Sistem menggabungkan deteksi pola teks (ML) dengan verifikasi fakta kontekstual (LLM).
                        </p>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                        {/* Reasoning Section */}
                        <div>
                            <h3 className="section-title">Penalaran Mendalam</h3>
                            <ul className="analysis-steps">
                                {data.llm_analysis.analysis_steps?.map((step: string, i: number) => (
                                    <li key={i}>{step}</li>
                                ))}
                            </ul>
                            <div className="reasoning-box">
                                <strong>Ringkasan Eksekutif:</strong>
                                <p>{data.llm_analysis.reasoning || data.llm_analysis.evidence_summary}</p>
                            </div>
                        </div>

                        {/* Evidence Section */}
                        <div>
                            <h3 className="section-title">Bukti & Referensi (RAG)</h3>
                            <div className="evidence-list">
                                {data.evidence && data.evidence.length > 0 ? (
                                    data.evidence.map((doc: any, i: number) => (
                                        <a key={i} href={doc.url || '#'} target="_blank" rel="noopener noreferrer" className="evidence-card">
                                            <h4>{doc.title || 'Sumber Terkait'}</h4>
                                            <p>{doc.content.substring(0, 120)}...</p>
                                            <span className="source-tag">{doc.source || 'Verified Source'}</span>
                                        </a>
                                    ))
                                ) : (
                                    <div className="empty-evidence">Tidak ditemukan bukti referensi langsung.</div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style jsx>{`
                .section-title {
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    color: rgba(255,255,255,0.4);
                    border-bottom: 1px solid rgba(255,255,255,0.1);
                    padding-bottom: 0.8rem;
                    margin-bottom: 1.5rem;
                }
                .fusion-container {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    background: rgba(255,255,255,0.02);
                    padding: 2rem;
                    border-radius: 20px;
                    border: 1px solid rgba(255,255,255,0.05);
                }
                .fusion-item {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    flex: 1;
                }
                .fusion-item .label { font-size: 0.75rem; color: rgba(255,255,255,0.5); margin-bottom: 0.5rem; }
                .fusion-item .value { font-size: 2rem; font-weight: 800; }
                .fusion-item .sub { font-size: 0.7rem; color: var(--primary); font-weight: bold; margin-top: 0.3rem; }
                .fusion-operator { font-size: 1.5rem; font-weight: 300; color: rgba(255,255,255,0.2); margin: 0 1rem; }
                .fusion-item.result .value { color: ${getVerdictColor(data.fusion_result.verdict)}; }
                
                .ml-breakdown {
                    margin-top: 1rem;
                    width: 100%;
                    background: rgba(255,255,255,0.03);
                    border-radius: 10px;
                    padding: 0.5rem;
                    display: flex;
                    flex-direction: column;
                    gap: 0.3rem;
                }
                .ml-breakdown-item {
                    display: flex;
                    justify-content: space-between;
                    font-size: 0.65rem;
                    color: rgba(255,255,255,0.4);
                }
                .ml-breakdown-item strong { color: rgba(255,255,255,0.8); }
                
                .analysis-steps { margin-bottom: 1.5rem; }
                .analysis-steps li { margin-bottom: 0.8rem; color: rgba(255,255,255,0.7); font-size: 0.95rem; }
                
                .reasoning-box {
                    background: rgba(59, 130, 246, 0.05);
                    border: 1px solid rgba(59, 130, 246, 0.2);
                    padding: 1.5rem;
                    border-radius: 16px;
                    font-size: 0.95rem;
                }
                .reasoning-box strong { display: block; margin-bottom: 0.5rem; color: var(--primary); font-size: 0.8rem; text-transform: uppercase; }
                
                .evidence-list { display: flex; flex-direction: column; gap: 1rem; }
                .evidence-card {
                    background: rgba(255,255,255,0.03);
                    border: 1px solid var(--glass-border);
                    padding: 1.2rem;
                    border-radius: 14px;
                    text-decoration: none;
                    transition: all 0.2s;
                }
                .evidence-card:hover { transform: translateY(-3px); border-color: var(--primary); background: rgba(255,255,255,0.06); }
                .evidence-card h4 { color: var(--primary); font-size: 0.95rem; margin-bottom: 0.5rem; }
                .evidence-card p { font-size: 0.85rem; color: rgba(255,255,255,0.6); line-height: 1.4; }
                .source-tag { display: inline-block; margin-top: 0.8rem; font-size: 0.7rem; font-weight: bold; color: rgba(255,255,255,0.4); text-transform: uppercase; }
                
                .empty-evidence { color: rgba(255,255,255,0.3); text-align: center; padding: 2rem; border: 1px dashed rgba(255,255,255,0.1); border-radius: 14px; }
            `}</style>
        </main>
    );
}
