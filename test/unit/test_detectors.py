import unittest

from snews.models import detectors


class TestDetectors(unittest.TestCase):

    def test_dir(self):
        expected = detectors.__all__
        actual = detectors.__dir__()
        self.assertEqual(expected, actual)
