import React from 'react';
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
