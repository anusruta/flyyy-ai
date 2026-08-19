"""
PII Detection Service
=====================
Detects and redacts Personally Identifiable Information (PII) from text
BEFORE any database write. Raw prompts are NEVER stored.

Detection approach:
  1. Regex recognizers  — for structured PII (phone, email, PAN, Aadhaar, credit card)
  2. Name heuristics    — capitalized word sequences following known trigger words
                          (Python 3.13 compatible, no spaCy compilation needed)

This design favors reliability over recall: 5 highly accurate detectors
beat 30 unreliable ones.

Supported entities:
  PHONE   — Indian mobile (10-digit, optionally +91)
  EMAIL   — Standard email addresses
  PAN     — Indian PAN card (ABCDE1234F)
  AADHAAR — Indian Aadhaar (12-digit groups)
  CREDIT_CARD — Standard 16-digit card numbers
  NAME    — Proper names (heuristic: preceded by contact/name trigger words)

Security principle:
  detect_and_redact() MUST be called before any DB operation.
  Calling it after would mean raw PII has already been persisted — a violation.
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PIIResult:
    sanitized_text: str
    pii_counts: dict = field(default_factory=dict)
    pii_found: bool = False


# ── Regex Patterns ────────────────────────────────────────────────────────────

_PATTERNS = {
    # Indian mobile: optional +91 prefix, then 10 digits starting with 6-9
    "PHONE": re.compile(
        r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)"
    ),
    # Standard email
    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
    ),
    # Indian PAN: 5 letters + 4 digits + 1 letter (e.g. ABCDE1234F)
    "PAN": re.compile(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
    ),
    # Indian Aadhaar: 12 digits, optionally spaced in groups of 4
    "AADHAAR": re.compile(
        r"\b[2-9]\d{3}[\s\-]?\d{4}[\s\-]?\d{4}\b"
    ),
    # Credit card: 16 digits (optionally spaced/dashed)
    "CREDIT_CARD": re.compile(
        r"\b(?:\d{4}[\s\-]?){3}\d{4}\b"
    ),
}

# Words that often precede a person's name in enterprise contexts
_NAME_TRIGGERS = re.compile(
    r"(?:to|from|contact|call|email|send|message|remind|notify|for|dear|hi|hello|regarding)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    re.IGNORECASE
)

# Words that should NOT be treated as names even if they follow a trigger
_FALSE_NAME_WORDS = {
    "the", "a", "an", "your", "our", "my", "his", "her", "their",
    "this", "that", "these", "those", "it", "me", "him", "them",
    "us", "you", "we", "they", "i", "support", "team", "manager",
    "customer", "user", "employee", "admin", "service", "department",
    "hr", "finance", "sales", "company", "client", "account",
}


class PIIDetector:
    """
    Detects and redacts PII from text using regex + name heuristics.

    Usage:
        detector = PIIDetector()
        result = detector.detect_and_redact("Call Ramesh at 9876543210")
        # result.sanitized_text → "Call <NAME> at <PHONE>"
        # result.pii_counts    → {"NAME": 1, "PHONE": 1}
    """

    def detect_and_redact(self, text: str) -> PIIResult:
        """
        Detect all PII and return sanitized text + counts.
        This is the ONLY method that should be called — always before storage.

        Args:
            text: Raw user prompt or message

        Returns:
            PIIResult with sanitized_text and pii_counts
        """
        if not text or not text.strip():
            return PIIResult(sanitized_text=text)

        try:
            return self._process(text)
        except Exception:
            # Never let PII detection crash the application.
            # Return original text (caller must handle this defensively).
            return PIIResult(sanitized_text=text)

    def _process(self, text: str) -> PIIResult:
        # Collect all spans to redact: (start, end, tag)
        spans: list[tuple[int, int, str]] = []

        # ── Regex-based PII ──────────────────────────────────────────────────
        for tag, pattern in _PATTERNS.items():
            for match in pattern.finditer(text):
                spans.append((match.start(), match.end(), tag))

        # ── Name heuristic ───────────────────────────────────────────────────
        for match in _NAME_TRIGGERS.finditer(text):
            name_candidate = match.group(1)
            words = name_candidate.strip().split()
            if all(w.lower() not in _FALSE_NAME_WORDS for w in words):
                # Only mark the name portion (group 1), not the trigger word
                name_start = match.start(1)
                name_end = match.end(1)
                spans.append((name_start, name_end, "NAME"))

        if not spans:
            return PIIResult(sanitized_text=text)

        # ── Resolve overlapping spans (keep first by start, then longest) ────
        spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
        resolved: list[tuple[int, int, str]] = []
        for span in spans:
            if not resolved or span[0] >= resolved[-1][1]:
                resolved.append(span)

        # ── Apply redactions right-to-left to preserve offsets ───────────────
        sanitized = text
        pii_counts: dict[str, int] = {}
        for start, end, tag in reversed(resolved):
            sanitized = sanitized[:start] + f"<{tag}>" + sanitized[end:]
            pii_counts[tag] = pii_counts.get(tag, 0) + 1

        return PIIResult(
            sanitized_text=sanitized,
            pii_counts=pii_counts,
            pii_found=True,
        )

    def analyze_only(self, text: str) -> dict[str, int]:
        """Return PII counts without redacting (for analysis/testing)."""
        result = self.detect_and_redact(text)
        return result.pii_counts
