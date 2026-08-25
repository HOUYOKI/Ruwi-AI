import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agents.connector import EvidenceItem
from agents.narrator.narrator import run_narrator_turn
from agents.narrator.tools import execute_tool


ARTIFACT = {
    "id": 46,
    "name": "Stone vessel",
    "age": "Bronze Age",
    "location": "AlUla",
    "material": "Sandstone",
    "description": "A carved sandstone vessel.",
}


def run_with_mock(evidence=None, conversation_history=None):
    response = SimpleNamespace(
        choices=[SimpleNamespace(
            finish_reason="stop",
            message=SimpleNamespace(content="Grounded answer"),
        )],
        model_dump=lambda: {"mock": True},
    )
    client = MagicMock()
    client.chat.completions.create.return_value = response
    with (
        patch("agents.narrator.narrator.OpenAI", return_value=client),
        patch("agents.narrator.narrator.config.get_narrator_provider_credentials", return_value=("https://mock", "key")),
    ):
        result = run_narrator_turn(
            "Compare this object",
            ARTIFACT,
            {46: ARTIFACT},
            conversation_history=conversation_history,
            supplemental_evidence=evidence,
        )
    return result, client.chat.completions.create.call_args.kwargs["messages"]


class NarratorConnectorTests(unittest.TestCase):
    def test_existing_local_only_behavior_works_without_connector(self):
        result, messages = run_with_mock()
        self.assertEqual(result.text, "Grounded answer")
        self.assertIn("LOCAL_MUSEUM_CONTEXT", messages[-1]["content"])
        self.assertNotIn("SUPPLEMENTAL_TRUSTED_EVIDENCE", messages[-1]["content"])

    def test_connector_evidence_is_traceable_in_narrator_context(self):
        item = EvidenceItem(
            title="Comparable vessels",
            publisher="UNESCO",
            url="https://whc.unesco.org/example",
            supporting_text="Comparable carved vessels occur in a neighboring region.",
            relevance_score=0.9,
            trust_score=0.95,
        )
        _, messages = run_with_mock([item])
        content = messages[-1]["content"]
        self.assertIn("SUPPLEMENTAL_TRUSTED_EVIDENCE", content)
        self.assertIn(item.publisher, content)
        self.assertIn(item.url, content)
        self.assertIn(item.supporting_text, content)

    def test_get_artifact_tool_call_is_executed(self):
        tool_call = SimpleNamespace(
            id="call_1",
            function=SimpleNamespace(
                name="get_artifact",
                arguments='{"artifact_id": "46"}',
            ),
        )

        first_response = SimpleNamespace(
            choices=[SimpleNamespace(
                finish_reason="tool_calls",
                message=SimpleNamespace(
                    content=None,
                    tool_calls=[tool_call],
                    model_dump=lambda: {},
                ),
            )],
            model_dump=lambda: {"tool_call": True},
        )

        second_response = SimpleNamespace(
            choices=[SimpleNamespace(
                finish_reason="stop",
                message=SimpleNamespace(content="Grounded answer"),
            )],
            model_dump=lambda: {"final": True},
        )

        client = MagicMock()
        client.chat.completions.create.side_effect = [
            first_response,
            second_response,
        ]

        with (
            patch("agents.narrator.narrator.OpenAI", return_value=client),
            patch(
                "agents.narrator.narrator.config.get_narrator_provider_credentials",
                return_value=("https://mock", "key"),
            ),
        ):
            result = run_narrator_turn(
                "Tell me about this object",
                ARTIFACT,
                {46: ARTIFACT},
            )

        self.assertEqual(result.text, "Grounded answer")
        self.assertEqual(result.tool_calls_made, 1)
        self.assertEqual(client.chat.completions.create.call_count, 2)

    def test_empty_model_response_returns_empty_text(self):
        response = SimpleNamespace(
            choices=[SimpleNamespace(
                finish_reason="stop",
                message=SimpleNamespace(content=None),
            )],
            model_dump=lambda: {"mock": True},
        )

        client = MagicMock()
        client.chat.completions.create.return_value = response

        with (
            patch("agents.narrator.narrator.OpenAI", return_value=client),
            patch(
                "agents.narrator.narrator.config.get_narrator_provider_credentials",
                return_value=("https://mock", "key"),
            ),
        ):
            result = run_narrator_turn(
                "What is this?",
                ARTIFACT,
                {46: ARTIFACT},
            )

        self.assertEqual(result.text, "")
        self.assertFalse(result.hit_iteration_cap)

    def test_iteration_cap_returns_controlled_fallback(self):
        tool_call = SimpleNamespace(
            id="call_loop",
            function=SimpleNamespace(
                name="get_artifact",
                arguments='{"artifact_id": "46"}',
            ),
        )

        response = SimpleNamespace(
            choices=[SimpleNamespace(
                finish_reason="tool_calls",
                message=SimpleNamespace(
                    content=None,
                    tool_calls=[tool_call],
                    model_dump=lambda: {},
                ),
            )],
            model_dump=lambda: {"tool_call": True},
        )

        client = MagicMock()
        client.chat.completions.create.return_value = response

        with (
            patch("agents.narrator.narrator.OpenAI", return_value=client),
            patch(
                "agents.narrator.narrator.config.get_narrator_provider_credentials",
                return_value=("https://mock", "key"),
            ),
        ):
            result = run_narrator_turn(
                "Tell me about another artifact",
                ARTIFACT,
                {46: ARTIFACT},
            )

        self.assertTrue(result.hit_iteration_cap)
        self.assertEqual(result.tool_calls_made, 4)
        self.assertEqual(client.chat.completions.create.call_count, 5)
        self.assertIn("not able to find a good answer", result.text)

    def test_get_artifact_returns_existing_artifact(self):
        result = execute_tool(
            "get_artifact",
            {"artifact_id": "46"},
            {46: ARTIFACT},
        )

        self.assertTrue(result["found"])
        self.assertEqual(result["artifact"], ARTIFACT)

    def test_get_artifact_returns_not_found_for_unknown_id(self):
        result = execute_tool(
            "get_artifact",
            {"artifact_id": "999"},
            {46: ARTIFACT},
        )

        self.assertFalse(result["found"])
        self.assertEqual(result["artifact_id"], 999)

    def test_get_artifact_handles_invalid_id(self):
        result = execute_tool(
            "get_artifact",
            {"artifact_id": "not-a-number"},
            {46: ARTIFACT},
        )

        self.assertFalse(result["found"])
        self.assertEqual(result["artifact_id"], "not-a-number")

    def test_unknown_tool_fails_loudly(self):
        with self.assertRaises(NotImplementedError):
            execute_tool(
                "unknown_tool",
                {},
                {46: ARTIFACT},
            )

    def test_conversation_history_is_forwarded_to_narrator(self):
        history = [
            {"role": "user", "content": "What is this?"},
            {"role": "assistant", "content": "This is a stone vessel."},
        ]

        _, messages = run_with_mock(
            conversation_history=history,
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1], history[0])
        self.assertEqual(messages[2], history[1])


if __name__ == "__main__":
    unittest.main()
