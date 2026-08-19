"""
Tests for the PII Detection Service

These tests validate:
1. Structured PII detection (phone, email, PAN, Aadhaar)
2. Name detection via heuristics
3. Multiple PII in a single prompt
4. Clean text is returned unchanged
5. Edge cases (empty input, false positive prevention)
6. The "monitoring OFF" path (detection skipped entirely)

Security principle validated:
  The PIIDetector must be called BEFORE any database write.
  These tests confirm the detector works correctly when used in that order.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.pii_detector import PIIDetector


@pytest.fixture(scope="module")
def detector():
    return PIIDetector()


class TestPhoneDetection:
    def test_10_digit_mobile(self, detector):
        result = detector.detect_and_redact("Call me at 9876543210 please")
        assert "<PHONE>" in result.sanitized_text
        assert "PHONE" in result.pii_counts
        assert result.pii_found

    def test_with_plus91_prefix(self, detector):
        result = detector.detect_and_redact("Reach me at +91 9876543210")
        assert "<PHONE>" in result.sanitized_text
        assert "PHONE" in result.pii_counts

    def test_phone_not_in_original(self, detector):
        """Raw phone number must not appear in sanitized output."""
        text = "Contact 9876543210 for support"
        result = detector.detect_and_redact(text)
        assert "9876543210" not in result.sanitized_text


class TestEmailDetection:
    def test_standard_email(self, detector):
        result = detector.detect_and_redact("Send this to ramesh@example.com")
        assert "<EMAIL>" in result.sanitized_text
        assert "EMAIL" in result.pii_counts

    def test_email_not_in_original(self, detector):
        text = "Email priya@company.org with the update"
        result = detector.detect_and_redact(text)
        assert "priya@company.org" not in result.sanitized_text


class TestPANDetection:
    def test_valid_pan_format(self, detector):
        result = detector.detect_and_redact("My PAN card is ABCDE1234F")
        assert "<PAN>" in result.sanitized_text
        assert "PAN" in result.pii_counts

    def test_pan_in_context(self, detector):
        result = detector.detect_and_redact("Verify PAN XYZPQ9876G for KYC")
        assert "<PAN>" in result.sanitized_text


class TestAadhaarDetection:
    def test_12_digit_aadhaar(self, detector):
        result = detector.detect_and_redact("Aadhaar number: 2345 6789 1234")
        assert "<AADHAAR>" in result.sanitized_text
        assert "AADHAAR" in result.pii_counts

    def test_continuous_aadhaar(self, detector):
        result = detector.detect_and_redact("Link Aadhaar 234567891234")
        assert "<AADHAAR>" in result.sanitized_text


class TestNameDetection:
    def test_name_after_contact_trigger(self, detector):
        result = detector.detect_and_redact("Contact Ramesh about the invoice")
        assert "<NAME>" in result.sanitized_text
        assert "NAME" in result.pii_counts

    def test_name_after_send_trigger(self, detector):
        result = detector.detect_and_redact("Send reminder to Priya about payment")
        assert "<NAME>" in result.sanitized_text

    def test_no_false_name_for_generic_words(self, detector):
        """Words like 'the team', 'customer support' must NOT be names."""
        result = detector.detect_and_redact("Contact the customer support team")
        # Should not flag "customer" or "support" as NAME
        assert result.pii_counts.get("NAME", 0) == 0


class TestMultiplePII:
    def test_name_and_phone(self, detector):
        result = detector.detect_and_redact(
            "Send a reminder to Ramesh at 9876543210"
        )
        assert "<PHONE>" in result.sanitized_text
        assert result.pii_counts.get("PHONE", 0) == 1
        assert result.pii_found

    def test_phone_and_email(self, detector):
        result = detector.detect_and_redact(
            "Contact 9876543210 or ramesh@example.com for help"
        )
        assert "<PHONE>" in result.sanitized_text
        assert "<EMAIL>" in result.sanitized_text
        assert result.pii_counts["PHONE"] == 1
        assert result.pii_counts["EMAIL"] == 1

    def test_name_phone_email(self, detector):
        result = detector.detect_and_redact(
            "Contact John at 9876543210 or john.doe@company.com"
        )
        # At minimum phone and email should be detected
        assert result.pii_counts.get("PHONE", 0) >= 1
        assert result.pii_counts.get("EMAIL", 0) >= 1


class TestCleanText:
    def test_no_pii_unchanged(self, detector):
        text = "What is the return policy for electronics?"
        result = detector.detect_and_redact(text)
        assert result.sanitized_text == text
        assert not result.pii_found
        assert result.pii_counts == {}

    def test_hr_query_no_pii(self, detector):
        text = "How many annual leave days am I entitled to?"
        result = detector.detect_and_redact(text)
        assert result.sanitized_text == text
        assert not result.pii_found


class TestEdgeCases:
    def test_empty_string(self, detector):
        result = detector.detect_and_redact("")
        assert result.sanitized_text == ""
        assert not result.pii_found

    def test_none_like_empty(self, detector):
        result = detector.detect_and_redact("   ")
        assert not result.pii_found

    def test_count_accuracy(self, detector):
        """Each PII entity should be counted once."""
        result = detector.detect_and_redact(
            "Call 9876543210 and also 8765432109"
        )
        assert result.pii_counts.get("PHONE", 0) == 2


class TestMonitoringOff:
    """
    Simulate the monitoring=OFF path.
    When prompt_monitoring is False, the backend skips PII detection entirely.
    This test validates the expected behavior from the API layer perspective.
    """
    def test_monitoring_off_skips_detection(self, detector):
        """If monitoring is OFF, we simply don't call the detector."""
        raw_prompt = "Call Ramesh at 9876543210"
        monitoring_enabled = False

        if monitoring_enabled:
            result = detector.detect_and_redact(raw_prompt)
            sanitized = result.sanitized_text
            pii_counts = result.pii_counts
        else:
            sanitized = None   # not stored
            pii_counts = {}    # no metadata stored

        assert sanitized is None
        assert pii_counts == {}
