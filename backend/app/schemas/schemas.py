from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class PolicyCreate(BaseModel):
    allowed_sources: List[str] = []
    allowed_pii_types: List[str] = []

class PolicyResponse(BaseModel):
    id: str
    asset_id: str
    allowed_sources: List[str]
    allowed_pii_types: List[str]

    model_config = ConfigDict(from_attributes=True)

class AssetCreate(BaseModel):
    name: str
    type: str
    provider: Optional[str] = None
    model: Optional[str] = None
    declared_purpose: Optional[str] = None
    prompt_monitoring: bool = True
    retention_days: int = 30
    policy: Optional[PolicyCreate] = None

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    declared_purpose: Optional[str] = None
    prompt_monitoring: Optional[bool] = None
    retention_days: Optional[int] = None

class AssetResponse(BaseModel):
    id: str
    name: str
    type: str
    provider: Optional[str]
    model: Optional[str]
    declared_purpose: Optional[str]
    prompt_monitoring: bool
    retention_days: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AssetDetail(AssetResponse):
    interactions_count: int = 0
    pii_incidents_count: int = 0
    policy: Optional[PolicyResponse] = None

class InteractionCreate(BaseModel):
    asset_id: str
    user_id: Optional[str] = None
    prompt: Optional[str] = None
    model: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_ms: Optional[int] = None
    status: str = "success"
    trace_id: Optional[str] = None

class InteractionResponse(BaseModel):
    id: str
    asset_id: str
    timestamp: datetime
    user_id: Optional[str]
    sanitized_prompt: Optional[str]
    pii_detected: Dict[str, int]
    model: Optional[str]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    latency_ms: Optional[int]
    status: str
    trace_id: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class AgentRunCreate(BaseModel):
    asset_id: str
    declared_sources: List[str] = []
    trace_id: Optional[str] = None
    user_id: Optional[str] = None

class AgentRunResponse(BaseModel):
    id: str
    asset_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    status: str
    declared_sources: List[str]
    observed_sources: List[str]
    violation: bool
    trace_id: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class AccessEventCreate(BaseModel):
    source_name: str
    operation: str = "SELECT"
    status: str = "success"

class AccessEventResponse(BaseModel):
    id: str
    run_id: str
    timestamp: datetime
    source_name: str
    operation: str
    status: str

    model_config = ConfigDict(from_attributes=True)

class AgentRunDetail(AgentRunResponse):
    access_events: List[AccessEventResponse]
    governance_result: Optional[Dict[str, Any]] = None
    asset_name: Optional[str] = None

class OverviewStats(BaseModel):
    total_assets: int
    total_interactions: int
    total_pii_incidents: int
    total_violations: int

class PIIBreakdown(BaseModel):
    type: str
    count: int

class UsageTrendPoint(BaseModel):
    date: str
    interactions: int

class GovernanceViolation(BaseModel):
    run_id: str
    asset_name: str
    started_at: datetime
    unexpected_sources: List[str]
