"""
Perform a PEP8 conformance test of the hazimp code base.

"""
import os
import unittest

import pycodestyle

import hazimp


class TestCodeFormat(unittest.TestCase):
    def test_pep8_conformance(self):
        # Tests the hazimp code base against the "pycodestyle" tool.
        #
        # Users can add their own excluded files (should files exist in the
        # local directory which is not in the repository) by adding a
        # ".pep8_test_exclude.txt" file in the same directory as this test.
        # The file should be a line separated list of filenames/directories
        # as can be passed to the "pep8" tool's exclude list.

        pep8style = pycodestyle.StyleGuide(quiet=False)
        pep8style.options.exclude.extend(['*/_version.py'])

        # Allow users to add their own exclude list.
        extra_exclude_file = os.path.join(os.path.dirname(__file__),
                                          '.pep8_test_exclude.txt')
        if os.path.exists(extra_exclude_file):
            with open(extra_exclude_file, 'r') as fhandle:
                extra_exclude = [line.strip()
                                 for line in fhandle if line.strip()]
            pep8style.options.exclude.extend(extra_exclude)

        root = os.path.abspath(hazimp.__file__)
        result = pep8style.check_files([os.path.dirname(root)])
        self.assertEqual(result.total_errors, 0,
                        "Found code syntax errors (and warnings).")


if __name__ == '__main__':
    unittest.main()
