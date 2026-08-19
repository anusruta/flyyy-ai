import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, init_db
from app.models.models import AIAsset, Policy, AIInteraction, AgentRun, AccessEvent
from app.services.pii_detector import PIIDetector
from app.services.governance import evaluate_agent_run
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed():
    logger.info("Initializing DB...")
    await init_db()
    
    pii_detector = PIIDetector()
    
    async with AsyncSessionLocal() as db:
        logger.info("Creating Assets...")
        asset1 = AIAsset(name="Customer Support AI", type="llm", prompt_monitoring=True, retention_days=30)
        asset2 = AIAsset(name="HR Assistant", type="llm", prompt_monitoring=True, retention_days=7)
        asset3 = AIAsset(name="Customer Support Agent", type="agent", prompt_monitoring=True, retention_days=30)
        db.add_all([asset1, asset2, asset3])
        await db.commit()
        await db.refresh(asset1)
        await db.refresh(asset2)
        await db.refresh(asset3)
        
        logger.info("Creating Policies...")
        db.add(Policy(asset_id=asset1.id, allowed_sources=["FAQ_DB"], allowed_pii_types=[]))
        db.add(Policy(asset_id=asset2.id, allowed_sources=[], allowed_pii_types=[]))
        db.add(Policy(asset_id=asset3.id, allowed_sources=["FAQ_DB"], allowed_pii_types=[]))
        await db.commit()
        
        logger.info("Seeding Interactions for Customer Support AI...")
        prompts1 = [
            "How do I reset my password?",
            "My name is John Doe and my phone is 9876543210. I need help.",
            "Can I change my order status?",
            "Refund my money, my Aadhaar is 2345 6789 1234.",
            "What are your business hours?",
            "Call me at +91 9123456789 to fix this.",
            "I want a new product",
            "My email is test@example.com",
            "Hello, what is your name?",
            "My PAN card number is ABCDE1234F.",
            "Help me with my bill.",
            "Invoice issue for account.",
            "My phone number is 9876543210 and my name is Jane.",
            "Where is the store?",
            "I have a complaint about delivery.",
            "Track package 123456.",
            "Are you a robot?",
            "I want to speak to a human.",
            "Cancel my subscription.",
            "Does it cost money?"
        ]
        
        for p in prompts1:
            res = pii_detector.detect_and_redact(p)
            interaction = AIInteraction(
                asset_id=asset1.id,
                sanitized_prompt=res.sanitized_text,
                pii_detected=res.pii_counts,
                input_tokens=10,
                output_tokens=15,
                latency_ms=100
            )
            db.add(interaction)
            
        logger.info("Seeding Interactions for HR Assistant...")
        for i in range(10):
            interaction = AIInteraction(
                asset_id=asset2.id,
                sanitized_prompt=f"HR policy question {i}",
                pii_detected={},
                input_tokens=5,
                output_tokens=20,
                latency_ms=80
            )
            db.add(interaction)
        await db.commit()
        
        logger.info("Seeding Agent Runs...")
        # Run 1: COMPLIANT
        run1 = AgentRun(asset_id=asset3.id, declared_sources=["FAQ_DB"], observed_sources=["FAQ_DB"], violation=False, status="completed")
        db.add(run1)
        await db.commit()
        db.add(AccessEvent(run_id=run1.id, source_name="FAQ_DB"))
        
        # Run 2: VIOLATION
        run2 = AgentRun(asset_id=asset3.id, declared_sources=["FAQ_DB"], observed_sources=["FAQ_DB", "ORDERS_DB"], violation=True, status="completed")
        db.add(run2)
        await db.commit()
        db.add_all([
            AccessEvent(run_id=run2.id, source_name="FAQ_DB"),
            AccessEvent(run_id=run2.id, source_name="ORDERS_DB")
        ])
        
        # Run 3: COMPLIANT
        run3 = AgentRun(asset_id=asset3.id, declared_sources=["FAQ_DB"], observed_sources=["FAQ_DB"], violation=False, status="completed")
        db.add(run3)
        await db.commit()
        db.add(AccessEvent(run_id=run3.id, source_name="FAQ_DB"))
        
        # Run 4: VIOLATION
        run4 = AgentRun(asset_id=asset3.id, declared_sources=["FAQ_DB"], observed_sources=["FAQ_DB", "ORDERS_DB", "PAYMENTS_DB"], violation=True, status="completed")
        db.add(run4)
        await db.commit()
        db.add_all([
            AccessEvent(run_id=run4.id, source_name="FAQ_DB"),
            AccessEvent(run_id=run4.id, source_name="ORDERS_DB"),
            AccessEvent(run_id=run4.id, source_name="PAYMENTS_DB")
        ])
        
        await db.commit()
        logger.info("Seed complete.")

if __name__ == "__main__":
    asyncio.run(seed())
