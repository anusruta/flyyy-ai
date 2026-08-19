import uuid
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class AIAsset(Base):
    __tablename__ = "ai_assets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False) # 'llm' or 'agent'
    provider = Column(String(100))
    model = Column(String(100))
    declared_purpose = Column(Text)
    prompt_monitoring = Column(Boolean, default=True)
    retention_days = Column(Integer, default=30)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    interactions = relationship("AIInteraction", back_populates="asset", cascade="all, delete")
    agent_runs = relationship("AgentRun", back_populates="asset", cascade="all, delete")
    policy = relationship("Policy", back_populates="asset", uselist=False, cascade="all, delete")

class AIInteraction(Base):
    __tablename__ = "ai_interactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), ForeignKey("ai_assets.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String(255))
    sanitized_prompt = Column(Text, nullable=True)
    pii_detected = Column(JSON, default=dict)
    model = Column(String(100))
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    latency_ms = Column(Integer)
    status = Column(String(50), default="success")
    trace_id = Column(String(255))
    
    asset = relationship("AIAsset", back_populates="interactions")

class AgentRun(Base):
    __tablename__ = "agent_runs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), ForeignKey("ai_assets.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="running")
    declared_sources = Column(JSON, default=list)
    observed_sources = Column(JSON, default=list)
    violation = Column(Boolean, default=False)
    trace_id = Column(String(255))
    
    asset = relationship("AIAsset", back_populates="agent_runs")
    access_events = relationship("AccessEvent", back_populates="run", cascade="all, delete")

class AccessEvent(Base):
    __tablename__ = "access_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("agent_runs.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source_name = Column(String(255))
    operation = Column(String(50), default="SELECT")
    status = Column(String(50), default="success")
    
    run = relationship("AgentRun", back_populates="access_events")

class Policy(Base):
    __tablename__ = "policies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), ForeignKey("ai_assets.id"), unique=True, nullable=False)
    allowed_sources = Column(JSON, default=list)
    allowed_pii_types = Column(JSON, default=list)
    
    asset = relationship("AIAsset", back_populates="policy")
