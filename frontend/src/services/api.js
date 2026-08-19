import axios from 'axios';

// On Railway: set VITE_API_URL=https://your-backend.up.railway.app in frontend service variables
// Locally: falls back to /api (proxied by nginx)
const BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: BASE_URL
});

// Analytics — no trailing slash (matches FastAPI route definitions)
export const getOverview = () => api.get('/analytics/overview').then(res => res.data);
export const getUsageOverTime = () => api.get('/analytics/usage-over-time').then(res => res.data);
export const getPIIByAsset = () => api.get('/analytics/pii-by-asset').then(res => res.data);
export const getPIITypes = () => api.get('/analytics/pii-types').then(res => res.data);
export const getAgentStats = () => api.get('/analytics/agent-stats').then(res => res.data);

// Assets
export const getAssets = () => api.get('/assets/').then(res => res.data);
export const getAsset = (id) => api.get(`/assets/${id}`).then(res => res.data);
export const createAsset = (data) => api.post('/assets/', data).then(res => res.data);
export const updateAsset = (id, data) => api.patch(`/assets/${id}`, data).then(res => res.data);
export const getAssetPolicy = (id) => api.get(`/assets/${id}/policy`).then(res => res.data);
export const updateAssetPolicy = (id, data) => api.put(`/assets/${id}/policy`, data).then(res => res.data);

// Interactions
export const getInteractions = (params) => api.get('/interactions/', { params }).then(res => res.data);
export const getPIISummary = (params) => api.get('/interactions/pii-summary', { params }).then(res => res.data);

// Agent Runs
export const getAgentRuns = (params) => api.get('/agent-runs/', { params }).then(res => res.data);
export const getAgentRun = (id) => api.get(`/agent-runs/${id}`).then(res => res.data);

// Governance
export const getViolations = () => api.get('/governance/violations').then(res => res.data);
export const getPolicies = () => api.get('/governance/policies').then(res => res.data);
export const getGovernanceSummary = () => api.get('/governance/summary').then(res => res.data);
