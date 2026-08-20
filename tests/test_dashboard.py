"""
Unit tests for Database and Health Department Dashboard Aggregation.
Tests zero-PII logging, risk aggregations, and district surveillance metrics.
"""

import unittest
from backend.database import get_admin_dashboard_metrics, log_consultation


class TestDashboardAnalytics(unittest.TestCase):
    """Test suite for public health surveillance data aggregation."""

    def test_dashboard_metrics_structure(self):
        """Dashboard metrics must contain required surveillance components."""
        metrics = get_admin_dashboard_metrics()
        self.assertIn("total_consultations", metrics)
        self.assertIn("emergency_count", metrics)
        self.assertIn("urgent_count", metrics)
        self.assertIn("routine_count", metrics)
        self.assertIn("top_symptoms", metrics)
        self.assertIn("specialty_demand", metrics)
        self.assertIn("district_trends", metrics)
        self.assertIn("recent_consultations", metrics)

    def test_anonymized_logging(self):
        """Logged consultations must increment total count without storing PII."""
        before = get_admin_dashboard_metrics()
        initial_total = before["total_consultations"]

        log_consultation(
            conversation_id="test-conv-999",
            district="Sambalpur",
            language_detected="English",
            symptoms=["fever", "cough"],
            risk_level="ROUTINE",
            matched_indicators=[],
            recommended_specialty="General Medicine",
            matched_facility="VIMSAR Burla",
            extraction_method="rule_based_nlp"
        )

        after = get_admin_dashboard_metrics()
        self.assertEqual(after["total_consultations"], initial_total + 1)

        # Verify recent consultation record contains zero PII fields
        recent = after["recent_consultations"][0]
        self.assertNotIn("name", recent)
        self.assertNotIn("phone", recent)
        self.assertNotIn("email", recent)
        self.assertNotIn("address", recent)


if __name__ == "__main__":
    unittest.main()
