import os

base_dir = "/Users/anusrutamohanty/Desktop/FLYY/frontend"

dirs = [
    "src/components",
    "src/pages",
    "src/services",
    "src/utils"
]

for d in dirs:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

files = {}

files["package.json"] = """{
  "name": "flyy-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.7.2",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "recharts": "^2.12.7"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^5.2.12"
  }
}
"""

files["vite.config.js"] = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
"""

files["index.html"] = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>FLYYY.AI — AI Governance</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""

files["src/main.jsx"] = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""

files["src/index.css"] = """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg-primary: #0a0b0f;
  --bg-secondary: #12141a;
  --bg-card: #1a1d26;
  --bg-card-hover: #1f2333;
  --border: rgba(255,255,255,0.08);
  --border-accent: rgba(99,102,241,0.3);
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #475569;
  --accent-blue: #6366f1;
  --accent-purple: #8b5cf6;
  --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  --danger: #ef4444;
  --danger-bg: rgba(239,68,68,0.1);
  --success: #22c55e;
  --success-bg: rgba(34,197,94,0.1);
  --warning: #f59e0b;
  --warning-bg: rgba(245,158,11,0.1);
  --info: #38bdf8;
  --sidebar-width: 260px;
  --header-height: 64px;
  --radius: 12px;
  --radius-sm: 8px;
  --shadow: 0 4px 24px rgba(0,0,0,0.4);
  --shadow-glow: 0 0 30px rgba(99,102,241,0.15);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: var(--bg-primary);
}
::-webkit-scrollbar-thumb {
  background: var(--bg-secondary);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: var(--sidebar-width);
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border);
  position: fixed;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  z-index: 10;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 40px;
  padding: 0 12px;
}

.sidebar-logo span.brand {
  font-size: 20px;
  font-weight: 800;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sidebar-logo span.sub {
  color: var(--text-secondary);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
  font-weight: 500;
}

.nav-item:hover {
  background-color: var(--bg-card);
  color: var(--text-primary);
  transform: translateX(4px);
}

.nav-item.active {
  background-color: var(--bg-card-hover);
  color: var(--text-primary);
  border-left: 3px solid var(--accent-blue);
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border);
  margin-top: auto;
}

.version-badge {
  display: inline-block;
  padding: 4px 8px;
  background-color: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 11px;
  color: var(--text-muted);
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  padding: 32px 40px;
}

.page-header {
  margin-bottom: 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.page-header p {
  color: var(--text-secondary);
}

.card {
  background-color: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  backdrop-filter: blur(10px);
  transition: all 0.2s ease;
  box-shadow: var(--shadow);
}

.card:hover {
  border-color: var(--border-accent);
  box-shadow: var(--shadow-glow);
}

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
  background: var(--accent-gradient);
  opacity: 0;
  transition: opacity 0.2s;
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.stat-card-title {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}

.stat-card-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
}

.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }

.table-container {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-card);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

th {
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: var(--bg-secondary);
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background: var(--bg-card-hover);
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge.danger { background: var(--danger-bg); color: var(--danger); border: 1px solid rgba(239,68,68,0.2); }
.badge.success { background: var(--success-bg); color: var(--success); border: 1px solid rgba(34,197,94,0.2); }
.badge.warning { background: var(--warning-bg); color: var(--warning); border: 1px solid rgba(245,158,11,0.2); }
.badge.info { background: rgba(56,189,248,0.1); color: var(--info); border: 1px solid rgba(56,189,248,0.2); }

.pii-pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  margin: 2px;
}

.tag {
  display: inline-block;
  padding: 4px 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 12px;
  color: var(--text-primary);
  margin-right: 8px;
  margin-bottom: 8px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: all 0.2s;
}

.btn:hover {
  background: var(--bg-card-hover);
}

.btn-primary {
  background: var(--accent-gradient);
  border: none;
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: var(--shadow-glow);
}

