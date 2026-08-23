import unittest

from agents.connector import EvidenceItem
from agents.reflection import evaluate_answer, unavailable_reflection


ARTIFACT = {
    "id": 46,
    "name": "Stone vessel",
    "age": "Bronze Age",
    "location": "AlUla",
    "material": "Sandstone",
    "description": "A carved sandstone vessel.",
}


def trusted_evidence() -> EvidenceItem:
    return EvidenceItem(
        title="Stone vessels",
        publisher="UNESCO",
        url="https://whc.unesco.org/example",
        supporting_text="Related carved stone vessels appear in neighboring regions.",
        relevance_score=0.9,
        trust_score=0.95,
    )


class ReflectionTests(unittest.TestCase):
    def test_grounded_local_answer(self):
        result = evaluate_answer(
            "What is this made of?", "This stone vessel is carved from sandstone.", ARTIFACT, [], False
        )
        self.assertTrue(result.grounded)
        self.assertEqual(result.source_coverage_score, 1)

    def test_missing_sources_are_flagged(self):
        result = evaluate_answer("Compare this object", "It has parallels elsewhere.", ARTIFACT, [], True)
        self.assertFalse(result.grounded)
        self.assertTrue(result.flagged_for_caution)
        self.assertIn("without supporting evidence", result.warnings[0])

    def test_unsupported_url_is_flagged(self):
        result = evaluate_answer(
            "Compare this object",
            "A comparison appears at https://untrusted.test/post",
            ARTIFACT,
            [trusted_evidence()],
            True,
        )
        self.assertFalse(result.grounded)
        self.assertIn("https://untrusted.test/post", result.unsupported_claims)

    def test_irrelevant_and_empty_answers_are_flagged(self):
        irrelevant = evaluate_answer("What is this made of?", "Penguins swim in cold water.", ARTIFACT, [], False)
        empty = evaluate_answer("What is this?", "  ", ARTIFACT, [], False)
        self.assertTrue(irrelevant.flagged_for_caution)
        self.assertEqual(irrelevant.grounding_score, 0)
        self.assertFalse(empty.grounded)
        self.assertEqual(empty.relevance_score, 0)

    def test_unavailable_result_is_safe_metadata(self):
        result = unavailable_reflection(RuntimeError("failed"))
        self.assertFalse(result.available)
        self.assertTrue(result.flagged_for_caution)


if __name__ == "__main__":
    unittest.main()
