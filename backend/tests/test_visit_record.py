import unittest

from agents.visit.record import VisitRecord


class VisitRecordTests(unittest.TestCase):

    def test_new_visit_is_empty(self):
        visit = VisitRecord()

        self.assertEqual(visit.turn_count, 0)
        self.assertEqual(visit.get_turns(), [])

    def test_add_turn_stores_interaction(self):
        visit = VisitRecord()

        turn = visit.add_turn(
            "What is this?",
            "This is a stone vessel.",
            artifact_id=46,
            language="en",
        )

        self.assertEqual(visit.turn_count, 1)
        self.assertEqual(turn.user_message, "What is this?")
        self.assertEqual(turn.assistant_message, "This is a stone vessel.")
        self.assertEqual(turn.artifact_id, 46)
        self.assertEqual(turn.language, "en")

    def test_recent_turns_return_newest_last(self):
        visit = VisitRecord()

        for index in range(3):
            visit.add_turn(
                f"Question {index}",
                f"Answer {index}",
            )

        recent = visit.get_recent_turns(2)

        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0].user_message, "Question 1")
        self.assertEqual(recent[1].user_message, "Question 2")

    def test_recent_turns_can_be_limited_to_zero(self):
        visit = VisitRecord()
        visit.add_turn("Question", "Answer")

        self.assertEqual(visit.get_recent_turns(0), [])

    def test_negative_limit_is_rejected(self):
        visit = VisitRecord()

        with self.assertRaises(ValueError):
            visit.get_recent_turns(-1)

    def test_turns_are_returned_as_a_copy(self):
        visit = VisitRecord()
        visit.add_turn("Question", "Answer")

        turns = visit.get_turns()
        turns.clear()

        self.assertEqual(visit.turn_count, 1)

    def test_sources_are_stored(self):
        visit = VisitRecord()

        sources = [
            {
                "title": "UNESCO",
                "url": "https://unesco.org/example",
            }
        ]

        turn = visit.add_turn(
            "Tell me more",
            "Here is more information.",
            artifact_id=46,
            sources=sources,
        )

        self.assertEqual(turn.sources, sources)

    def test_clear_ends_visit(self):
        visit = VisitRecord()

        visit.add_turn("Question", "Answer")
        visit.add_turn("Another question", "Another answer")

        visit.clear()

        self.assertEqual(visit.turn_count, 0)
        self.assertEqual(visit.get_turns(), [])

    def test_clear_prevents_previous_visit_history_from_leaking(self):
        visit = VisitRecord()

        visit.add_turn(
            "What is this?",
            "This is artifact 46.",
            artifact_id=46,
        )

        visit.clear()

        visit.add_turn(
            "What is this?",
            "This is artifact 79.",
            artifact_id=79,
        )

        turns = visit.get_turns()

        self.assertEqual(len(turns), 1)
        self.assertEqual(turns[0].artifact_id, 79)
        self.assertNotIn("artifact 46", turns[0].assistant_message)


if __name__ == "__main__":
    unittest.main()