.violation-banner {
  background: linear-gradient(90deg, rgba(239,68,68,0.2) 0%, rgba(239,68,68,0.05) 100%);
  border-left: 4px solid var(--danger);
  padding: 16px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.compliant-banner {
  background: linear-gradient(90deg, rgba(34,197,94,0.2) 0%, rgba(34,197,94,0.05) 100%);
  border-left: 4px solid var(--success);
  padding: 16px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.declared-observed-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.do-col {
  padding: 24px;
}

.do-col:first-child {
  border-right: 1px solid var(--border);
  background: rgba(255,255,255,0.02);
}

.do-header {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 16px;
  text-align: center;
}

.do-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255,255,255,0.1);
  border-radius: 50%;
  border-top-color: var(--accent-blue);
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.page-fade-in {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Recharts overrides */
.recharts-default-tooltip {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  box-shadow: var(--shadow) !important;
}
.recharts-tooltip-item {
  color: var(--text-primary) !important;
}
"""

files["src/services/api.js"] = """import axios from 'axios';

const api = axios.create({
  baseURL: '/api'
});

export const getOverview = () => api.get('/analytics/overview').then(res => res.data);
export const getUsageOverTime = () => api.get('/analytics/usage-over-time').then(res => res.data);
export const getPIIByAsset = () => api.get('/analytics/pii-by-asset').then(res => res.data);
export const getPIITypes = () => api.get('/analytics/pii-types').then(res => res.data);
export const getAgentStats = () => api.get('/analytics/agent-stats').then(res => res.data);

export const getAssets = () => api.get('/assets').then(res => res.data);
export const getAsset = (id) => api.get(`/assets/${id}`).then(res => res.data);
export const updateAsset = (id, data) => api.patch(`/assets/${id}`, data).then(res => res.data);
export const getAssetPolicy = (id) => api.get(`/assets/${id}/policy`).then(res => res.data);
export const updateAssetPolicy = (id, data) => api.put(`/assets/${id}/policy`, data).then(res => res.data);

export const getInteractions = (params) => api.get('/interactions', { params }).then(res => res.data);
export const getPIISummary = (params) => api.get('/interactions/pii-summary', { params }).then(res => res.data);

export const getAgentRuns = (params) => api.get('/agent-runs', { params }).then(res => res.data);
export const getAgentRun = (id) => api.get(`/agent-runs/${id}`).then(res => res.data);

export const getViolations = () => api.get('/governance/violations').then(res => res.data);
export const getPolicies = () => api.get('/governance/policies').then(res => res.data);
export const getGovernanceSummary = () => api.get('/governance/summary').then(res => res.data);
"""

files["src/components/Sidebar.jsx"] = """import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span style={{fontSize: '24px'}}>🛡️</span>
        <div style={{display: 'flex', flexDirection: 'column'}}>
          <span className="brand">FLYYY.AI</span>
          <span className="sub">AI Governance</span>
        </div>
      </div>
      <div className="nav-links">
        <NavLink to="/" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'} end>
          📊 Overview
        </NavLink>
        <NavLink to="/assets" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
          🤖 AI Assets
        </NavLink>
        <NavLink to="/prompts" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
          💬 Prompt Monitor
        </NavLink>
        <NavLink to="/agent-runs" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
          ⚡️ Agent Runs
        </NavLink>
        <NavLink to="/governance" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
          ⚖️ Governance
        </NavLink>
      </div>
      <div className="sidebar-footer">
        <span className="version-badge">v1.0 · POC</span>
      </div>
    </aside>
  );
};

export default Sidebar;
"""

files["src/components/StatCard.jsx"] = """import React from 'react';

const StatCard = ({ title, value, icon, trend, accentColor = '#6366f1' }) => {
  return (
    <div className="card stat-card" style={{'--accent-gradient': accentColor}}>
      <div className="stat-card-header">
        <span className="stat-card-title">{title}</span>
        <span style={{fontSize: '20px'}}>{icon}</span>
      </div>
      <div className="stat-card-value">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      {trend && (
        <div style={{marginTop: '12px', fontSize: '12px', color: 'var(--text-muted)'}}>
          {trend}
        </div>
      )}
    </div>
  );
};

export default StatCard;
"""

files["src/components/PIIBadge.jsx"] = """import React from 'react';

const COLORS = {
  NAME: { bg: 'rgba(99,102,241,0.1)', color: '#818cf8', border: 'rgba(99,102,241,0.3)' },
  PHONE: { bg: 'rgba(168,85,247,0.1)', color: '#c084fc', border: 'rgba(168,85,247,0.3)' },
  EMAIL: { bg: 'rgba(6,182,212,0.1)', color: '#22d3ee', border: 'rgba(6,182,212,0.3)' },
  PAN: { bg: 'rgba(249,115,22,0.1)', color: '#fb923c', border: 'rgba(249,115,22,0.3)' },
  AADHAAR: { bg: 'rgba(239,68,68,0.1)', color: '#f87171', border: 'rgba(239,68,68,0.3)' },
  CREDIT_CARD: { bg: 'rgba(236,72,153,0.1)', color: '#f472b6', border: 'rgba(236,72,153,0.3)' },
  DEFAULT: { bg: 'rgba(148,163,184,0.1)', color: '#94a3b8', border: 'rgba(148,163,184,0.3)' }
};

