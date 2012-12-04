#!/usr/bin/env python
# -*- coding: utf-8 -*-


# pylint: disable=R0904
# Disable too many public methods for test cases

"""
Test the xml interface module.
"""

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
             '-35 121',
             '-36 122',
             '-35 121',
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
        assert  len(self.xml['polygon']) == 2

    def test_getting_excludes(self):
        assert len(self.xml['polygon'][0]['exclude']) == 0
        assert len(self.xml['polygon'][1]['exclude']) == 2

    def test_getting_array(self):
        exclude_array = self.xml['polygon'][1]['exclude'][0].array
        expected_exclude_array = [[-32.0, 121], [-34, 122], [-32, 121]]
        assert allclose(asarray(exclude_array), asarray(expected_exclude_array))


    def test_top_level_tag_name(self):
        # Test getting some info about the XML document.
        #Mainly to test various operations we will use.

        # test getting name of top-level tag
        # NOTE: There *must* be a better way to do this!?
        top_tag = self.xml.xml_node.documentElement.nodeName
        msg = "Expected top-level tag of 'Event', got '%s'" % top_tag
        self.failUnlessEqual(top_tag, 'Event', msg)

#-------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestXmlLayer,'test')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)
       
