import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate, useLocation } from 'react-router-dom';
import {
  Sprout, CloudRain, FlaskConical, Activity, Download, RefreshCw, Cpu,
  ChevronDown, ChevronUp, DollarSign, Droplets, Leaf, LogOut, History as HistoryIcon
} from 'lucide-react';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import './index.css';

import { LoginPage, SignupPage } from './AuthPages.jsx';
import SensorDashboard from './SensorDashboard.jsx';
import History from './History.jsx';
import Chatbot from './Chatbot.jsx';

const API_BASE = 'http://localhost:8000';

function Analyzer({ user }) {
  const [sensorData, setSensorData] = useState(null);
  const [results, setResults] = useState(null);
  const [loadingSensors, setLoadingSensors] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [expandedCrop, setExpandedCrop] = useState(0);
  const [currentHistoryId, setCurrentHistoryId] = useState(null);
  const [simulationMode, setSimulationMode] = useState('random');
  const [testScenario, setTestScenario] = useState('rice');
  const [manualData, setManualData] = useState({
    N: 50, P: 50, K: 50, temperature: 25, humidity: 60, ph: 6.5, rainfall: 100
  });

  const handleManualChange = (e) => {
    setManualData({ ...manualData, [e.target.name]: e.target.value });
  };
  const contentRef = useRef(null);
  const navigate = useNavigate();

  const fetchSensorData = async () => {
    setLoadingSensors(true);
    setResults(null);
    try {
      if (simulationMode === 'manual') {
        const parsedData = {
          N: Number(manualData.N),
          P: Number(manualData.P),
          K: Number(manualData.K),
          temperature: Number(manualData.temperature),
          humidity: Number(manualData.humidity),
          ph: Number(manualData.ph),
          rainfall: Number(manualData.rainfall),
        };
        setSensorData(parsedData);
        setLoadingSensors(false);
        return;
      }
      await new Promise(r => setTimeout(r, 1500));
      const res = await axios.get(`${API_BASE}/get-soil-data`, {
        params: { mode: simulationMode, scenario: simulationMode === 'test' ? testScenario : undefined }
      });
      setSensorData(res.data);
    } catch (error) {
      console.error("Error fetching sensor data:", error);
    } finally {
      setLoadingSensors(false);
    }
  };

  const analyzeSoil = async () => {
    if (!sensorData) return;
    setAnalyzing(true);
    try {
      const res = await axios.post(`${API_BASE}/predict-all`, sensorData);
      setResults(res.data);
      setExpandedCrop(0);

      // Save analysis history to DB
      const token = localStorage.getItem('token');
      if (token) {
        const historyRes = await axios.post(`${API_BASE}/save-analysis`, {
          soil_data: sensorData,
          top_crops: res.data.top_crops,
          health: res.data.health
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setCurrentHistoryId(historyRes.data.history_id);
      }
    } catch (error) {
      console.error("Error analyzing soil or saving history:", error);
    } finally {
      setAnalyzing(false);
    }
  };

  const exportPDF = async () => {
    if (!currentHistoryId) {
      alert("Please ensure you are logged in and the analysis is saved before downloading.");
      return;
    }
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_BASE}/download-report/${currentHistoryId}`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SoilSmart_Report_${currentHistoryId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error downloading PDF:", error);
    }
  };

  const getHealthColor = (health) => {
    if (health === 'Healthy') return '#10b981';
    if (health === 'Moderate') return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div ref={contentRef} style={{ animation: 'fadeIn 0.5s ease-out' }}>
      <div className="controls" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '1rem' }}>
        <h2 className="section-title" style={{ margin: 0, borderBottom: 'none', padding: 0 }}>
          <Sprout size={24} style={{ color: '#10b981' }} /> New Analysis
        </h2>

        <div className="simulation-controls" style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap', width: '100%' }}>
          <div className="mode-selector" style={{ display: 'flex', gap: '0.5rem', background: 'rgba(255,255,255,0.05)', padding: '0.4rem', borderRadius: '0.5rem' }}>
            <button className={`btn ${simulationMode === 'random' ? 'btn-primary' : ''}`} style={{ padding: '0.5rem 1rem', background: simulationMode === 'random' ? '' : 'transparent' }} onClick={() => setSimulationMode('random')}>Random Mode</button>
            <button className={`btn ${simulationMode === 'test' ? 'btn-primary' : ''}`} style={{ padding: '0.5rem 1rem', background: simulationMode === 'test' ? '' : 'transparent' }} onClick={() => setSimulationMode('test')}>Test Mode</button>
            <button className={`btn ${simulationMode === 'manual' ? 'btn-primary' : ''}`} style={{ padding: '0.5rem 1rem', background: simulationMode === 'manual' ? '' : 'transparent' }} onClick={() => setSimulationMode('manual')}>Manual Input</button>
          </div>
          {simulationMode === 'test' && (
            <select className="scenario-select" value={testScenario} onChange={(e) => setTestScenario(e.target.value)} style={{ padding: '0.6rem', borderRadius: '0.5rem', background: 'rgba(0,0,0,0.5)', color: 'white', border: '1px solid rgba(255,255,255,0.2)', flexGrow: 1 }}>
              <option value="rice">Condition: High N, High Humidity (Rice-like)</option>
              <option value="wheat">Condition: Moderate Nutrients (Wheat-like)</option>
              <option value="poor">Condition: Low Nutrients (Poor Soil)</option>
            </select>
          )}
          {simulationMode === 'manual' && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '0.8rem', width: '100%', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '0.5rem' }}>
              {['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'].map((field) => (
                <div key={field} style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                  <label style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'capitalize' }}>{field}</label>
                  <input type="number" step="any" name={field} value={manualData[field]} onChange={handleManualChange} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', padding: '0.5rem', borderRadius: '0.3rem', width: '100%', fontSize: '0.9rem' }} />
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={{ display: 'flex', gap: '1rem', width: '100%', flexWrap: 'wrap' }}>
          <button
            className="btn btn-secondary"
            onClick={fetchSensorData}
            disabled={loadingSensors || analyzing}
            style={{ flex: 1 }}
          >
            {loadingSensors ? <span className="loader"></span> : <RefreshCw size={20} />}
            Get Soil Data
          </button>

          <button
            className="btn btn-primary"
            onClick={analyzeSoil}
            disabled={!sensorData || analyzing || loadingSensors}
            style={{ flex: 2 }}
          >
            {analyzing ? <span className="loader"></span> : <Cpu size={20} />}
            Analyze Soil & Generate Plan
          </button>
        </div>
      </div>

      <div className="glass-panel">
        <h2 className="section-title">
          <Activity size={24} style={{ color: '#10b981' }} />
          Live Sensor Readings
        </h2>

        {loadingSensors ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem', color: '#10b981' }}>
            <span className="loader" style={{ width: '48px', height: '48px', borderWidth: '4px', marginBottom: '1.5rem', borderColor: '#10b981', borderBottomColor: 'transparent' }}></span>
            <p style={{ fontSize: '1.25rem', fontWeight: '500', animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' }}>Fetching data from sensors...</p>
          </div>
        ) : sensorData ? (
          <div className="sensor-grid">
            <div className="sensor-card">
              <span className="sensor-label">Nitrogen (N)</span>
              <span className="sensor-value">{sensorData.N}</span>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>mg/kg</span>
            </div>
            <div className="sensor-card">
              <span className="sensor-label">Phosphorus (P)</span>
              <span className="sensor-value">{sensorData.P}</span>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>mg/kg</span>
            </div>
            <div className="sensor-card">
              <span className="sensor-label">Potassium (K)</span>
              <span className="sensor-value">{sensorData.K}</span>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>mg/kg</span>
            </div>
            <div className="sensor-card">
              <span className="sensor-label">Temperature</span>
              <span className="sensor-value">{sensorData.temperature}°</span>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Celsius</span>
            </div>
            <div className="sensor-card">
              <span className="sensor-label">Humidity</span>
              <span className="sensor-value">{sensorData.humidity}%</span>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Relative</span>
            </div>
            <div className="sensor-card">
              <span className="sensor-label">Soil pH</span>
              <span className="sensor-value">{sensorData.ph}</span>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Scale (1-14)</span>
            </div>
            <div className="sensor-card" style={{ gridColumn: '1 / -1' }}>
              <span className="sensor-label">Rainfall</span>
              <span className="sensor-value">{sensorData.rainfall}</span>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>mm</span>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2rem', color: '#94a3b8', textAlign: 'center', opacity: 0.6 }}>
            <Sprout size={48} style={{ marginBottom: '1rem' }} />
            <p>Click "Get Soil Data" to simulate IoT sensors and retrieve real-time field data.</p>
          </div>
        )}
      </div>

      {results && (
        <>
          <div className="glass-panel" style={{ marginBottom: '2rem' }}>
            <div className="flex" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 className="section-title" style={{ margin: 0, border: 'none' }}>
                <Activity size={24} style={{ color: getHealthColor(results.health.prediction) }} />
                Overall Soil Health: <span style={{ marginLeft: '0.5rem', color: getHealthColor(results.health.prediction) }}>{results.health.prediction}</span>
              </h2>
              <span style={{ color: '#94a3b8' }}>AI Confidence: {results.health.confidence}%</span>
            </div>
          </div>

          <h2 className="section-title" style={{ borderBottom: 'none' }}>
            <Sprout size={28} style={{ color: '#10b981' }} />
            Top 5 AI Crop Recommendations
          </h2>

          <div className="crops-list">
            {results.top_crops.map((crop, index) => {
              const isOpen = expandedCrop === index || expandedCrop === -1;
              return (
                <div className="crop-card" key={index} style={{ animationDelay: `${index * 0.1}s` }}>
                  <div className="crop-header" onClick={() => setExpandedCrop(isOpen ? null : index)}>
                    <div className="crop-title-group">
                      <div className="crop-rank">{index + 1}</div>
                      <div className="crop-name">{crop.name}</div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                      <div className="crop-prob-group">
                        <span className="prob-text">{crop.probability}% Match</span>
                        <div className="prob-bar-bg">
                          <div className="prob-bar-fill" style={{ width: `${crop.probability}%` }}></div>
                        </div>
                      </div>
                      {isOpen ? <ChevronUp size={24} /> : <ChevronDown size={24} />}
                    </div>
                  </div>

                  {isOpen && (
                    <div className="crop-details">
                      <div className="detail-section">
                        <h4 className="detail-title econ"><DollarSign size={20} /> Economic Estimate (1 Acre)</h4>
                        <div className="detail-row">
                          <span className="row-label">Estimated Cost:</span>
                          <span className="row-value" style={{ color: '#ef4444' }}>₹{crop.economics.cost.toLocaleString()}</span>
                        </div>
                        <div className="detail-row">
                          <span className="row-label">Expected Yield:</span>
                          <span className="row-value">{crop.economics.yield.toLocaleString()} kg/acre</span>
                        </div>
                        <div className="detail-row">
                          <span className="row-label">Market Price Avg:</span>
                          <span className="row-value">₹{crop.economics.price}/kg</span>
                        </div>
                        <div className="detail-row" style={{ marginTop: '1rem', borderTop: '2px solid rgba(255,255,255,0.1)', paddingTop: '0.8rem' }}>
                          <span className="row-label font-bold">Expected Profit:</span>
                          <span className="row-value profit-value">₹{crop.economics.profit.toLocaleString()}</span>
                        </div>
                      </div>

                      <div className="detail-section">
                        <h4 className="detail-title fert"><FlaskConical size={20} /> Fertilizer Master Plan</h4>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', marginTop: '0.5rem' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8' }}>
                              <th style={{ padding: '0.5rem' }}>Growth Phase</th>
                              <th style={{ padding: '0.5rem' }}>Application Details</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                              <td style={{ padding: '0.5rem', fontWeight: 'bold' }}>Basal Dose</td>
                              <td style={{ padding: '0.5rem' }}>{crop.fertilizer_schedule.Basal}</td>
                            </tr>
                            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                              <td style={{ padding: '0.5rem', fontWeight: 'bold' }}>Vegetative</td>
                              <td style={{ padding: '0.5rem' }}>{crop.fertilizer_schedule.Vegetative}</td>
                            </tr>
                            <tr>
                              <td style={{ padding: '0.5rem', fontWeight: 'bold' }}>Flowering</td>
                              <td style={{ padding: '0.5rem' }}>{crop.fertilizer_schedule.Flowering}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>

                      <div className="detail-section">
                        <h4 className="detail-title water"><Droplets size={20} /> Irrigation Schedule</h4>
                        <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '0.5rem' }}>
                          <p style={{ margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ color: '#94a3b8' }}>Frequency:</span>
                            <span style={{ color: '#3b82f6', fontWeight: 'bold' }}>{crop.water_schedule.Frequency}</span>
                          </p>
                          <p style={{ margin: 0 }}>
                            <span style={{ color: '#94a3b8', display: 'block', marginBottom: '0.2rem' }}>Critical Stages:</span>
                            <span style={{ fontStyle: 'italic' }}>{crop.water_schedule.Stages}</span>
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <button className="export-btn" onClick={exportPDF} title="Export Detailed Plan as PDF">
            <Download size={24} />
          </button>
        </>
      )}
    </div>
  );
}

function MainApp() {
  const [user, setUser] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Check if logged in
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    navigate('/login');
  };

  const isAuthPage = location.pathname === '/login' || location.pathname === '/signup';

  if (!user && !isAuthPage) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="app-container">
      {!isAuthPage && (
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Leaf size={32} style={{ color: '#10b981' }} />
              SoilSmart AI
            </h1>
            <p className="subtitle" style={{ margin: '0.5rem 0 0 0' }}>Welcome back, {user?.name}</p>
          </div>

          <nav style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <Link to="/" className={`btn ${location.pathname === '/' ? 'btn-primary' : 'btn-secondary'}`} style={{ textDecoration: 'none' }}>
              <Sprout size={18} /> New Analysis
            </Link>
            <Link to="/sensor-dashboard" className={`btn ${location.pathname === '/sensor-dashboard' ? 'btn-primary' : 'btn-secondary'}`} style={{ textDecoration: 'none' }}>
              <Activity size={18} /> IoT Dashboard
            </Link>
            <Link to="/history" className={`btn ${location.pathname === '/history' ? 'btn-primary' : 'btn-secondary'}`} style={{ textDecoration: 'none' }}>
              <HistoryIcon size={18} /> History
            </Link>
            <button className="btn btn-secondary" onClick={handleLogout} style={{ border: '1px solid rgba(239,68,68,0.5)', color: '#ef4444', marginLeft: '1rem' }}>
              <LogOut size={18} /> Logout
            </button>
          </nav>
        </header>
      )}

      <Routes>
        <Route path="/login" element={<LoginPage onLogin={setUser} />} />
        <Route path="/signup" element={<SignupPage onLogin={setUser} />} />
        <Route path="/" element={<Analyzer user={user} />} />
        <Route path="/sensor-dashboard" element={<SensorDashboard onBack={() => navigate('/')} />} />
        <Route path="/history" element={<History />} />
      </Routes>

      {!isAuthPage && user && <Chatbot />}
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <MainApp />
    </BrowserRouter>
  );
}

export default App;
