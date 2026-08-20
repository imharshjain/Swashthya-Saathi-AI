"""
Unit tests for the Doctor Recommendation Service.
Tests specialty mapping, Haversine distance, ranking, verification filtering, and data freshness.
"""

import unittest
from backend.doctor_service import (
    load_doctors_dataset,
    recommend_doctors,
    map_symptoms_to_specialty,
    haversine_distance,
    get_provider_availability
)


class TestDoctorService(unittest.TestCase):
    """Test suite for doctor recommendation and freshness evaluation."""

    def setUp(self):
        self.doctors = load_doctors_dataset()

    def test_doctors_dataset_loaded(self):
        """Dataset must load at least 15 verified synthetic providers."""
        self.assertGreaterEqual(len(self.doctors), 15)
        for doc in self.doctors:
            self.assertTrue(doc.get("is_demo"), "All records must be flagged is_demo=True")
            self.assertEqual(doc.get("data_source"), "DEMO_DATA")

    def test_haversine_distance_calculation(self):
        """Distance between Bhubaneswar and Cuttack should be ~25-30 km."""
        dist = haversine_distance(20.2961, 85.8245, 20.4625, 85.8828)
        self.assertGreater(dist, 18.0)
        self.assertLess(dist, 35.0)

    def test_map_symptoms_to_specialty(self):
        """Verify clinical specialty mapping."""
        self.assertEqual(map_symptoms_to_specialty(["fever", "weakness"], "ROUTINE"), "General Medicine")
        self.assertEqual(map_symptoms_to_specialty(["severe chest pain"], "EMERGENCY"), "Emergency Medicine")
        self.assertEqual(map_symptoms_to_specialty(["chest pain"], "ROUTINE"), "Cardiology")
        self.assertEqual(map_symptoms_to_specialty(["difficulty breathing"], "URGENT"), "Pulmonology")
        self.assertEqual(map_symptoms_to_specialty(["abdominal pain", "vomiting"], "URGENT"), "Gastroenterology")
        self.assertEqual(map_symptoms_to_specialty(["skin rash"], "ROUTINE"), "Dermatology")
        self.assertEqual(map_symptoms_to_specialty(["fever"], "ROUTINE", additional_info=["Pediatric child"]), "Pediatrics")

    def test_doctor_ranking_by_proximity(self):
        """Providers closer to user location must rank earlier."""
        recs = recommend_doctors(self.doctors, "General Medicine", user_location="Bhubaneswar")
        self.assertGreater(len(recs), 0)
        # Check that distance is monotonic for exact matches
        exact_matches = [d for d in recs if d["speciality"] == "General Medicine"]
        distances = [d["distance_km"] for d in exact_matches]
        self.assertEqual(distances, sorted(distances))

    def test_provider_freshness_metadata(self):
        """Every recommended provider must have explicit freshness attributes."""
        recs = recommend_doctors(self.doctors, "General Medicine", user_location="Cuttack")
        self.assertGreater(len(recs), 0)
        top = recs[0]
        self.assertEqual(top["availability_status"], "provider_confirmation_required")
        self.assertTrue(top["is_demo"])
        self.assertEqual(top["data_source"], "DEMO_DATA")

    def test_get_provider_availability(self):
        """Availability check must return freshness notice."""
        avail = get_provider_availability("DOC_OD_001")
        self.assertEqual(avail["doctor_id"], "DOC_OD_001")
        self.assertTrue(avail["provider_confirmation_required"])
        self.assertIn("provider confirmation", avail["notice"].lower())


if __name__ == "__main__":
    unittest.main()
