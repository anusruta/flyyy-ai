import React, { useEffect, useState } from 'react';
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
