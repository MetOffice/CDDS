# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest
from unittest.mock import patch

from mip_convert.load.user_config import PpRequestVariableReader


class TestPpRequest(unittest.TestCase):
    SECTIONS = {'DEFAULT': {'MIPtable': 'CMIP5_Amon', },
                'var_with_lbproc': {'lbproc': '128', 'mapping_id': 'map1'},
                'var_with_lbproc_1': {'lbproc': '128', 'mapping_id': 'map1'},
                'var_no_sections': {'mapping_id': 'amap'},
                'var_with_lbtim': {'lbtim': '622', 'mapping_id': 'map2'},
                'var_with_all': {'lbproc': '128', 'lbtim': '622', 'lbuser5': '1', 'mapping_id': 'map3'},
                'var_with_fill_value': {'fill_value': '-1.0', 'mapping_id': 'map4'},
                'var_with_blev': {'blev': '0. 1.', 'mapping_id': 'map4'},
                'var_with_outputs_per_file': {'blev': '0. 1.', 'mapping_id': 'map4', 'outputs_per_file': 1},
                'nomapping': {},
                'var_with_first': {'mapping_id': 'amap', 'first_only': 'y'}
                }

    def get(self, section, option):
        """
        act as a stub config parser
        """
        if option in self.SECTIONS[section]:
            result = self.SECTIONS[section][option]
        else:
            result = self.SECTIONS['DEFAULT'][option]
        return result

    def getboolean(self, section, option):
        value = self.get(section, option)
        return value == 'y'

    def has_option(self, section, option):
        """
        act as a stub config parser
        """
        if option in self.SECTIONS[section]:
            result = option in self.SECTIONS[section]
        else:
            result = option in self.SECTIONS['DEFAULT']
        return result

    def assertOnStreamTable(self, request, variable):
        self.assertEqual(self.table, request.table)
        self.assertEqual(self.stream_name, request.stream)

    def makeRequest(self, variable):
        return self.request_reader.readRequest(self.stream_name, variable, self)

    def getProcessor(self, mapping_id):
        return 'processor' + mapping_id

    def setUp(self):
        self.stream_name = 'apa'
        self.table = 'CMIP5_Amon'
        self.request_reader = PpRequestVariableReader(self)

    @patch('mip_convert.save.cmor.cmor_lite.get_saver')
    def testMapping(self, mock_saver):
        request = self.makeRequest('var_with_lbproc')
        self.assertEqual(self.getProcessor('map1'), request._processor)
        mock_saver.assert_called_once_with('CMIP5_Amon', 'var_with_lbproc', None)

    @patch('mip_convert.save.cmor.cmor_lite.get_saver')
    def testNoMapping(self, mock_saver):
        request = self.makeRequest('nomapping')
        self.assertEqual(self.getProcessor('CMIP5 (Amon' + ', ' + 'nomapping)'), request._processor)

    @patch('mip_convert.save.cmor.cmor_lite.get_saver')
    def testOutputsPerFileSet(self, mock_saver):
        # test around a BUG introduced just before release 1.6
        request = self.makeRequest('var_with_outputs_per_file')
        self.assertEqual(self.get('var_with_outputs_per_file', 'outputs_per_file'), request.outputs_per_file)

        mock_saver.assert_called_once_with(
            'CMIP5_Amon',
            'var_with_outputs_per_file',
            self.get('var_with_outputs_per_file', 'outputs_per_file')
        )

    @patch('mip_convert.save.cmor.cmor_lite.get_saver')
    def testReadInts(self, mk_saver):
        examples = [
            ('var_with_lbproc', ('lbproc',)),
            ('var_with_lbtim', ('lbtim',)),
            ('var_with_all', ('lbtim', 'lbproc', 'lbuser5')),
        ]
        for (variable, attributes) in examples:
            request = self.makeRequest(variable)
            for attribute in attributes:
                self.assertOnStreamTable(request, variable)
                self.assertEqual(int(self.SECTIONS[variable][attribute]), getattr(request, attribute))

    @patch('mip_convert.save.cmor.cmor_lite.get_saver')
    def testReadReals(self, mock_saver):
        variable = 'var_with_fill_value'
        request = self.makeRequest(variable)
        self.assertOnStreamTable(request, variable)
        self.assertEqual(float(self.SECTIONS[variable]['fill_value']), getattr(request, 'fill_value'))

    @patch('mip_convert.save.cmor.cmor_lite.get_saver')
    def testReadRealList(self, mock_saver):
        variable = 'var_with_blev'
        request = self.makeRequest(variable)
        self.assertOnStreamTable(request, variable)
        expect = [float(value) for value in self.SECTIONS[variable]['blev'].split(' ')]
        self.assertEqual(expect, getattr(request, 'blev'))

    @patch('mip_convert.save.cmor.cmor_lite.get_saver')
    def testRepeatSectionWithNumber(self, mk_saver):
        # occasionaly have same MIP entries in the same stream - have to append
        # a number
        variable = 'var_with_lbproc_1'
        request = self.makeRequest(variable)
        self.assertEqual('var_with_lbproc', request.entry)

    @patch('mip_convert.save.cmor.cmor_lite.get_saver')
    def testNoLbproc(self, mock_saver):
        examples = [
            ('var_no_sections', 'lbproc'),
            ('var_no_sections', 'lbtim'),
        ]
        for (variable, attribute) in examples:
            request = self.makeRequest(variable)
            self.assertRaises(AttributeError, getattr, request, attribute)

    @patch('mip_convert.save.cmor.cmor_lite.get_saver')
    def testDefaultLogicalFalse(self, mock_saver):
        variable = 'var_no_sections'
        request = self.makeRequest(variable)
        self.assertFalse(request.first_only)

    @patch('mip_convert.save.cmor.cmor_lite.get_saver')
    def testLogicalOn(self, mock_saver):
        variable = 'var_with_first'
        request = self.makeRequest(variable)
        self.assertTrue(request.first_only)


if __name__ == '__main__':
    unittest.main()
