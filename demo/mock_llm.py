"""
Mock LLM Engine
===============
Simulates an LLM without requiring any API key.
Returns realistic, scripted responses based on prompt keywords.
Tracks token usage and latency for realistic telemetry.

This is the AI testbed — the actual product is the monitoring layer.
"""

import time
import random
import re
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int


CUSTOMER_SUPPORT_RESPONSES = [
    (
        ["order", "arrive", "delivery", "shipping", "track"],
        "I'm sorry to hear your order hasn't arrived yet. I can help you track it. "
        "Standard delivery takes 5-7 business days. If it's been longer, please contact us "
        "at support@company.com with your order number and we'll investigate immediately."
    ),
    (
        ["return", "refund", "exchange"],
        "Our return policy allows returns within 30 days of purchase for a full refund. "
        "Items must be unused and in original packaging. Please initiate the return through "
        "our website or contact support. Refunds are processed within 5-7 business days."
    ),
    (
        ["cancel", "cancellation"],
        "I can help you cancel your order. Orders can be cancelled within 2 hours of placement. "
        "After that, you'll need to wait for delivery and initiate a return. "
        "Please share your order number so I can check the status."
    ),
    (
        ["reminder", "invoice", "payment", "due", "pending"],
        "I'll help you with the payment reminder. I can see the invoice details in our system. "
        "The reminder has been queued for delivery. Please allow 1 business hour for processing."
    ),
    (
        ["damaged", "broken", "defective"],
        "I'm sorry you received a damaged item. We'll resolve this immediately. "
        "Please send photos of the damage to support@company.com, and we'll either send a "
        "replacement or process a full refund — whichever you prefer."
    ),
    (
        ["warranty", "guarantee"],
        "All our products come with a 1-year manufacturer warranty. Extended warranty "
        "plans are available for purchase. Please keep your receipt as proof of purchase."
    ),
]

HR_RESPONSES = [
    (
        ["leave", "vacation", "holiday", "pto", "time off"],
        "The company leave policy provides 20 days of paid annual leave per year, accrued monthly. "
        "Additionally, employees receive 10 public holidays. Leave requests must be submitted "
        "at least 2 weeks in advance through the HR portal. Sick leave is separate and unlimited "
        "with a doctor's note after 3 consecutive days."
    ),
    (
        ["salary", "pay", "compensation", "raise", "increment"],
        "Salary reviews are conducted annually in Q4. Performance-based increments range from "
        "5-15% based on performance ratings. Mid-year corrections may be approved for exceptional "
        "performers or market adjustments. Please contact your HR business partner for specifics."
    ),
    (
        ["onboard", "joining", "new employee", "first day"],
        "Welcome! On your first day, please arrive at 9 AM and ask for the HR team at reception. "
        "You'll complete documentation, receive your equipment, and meet your team. "
        "The onboarding program runs for 2 weeks and includes product training and shadowing."
    ),
    (
        ["health", "insurance", "medical", "benefits"],
        "The company provides comprehensive health insurance covering employees and dependents. "
        "Coverage includes hospitalization, outpatient, dental, and vision. "
        "The company covers 80% of the premium; employees contribute 20%. "
        "Open enrollment is in November each year."
    ),
    (
        ["remote", "work from home", "wfh", "hybrid"],
        "The company follows a hybrid work model: 3 days in-office, 2 days remote per week. "
        "Specific days are decided at the team level. Full remote may be approved in exceptional "
        "circumstances with manager and HR approval."
    ),
    (
        ["training", "learning", "development", "course"],
        "The company provides an annual learning budget of ₹50,000 per employee for professional "
        "development. This covers courses, certifications, conferences, and books. "
        "Submit requests through the L&D portal for pre-approval."
    ),
]

FALLBACK_RESPONSES = [
    "Thank you for your query. Let me help you with that. Based on our records and policies, "
    "I'll provide the most accurate information available. Please feel free to follow up "
    "if you need any clarification.",
    "I understand your concern. Our team is dedicated to providing the best service possible. "
    "I've reviewed the relevant information and here's what I can tell you...",
    "Great question! I'm happy to assist. Here's the information you requested based on "
    "our current policies and available data.",
]


class MockLLM:
    """
    Mock LLM that returns scripted responses for demo purposes.
    
    Simulates realistic token usage and latency to generate
    meaningful telemetry data for the observability platform.
    """

    MODEL_NAME = "mock-gpt-4o"

    def __init__(self, persona: str = "general"):
        """
        Args:
            persona: 'customer_support' | 'hr' | 'general'
        """
        self.persona = persona
        self._response_bank = {
            "customer_support": CUSTOMER_SUPPORT_RESPONSES,
            "hr": HR_RESPONSES,
            "general": CUSTOMER_SUPPORT_RESPONSES + HR_RESPONSES,
        }

    def _count_tokens(self, text: str) -> int:
        """Approximate token count (roughly 4 chars per token)."""
        return max(1, len(text) // 4)

    def _find_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        bank = self._response_bank.get(self.persona, CUSTOMER_SUPPORT_RESPONSES)

        for keywords, response in bank:
            if any(kw in prompt_lower for kw in keywords):
                return response

        return random.choice(FALLBACK_RESPONSES)

    def complete(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        """
        Generate a mock LLM response.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt (counted for tokens)
            
        Returns:
            LLMResponse with content, token counts, and latency
        """
        start = time.monotonic()

        # Simulate LLM processing latency (80-400ms)
        simulated_latency = random.uniform(0.08, 0.4)
        time.sleep(simulated_latency)

        response_text = self._find_response(prompt)

        end = time.monotonic()
        latency_ms = int((end - start) * 1000)

        input_tokens = self._count_tokens(prompt) + self._count_tokens(system_prompt)
        output_tokens = self._count_tokens(response_text)

        return LLMResponse(
            content=response_text,
            model=self.MODEL_NAME,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )
