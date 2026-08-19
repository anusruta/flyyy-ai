from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.models import AIAsset, Policy, AIInteraction
from app.schemas.schemas import AssetCreate, AssetUpdate, AssetResponse, AssetDetail, PolicyCreate, PolicyResponse

router = APIRouter()

@router.get("/", response_model=List[AssetResponse])
async def list_assets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AIAsset).order_by(AIAsset.created_at.desc()))
    return result.scalars().all()

@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(asset_in: AssetCreate, db: AsyncSession = Depends(get_db)):
    asset_data = asset_in.model_dump(exclude={"policy"})
    new_asset = AIAsset(**asset_data)
    db.add(new_asset)
    await db.flush() # To get the id
    
    policy_data = asset_in.policy.model_dump() if asset_in.policy else {"allowed_sources": [], "allowed_pii_types": []}
    new_policy = Policy(asset_id=new_asset.id, **policy_data)
    db.add(new_policy)
    
    await db.commit()
    await db.refresh(new_asset)
    return new_asset

@router.get("/{id}", response_model=AssetDetail)
async def get_asset(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AIAsset).options(selectinload(AIAsset.policy)).where(AIAsset.id == id)
    )
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    # Get stats
    interactions_count_query = select(func.count(AIInteraction.id)).where(AIInteraction.asset_id == id)
    interactions_count = await db.scalar(interactions_count_query)
    
    pii_incidents_query = select(func.count(AIInteraction.id)).where(
        AIInteraction.asset_id == id, 
        func.json_array_length(func.json_object_keys(AIInteraction.pii_detected)) > 0
    )
    # Alternatively for sqlite/postgres compatibility:
    result = await db.execute(select(AIInteraction.pii_detected).where(AIInteraction.asset_id == id))
    interactions = result.scalars().all()
    pii_incidents_count = sum(1 for p in interactions if p and len(p) > 0)
    
    asset_dict = {
        "id": asset.id,
        "name": asset.name,
        "type": asset.type,
        "provider": asset.provider,
        "model": asset.model,
        "declared_purpose": asset.declared_purpose,
        "prompt_monitoring": asset.prompt_monitoring,
        "retention_days": asset.retention_days,
        "created_at": asset.created_at,
        "interactions_count": interactions_count or 0,
        "pii_incidents_count": pii_incidents_count,
        "policy": asset.policy
    }
    return asset_dict

@router.patch("/{id}", response_model=AssetResponse)
async def update_asset(id: str, asset_update: AssetUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AIAsset).where(AIAsset.id == id))
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    update_data = asset_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(asset, key, value)
        
    await db.commit()
    await db.refresh(asset)
    return asset

@router.get("/{id}/policy", response_model=PolicyResponse)
async def get_asset_policy(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Policy).where(Policy.asset_id == id))
    policy = result.scalars().first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.put("/{id}/policy", response_model=PolicyResponse)
async def update_asset_policy(id: str, policy_update: PolicyCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Policy).where(Policy.asset_id == id))
    policy = result.scalars().first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    policy.allowed_sources = policy_update.allowed_sources
    policy.allowed_pii_types = policy_update.allowed_pii_types
    
    await db.commit()
    await db.refresh(policy)
    return policy
