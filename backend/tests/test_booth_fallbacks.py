import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi.testclient import TestClient

import main
from agents.connector import ConnectorAgent, EvidenceItem, StaticRetrievalProvider
from agents.narrator.narrator import NarratorResult


class BoothFallbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def test_chat_is_controlled_when_narrator_is_unconfigured(self):
        with patch("main.config.narrator_is_configured", return_value=False):
            response = self.client.post(
                "/chat",
                json={"artifact_id": 46, "question": "What is this?"},
            )
        self.assertEqual(response.status_code, 503)
        self.assertIn("artifact experience remains available", response.json()["detail"])

    def test_tts_failure_preserves_text_answer(self):
        with (
            patch("main.config.narrator_is_configured", return_value=True),
            patch("main.config.tts_configuration_status", return_value={"configured": True}),
            patch("main.run_narrator_turn", return_value=NarratorResult(text="Grounded answer")),
            patch("main.speak_text", side_effect=TimeoutError("TTS unavailable")),
        ):
            response = self.client.post(
                "/chat",
                json={"artifact_id": 46, "question": "What is this?"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Grounded answer")
        self.assertIsNone(response.json()["audio_url"])
        self.assertIn("sources", response.json())
        self.assertIn("reflection", response.json())

    def test_connector_sources_and_reflection_serialize(self):
        item = EvidenceItem(
            title="Comparable vessels",
            publisher="UNESCO",
            url="https://whc.unesco.org/example",
            supporting_text="Comparable carved vessels appear in neighboring regions.",
            relevance_score=0.9,
            trust_score=0.95,
        )
        connector = ConnectorAgent(StaticRetrievalProvider([item]))
        with (
            patch("main.config.narrator_is_configured", return_value=True),
            patch("main.config.tts_configuration_status", return_value={"configured": False}),
            patch("main.CONNECTOR", connector),
            patch("main.run_narrator_turn", return_value=NarratorResult(text="Comparable carved vessels appear in neighboring regions.")) as narrator,
        ):
            response = self.client.post(
                "/chat",
                json={"artifact_id": 46, "question": "Were similar objects used elsewhere?"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sources"][0]["publisher"], "UNESCO")
        self.assertTrue(response.json()["reflection"]["available"])
        self.assertEqual(narrator.call_args.kwargs["supplemental_evidence"], [item])

    def test_successful_tts_keeps_existing_audio_url_shape(self):
        with TemporaryDirectory() as directory:
            audio_dir = Path(directory).resolve()
            with (
                patch("main.config.narrator_is_configured", return_value=True),
                patch("main.config.tts_configuration_status", return_value={"configured": True}),
                patch("main.run_narrator_turn", return_value=NarratorResult(text="This object is made of stone.")),
                patch("main.speak_text", return_value=b"mock-mp3"),
                patch("main.AUDIO_DIR", audio_dir),
                patch("main.uuid.uuid4", return_value=type("Uuid", (), {"hex": "fixed"})()),
            ):
                response = self.client.post(
                    "/chat",
                    json={"artifact_id": 46, "question": "What is this made of?"},
                )
                self.assertTrue((audio_dir / "fixed.mp3").is_file())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["audio_url"], "/static/audio/fixed.mp3")

    def test_reflection_failure_does_not_destroy_answer(self):
        with (
            patch("main.config.narrator_is_configured", return_value=True),
            patch("main.config.tts_configuration_status", return_value={"configured": False}),
            patch("main.run_narrator_turn", return_value=NarratorResult(text="Usable answer")),
            patch("main.evaluate_answer", side_effect=RuntimeError("reflection failed")),
        ):
            response = self.client.post(
                "/chat",
                json={"artifact_id": 46, "question": "What is this?"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Usable answer")
        self.assertFalse(response.json()["reflection"]["available"])


if __name__ == "__main__":
    unittest.main()
