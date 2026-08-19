import React, { useEffect, useState } from 'react';
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
            <p style={{fontSize: '14px'}}>
              Unexpected access to:{' '}
              <strong>{(run.governance_result?.unexpected_sources || []).join(', ') || 'unauthorized source'}</strong>
            </p>
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
            {(run.access_events || []).map((ev, i) => {
              const isUnexpected = !(run.declared_sources || []).map(s => s.toUpperCase()).includes((ev.source_name || '').toUpperCase());
              return (
                <tr key={i} style={isUnexpected ? {background: 'rgba(239,68,68,0.05)'} : {}}>
                  <td>{new Date(ev.timestamp).toLocaleString()}</td>
                  <td style={isUnexpected ? {color: 'var(--danger)', fontWeight: 600} : {}}>
                    {isUnexpected && '⚠ '}{ev.source_name}
                  </td>
                  <td>{ev.operation}</td>
                  <td>
                    <span className={`badge ${ev.status === 'error' ? 'danger' : 'success'}`}>{ev.status}</span>
                  </td>
                </tr>
              );
            })}
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
