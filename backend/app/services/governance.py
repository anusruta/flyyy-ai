"""
Governance Engine

Compares declared data sources (from policy) against observed sources
(recorded during agent execution). Flags violations.
"""
from typing import Optional


def evaluate_agent_run(
    declared_sources: list[str],
    observed_sources: list[str]
) -> dict:
    """
    Returns:
        {
            "violation": bool,
            "unexpected_sources": list[str],
            "missing_sources": list[str],  # declared but not observed (informational)
            "governance_status": "COMPLIANT" | "POLICY_VIOLATION"
        }
    """
    declared_set = set(s.upper() for s in declared_sources)
    observed_set = set(s.upper() for s in observed_sources)
    
    unexpected = sorted(list(observed_set - declared_set))
    missing = sorted(list(declared_set - observed_set))
    violation = len(unexpected) > 0
    
    return {
        "violation": violation,
        "unexpected_sources": unexpected,
        "missing_sources": missing,
        "governance_status": "POLICY_VIOLATION" if violation else "COMPLIANT"
    }
