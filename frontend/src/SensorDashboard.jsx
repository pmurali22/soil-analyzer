import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { Activity, Thermometer, Droplets, Leaf, ArrowLeft, RefreshCw } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

function SensorDashboard({ onBack }) {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchHistory = async () => {
        try {
            const res = await axios.get(`${API_BASE}/sensor-history`);
            // Format timestamp to readable time string "HH:MM:SS"
            const formattedData = res.data.map(item => ({
                ...item,
                timeLabel: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
            }));
            setHistory(formattedData);
        } catch (error) {
            console.error("Error fetching sensor history:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
        const interval = setInterval(fetchHistory, 5000);
        return () => clearInterval(interval);
    }, []);

    const latest = history.length > 0 ? history[history.length - 1] : null;

    return (
        <div className="dashboard-container" style={{ width: '100%', animation: 'fadeIn 0.5s ease-out' }}>
            <div className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h2 className="section-title" style={{ margin: 0, border: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Activity size={28} style={{ color: '#3b82f6' }} />
                        Live Sensor Monitoring
                    </h2>
                    <p style={{ color: '#94a3b8', margin: '0.5rem 0 0 0' }}>Continuous IoT Data Stream (Last 24 Hours Simulated)</p>
                </div>
                <button className="btn btn-secondary" onClick={onBack}>
                    <ArrowLeft size={20} />
                    Back to Analyzer
                </button>
            </div>

            {loading ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem', color: '#3b82f6' }}>
                    <span className="loader" style={{ borderColor: '#3b82f6', borderBottomColor: 'transparent' }}></span>
                </div>
            ) : history.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '4rem', color: '#94a3b8' }}>
                    No data received from sensors yet...
                </div>
            ) : (
                <>
                    {/* Latest Values Summary */}
                    <div className="glass-panel" style={{ marginBottom: '2rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                            <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f8fafc' }}>
                                <RefreshCw size={20} className="spin-slow" style={{ color: '#10b981' }} />
                                Current Readings
                            </h3>
                            <span style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Updated: {latest.timeLabel}</span>
                        </div>

                        <div className="sensor-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))' }}>
                            <div className="sensor-card">
                                <span className="sensor-label" style={{ color: '#3b82f6' }}>Temperature</span>
                                <span className="sensor-value">{latest.temperature}°C</span>
                            </div>
                            <div className="sensor-card">
                                <span className="sensor-label" style={{ color: '#0ea5e9' }}>Humidity</span>
                                <span className="sensor-value">{latest.humidity}%</span>
                            </div>
                            <div className="sensor-card">
                                <span className="sensor-label" style={{ color: '#10b981' }}>Nitrogen (N)</span>
                                <span className="sensor-value">{latest.N}</span>
                            </div>
                            <div className="sensor-card">
                                <span className="sensor-label" style={{ color: '#8b5cf6' }}>Phosphorus (P)</span>
                                <span className="sensor-value">{latest.P}</span>
                            </div>
                            <div className="sensor-card">
                                <span className="sensor-label" style={{ color: '#f59e0b' }}>Potassium (K)</span>
                                <span className="sensor-value">{latest.K}</span>
                            </div>
                            <div className="sensor-card">
                                <span className="sensor-label" style={{ color: '#ef4444' }}>pH Level</span>
                                <span className="sensor-value">{latest.ph}</span>
                            </div>
                        </div>
                    </div>

                    {/* Charts Grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>

                        {/* Temperature & Humidity Chart */}
                        <div className="glass-panel" style={{ padding: '1.5rem' }}>
                            <h3 style={{ marginTop: 0, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f8fafc' }}>
                                <Thermometer size={20} style={{ color: '#ef4444' }} /> Environmental Conditions
                            </h3>
                            <div style={{ height: '300px', width: '100%' }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={history} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                        <XAxis dataKey="timeLabel" stroke="#94a3b8" fontSize={12} tickMargin={10} />
                                        <YAxis yAxisId="left" stroke="#ef4444" fontSize={12} domain={['dataMin - 2', 'dataMax + 2']} />
                                        <YAxis yAxisId="right" orientation="right" stroke="#3b82f6" fontSize={12} domain={['dataMin - 5', 'dataMax + 5']} />
                                        <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '0.5rem' }} />
                                        <Legend wrapperStyle={{ paddingTop: '20px' }} />
                                        <Line yAxisId="left" type="monotone" dataKey="temperature" name="Temp (°C)" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 6 }} isAnimationActive={false} />
                                        <Line yAxisId="right" type="monotone" dataKey="humidity" name="Humidity (%)" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 6 }} isAnimationActive={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* NPK Nutrients Chart */}
                        <div className="glass-panel" style={{ padding: '1.5rem' }}>
                            <h3 style={{ marginTop: 0, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f8fafc' }}>
                                <Leaf size={20} style={{ color: '#10b981' }} /> Soil Nutrients (NPK)
                            </h3>
                            <div style={{ height: '300px', width: '100%' }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={history} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                        <XAxis dataKey="timeLabel" stroke="#94a3b8" fontSize={12} tickMargin={10} />
                                        <YAxis stroke="#94a3b8" fontSize={12} domain={['dataMin - 10', 'dataMax + 10']} />
                                        <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '0.5rem' }} />
                                        <Legend wrapperStyle={{ paddingTop: '20px' }} />
                                        <Line type="monotone" dataKey="N" name="Nitrogen (N)" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 6 }} isAnimationActive={false} />
                                        <Line type="monotone" dataKey="P" name="Phosphorus (P)" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 6 }} isAnimationActive={false} />
                                        <Line type="monotone" dataKey="K" name="Potassium (K)" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 6 }} isAnimationActive={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                    </div>
                </>
            )}
        </div>
    );
}

export default SensorDashboard;
