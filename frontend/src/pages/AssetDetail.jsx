import React, { useEffect, useState } from 'react';
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
