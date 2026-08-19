import React from 'react';

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
