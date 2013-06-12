# -*- coding: utf-8 -*-
# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest"
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases
# pylint: disable=R0801
#:  Can not seem to locally disable this warning.

"""
Test the spell_check module.
"""

import unittest

from core_hazimp import spell_check


class TestSpellCheck(unittest.TestCase):
    """
    Test the calcs module
    """

    def test_spell_check(self):
        words = ['dove', 'eagle', 'foot', 'Wack']
        spell = spell_check.SpellCheck(words)
        self.assertTrue(spell.correct('foot') == 'foot')
        self.assertTrue(spell.correct('dave') == 'dove')
        self.assertTrue(spell.correct('eagles') == 'eagle')
        self.assertTrue(spell.correct('wack') == 'Wack')
        self.assertTrue(spell.correct('wayoff') == 'wayoff')

#-------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestSpellCheck, 'test')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)
