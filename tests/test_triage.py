"""
Unit tests for the Clinical Triage Engine.
Tests emergency detection, urgent criteria, routine classification, and safety disclaimers.
"""

import unittest
from backend.triage_engine import assess_triage, EMERGENCY_SYMPTOMS, URGENT_SYMPTOMS


class TestTriageEngine(unittest.TestCase):
    """Test suite for deterministic clinical triage rules."""

    def test_emergency_chest_pain(self):
        """Severe chest pain must trigger EMERGENCY risk."""
        result = assess_triage(["severe chest pain"])
        self.assertEqual(result["risk_level"], "EMERGENCY")
        self.assertIn("severe chest pain", result["matched_indicators"])
        self.assertIsNotNone(result["emergency_contacts"])
        self.assertTrue(any(c["number"] == "108" for c in result["emergency_contacts"]))

    def test_emergency_difficulty_breathing(self):
        """Difficulty breathing must trigger EMERGENCY risk."""
        result = assess_triage(["difficulty breathing"])
        self.assertEqual(result["risk_level"], "EMERGENCY")
        self.assertIn("difficulty breathing", result["matched_indicators"])

    def test_emergency_loss_of_consciousness(self):
        """Loss of consciousness must trigger EMERGENCY risk."""
        result = assess_triage(["loss of consciousness"])
        self.assertEqual(result["risk_level"], "EMERGENCY")

    def test_urgent_persistent_vomiting(self):
        """Persistent vomiting must trigger URGENT risk."""
        result = assess_triage(["persistent vomiting"])
        self.assertEqual(result["risk_level"], "URGENT")
        self.assertIn("persistent vomiting", result["matched_indicators"])

    def test_urgent_prolonged_fever(self):
        """Fever lasting 3 days must be upgraded to URGENT."""
        result = assess_triage(["fever"], duration="3 days")
        self.assertEqual(result["risk_level"], "URGENT")
        self.assertTrue(any("prolonged fever" in ind for ind in result["matched_indicators"]))

    def test_urgent_high_fever_severity(self):
        """Fever with 102°F or severe rating must be URGENT."""
        result = assess_triage(["fever"], severity="102°F")
        self.assertEqual(result["risk_level"], "URGENT")

    def test_routine_cold_cough(self):
        """Standard cold and cough without red flags must be ROUTINE."""
        result = assess_triage(["cold", "cough"])
        self.assertEqual(result["risk_level"], "ROUTINE")
        self.assertEqual(len(result["matched_indicators"]), 0)
        self.assertIn("routine consultation", result["recommended_action"].lower())

    def test_empty_symptoms_handling(self):
        """Empty symptom list must return safe routine message."""
        result = assess_triage([])
        self.assertEqual(result["risk_level"], "ROUTINE")
        self.assertIn("clinical_disclaimer", result)

    def test_clinical_disclaimer_present(self):
        """All assessments must include the non-diagnostic clinical disclaimer."""
        result = assess_triage(["headache"])
        self.assertIn("Swasthya Saathi AI", result["clinical_disclaimer"])
        self.assertIn("does not", result["clinical_disclaimer"].lower())


if __name__ == "__main__":
    unittest.main()
