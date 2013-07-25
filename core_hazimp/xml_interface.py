
# Copyright (C) 2007 Geoscience Australia

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

"""
 Title: xml_interface.py

  Author:  Peter Row

  Description: Class to access XML information
"""


from scipy import array, NaN
import xml.dom.minidom


class XmlLayer(object):
    """
    Simplified XML parsing.
    """
    def __init__(self, node=None, string=None, filename=None):
        """
        supports:
        node['child'] => returns a list of all child nodes named 'child'.

        node.attributes => return a dictionary of all attributes of the node
        node.array => turn the node value into an float array

        Note, if you don't know xml:
            xml nodes have both children (which have names, and an order),
            attributes (which have values), and values (the main text).

            Example:
                (in python, not xml, but highlighting the way xml works)

                node0
                    attributes = {dtype:float,size:10}
                    children
                        [
                        'alice' => node1
                        'bob' => node2
                        'alice' => node3 (yes, same named nodes are legal)
                        'charlie' => node4
                        ]
                    value = '1,2,3,4,5,6,7,8,9,0'
        """
        self.dom = xml.dom.minidom

        if node is not None:
            self.xml_node = node
        elif string is not None:
            self.parse_string(string)
        elif filename is not None:
            self.parse_file(filename)

    def parse_string(self, string):
        """Parse a string

        Args:
            string: String to parse.
        """
        self.xml_node = self.dom.parseString(string)
        return

    def parse_file(self, filename):
        """Parse an xml file

        Args:
            filename: File to parse.
        """
        self.xml_node = self.dom.parse(filename)
        return

    def __getitem__(self, item_name):
        node_list = self.xml_node.getElementsByTagName(item_name)
        return [XmlLayer(node=node) for node in node_list]

    def __attributes(self):
        """
        Returns:
            A dictionary of the attributes.
        """
        get_item = self.xml_node.attributes.getNamedItem
        #get_item is now a shortcut for xml_node.attributes.getNamedItem
        attributes_dictionary = {}
        for key in self.xml_node.attributes.keys():
            attributes_dictionary[str(key)] = str(get_item(key).value)
        return attributes_dictionary

    def keys(self):
        """
        Returns:
            A dictionary of the attributes.
        """
        node_list = self.xml_node.childNodes
        keys = {}
        for node in node_list:
            try:
                name = node.tagName
                keys[name] = None
            except AttributeError:
                pass
        return keys.keys()

    def __array(self):
        """ Converts info into a numpy array.

        Returns:
            A numpy array.
        """
        string = self.xml_node.firstChild.nodeValue
        #In one ugly step. 5.1.3

        def _float(x_string):
            """ Converts a string into a float of a numpy NaN.

            Returns:
                A float or a numpy NaN.
            """
            try:
                val = float(x_string)
            except ValueError:
                if x_string == 'NaN':
                    val = NaN
                else:
                    raise
            return val
        # pylint: disable=W0141
        tuple_list = [tuple(map(_float,
                                pair.split())) for pair in string.split('\n')]

        #or (a bit slower)
        #list_of_strings = string.split('\n')
        #split it up into small strings

        #list_of_lists = [coordinate.split() for coordinate in list_of_strings]
        #split the small strings (coordinates) into ['lat','long'] lists

        #list_of_lists = [map(float,coord) for coord in list_of_lists]
        #coordintates into [lat,long] lists

        #list_of_tuples = [tuple(coordinate) for coordinate in list_of_lists]
        #coordintates into (lat,long)

        #or
        #list_of_tuples=[]
        #for coordinate in string.split('\n')[1:-1]:
        #    coordinate = coordinate.split()
        #    coordinate = (float(coordinate[0]),float(coordinate[1]))
        #    list_of_tuples.append(coordinate)

        list_of_tuples = [t for t in tuple_list if len(t) > 0]
        #Chomp out the empty lines
        return array(list_of_tuples)

    attributes = property(__attributes)
    array = property(__array)

    def unlink(self):
        """unlink to cleanup unneeded objects.
        """
        self.xml_node.unlink()
