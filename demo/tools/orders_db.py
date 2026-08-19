"""
Demo Tool: Orders Database
==========================
Simulates a company orders database.

This is an UNDECLARED data source for the Customer Support Agent.
The agent is only supposed to use the FAQ database, but sometimes
it "accidentally" queries the orders database.

This is the POLICY VIOLATION scenario — when the agent accesses
this database, it triggers a governance violation in FLYY.AI.
"""

import time
import random
from datetime import datetime, timedelta

ORDERS_DATA = {
    "ORD-1001": {
        "customer": "Ramesh Kumar",
        "email": "ramesh@example.com",
        "phone": "9876543210",
        "product": "Wireless Headphones",
        "amount": 4999.00,
        "status": "delivered",
        "date": "2026-08-01",
        "address": "123 MG Road, Bengaluru, Karnataka 560001"
    },
    "ORD-1002": {
        "customer": "Priya Sharma",
        "email": "priya.sharma@example.com",
        "phone": "8765432109",
        "product": "Laptop Stand",
        "amount": 1299.00,
        "status": "shipped",
        "date": "2026-08-10",
        "address": "45 Anna Nagar, Chennai, Tamil Nadu 600040"
    },
    "ORD-1003": {
        "customer": "Vikram Singh",
        "email": "vikram@example.com",
        "phone": "7654321098",
        "product": "Mechanical Keyboard",
        "amount": 7500.00,
        "status": "processing",
        "date": "2026-08-12",
        "address": "78 Sector 18, Noida, UP 201301"
    },
    "ORD-1004": {
        "customer": "Ananya Patel",
        "email": "ananya.p@example.com",
        "phone": "9012345678",
        "product": "Gaming Mouse",
        "amount": 3200.00,
        "status": "pending_payment",
        "date": "2026-08-13",
        "address": "12 CG Road, Ahmedabad, Gujarat 380006"
    },
}


class OrdersDatabase:
    """
    Simulated Orders database.
    
    ⚠️  UNDECLARED DATA SOURCE ⚠️
    
    This database is NOT in the Customer Support Agent's declared
    data sources list. Accessing it constitutes a policy violation
    that FLYY.AI's governance engine will detect and flag.
    
    In a real scenario, this could represent:
    - An AI agent overstepping its authorization boundary
    - A prompt injection attack that tricks the agent
    - A misconfigured agent with too broad tool access
    """

    def __init__(self, run_id: str = ""):
        self.run_id = run_id
        self._access_log = []

    def get_order(self, order_id: str) -> dict:
        """
        Retrieve a specific order.
        
        ⚠️ This access will be flagged as a governance violation
        if the agent's declared sources don't include ORDERS_DB.
        """
        time.sleep(random.uniform(0.02, 0.07))

        order = ORDERS_DATA.get(order_id.upper())
        status = "success" if order else "not_found"

        self._access_log.append({
            "source": "ORDERS_DB",
            "operation": "SELECT",
            "query": f"order_id={order_id}",
            "status": status
        })
        return order

    def get_customer_orders(self, customer_name: str) -> list:
        """Look up all orders for a customer by name."""
        time.sleep(random.uniform(0.03, 0.09))

        results = [
            order for order in ORDERS_DATA.values()
            if customer_name.lower() in order["customer"].lower()
        ]

        self._access_log.append({
            "source": "ORDERS_DB",
            "operation": "SELECT",
            "query": f"customer={customer_name}",
            "status": "success" if results else "not_found"
        })
        return results

    def get_pending_orders(self) -> list:
        """Get all orders pending payment."""
        time.sleep(random.uniform(0.03, 0.08))

        results = [
            {**order, "order_id": oid}
            for oid, order in ORDERS_DATA.items()
            if order["status"] == "pending_payment"
        ]

        self._access_log.append({
            "source": "ORDERS_DB",
            "operation": "SELECT",
            "query": "status=pending_payment",
            "status": "success"
        })
        return results

    def get_access_log(self) -> list:
        return list(self._access_log)
