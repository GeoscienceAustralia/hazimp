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

import logging

from lxml import etree
from pathlib import Path

LOGGER = logging.getLogger(__name__)

NRML_SCHEMA = str(Path(__file__).parent / '../schema/openquake/nrml.xsd')


class Validator:
    """
    XML file validator using XSD schema
    """

    def __init__(self, xsd_file: str):
        self.schema = etree.XMLSchema(
            etree.parse(xsd_file)
        )

    def validate(self, xml_filename: str):
        """
        Validate XML file against XSD schema

        :param xml_filename: name of xml file to validate
        :raises AssertionError: on schema validation error
        """

        LOGGER.debug('Validating XML file')

        return self.schema.assert_(
            etree.parse(xml_filename)
        )
