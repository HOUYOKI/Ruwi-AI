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
                json={"visit_id": "test-visit", "artifact_id": 46, "question": "What is this?"},
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
                json={"visit_id": "test-visit", "artifact_id": 46, "question": "What is this?"},
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
                json={"visit_id": "test-visit", "artifact_id": 46, "question": "Were similar objects used elsewhere?"},
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
                    json={"visit_id": "test-visit", "artifact_id": 46, "question": "What is this made of?"},
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
                json={"visit_id": "test-visit", "artifact_id": 46, "question": "What is this?"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Usable answer")
        self.assertFalse(response.json()["reflection"]["available"])


    def test_self_correction_retries_narrator_once(self):
        bad_reflection = main.ReflectionResult(
            grounded=False,
            relevance_score=0.2,
            grounding_score=0.0,
            source_coverage_score=1.0,
            flagged_for_caution=True,
            unsupported_claims=["Unsupported historical claim"],
            warnings=["Answer was not sufficiently grounded"],
        )

        good_reflection = main.ReflectionResult(
            grounded=True,
            relevance_score=0.9,
            grounding_score=0.8,
            source_coverage_score=1.0,
            flagged_for_caution=False,
        )

        narrator_results = [
            NarratorResult(text="First answer with an unsupported claim"),
            NarratorResult(text="Corrected grounded answer"),
        ]

        with (
            patch("main.config.narrator_is_configured", return_value=True),
            patch("main.config.tts_configuration_status", return_value={"configured": False}),
            patch(
                "main.run_narrator_turn",
                side_effect=narrator_results,
            ) as narrator,
            patch(
                "main.evaluate_answer",
                side_effect=[bad_reflection, good_reflection],
            ),
            patch(
                "main.needs_regeneration",
                side_effect=[True, False],
            ),
        ):
            response = self.client.post(
                "/chat",
                json={"visit_id": "test-visit", "artifact_id": 46, "question": "What is this?"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Corrected grounded answer")
        self.assertTrue(response.json()["reflection"]["grounded"])
        self.assertEqual(narrator.call_count, 2)

        second_call = narrator.call_args_list[1]
        self.assertIn("correction_feedback", second_call.kwargs)
        self.assertTrue(second_call.kwargs["correction_feedback"])

    def test_chat_reuses_visit_history_for_same_visit(self):
        history = []

        first_result = NarratorResult(text="First answer")
        second_result = NarratorResult(text="Second answer")

        with (
            patch("main.config.narrator_is_configured", return_value=True),
            patch("main.config.tts_configuration_status", return_value={"configured": False}),
            patch("main.run_narrator_turn", side_effect=[first_result, second_result]) as narrator,
            patch("main.evaluate_answer", return_value=main.ReflectionResult(
                grounded=True,
                relevance_score=1.0,
                grounding_score=1.0,
                source_coverage_score=1.0,
                flagged_for_caution=False,
            )),
        ):
            first_response = self.client.post(
                "/chat",
                json={
                    "visit_id": "history-test",
                    "artifact_id": 46,
                    "question": "What is this?",
                },
            )

            second_response = self.client.post(
                "/chat",
                json={
                    "visit_id": "history-test",
                    "artifact_id": 46,
                    "question": "Tell me more.",
                },
            )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(narrator.call_count, 2)

        first_call = narrator.call_args_list[0]
        second_call = narrator.call_args_list[1]

        self.assertEqual(first_call.kwargs["conversation_history"], [])

        self.assertEqual(
            second_call.kwargs["conversation_history"],
            [
                {"role": "user", "content": "What is this?"},
                {"role": "assistant", "content": "First answer"},
            ],
        )

    def test_different_visits_do_not_share_history(self):
        first_result = NarratorResult(text="Visit A answer")
        second_result = NarratorResult(text="Visit B answer")

        with (
            patch("main.config.narrator_is_configured", return_value=True),
            patch("main.config.tts_configuration_status", return_value={"configured": False}),
            patch(
                "main.run_narrator_turn",
                side_effect=[first_result, second_result],
            ) as narrator,
            patch(
                "main.evaluate_answer",
                return_value=main.ReflectionResult(
                    grounded=True,
                    relevance_score=1.0,
                    grounding_score=1.0,
                    source_coverage_score=1.0,
                    flagged_for_caution=False,
                ),
            ),
        ):
            first_response = self.client.post(
                "/chat",
                json={
                    "visit_id": "visit-A",
                    "artifact_id": 46,
                    "question": "Question from A",
                },
            )

            second_response = self.client.post(
                "/chat",
                json={
                    "visit_id": "visit-B",
                    "artifact_id": 46,
                    "question": "Question from B",
                },
            )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)

        self.assertEqual(
            narrator.call_args_list[0].kwargs["conversation_history"],
            [],
        )
        self.assertEqual(
            narrator.call_args_list[1].kwargs["conversation_history"],
            [],
        )

    def test_same_visit_keeps_history_when_switching_artifacts(self):
        first_result = NarratorResult(text="Answer about artifact 46")
        second_result = NarratorResult(text="Answer about another artifact")

        with (
            patch("main.config.narrator_is_configured", return_value=True),
            patch("main.config.tts_configuration_status", return_value={"configured": False}),
            patch(
                "main.run_narrator_turn",
                side_effect=[first_result, second_result],
            ) as narrator,
            patch(
                "main.evaluate_answer",
                return_value=main.ReflectionResult(
                    grounded=True,
                    relevance_score=1.0,
                    grounding_score=1.0,
                    source_coverage_score=1.0,
                    flagged_for_caution=False,
                ),
            ),
        ):
            first_response = self.client.post(
                "/chat",
                json={
                    "visit_id": "artifact-switch-test",
                    "artifact_id": 46,
                    "question": "Tell me about this artifact.",
                },
            )

            second_response = self.client.post(
                "/chat",
                json={
                    "visit_id": "artifact-switch-test",
                    "artifact_id": 14,
                    "question": "Now tell me about this one.",
                },
            )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)

        self.assertEqual(
            narrator.call_args_list[0].kwargs["conversation_history"],
            [],
        )

        self.assertEqual(
            narrator.call_args_list[1].kwargs["conversation_history"],
            [
                {"role": "user", "content": "Tell me about this artifact."},
                {"role": "assistant", "content": "Answer about artifact 46"},
            ],
        )


if __name__ == "__main__":
    unittest.main()

