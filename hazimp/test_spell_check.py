# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Geoscience Australia

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

from hazimp import spell_check


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

# -------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestSpellCheck, 'test')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)
