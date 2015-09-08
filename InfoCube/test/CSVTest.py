__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

import CSVOutput

import unittest

class CSVTest(unittest.TestCase):
    def test_drange(self):
        nums_to_generate = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        nums = []
        for i in CSVOutput.drange(0.0, 1.0, 0.1):
            nums.append(i)
        for i in range(len(nums_to_generate)):
            self.assertAlmostEqual(nums_to_generate[i], nums[i], delta=0.00001)
