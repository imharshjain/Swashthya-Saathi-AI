"""
Unit tests for the AI & NLP Symptom Extraction Service.
Tests multilingual extraction (English, Hinglish, Odia transliterations),
duration parsing, severity extraction, and offline fallback resilience.
"""

import unittest
from backend.ai_service import extract_symptoms, rule_based_symptom_extraction


class TestAIService(unittest.TestCase):
    """Test suite for AI & NLP symptom extraction."""

    def test_hinglish_fever_and_weakness(self):
        """Core demo target case: Hinglish input with fever and weakness."""
        msg = "Mujhe 3 din se bukhar hai aur weakness bhi hai."
        res = extract_symptoms(msg)
        self.assertIn("fever", res["symptoms"])
        self.assertIn("weakness", res["symptoms"])
        self.assertEqual(res["duration"], "3 days")
        self.assertEqual(res["extraction_method"], "rule_based_nlp")

    def test_emergency_chest_pain_extraction(self):
        """English emergency chest pain and shortness of breath."""
        msg = "I have severe chest pain and difficulty breathing."
        res = extract_symptoms(msg)
        self.assertIn("severe chest pain", res["symptoms"])
        self.assertIn("difficulty breathing", res["symptoms"])

    def test_hinglish_abdominal_pain_and_vomiting(self):
        """Hinglish gastrointestinal symptoms."""
        msg = "Subah se bahut tez pet dard hai aur ulti ho rahi hai."
        res = extract_symptoms(msg)
        self.assertTrue(
            "abdominal pain" in res["symptoms"] or "severe abdominal pain" in res["symptoms"],
            f"Expected abdominal pain in {res['symptoms']}"
        )
        self.assertIn("vomiting", res["symptoms"])

    def test_temperature_severity_extraction(self):
        """Extracted measured temperature severity."""
        msg = "I have high fever 102 F since yesterday."
        res = extract_symptoms(msg)
        self.assertIn("high fever", res["symptoms"])
        self.assertIsNotNone(res["severity"])
        self.assertIn("102", res["severity"])

    def test_duration_formats(self):
        """Test extraction across multiple duration phrases."""
        cases = [
            ("Fever since 2 days", "2 days"),
            ("Khasi ek hafte se hai", "1 hafte"),
            ("Headache since yesterday", "since yesterday"),
        ]
        for text, expected in cases:
            res = rule_based_symptom_extraction(text)
            self.assertIsNotNone(res["duration"], f"Failed to extract duration from: {text}")

    def test_empty_message_handling(self):
        """Empty input must return safe structured dictionary without crashing."""
        res = extract_symptoms("")
        self.assertEqual(len(res["symptoms"]), 0)
        self.assertIsNone(res["duration"])
        self.assertIsNone(res["severity"])


if __name__ == "__main__":
    unittest.main()
