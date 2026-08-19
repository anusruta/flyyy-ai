import React from 'react';

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
