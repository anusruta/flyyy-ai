from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone

from app.database import get_db
from app.models.models import AIAsset, AgentRun, AccessEvent, Policy
from app.schemas.schemas import AgentRunCreate, AgentRunResponse, AccessEventCreate, AccessEventResponse, AgentRunDetail
from app.services.governance import evaluate_agent_run

router = APIRouter()

@router.post("/", response_model=AgentRunResponse)
async def create_agent_run(run_in: AgentRunCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AIAsset).where(AIAsset.id == run_in.asset_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Asset not found")
        
    run = AgentRun(
        asset_id=run_in.asset_id,
        declared_sources=run_in.declared_sources,
        trace_id=run_in.trace_id,
        status="running",
        observed_sources=[],
        violation=False
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run

@router.post("/{id}/access-events", response_model=AccessEventResponse)
async def record_access_event(id: str, event_in: AccessEventCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentRun).where(AgentRun.id == id))
    run = result.scalars().first()
    if not run:
        raise HTTPException(status_code=404, detail="Agent run not found")
        
    event = AccessEvent(
        run_id=id,
        source_name=event_in.source_name,
        operation=event_in.operation,
        status=event_in.status
    )
    db.add(event)
    
    observed = list(run.observed_sources) if run.observed_sources else []
    if event_in.source_name not in observed:
        observed.append(event_in.source_name)
        run.observed_sources = observed
        
    await db.commit()
    await db.refresh(event)
    return event

@router.post("/{id}/complete", response_model=AgentRunDetail)
async def complete_agent_run(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AgentRun)
        .options(selectinload(AgentRun.access_events))
        .where(AgentRun.id == id)
    )
    run = result.scalars().first()
    if not run:
        raise HTTPException(status_code=404, detail="Agent run not found")
        
    # Get Policy to evaluate governance against allowed sources
    policy_result = await db.execute(select(Policy).where(Policy.asset_id == run.asset_id))
    policy = policy_result.scalars().first()
    
    # Evaluate governance - combine run declared sources with policy allowed sources
    allowed_sources = list(set(run.declared_sources + (policy.allowed_sources if policy else [])))
    governance = evaluate_agent_run(allowed_sources, run.observed_sources)
    
    run.ended_at = datetime.now(timezone.utc)
    run.status = "completed"
    run.violation = governance["violation"]
    
    await db.commit()
    await db.refresh(run)
    
    run_dict = {
        "id": run.id,
        "asset_id": run.asset_id,
        "started_at": run.started_at,
        "ended_at": run.ended_at,
        "status": run.status,
        "declared_sources": run.declared_sources,
        "observed_sources": run.observed_sources,
        "violation": run.violation,
        "trace_id": run.trace_id,
        "access_events": run.access_events,
        "governance_result": governance
    }
    return run_dict

@router.get("/", response_model=List[AgentRunResponse])
async def list_agent_runs(
    asset_id: Optional[str] = None,
    violation: Optional[bool] = None,
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(AgentRun).order_by(AgentRun.started_at.desc()).limit(limit).offset(offset)
    if asset_id:
        query = query.where(AgentRun.asset_id == asset_id)
    if violation is not None:
        query = query.where(AgentRun.violation == violation)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{id}", response_model=AgentRunDetail)
async def get_agent_run(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AgentRun)
        .options(selectinload(AgentRun.access_events))
        .where(AgentRun.id == id)
    )
    run = result.scalars().first()
    if not run:
        raise HTTPException(status_code=404, detail="Agent run not found")
        
    policy_result = await db.execute(select(Policy).where(Policy.asset_id == run.asset_id))
    policy = policy_result.scalars().first()
    allowed_sources = list(set(run.declared_sources + (policy.allowed_sources if policy else [])))
    governance = evaluate_agent_run(allowed_sources, run.observed_sources)
    
    return {
        "id": run.id,
        "asset_id": run.asset_id,
        "started_at": run.started_at,
        "ended_at": run.ended_at,
        "status": run.status,
        "declared_sources": run.declared_sources,
        "observed_sources": run.observed_sources,
        "violation": run.violation,
        "trace_id": run.trace_id,
        "access_events": run.access_events,
        "governance_result": governance
    }
