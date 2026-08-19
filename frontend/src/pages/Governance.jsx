import React, { useEffect, useState } from 'react';
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
        <StatCard title="Total Violations" value={summary.total_violations || 0} accentColor="#ef4444" />
        <StatCard title="PII Exposure" value={summary.breakdown?.PII_EXPOSURE || 0} accentColor="#f59e0b" />
        <StatCard title="Unexpected DB Access" value={summary.breakdown?.UNEXPECTED_DB_ACCESS || 0} accentColor="#f59e0b" />
        <StatCard title="Unmonitored Assets" value={summary.breakdown?.UNMONITORED_ASSETS || 0} accentColor="#6366f1" />
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
                <td>{new Date(v.started_at).toLocaleString()}</td>
                <td>{v.asset_name} <span style={{color:'var(--text-muted)',fontSize:'12px'}}>({(v.run_id||'').substring(0,8)}...)</span></td>
                <td style={{color:'var(--danger)'}}>
                  ⚠ Unexpected: {(v.unexpected_sources || []).join(', ')}
                </td>
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
