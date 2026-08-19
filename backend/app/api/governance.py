from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.models import AgentRun, Policy, AIAsset
from app.schemas.schemas import GovernanceViolation
from app.services.governance import evaluate_agent_run

router = APIRouter()

@router.get("/violations", response_model=List[GovernanceViolation])
async def get_violations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AgentRun)
        .options(selectinload(AgentRun.asset))
        .where(AgentRun.violation == True)
        .order_by(AgentRun.started_at.desc())
    )
    runs = result.scalars().all()
    
    violations = []
    for run in runs:
        policy_result = await db.execute(select(Policy).where(Policy.asset_id == run.asset_id))
        policy = policy_result.scalars().first()
        
        allowed_sources = list(set(run.declared_sources + (policy.allowed_sources if policy else [])))
        gov_result = evaluate_agent_run(allowed_sources, run.observed_sources)
        
        violations.append(GovernanceViolation(
            run_id=run.id,
            asset_name=run.asset.name if run.asset else "Unknown",
            started_at=run.started_at,
            unexpected_sources=gov_result["unexpected_sources"]
        ))
        
    return violations

@router.get("/policies")
async def get_policies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Policy).options(selectinload(Policy.asset)))
    policies = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "asset_name": p.asset.name if p.asset else "Unknown",
            "allowed_sources": p.allowed_sources,
            "allowed_pii_types": p.allowed_pii_types
        }
        for p in policies
    ]

@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AgentRun)
        .where(AgentRun.violation == True)
    )
    violation_runs = result.scalars().all()
    
    unexpected_db_count = len(violation_runs)
    
    return {
        "total_violations": unexpected_db_count,
        "breakdown": {
            "UNEXPECTED_DB_ACCESS": unexpected_db_count,
            "PII_EXPOSURE": 0  # Assuming PII is handled synchronously in interactions for now
        }
    }
