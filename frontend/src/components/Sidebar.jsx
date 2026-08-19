import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span style={{fontSize: '24px'}}>🛡️</span>
        <div style={{display: 'flex', flexDirection: 'column'}}>
          <span className="brand">FLYYY.AI</span>
          <span className="sub">AI Governance</span>
        </div>
      </div>
      <div className="nav-links">
        <NavLink to="/" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'} end>
          📊 Overview
        </NavLink>
        <NavLink to="/assets" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
          🤖 AI Assets
        </NavLink>
        <NavLink to="/prompts" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
          💬 Prompt Monitor
        </NavLink>
        <NavLink to="/agent-runs" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
          ⚡️ Agent Runs
        </NavLink>
        <NavLink to="/governance" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
          ⚖️ Governance
        </NavLink>
      </div>
      <div className="sidebar-footer">
        <span className="version-badge">v1.0 · POC</span>
      </div>
    </aside>
  );
};

export default Sidebar;
