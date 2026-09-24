import unittest

from ringapi import Log
from ringcursor import Ring


class TestRing(unittest.TestCase):
    def test_append_counts(self):
        self.assertEqual(Ring().append("a")["size"], 1)

    def test_capacity_reported(self):
        self.assertEqual(Ring(3).stats()["capacity"], 3)

    def test_cursors_initial(self):
        self.assertEqual(Ring().stats()["cursors"], 0)

    def test_stats_shape(self):
        self.assertIn("overwritten", Ring().stats())

    def test_log_wraps_ring(self):
        log = Log()
        log.append("a")
        self.assertEqual(log.ring.stats()["size"], 1)


if __name__ == "__main__":
    unittest.main()