const PIIBadge = ({ type, count }) => {
  const style = COLORS[type] || COLORS.DEFAULT;
  return (
    <span className="pii-pill" style={{
      backgroundColor: style.bg,
      color: style.color,
      border: `1px solid ${style.border}`
    }}>
      {type} {count !== undefined && `(${count})`}
    </span>
  );
};

export default PIIBadge;
"""

files["src/components/LoadingSpinner.jsx"] = """import React from 'react';

const LoadingSpinner = () => (
  <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '40px'}}>
    <div className="spinner"></div>
  </div>
);

export default LoadingSpinner;
"""

files["src/components/ErrorBanner.jsx"] = """import React from 'react';

const ErrorBanner = ({ message }) => (
  <div style={{
    padding: '16px',
    backgroundColor: 'var(--danger-bg)',
    color: 'var(--danger)',
    border: '1px solid rgba(239,68,68,0.3)',
    borderRadius: 'var(--radius-sm)',
    marginBottom: '24px'
  }}>
    ⚠️ {message}
  </div>
);

export default ErrorBanner;
"""

files["src/App.jsx"] = """import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import AIAssets from './pages/AIAssets';
import AssetDetail from './pages/AssetDetail';
import PromptMonitor from './pages/PromptMonitor';
import AgentRuns from './pages/AgentRuns';
import AgentRunDetail from './pages/AgentRunDetail';
import Governance from './pages/Governance';

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/assets" element={<AIAssets />} />
            <Route path="/assets/:id" element={<AssetDetail />} />
            <Route path="/prompts" element={<PromptMonitor />} />
            <Route path="/agent-runs" element={<AgentRuns />} />
            <Route path="/agent-runs/:id" element={<AgentRunDetail />} />
            <Route path="/governance" element={<Governance />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
"""

files["src/pages/Overview.jsx"] = """import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { getOverview, getUsageOverTime, getPIIByAsset, getPIITypes, getAgentStats } from '../services/api';
import StatCard from '../components/StatCard';
import PIIBadge from '../components/PIIBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b'];

const Overview = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      getOverview().catch(() => ({ assets_count: 0, interactions_count: 0, pii_incidents_count: 0, violations_count: 0 })),
      getUsageOverTime().catch(() => []),
      getPIIByAsset().catch(() => []),
      getPIITypes().catch(() => ({})),
      getAgentStats().catch(() => ({ total_runs: 0, compliant_runs: 0, violation_runs: 0 }))
    ]).then(([overview, usage, piiAsset, piiTypes, agentStats]) => {
      setData({ overview, usage, piiAsset, piiTypes, agentStats });
      setLoading(false);
    }).catch(err => {
      setError(err.message);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorBanner message={error} />;

  const pieData = [
    { name: 'Compliant', value: data.agentStats.compliant_runs },
    { name: 'Violations', value: data.agentStats.violation_runs }
  ];

  return (
    <div className="page-fade-in">
      <div className="page-header">
        <div>
          <h1>Overview</h1>
          <p>Global view of AI usage and governance posture</p>
        </div>
      </div>

      <div className="grid-4" style={{marginBottom: '32px'}}>
        <StatCard title="Total AI Assets" value={data.overview.assets_count} icon="🤖" />
        <StatCard title="Interactions" value={data.overview.interactions_count} icon="💬" accentColor="#38bdf8" />
        <StatCard title="PII Incidents" value={data.overview.pii_incidents_count} icon="🔐" accentColor="#f59e0b" />
        <StatCard title="Policy Violations" value={data.overview.violations_count} icon="⚠️" accentColor="#ef4444" />
      </div>

      <div className="grid-2" style={{marginBottom: '32px'}}>
        <div className="card">
          <h3 style={{marginBottom: '24px'}}>AI Interactions (7 Days)</h3>
          <div style={{height: '300px'}}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.usage}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Area type="monotone" dataKey="count" stroke="#6366f1" fillOpacity={1} fill="url(#colorCount)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card">
          <h3 style={{marginBottom: '24px'}}>PII Exposure by Asset</h3>
          <div style={{height: '300px'}}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.piiAsset}>
                <XAxis dataKey="asset_name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Bar dataKey="total_pii" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 style={{marginBottom: '24px'}}>Detected PII Types</h3>
          <div style={{display: 'flex', flexWrap: 'wrap', gap: '8px'}}>
            {Object.entries(data.piiTypes).map(([type, count]) => (
              <PIIBadge key={type} type={type} count={count} />
            ))}
          </div>
        </div>
        <div className="card">
          <h3 style={{marginBottom: '24px'}}>Agent Governance Summary</h3>
          <div style={{height: '200px', display: 'flex', alignItems: 'center'}}>
            <ResponsiveContainer width="50%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  <Cell fill="#10b981" />
                  <Cell fill="#ef4444" />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div style={{flex: 1}}>
              <div style={{marginBottom: '16px'}}>
                <span className="badge success" style={{marginBottom: '8px'}}>Compliant</span>
                <div style={{fontSize: '24px', fontWeight: 'bold'}}>{data.agentStats.compliant_runs}</div>
              </div>
              <div>
                <span className="badge danger" style={{marginBottom: '8px'}}>Violations</span>
                <div style={{fontSize: '24px', fontWeight: 'bold'}}>{data.agentStats.violation_runs}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Overview;
"""

files["src/pages/AIAssets.jsx"] = """import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAssets } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';

