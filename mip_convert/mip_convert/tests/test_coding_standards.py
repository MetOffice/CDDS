# (C) British Crown Copyright 2015-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for coding standards and copyright headers.
"""
import os
import regex as re
import unittest
import pytest

import pep8

import mip_convert


@pytest.mark.style
class TestCodingStandards(unittest.TestCase):
    """
    Tests for coding standards.
    """

    def setUp(self):
        mip_convert_dir = os.path.dirname(mip_convert.__file__)
        self.all_files = [
            os.path.join(dirpath, filename)
            for dirpath, _, filenames in os.walk(mip_convert_dir)
            for filename in filenames
        ]
        self.exclude_patterns = ['conf.py']

    def test_pep8_conformance(self):
        # Only run the PEP8 test on *.py files.
        py_files = [
            filename for filename in self.all_files
            if filename.endswith('.py') and True not in set(
                [exclude_pattern in filename for exclude_pattern in self.exclude_patterns]
            )
        ]
        pep8style = pep8.StyleGuide(quiet=False)
        pep8style.options.max_line_length = 120
        # Ignore 'line break occurred before a binary operator'.
        pep8style.options.ignore = ('W503', 'E701')
        result = pep8style.check_files(py_files)
        self.assertEqual(result.total_errors, 0, 'Found code style errors (and warnings)')

    def test_copyright_headers(self):
        copyright_template = (
            '{start_comment} (C) British Crown Copyright {years}, Met Office.'
            '{end_comment}\n'
            '{start_comment} Please see LICENSE.rst for license details.'
            '{end_comment}'
        )
        # Add optional shebang.
        copyright_format = r'((\#\!.*)\n)?' + re.escape(copyright_template)
        copyright_format = copyright_format.replace(r'\{start_comment\}', r'(\#|\;|\.{2}|\/\*)')
        copyright_format = copyright_format.replace(r'\{years\}', r'(.*?)')
        copyright_format = copyright_format.replace(r'\{end_comment\}', r'(\s\*\/)?')
        copyright_pattern = re.compile(copyright_format)

        # Run the copyright test on all files except those listed below.
        self.exclude_patterns.extend(
            ['egg-info', 'EGG-INFO', 'dist', '.pyc', 'etc', 'Makefile', '.log',
             'doctrees', 'html', 'pylintrc', 'TAGS', '~',
             'conda_spec_file.txt'])
        copyright_files = [
            filename for filename in self.all_files
            if True not in set([exclude_pattern in filename for exclude_pattern in self.exclude_patterns])
        ]
        matched = True
        for full_path in copyright_files:
            match = None
            with open(full_path, 'r') as file_handler:
                match = copyright_pattern.match(file_handler.read())
            if not match:
                matched = False
                print(('{full_path}: Missing or incorrect formatting of copyright notice'.format(full_path=full_path)))
        self.assertTrue(matched, 'There were license header failures')


if __name__ == '__main__':
    unittest.main()
