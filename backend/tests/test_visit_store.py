import unittest

from agents.visit.store import VisitStore


class VisitStoreTests(unittest.TestCase):

    def test_get_or_create_returns_same_visit(self):
        store = VisitStore()

        first = store.get_or_create("visit-1")
        second = store.get_or_create("visit-1")

        self.assertIs(first, second)
        self.assertEqual(store.visit_count, 1)

    def test_different_visits_are_isolated(self):
        store = VisitStore()

        visit_a = store.get_or_create("visit-a")
        visit_b = store.get_or_create("visit-b")

        visit_a.add_turn("Question A", "Answer A")
        visit_b.add_turn("Question B", "Answer B")

        self.assertEqual(visit_a.turn_count, 1)
        self.assertEqual(visit_b.turn_count, 1)
        self.assertEqual(
            visit_a.get_turns()[0].user_message,
            "Question A",
        )
        self.assertEqual(
            visit_b.get_turns()[0].user_message,
            "Question B",
        )

    def test_get_does_not_create_missing_visit(self):
        store = VisitStore()

        self.assertIsNone(store.get("missing"))
        self.assertEqual(store.visit_count, 0)

    def test_empty_visit_id_is_rejected(self):
        store = VisitStore()

        with self.assertRaises(ValueError):
            store.get_or_create("")

    def test_delete_visit(self):
        store = VisitStore()

        store.get_or_create("visit-1")

        self.assertTrue(store.delete("visit-1"))
        self.assertIsNone(store.get("visit-1"))
        self.assertEqual(store.visit_count, 0)

    def test_delete_missing_visit_is_safe(self):
        store = VisitStore()

        self.assertFalse(store.delete("missing"))

    def test_clear_removes_all_visits(self):
        store = VisitStore()

        store.get_or_create("visit-a")
        store.get_or_create("visit-b")

        store.clear()

        self.assertEqual(store.visit_count, 0)
        self.assertIsNone(store.get("visit-a"))
        self.assertIsNone(store.get("visit-b"))


if __name__ == "__main__":
    unittest.main()