const AIAssets = () => {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    getAssets()
      .then(data => { setAssets(data); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); });
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorBanner message={error} />;

  return (
    <div className="page-fade-in">
      <div className="page-header">
        <div>
          <h1>AI Assets</h1>
          <p>Manage and monitor all deployed AI models and agents.</p>
        </div>
      </div>
      <div className="grid-3">
        {assets.map(asset => (
          <div className="card" key={asset.id} onClick={() => navigate(`/assets/${asset.id}`)} style={{cursor: 'pointer'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '16px'}}>
              <h3 style={{fontSize: '18px', fontWeight: '600'}}>{asset.name}</h3>
              <span className={`badge ${asset.type === 'AGENT' ? 'info' : 'warning'}`}>{asset.type}</span>
            </div>
            <div style={{fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '16px'}}>
              {asset.provider} · {asset.model}
            </div>
            <div style={{marginBottom: '16px'}}>
              {asset.prompt_monitoring ? 
                <span className="badge success">🟢 Monitored</span> : 
                <span className="badge danger">🔴 Not Monitored</span>}
            </div>
            <div style={{fontSize: '14px', color: 'var(--text-muted)'}}>
              <p>Interactions: {asset.interactions_count || 0}</p>
              <p>PII Incidents: {asset.pii_incidents_count || 0}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AIAssets;
"""

files["src/pages/AssetDetail.jsx"] = """import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getAsset, updateAsset, getInteractions, getAgentRuns } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import PIIBadge from '../components/PIIBadge';

const AssetDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [interactions, setInteractions] = useState([]);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      getAsset(id),
      getInteractions({ asset_id: id, limit: 10 }),
      getAgentRuns({ asset_id: id, limit: 10 })
    ]).then(([assetData, ints, agentRuns]) => {
      setData(assetData);
      setInteractions(ints);
      setRuns(agentRuns);
      setLoading(false);
    }).catch(err => {
      setError(err.message);
      setLoading(false);
    });
  }, [id]);

  const toggleMonitoring = async () => {
    try {
      const updated = await updateAsset(id, { prompt_monitoring: !data.prompt_monitoring });
      setData(prev => ({ ...prev, prompt_monitoring: updated.prompt_monitoring }));
    } catch(e) {
      alert("Failed to update asset.");
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorBanner message={error} />;

  return (
    <div className="page-fade-in">
      <button className="btn" onClick={() => navigate(-1)} style={{marginBottom: '24px'}}>← Back</button>
      
      <div className="card" style={{marginBottom: '32px'}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div>
            <h1 style={{fontSize: '28px', marginBottom: '8px'}}>{data.name} <span className={`badge ${data.type === 'AGENT' ? 'info' : 'warning'}`}>{data.type}</span></h1>
            <p style={{color: 'var(--text-secondary)'}}>{data.description}</p>
          </div>
          <div>
            <button className="btn-primary" onClick={toggleMonitoring}>
              {data.prompt_monitoring ? 'Disable Monitoring' : 'Enable Monitoring'}
            </button>
          </div>
        </div>
        <div style={{marginTop: '24px', display: 'flex', gap: '24px', color: 'var(--text-muted)', fontSize: '14px'}}>
          <p>Provider: {data.provider}</p>
          <p>Model: {data.model}</p>
          <p>Retention: {data.retention_days} days</p>
        </div>
      </div>

      <div className="grid-2" style={{marginBottom: '32px'}}>
         <div className="card">
           <h3>Stats</h3>
           <div style={{marginTop: '16px'}}>
             <p>Total Interactions: <strong>{data.interactions_count || 0}</strong></p>
             <p>PII Incidents: <strong>{data.pii_incidents_count || 0}</strong></p>
           </div>
         </div>
      </div>

      <h3>Recent Interactions</h3>
      <div className="table-container" style={{marginTop: '16px', marginBottom: '32px'}}>
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Prompt Preview</th>
              <th>PII Detected</th>
            </tr>
          </thead>
          <tbody>
            {interactions.map(int => (
              <tr key={int.id}>
                <td>{new Date(int.timestamp).toLocaleString()}</td>
                <td>{int.sanitized_prompt ? int.sanitized_prompt.substring(0, 80) + '...' : '⊘ Not stored'}</td>
                <td>
                  {(int.pii_detected || []).map(p => (
                    <PIIBadge key={p.type} type={p.type} />
                  ))}
                </td>
              </tr>
            ))}
            {interactions.length === 0 && <tr><td colSpan="3" style={{textAlign: 'center', color: 'var(--text-muted)'}}>No interactions found</td></tr>}
          </tbody>
        </table>
      </div>

      {data.type === 'AGENT' && (
        <>
          <h3>Recent Agent Runs</h3>
          <div className="table-container" style={{marginTop: '16px'}}>
            <table>
              <thead>
                <tr>
                  <th>Run ID</th>
                  <th>Started</th>
                  <th>Status</th>
                  <th>Governance</th>
                </tr>
              </thead>
              <tbody>
                {runs.map(run => (
                  <tr key={run.id} onClick={() => navigate(`/agent-runs/${run.id}`)} style={{cursor: 'pointer'}}>
                    <td>{run.id.substring(0,8)}</td>
                    <td>{new Date(run.started_at).toLocaleString()}</td>
                    <td>{run.status}</td>
                    <td>
                      {run.violation ? <span className="badge danger">⚠ VIOLATION</span> : <span className="badge success">✓ COMPLIANT</span>}
                    </td>
                  </tr>
                ))}
                {runs.length === 0 && <tr><td colSpan="4" style={{textAlign: 'center', color: 'var(--text-muted)'}}>No agent runs found</td></tr>}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default AssetDetail;
"""

files["src/pages/PromptMonitor.jsx"] = """import React, { useEffect, useState } from 'react';
import { getInteractions, getPIISummary, getAssets } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import PIIBadge from '../components/PIIBadge';

const PromptMonitor = () => {
  const [interactions, setInteractions] = useState([]);
  const [summary, setSummary] = useState({});
  const [assets, setAssets] = useState([]);
  const [assetFilter, setAssetFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      getInteractions({ asset_id: assetFilter, limit: 50 }),
      getPIISummary({ asset_id: assetFilter }),
      getAssets()
    ]).then(([ints, sum, asts]) => {
      setInteractions(ints);
      setSummary(sum);
      setAssets(asts);
      setLoading(false);
    }).catch(err => {
      setError(err.message);
      setLoading(false);
    });
  };

  useEffect(() => {
    fetchData();
  }, [assetFilter]);

  if (loading && interactions.length === 0) return <LoadingSpinner />;
  if (error) return <ErrorBanner message={error} />;

  return (
    <div className="page-fade-in">
      <div className="page-header">
        <div>
          <h1>Prompt Monitor</h1>
          <p>Real-time stream of sanitized AI interactions and PII detection.</p>
        </div>
        <select value={assetFilter} onChange={e => setAssetFilter(e.target.value)} style={{padding: '8px', background: 'var(--bg-secondary)', color: 'white', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)'}}>
          <option value="">All Assets</option>
          {assets.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
        </select>
      </div>

      <div style={{background: 'var(--info)', color: '#000', padding: '12px 16px', borderRadius: 'var(--radius-sm)', marginBottom: '24px', fontWeight: '500', fontSize: '14px'}}>
        🛡️ Privacy notice: Raw prompts are never stored. All content shown is PII-sanitized.
      </div>

      <div className="grid-4" style={{marginBottom: '24px'}}>
        {Object.entries(summary).map(([type, count]) => (
           <div className="card" key={type} style={{padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
             <span style={{fontWeight: '600'}}>{type}</span>
             <span className="badge info">{count}</span>
           </div>
        ))}
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Sanitized Prompt</th>
              <th>PII Detected</th>
              <th>Tokens</th>
              <th>Latency</th>
            </tr>
          </thead>
          <tbody>
            {interactions.map(int => (
              <tr key={int.id}>
                <td>{new Date(int.timestamp).toLocaleString()}</td>
                <td>{int.sanitized_prompt ? int.sanitized_prompt.substring(0, 80) + '...' : <span style={{color: 'var(--text-muted)'}}>⊘ Not stored (monitoring disabled)</span>}</td>
                <td>
                  {(int.pii_detected || []).map(p => (
                    <PIIBadge key={p.type} type={p.type} />
                  ))}
                </td>
                <td>{int.tokens || '-'}</td>
                <td>{int.latency_ms ? `${int.latency_ms}ms` : '-'}</td>
              </tr>
            ))}
            {interactions.length === 0 && <tr><td colSpan="5" style={{textAlign: 'center', padding: '24px'}}>No interactions found</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PromptMonitor;
"""

files["src/pages/AgentRuns.jsx"] = """import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAgentRuns, getAgentStats } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import StatCard from '../components/StatCard';

const AgentRuns = () => {
  const [runs, setRuns] = useState([]);
  const [stats, setStats] = useState({});
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      getAgentRuns(filter === 'violation' ? { violation: true } : {}),
      getAgentStats()
    ]).then(([runsData, statsData]) => {
      setRuns(runsData);
      setStats(statsData);
      setLoading(false);
    }).catch(err => {
      setError(err.message);
      setLoading(false);
    });
  }, [filter]);

  if (loading && runs.length === 0) return <LoadingSpinner />;
  if (error) return <ErrorBanner message={error} />;

  const rate = stats.total_runs ? ((stats.violation_runs / stats.total_runs) * 100).toFixed(1) : 0;

  return (
    <div className="page-fade-in">
      <div className="page-header">
        <div>
          <h1>Agent Runs</h1>
          <p>Trace agent executions, tool calls, and verify access scopes.</p>
        </div>
        <div style={{display: 'flex', gap: '8px'}}>
          <button className={`btn ${filter==='all'?'btn-primary':''}`} onClick={()=>setFilter('all')}>All</button>
          <button className={`btn ${filter==='violation'?'btn-primary':''}`} onClick={()=>setFilter('violation')}>Violations</button>
        </div>
      </div>

      <div className="grid-4" style={{marginBottom: '32px'}}>
        <StatCard title="Total Runs" value={stats.total_runs || 0} />
        <StatCard title="Compliant" value={stats.compliant_runs || 0} accentColor="#10b981" />
        <StatCard title="Violations" value={stats.violation_runs || 0} accentColor="#ef4444" />
        <StatCard title="Violation Rate" value={`${rate}%`} accentColor="#f59e0b" />
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Run ID</th>
              <th>Started</th>
              <th>Status</th>
              <th>Governance</th>
            </tr>
          </thead>
          <tbody>
            {runs.map(run => (
              <tr key={run.id} onClick={() => navigate(`/agent-runs/${run.id}`)} style={{cursor: 'pointer'}}>
                <td>{run.id.substring(0,8)}</td>
                <td>{new Date(run.started_at).toLocaleString()}</td>
                <td>{run.status}</td>
                <td>
                  {run.violation ? <span className="badge danger">⚠ VIOLATION</span> : <span className="badge success">✓ COMPLIANT</span>}
                </td>
              </tr>
            ))}
            {runs.length === 0 && <tr><td colSpan="4" style={{textAlign: 'center'}}>No runs found</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AgentRuns;
"""

files["src/pages/AgentRunDetail.jsx"] = """import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getAgentRun } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';

const AgentRunDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [run, setRun] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getAgentRun(id)
      .then(data => { setRun(data); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); });
  }, [id]);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorBanner message={error} />;
  if (!run) return <div>No data</div>;

  return (
    <div className="page-fade-in">
      <button className="btn" onClick={() => navigate(-1)} style={{marginBottom: '24px'}}>← Back</button>
      
      <div style={{marginBottom: '24px'}}>
        <h1 style={{fontSize: '24px', marginBottom: '8px'}}>Run {run.id}</h1>
        <p style={{color: 'var(--text-secondary)'}}>Started at: {new Date(run.started_at).toLocaleString()}</p>
      </div>

      {run.violation ? (
        <div className="violation-banner">
          <span style={{fontSize: '24px'}}>⚠️</span>
          <div>
            <h4 style={{color: 'var(--danger)', marginBottom: '4px'}}>POLICY VIOLATION</h4>
            <p style={{fontSize: '14px'}}>{run.violation_reason || 'Unexpected access to unauthorized source.'}</p>
          </div>
        </div>
      ) : (
        <div className="compliant-banner">
          <span style={{fontSize: '24px'}}>✓</span>
          <div>
            <h4 style={{color: 'var(--success)', marginBottom: '4px'}}>COMPLIANT</h4>
            <p style={{fontSize: '14px'}}>All accesses within declared scope.</p>
          </div>
        </div>
      )}

      <div className="declared-observed-grid" style={{marginBottom: '32px'}}>
        <div className="do-col">
          <div className="do-header">DECLARED SOURCES</div>
          {(run.declared_sources || []).map((src, i) => (
            <div className="do-item" key={i}>
              <span style={{color: 'var(--success)'}}>✓</span>
              {src}
            </div>
          ))}
          {(!run.declared_sources || run.declared_sources.length === 0) && <div style={{color: 'var(--text-muted)'}}>None</div>}
        </div>
        <div className="do-col">
          <div className="do-header">OBSERVED SOURCES</div>
          {(run.observed_sources || []).map((src, i) => {
            const isUnexpected = !(run.declared_sources || []).includes(src);
            return (
              <div className="do-item" key={i} style={isUnexpected ? {borderColor: 'var(--danger)', background: 'var(--danger-bg)'} : {}}>
                {isUnexpected ? <span style={{color: 'var(--danger)'}}>⚠</span> : <span style={{color: 'var(--success)'}}>✓</span>}
                {src}
              </div>
            );
          })}
          {(!run.observed_sources || run.observed_sources.length === 0) && <div style={{color: 'var(--text-muted)'}}>None</div>}
        </div>
      </div>

      <h3>Access Events</h3>
      <div className="table-container" style={{marginTop: '16px'}}>
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Source</th>
              <th>Operation</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {(run.access_events || []).map((ev, i) => (
              <tr key={i}>
                <td>{new Date(ev.timestamp).toLocaleString()}</td>
                <td>{ev.source}</td>
                <td>{ev.operation}</td>
                <td>
                  <span className={`badge ${ev.status === 'BLOCKED' ? 'danger' : 'success'}`}>{ev.status}</span>
                </td>
              </tr>
            ))}
            {(!run.access_events || run.access_events.length === 0) && <tr><td colSpan="4" style={{textAlign: 'center'}}>No access events recorded.</td></tr>}
          </tbody>
        </table>
      </div>
      
      {run.trace_id && (
        <div className="card" style={{marginTop: '32px'}}>
          <h4 style={{marginBottom: '8px'}}>OpenTelemetry Trace</h4>
          <p style={{fontSize: '14px', color: 'var(--text-muted)', marginBottom: '12px'}}>This execution is linked to a distributed trace for deeper observability.</p>
          <div style={{display: 'flex', gap: '8px', alignItems: 'center'}}>
            <code style={{background: 'var(--bg-secondary)', padding: '8px 12px', borderRadius: '4px', border: '1px solid var(--border)'}}>{run.trace_id}</code>
            <button className="btn" onClick={() => navigator.clipboard.writeText(run.trace_id)}>Copy</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentRunDetail;
"""

files["src/pages/Governance.jsx"] = """import React, { useEffect, useState } from 'react';
import { getGovernanceSummary, getViolations, getPolicies } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import StatCard from '../components/StatCard';
import { useNavigate } from 'react-router-dom';

const Governance = () => {
  const [summary, setSummary] = useState(null);
  const [violations, setViolations] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      getGovernanceSummary(),
      getViolations(),
      getPolicies()
    ]).then(([sum, viols, pols]) => {
      setSummary(sum);
      setViolations(viols);
      setPolicies(pols);
      setLoading(false);
    }).catch(err => {
      setError(err.message);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorBanner message={error} />;

  return (
    <div className="page-fade-in">
      <div className="page-header">
        <div>
          <h1>Governance</h1>
          <p>Centralized policy management and violation tracking.</p>
        </div>
      </div>

      <div className="grid-4" style={{marginBottom: '32px'}}>
        <StatCard title="Total Violations" value={summary.total || 0} accentColor="#ef4444" />
        <StatCard title="PII Exposure" value={summary.by_type?.PII_EXPOSURE || 0} accentColor="#f59e0b" />
        <StatCard title="Unexpected DB Access" value={summary.by_type?.UNEXPECTED_DB_ACCESS || 0} accentColor="#f59e0b" />
        <StatCard title="Unmonitored Assets" value={summary.by_type?.UNMONITORED_ASSETS || 0} accentColor="#6366f1" />
      </div>

      <h3>Recent Violations</h3>
      <div className="table-container" style={{marginTop: '16px', marginBottom: '32px'}}>
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Agent / Run</th>
              <th>Details</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {violations.map((v, i) => (
              <tr key={i} onClick={() => v.run_id && navigate(`/agent-runs/${v.run_id}`)} style={{cursor: v.run_id ? 'pointer' : 'default'}}>
                <td>{new Date(v.timestamp).toLocaleString()}</td>
                <td>{v.agent_name || v.asset_name} {v.run_id && `(${v.run_id.substring(0,8)})`}</td>
                <td>{v.details || v.reason}</td>
                <td><span className="badge danger">VIOLATION</span></td>
              </tr>
            ))}
            {violations.length === 0 && <tr><td colSpan="4" style={{textAlign: 'center'}}>No violations. Great job!</td></tr>}
          </tbody>
        </table>
      </div>

      <h3>Asset Policies</h3>
      <div className="table-container" style={{marginTop: '16px', marginBottom: '32px'}}>
        <table>
          <thead>
            <tr>
              <th>Asset</th>
              <th>Allowed Sources</th>
              <th>Allowed PII Types</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {policies.map((p, i) => (
              <tr key={i}>
                <td>{p.asset_name}</td>
                <td>{(p.allowed_sources || []).map(s => <span className="tag" key={s}>{s}</span>)}</td>
                <td>{(p.allowed_pii || []).map(t => <span className="tag" key={t}>{t}</span>)}</td>
                <td>
                  <span className={`badge ${p.active !== false ? 'success' : 'warning'}`}>
                    {p.active !== false ? 'Active' : 'No policy'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="card" style={{marginTop: '32px', background: 'linear-gradient(to right, rgba(15,23,42,1), rgba(30,41,59,1))'}}>
        <h3 style={{marginBottom: '16px', color: 'var(--info)'}}>🔍 Observability Depth Research</h3>
        <p style={{fontSize: '14px', marginBottom: '16px', color: 'var(--text-secondary)'}}>
          Comparison of telemetry collection strategies for AI Governance platforms.
        </p>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Capability</th>
                <th>Zero-code (Network)</th>
                <th>Gateway (Proxy)</th>
                <th>App Instrumentation (SDK)</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>AI service</td><td>✅</td><td>✅</td><td>✅</td></tr>
              <tr><td>Model</td><td>✅</td><td>✅</td><td>✅</td></tr>
              <tr><td>Prompt</td><td>✅</td><td>✅</td><td>✅</td></tr>
              <tr><td>Token usage</td><td>⚠️ (estimated)</td><td>✅</td><td>✅</td></tr>
              <tr><td>LLM latency</td><td>✅</td><td>✅</td><td>✅</td></tr>
              <tr><td>Tool calls</td><td>❌</td><td>❌</td><td>✅</td></tr>
              <tr><td>Agent execution</td><td>❌</td><td>❌</td><td>✅</td></tr>
              <tr><td>Database access</td><td>✅</td><td>❌</td><td>✅</td></tr>
              <tr><td>Declared sources</td><td>❌</td><td>❌</td><td>✅</td></tr>
              <tr><td>Governance violations</td><td>⚠️ (partial)</td><td>⚠️ (partial)</td><td>✅ (comprehensive)</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Governance;
"""

for filepath, content in files.items():
    with open(os.path.join(base_dir, filepath), "w", encoding="utf-8") as f:
        f.write(content)

print("All frontend files generated successfully!")
