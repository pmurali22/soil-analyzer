import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { History as HistoryIcon, Clock, Activity, Sprout, Download } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

function History() {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    const downloadReport = async (historyId) => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`${API_BASE}/download-report/${historyId}`, {
                headers: { Authorization: `Bearer ${token}` },
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `SoilSmart_Report_${historyId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Error downloading PDF:", error);
            alert("Failed to download report. Please try again.");
        }
    };

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await axios.get(`${API_BASE}/history`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setHistory(res.data);
            } catch (error) {
                console.error("Error fetching history:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, []);

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem', color: '#10b981' }}>
                <span className="loader" style={{ borderColor: '#10b981', borderBottomColor: 'transparent' }}></span>
            </div>
        );
    }

    if (history.length === 0) {
        return (
            <div style={{ textAlign: 'center', padding: '4rem', color: '#94a3b8' }}>
                <HistoryIcon size={48} style={{ margin: '0 auto 1rem auto', opacity: 0.5 }} />
                <p>No analysis history found. Run an analysis on the dashboard first!</p>
            </div>
        );
    }

    return (
        <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
            <h2 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem' }}>
                <HistoryIcon size={28} style={{ color: '#8b5cf6' }} />
                Your Analysis History
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {history.map((record) => (
                    <div key={record.id} className="glass-panel" style={{ padding: '1.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#94a3b8' }}>
                                    <Clock size={16} />
                                    <span>{new Date(record.timestamp).toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: record.health.prediction === 'Healthy' ? '#10b981' : '#f59e0b' }}>
                                    <Activity size={16} />
                                    <span style={{ fontWeight: 500 }}>Health: {record.health.prediction}</span>
                                </div>
                            </div>
                            <button onClick={() => downloadReport(record.id)} className="btn btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }} title="Download PDF Report">
                                <Download size={16} /> Download
                            </button>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                            <div>
                                <h4 style={{ margin: '0 0 1rem 0', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <Sprout size={18} style={{ color: '#10b981' }} />
                                    Top Recommendation
                                </h4>
                                {record.top_crops && record.top_crops.length > 0 && (
                                    <div>
                                        <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#10b981', marginBottom: '0.5rem' }}>
                                            {record.top_crops[0].name} ({record.top_crops[0].probability}% match)
                                        </div>
                                        <p style={{ margin: 0, fontSize: '0.9rem', color: '#94a3b8' }}>
                                            Expected Yield: {record.top_crops[0].economics.yield} kg/acre <br />
                                            Est. Profit: ₹{record.top_crops[0].economics.profit.toLocaleString()}
                                        </p>
                                    </div>
                                )}
                            </div>

                            <div>
                                <h4 style={{ margin: '0 0 1rem 0', color: '#f8fafc' }}>Soil Profile at Time</h4>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', fontSize: '0.9rem', color: '#cbd5e1' }}>
                                    <div>N: <span style={{ color: '#fff' }}>{record.soil_metrics.N}</span></div>
                                    <div>P: <span style={{ color: '#fff' }}>{record.soil_metrics.P}</span></div>
                                    <div>K: <span style={{ color: '#fff' }}>{record.soil_metrics.K}</span></div>
                                    <div>Temp: <span style={{ color: '#fff' }}>{record.soil_metrics.temperature}°C</span></div>
                                    <div>Hum: <span style={{ color: '#fff' }}>{record.soil_metrics.humidity}%</span></div>
                                    <div>pH: <span style={{ color: '#fff' }}>{record.soil_metrics.ph}</span></div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default History;
