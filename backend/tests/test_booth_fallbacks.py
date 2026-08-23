import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import main
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


if __name__ == "__main__":
    unittest.main()
