"""
Demo Tool: FAQ Database
=======================
Simulates a company FAQ database that the Customer Support Agent
is DECLARED to access. Access is expected and policy-compliant.
"""

import time
import random

FAQ_DATA = {
    "return_policy": {
        "question": "What is the return policy?",
        "answer": "Returns accepted within 30 days of purchase. Items must be unused and in original packaging.",
        "category": "returns"
    },
    "shipping_times": {
        "question": "How long does shipping take?",
        "answer": "Standard shipping: 5-7 business days. Express: 1-2 business days.",
        "category": "shipping"
    },
    "warranty": {
        "question": "What warranty do products come with?",
        "answer": "All products include a 1-year manufacturer warranty.",
        "category": "warranty"
    },
    "payment_methods": {
        "question": "What payment methods are accepted?",
        "answer": "We accept credit cards, debit cards, UPI, and net banking.",
        "category": "payment"
    },
    "track_order": {
        "question": "How can I track my order?",
        "answer": "Log in to your account and visit 'My Orders'. You'll see real-time tracking.",
        "category": "orders"
    },
    "cancel_order": {
        "question": "Can I cancel my order?",
        "answer": "Orders can be cancelled within 2 hours of placement via 'My Orders'.",
        "category": "orders"
    },
    "contact_support": {
        "question": "How do I contact support?",
        "answer": "Email: support@company.com | Phone: 1800-XXX-XXXX (9AM-6PM IST)",
        "category": "support"
    },
}


class FAQDatabase:
    """
    Simulated FAQ database.
    
    This is a DECLARED data source for the Customer Support Agent.
    All access to this database is expected and policy-compliant.
    """

    def __init__(self, run_id: str = ""):
        self.run_id = run_id
        self._access_log = []

    def query(self, topic: str) -> dict:
        """
        Query the FAQ database.
        
        Args:
            topic: keyword to search for
            
        Returns:
            dict with question, answer, category; or None if not found
        """
        # Simulate DB query latency
        time.sleep(random.uniform(0.01, 0.05))

        topic_lower = topic.lower()
        for key, entry in FAQ_DATA.items():
            if topic_lower in key or topic_lower in entry["category"]:
                self._access_log.append({
                    "source": "FAQ_DB",
                    "operation": "SELECT",
                    "query": topic,
                    "status": "success"
                })
                return entry

        # Record the access attempt even if no result found
        self._access_log.append({
            "source": "FAQ_DB",
            "operation": "SELECT",
            "query": topic,
            "status": "not_found"
        })
        return None

    def search_all(self, keyword: str) -> list:
        """Full-text search across all FAQ entries."""
        time.sleep(random.uniform(0.02, 0.08))
        results = []
        keyword_lower = keyword.lower()

        for key, entry in FAQ_DATA.items():
            if (keyword_lower in entry["question"].lower() or
                    keyword_lower in entry["answer"].lower() or
                    keyword_lower in entry["category"]):
                results.append(entry)

        self._access_log.append({
            "source": "FAQ_DB",
            "operation": "SELECT",
            "query": f"search:{keyword}",
            "status": "success" if results else "not_found"
        })
        return results

    def get_access_log(self) -> list:
        return list(self._access_log)
