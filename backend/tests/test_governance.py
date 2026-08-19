"""
Tests for the Governance Engine

Tests the core declared-vs-observed comparison logic that powers
FLYY.AI's policy violation detection.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.governance import evaluate_agent_run


class TestCompliantRuns:
    def test_exact_match(self):
        result = evaluate_agent_run(["FAQ_DB"], ["FAQ_DB"])
        assert result["violation"] is False
        assert result["governance_status"] == "COMPLIANT"
        assert result["unexpected_sources"] == []

    def test_subset_accessed(self):
        """Accessing fewer than declared is not a violation."""
        result = evaluate_agent_run(["FAQ_DB", "ORDERS_DB"], ["FAQ_DB"])
        assert result["violation"] is False
        assert result["governance_status"] == "COMPLIANT"

    def test_both_empty(self):
        result = evaluate_agent_run([], [])
        assert result["violation"] is False
        assert result["governance_status"] == "COMPLIANT"

    def test_case_insensitive(self):
        """Declared 'faq_db' should match observed 'FAQ_DB'."""
        result = evaluate_agent_run(["faq_db"], ["FAQ_DB"])
        assert result["violation"] is False
        assert result["governance_status"] == "COMPLIANT"


class TestViolatingRuns:
    def test_single_unexpected_source(self):
        result = evaluate_agent_run(["FAQ_DB"], ["FAQ_DB", "ORDERS_DB"])
        assert result["violation"] is True
        assert result["governance_status"] == "POLICY_VIOLATION"
        assert "ORDERS_DB" in result["unexpected_sources"]

    def test_multiple_unexpected_sources(self):
        result = evaluate_agent_run(
            ["FAQ_DB"],
            ["FAQ_DB", "ORDERS_DB", "PAYMENTS_DB"]
        )
        assert result["violation"] is True
        assert len(result["unexpected_sources"]) == 2
        assert "ORDERS_DB" in result["unexpected_sources"]
        assert "PAYMENTS_DB" in result["unexpected_sources"]

    def test_no_declared_but_access_observed(self):
        result = evaluate_agent_run([], ["ORDERS_DB"])
        assert result["violation"] is True
        assert "ORDERS_DB" in result["unexpected_sources"]

    def test_completely_wrong_access(self):
        result = evaluate_agent_run(["FAQ_DB"], ["ORDERS_DB"])
        assert result["violation"] is True
        assert "ORDERS_DB" in result["unexpected_sources"]


class TestMissingSources:
    def test_missing_declared_is_informational_not_violation(self):
        """
        Agent declaring FAQ_DB but not accessing it is informational only.
        A governance violation requires UNEXPECTED access — not missing access.
        """
        result = evaluate_agent_run(["FAQ_DB"], [])
        assert result["violation"] is False
        assert result["governance_status"] == "COMPLIANT"
        assert "FAQ_DB" in result["missing_sources"]


class TestGovernanceResultStructure:
    def test_response_has_all_fields(self):
        result = evaluate_agent_run(["FAQ_DB"], ["FAQ_DB", "ORDERS_DB"])
        assert "violation" in result
        assert "unexpected_sources" in result
        assert "missing_sources" in result
        assert "governance_status" in result

    def test_unexpected_sources_sorted(self):
        result = evaluate_agent_run([], ["ORDERS_DB", "FAQ_DB", "PAYMENTS_DB"])
        # Should be sorted alphabetically
        assert result["unexpected_sources"] == sorted(result["unexpected_sources"])
