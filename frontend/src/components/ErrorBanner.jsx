import React from 'react';

const ErrorBanner = ({ message }) => (
  <div style={{
    padding: '16px',
    backgroundColor: 'var(--danger-bg)',
    color: 'var(--danger)',
    border: '1px solid rgba(239,68,68,0.3)',
    borderRadius: 'var(--radius-sm)',
    marginBottom: '24px'
  }}>
    ⚠️ {message}
  </div>
);

export default ErrorBanner;
