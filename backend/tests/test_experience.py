import json
import os
import unittest
from unittest.mock import patch
from pathlib import Path

os.environ.setdefault("EXPERIENCE_LLM_ENABLED", "false")

from experience.graph import build_experience_graph
from experience.schemas import ExperienceResponse
from experience.repository import load_showcase_experiences


ROOT = Path(__file__).resolve().parents[2]


class ExperienceGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        artifacts = json.loads((ROOT / "data" / "artifacts.json").read_text(encoding="utf-8"))
        cls.graph = build_experience_graph({artifact["id"]: artifact for artifact in artifacts})

    def test_showcase_artifact_produces_valid_hotspot_experience(self):
        state = self.graph.invoke({"requested_artifact_id": 46, "warnings": []})
        experience = ExperienceResponse.model_validate(state["experience"])

        self.assertEqual(experience.artifact.id, 46)
        self.assertEqual(experience.template, "hotspot_story")
        self.assertEqual(len(experience.hotspots), 3)
        self.assertEqual(len(experience.quiz), 2)
        self.assertEqual(len(experience.sources), 1)

    def test_every_showcase_artifact_produces_a_valid_experience(self):
        showcase = load_showcase_experiences()
        self.assertEqual(set(showcase), {6, 14, 18, 43, 46, 79})
        for artifact_id, curated in showcase.items():
            with self.subTest(artifact_id=artifact_id):
                self.assertTrue(curated.get("featured"))
                self.assertEqual(curated.get("artifact_id"), artifact_id)
                state = self.graph.invoke({"requested_artifact_id": artifact_id, "warnings": []})
                experience = ExperienceResponse.model_validate(state["experience"])
                self.assertEqual(experience.artifact.id, artifact_id)
                self.assertTrue(experience.narration)
                self.assertTrue(experience.sources)
                self.assertGreaterEqual(len(experience.quiz), 2)
                for hotspot in experience.hotspots:
                    self.assertGreaterEqual(hotspot.x, 0)
                    self.assertLessEqual(hotspot.x, 1)
                    self.assertGreaterEqual(hotspot.y, 0)
                    self.assertLessEqual(hotspot.y, 1)

    def test_normal_artifact_does_not_fabricate_an_experience(self):
        state = self.graph.invoke({"requested_artifact_id": 1, "warnings": []})
        self.assertNotIn("experience", state)
        self.assertEqual(state["error"], "No curated experience is available for this artifact")

    def test_every_showcase_artifact_has_a_valid_arabic_experience(self):
        for artifact_id in load_showcase_experiences():
            with self.subTest(artifact_id=artifact_id):
                state = self.graph.invoke({"requested_artifact_id": artifact_id, "language": "ar", "warnings": []})
                experience = ExperienceResponse.model_validate(state["experience"])
                self.assertEqual(experience.metadata.language, "ar")
                self.assertRegex(experience.title, r"[\u0600-\u06ff]")
                self.assertRegex(experience.narration, r"[\u0600-\u06ff]")
                self.assertTrue(experience.sources)

    def test_live_generation_failure_uses_validated_curated_fallback(self):
        with patch("experience.graph.generate_experience", side_effect=TimeoutError("offline")):
            state = self.graph.invoke({"requested_artifact_id": 46, "warnings": []})
        experience = ExperienceResponse.model_validate(state["experience"])
        self.assertEqual(experience.artifact.id, 46)
        self.assertFalse(experience.metadata.generated)
        self.assertTrue(experience.metadata.warnings)

    def test_unknown_artifact_returns_not_found_error(self):
        state = self.graph.invoke({
            "requested_artifact_id": 999999,
            "warnings": [],
        })

        self.assertEqual(state["match_status"], "unsupported")
        self.assertEqual(state["error"], "Artifact not found")
        self.assertNotIn("experience", state)

    def test_live_generation_failure_preserves_curated_content(self):
        with patch(
            "experience.graph.generate_experience",
            side_effect=RuntimeError("generation failed"),
        ):
            state = self.graph.invoke({
                "requested_artifact_id": 46,
                "warnings": [],
            })

        experience = ExperienceResponse.model_validate(state["experience"])

        self.assertEqual(experience.artifact.id, 46)
        self.assertFalse(experience.metadata.generated)
        self.assertTrue(experience.metadata.warnings)


if __name__ == "__main__":
    unittest.main()
