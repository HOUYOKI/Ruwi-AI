import unittest

from agents.connector import ConnectorAgent, EvidenceItem, StaticRetrievalProvider
from agents.connector.tools import is_trusted_url, needs_connector


def evidence(url: str = "https://www.metmuseum.org/art/collection") -> EvidenceItem:
    return EvidenceItem(
        title="Comparable objects",
        publisher="The Metropolitan Museum of Art",
        url=url,
        supporting_text="Comparable stone objects were used in another cultural setting.",
        relevance_score=0.9,
        trust_score=0.95,
    )


class ConnectorTests(unittest.TestCase):
    artifact = {"id": 46, "name": "Stone object"}

    def test_local_question_does_not_retrieve(self):
        class ProviderThatMustNotRun:
            def search(self, query, artifact):
                raise AssertionError("provider should not be called")

        result = ConnectorAgent(ProviderThatMustNotRun()).retrieve("What is this made of?", self.artifact)
        self.assertFalse(result.used)
        self.assertEqual(result.evidence, [])

    def test_comparison_question_requires_retrieval(self):
        self.assertTrue(needs_connector("Were similar objects used elsewhere?", self.artifact))

    def test_trusted_source_is_accepted(self):
        result = ConnectorAgent(StaticRetrievalProvider([evidence()])).retrieve(
            "Were similar objects used elsewhere?", self.artifact
        )
        self.assertTrue(result.used)
        self.assertEqual(len(result.evidence), 1)

    def test_untrusted_source_is_rejected(self):
        result = ConnectorAgent(StaticRetrievalProvider([evidence("https://example-blog.test/post")])).retrieve(
            "Compare this with another civilization", self.artifact
        )
        self.assertFalse(result.used)
        self.assertEqual(result.evidence, [])
        self.assertIn("Rejected 1", result.warnings[0])

    def test_provider_unavailable_is_controlled(self):
        result = ConnectorAgent().retrieve("What other cultures used this?", self.artifact)
        self.assertFalse(result.used)
        self.assertIn("Connector unavailable", result.warnings[0])

    def test_provider_failure_is_controlled(self):
        class FailingProvider:
            def search(self, query, artifact):
                raise TimeoutError("timeout")

        result = ConnectorAgent(FailingProvider()).retrieve("What influenced this style?", self.artifact)
        self.assertFalse(result.used)
        self.assertIn("TimeoutError", result.warnings[0])

    def test_empty_provider_result_is_valid(self):
        result = ConnectorAgent(StaticRetrievalProvider([])).retrieve("Compare this object", self.artifact)
        self.assertFalse(result.used)
        self.assertEqual(result.warnings, [])

    def test_trusted_policy_accepts_subdomains_and_rejects_lookalikes(self):
        self.assertTrue(is_trusted_url("https://collection.britishmuseum.org/item"))
        self.assertTrue(is_trusted_url("https://museum.example.edu/object"))
        self.assertFalse(is_trusted_url("https://britishmuseum.org.example.test/item"))

    def test_evidence_is_deduplicated_and_ranked(self):
        low = EvidenceItem(
            title="Low quality",
            publisher="The Metropolitan Museum of Art",
            url="https://www.metmuseum.org/item/",
            supporting_text="Low quality evidence.",
            relevance_score=0.9,
            trust_score=0.7,
        )
        high = EvidenceItem(
            title="Better quality",
            publisher="The Metropolitan Museum of Art",
            url="https://www.metmuseum.org/item",
            supporting_text="Better quality evidence.",
            relevance_score=0.8,
            trust_score=0.95,
        )

        result = ConnectorAgent(
            StaticRetrievalProvider([low, high])
        ).retrieve(
            "Compare this with another civilization",
            self.artifact,
        )

        self.assertTrue(result.used)
        self.assertEqual(len(result.evidence), 1)
        self.assertEqual(result.evidence[0].title, "Better quality")

    def test_evidence_is_limited_to_five_sources(self):
        evidence_items = [
            EvidenceItem(
                title=f"Source {index}",
                publisher="The Metropolitan Museum of Art",
                url=f"https://www.metmuseum.org/item/{index}",
                supporting_text=f"Evidence {index}.",
                relevance_score=0.5 + index / 20,
                trust_score=0.7 + index / 20,
            )
            for index in range(7)
        ]

        result = ConnectorAgent(
            StaticRetrievalProvider(evidence_items)
        ).retrieve(
            "Compare this with another civilization",
            self.artifact,
        )

        self.assertEqual(len(result.evidence), 5)

    def test_arabic_comparison_question_requires_retrieval(self):
        self.assertTrue(
            needs_connector(
                "هل استُخدمت قطع مشابهة في حضارات أخرى؟",
                self.artifact,
            )
        )

    def test_arabic_local_question_does_not_retrieve(self):
        self.assertFalse(
            needs_connector(
                "ما مادة هذه القطعة؟",
                self.artifact,
            )
        )

    def test_trusted_policy_rejects_http_lookalike_domain(self):
        self.assertFalse(
            is_trusted_url("https://metmuseum.org.example.com/item")
        )

    def test_trusted_policy_accepts_saudi_government_subdomain(self):
        self.assertTrue(
            is_trusted_url("https://example.moc.gov.sa/page")
        )

    def test_trusted_policy_rejects_invalid_scheme(self):
        self.assertFalse(
            is_trusted_url("ftp://www.metmuseum.org/item")
        )

    def test_trusted_policy_accepts_custom_trusted_domain(self):
        self.assertTrue(
            is_trusted_url(
                "https://museum.example.com/item",
                {"museum.example.com"},
            )
        )

    def test_arabic_influence_question_requires_retrieval(self):
        self.assertTrue(
            needs_connector(
                "هل تأثرت هذه القطعة بحضارة أخرى؟",
                self.artifact,
            )
        )

    def test_arabic_relationship_question_requires_retrieval(self):
        self.assertTrue(
            needs_connector(
                "ما علاقتها بثقافات أخرى؟",
                self.artifact,
            )
        )

    def test_arabic_location_question_does_not_retrieve(self):
        self.assertFalse(
            needs_connector(
                "أين عُثر على هذه القطعة؟",
                self.artifact,
            )
        )


if __name__ == "__main__":
    unittest.main()
