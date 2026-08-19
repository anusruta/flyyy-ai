import React, { useEffect, useState } from 'react';
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
        <StatCard title="Total AI Assets" value={data.overview.total_assets} icon="🤖" />
        <StatCard title="Interactions" value={data.overview.total_interactions} icon="💬" accentColor="#38bdf8" />
        <StatCard title="PII Incidents" value={data.overview.total_pii_incidents} icon="🔐" accentColor="#f59e0b" />
        <StatCard title="Policy Violations" value={data.overview.total_violations} icon="⚠️" accentColor="#ef4444" />
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
                <Area type="monotone" dataKey="interactions" stroke="#6366f1" fillOpacity={1} fill="url(#colorCount)" />
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
                <Bar dataKey="pii_count" name="PII Events" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 style={{marginBottom: '24px'}}>Detected PII Types</h3>
          <div style={{display: 'flex', flexWrap: 'wrap', gap: '8px'}}>
            {(Array.isArray(data.piiTypes) ? data.piiTypes : Object.entries(data.piiTypes).map(([type, count]) => ({type, count}))).map((item) => (
              <PIIBadge key={item.type} type={item.type} count={item.count} />
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
