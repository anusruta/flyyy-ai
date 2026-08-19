from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database import get_db
from app.models.models import AIAsset, AIInteraction
from app.schemas.schemas import InteractionCreate, InteractionResponse
from app.services.pii_detector import PIIDetector

router = APIRouter()
pii_detector = PIIDetector()

@router.post("/", response_model=InteractionResponse)
async def capture_interaction(interaction_in: InteractionCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AIAsset).where(AIAsset.id == interaction_in.asset_id))
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    sanitized_prompt = None
    pii_counts = {}
    
    if asset.prompt_monitoring:
        if interaction_in.prompt:
            pii_result = pii_detector.detect_and_redact(interaction_in.prompt)
            sanitized_prompt = pii_result.sanitized_text
            pii_counts = pii_result.pii_counts
    
    interaction = AIInteraction(
        asset_id=interaction_in.asset_id,
        user_id=interaction_in.user_id,
        sanitized_prompt=sanitized_prompt,
        pii_detected=pii_counts,
        model=interaction_in.model,
        input_tokens=interaction_in.input_tokens,
        output_tokens=interaction_in.output_tokens,
        latency_ms=interaction_in.latency_ms,
        status=interaction_in.status,
        trace_id=interaction_in.trace_id
    )
    
    db.add(interaction)
    await db.commit()
    await db.refresh(interaction)
    return interaction

@router.get("/", response_model=List[InteractionResponse])
async def list_interactions(
    asset_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(AIInteraction).order_by(AIInteraction.timestamp.desc()).limit(limit).offset(offset)
    if asset_id:
        query = query.where(AIInteraction.asset_id == asset_id)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/pii-summary")
async def get_pii_summary(asset_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(AIInteraction.pii_detected)
    if asset_id:
        query = query.where(AIInteraction.asset_id == asset_id)
        
    result = await db.execute(query)
    interactions = result.scalars().all()
    
    summary = {}
    for pii_dict in interactions:
        if pii_dict:
            for k, v in pii_dict.items():
                summary[k] = summary.get(k, 0) + v
                
    return [{"type": k, "count": v} for k, v in summary.items()]
