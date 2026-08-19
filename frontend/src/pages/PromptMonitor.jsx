import React, { useEffect, useState } from 'react';
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
