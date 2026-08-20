"""
Integration tests for FastAPI endpoints.
Tests /health, /assistant, /extract-symptoms, /triage, /doctors, /facilities, /availability, /admin/dashboard.
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app


class TestFastAPIEndpoints(unittest.TestCase):
    """Test suite for FastAPI REST API."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        """GET / must return API operational info."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["service"], "Swasthya Saathi AI")
        self.assertEqual(data["status"], "operational")

    def test_health_endpoint(self):
        """GET /health must return healthy status."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")

    def test_assistant_hinglish_query(self):
        """POST /assistant with Hinglish input."""
        payload = {
            "message": "Mujhe 3 din se bukhar hai aur weakness bhi hai.",
            "district": "Khordha"
        }
        response = self.client.post("/assistant", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("conversation_id", data)
        self.assertEqual(data["triage_assessment"]["risk_level"], "URGENT")
        self.assertIn("fever", data["structured_symptoms"]["symptoms"])
        self.assertIn("weakness", data["structured_symptoms"]["symptoms"])
        self.assertGreater(len(data["providers"]), 0)
        self.assertTrue(data["providers"][0]["is_demo"])

    def test_assistant_emergency_query(self):
        """POST /assistant with Emergency symptoms."""
        payload = {
            "message": "I have severe chest pain and difficulty breathing.",
            "district": "Cuttack"
        }
        response = self.client.post("/assistant", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["triage_assessment"]["risk_level"], "EMERGENCY")
        self.assertEqual(data["recommended_specialty"], "Emergency Medicine")

    def test_assistant_empty_message_validation(self):
        """POST /assistant with empty message must return 400 Bad Request."""
        payload = {"message": "   "}
        response = self.client.post("/assistant", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_extract_symptoms_endpoint(self):
        """POST /extract-symptoms must return structured extraction."""
        payload = {"message": "I have high fever and severe headache since 2 days."}
        response = self.client.post("/extract-symptoms", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("symptoms", data)
        self.assertIn("duration", data)

    def test_triage_endpoint(self):
        """POST /triage must return deterministic risk level."""
        payload = {
            "symptoms": ["severe chest pain"],
            "duration": "1 hour",
            "severity": "severe"
        }
        response = self.client.post("/triage", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["risk_level"], "EMERGENCY")

    def test_get_doctors_filter(self):
        """GET /doctors with filters."""
        response = self.client.get("/doctors?speciality=Cardiology&district=Khordha")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            self.assertEqual(data[0]["speciality"], "Cardiology")

    def test_get_facilities_endpoint(self):
        """GET /facilities must return Odisha facilities directory."""
        response = self.client.get("/facilities")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data), 0)
        self.assertTrue(any("AIIMS" in f["name"] for f in data))

    def test_availability_endpoint(self):
        """GET /availability/{provider_id} must return freshness notice."""
        response = self.client.get("/availability/DOC_OD_001")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["availability_status"], "provider_confirmation_required")

    def test_admin_dashboard_endpoint(self):
        """GET /admin/dashboard must return aggregated surveillance stats."""
        response = self.client.get("/admin/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_consultations", data)
        self.assertIn("emergency_count", data)
        self.assertIn("top_symptoms", data)


if __name__ == "__main__":
    unittest.main()
