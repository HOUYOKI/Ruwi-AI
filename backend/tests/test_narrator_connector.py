import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agents.connector import EvidenceItem
from agents.narrator.narrator import run_narrator_turn


ARTIFACT = {
    "id": 46,
    "name": "Stone vessel",
    "age": "Bronze Age",
    "location": "AlUla",
    "material": "Sandstone",
    "description": "A carved sandstone vessel.",
}


def run_with_mock(evidence=None):
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
        result = run_narrator_turn("Compare this object", ARTIFACT, {46: ARTIFACT}, supplemental_evidence=evidence)
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


if __name__ == "__main__":
    unittest.main()
