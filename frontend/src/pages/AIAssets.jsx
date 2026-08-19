import React, { useEffect, useState } from 'react';
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
