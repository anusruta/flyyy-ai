from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import List, Dict, Any

from app.database import get_db
from app.models.models import AIAsset, AIInteraction, AgentRun
from app.schemas.schemas import OverviewStats, PIIBreakdown, UsageTrendPoint

router = APIRouter()

@router.get("/overview", response_model=OverviewStats)
async def get_overview(db: AsyncSession = Depends(get_db)):
    assets_count = await db.scalar(select(func.count(AIAsset.id)))
    interactions_count = await db.scalar(select(func.count(AIInteraction.id)))
    
    # Calculate PII incidents manually or via query
    result = await db.execute(select(AIInteraction.pii_detected))
    interactions = result.scalars().all()
    pii_incidents = sum(1 for p in interactions if p and len(p) > 0)
    
    violations = await db.scalar(select(func.count(AgentRun.id)).where(AgentRun.violation == True))
    
    return OverviewStats(
        total_assets=assets_count or 0,
        total_interactions=interactions_count or 0,
        total_pii_incidents=pii_incidents,
        total_violations=violations or 0
    )

@router.get("/usage-over-time", response_model=List[UsageTrendPoint])
async def get_usage_over_time(db: AsyncSession = Depends(get_db)):
    # Using python-side aggregation for DB agnosticism
    result = await db.execute(select(AIInteraction.timestamp))
    timestamps = result.scalars().all()
    
    daily_counts = {}
    for ts in timestamps:
        date_str = ts.strftime('%Y-%m-%d')
        daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
        
    return [{"date": k, "interactions": v} for k, v in sorted(daily_counts.items())[-7:]]

@router.get("/pii-by-asset")
async def get_pii_by_asset(db: AsyncSession = Depends(get_db)):
    assets_result = await db.execute(select(AIAsset))
    assets = assets_result.scalars().all()
    
    interactions_result = await db.execute(select(AIInteraction.asset_id, AIInteraction.pii_detected))
    interactions = interactions_result.all()
    
    stats = {a.id: {"asset_name": a.name, "interactions": 0, "pii_count": 0} for a in assets}
    for asset_id, pii in interactions:
        if asset_id in stats:
            stats[asset_id]["interactions"] += 1
            if pii:
                stats[asset_id]["pii_count"] += sum(pii.values())
                
    return list(stats.values())

@router.get("/pii-types", response_model=List[PIIBreakdown])
async def get_pii_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AIInteraction.pii_detected))
    interactions = result.scalars().all()
    
    summary = {}
    for pii_dict in interactions:
        if pii_dict:
            for k, v in pii_dict.items():
                summary[k] = summary.get(k, 0) + v
                
    return [{"type": k, "count": v} for k, v in sorted(summary.items(), key=lambda x: x[1], reverse=True)]

@router.get("/agent-stats")
async def get_agent_stats(db: AsyncSession = Depends(get_db)):
    total = await db.scalar(select(func.count(AgentRun.id)))
    violations = await db.scalar(select(func.count(AgentRun.id)).where(AgentRun.violation == True))
    
    total = total or 0
    violations = violations or 0
    compliant = total - violations
    
    return {
        "total_runs": total,
        "compliant_runs": compliant,
        "violation_runs": violations,
        "violation_rate": (violations / total * 100) if total > 0 else 0
    }
