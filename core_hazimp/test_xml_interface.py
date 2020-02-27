#!/usr/bin/env python
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

# pylint: disable=R0904
# Disable too many public methods for test cases

"""
Test the xml interface module.
"""

import math
import unittest

from scipy import allclose, asarray

from core_hazimp.xml_interface import XmlLayer


class TestXmlLayer(unittest.TestCase):

    def setUp(self):
        # correctly formed old-style XML
        str1 = '\n'.join(
            ['<Event magnitude_type="Mw">',
             '  <polygon>',
             '    <boundary>',
             '-20 120',
             '-30 120',
             '-20 120',
             '    </boundary>',
             '    <depth distribution="constant" mean="10"></depth>',
             '  </polygon>',
             '  <polygon>',
             '    <boundary>',
             '-30 121',
             '-35 122',
             '-30 135',
             '-30 121',
             '    </boundary>',
             '    <exclude>',
             '-32 121',
             '-34 122',
             '-32 121',
             '    </exclude>',
             '    <exclude>',
             '-22 nan',
             '-36 NaN',
             '-35 NAN',
             '    </exclude>',
             '    <depth distribution="constant" mean="5" />',
             '  </polygon>',
             '</Event>'])
        self.xml = XmlLayer(string=str1)

        # similar to above but simplified, wrong name for top-level tag
        str2 = '\n'.join([
            '<EventX magnitude_type="Mw">',
            '  <polygon>',
            '    <depth distribution="constant" mean="10"></depth>',
            '  </polygon>',
            '  <polygon>',
            '    <depth distribution="constant" mean="5" />',
            '  </polygon>',
            '</EventX>'])
        self.xml2 = XmlLayer(string=str2)

    def tearDown(self):
        self.xml.unlink()
        self.xml2.unlink()

    def test_attributes(self):
        assert self.xml['Event'][0].attributes['magnitude_type'] == 'Mw'

    def test_getting_polygons(self):
        assert len(self.xml['polygon']) == 2

    def test_getting_excludes(self):
        assert len(self.xml['polygon'][0]['exclude']) == 0
        assert len(self.xml['polygon'][1]['exclude']) == 2

    def test_getting_array(self):
        exclude_array = self.xml['polygon'][1]['exclude'][0].array
        expected_exclude_array = [[-32.0, 121], [-34, 122], [-32, 121]]
        assert allclose(asarray(exclude_array),
                        asarray(expected_exclude_array))

    def test_getting_array2(self):
        exclude_array = self.xml['polygon'][1]['exclude'][1].array
        math.isnan(exclude_array[2, 1])

    def test_top_level_tag_name(self):
        # Test getting some info about the XML document.
        # Mainly to test various operations we will use.

        top_tag = self.xml.xml_node.documentElement.nodeName
        msg = "Expected top-level tag of 'Event', got '%s'" % top_tag
        self.assertEqual(top_tag, 'Event', msg)

# -------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestXmlLayer, 'test')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)
