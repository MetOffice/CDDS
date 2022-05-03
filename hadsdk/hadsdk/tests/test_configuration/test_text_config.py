# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import unittest

from hadsdk.configuration.common import ValidateConfigError
from hadsdk.configuration.text_config import SitesConfig, HybridHeightConfig, MappingConfig, MatchError
from io import StringIO
from unittest.mock import patch
from textwrap import dedent


class TestSitesConfig(unittest.TestCase):
    """
    Tests for ``SitesConfig`` in configuration.py.
    """

    def setUp(self):
        self.read_path = '/path/to/sites.txt'
        self.site_number1 = 1
        self.longitude1 = 100.0
        self.latitude1 = 10.0
        self.orography1 = 0.0
        self.comment1 = 'site 1'
        self.site_number2 = 2
        self.longitude2 = 200.0
        self.latitude2 = -10.0
        self.orography2 = 5.5
        self.comment2 = 'site 2'
        self.site1 = (self.site_number1, self.longitude1, self.latitude1, self.orography1, self.comment1)
        self.site2 = (self.site_number2, self.longitude2, self.latitude2, self.orography2, self.comment2)
        site_string = '{site_number}, {longitude}, {latitude}, {orography}, {comment}\n'
        self.site_string1 = site_string.format(
            site_number=self.site_number1,
            longitude=self.longitude1,
            latitude=self.latitude1,
            orography=self.orography1,
            comment=self.comment1
        )
        self.site_string2 = site_string.format(
            site_number=self.site_number2,
            longitude=self.longitude2,
            latitude=self.latitude2,
            orography=self.orography2,
            comment=self.comment2
        )
        self.sites_config = self.site_string1 + self.site_string2
        self.obj = None
        self.test_sites_config_instantiation()

    @patch('builtins.open')
    def test_sites_config_instantiation(self, mopen):
        mopen.return_value = StringIO(dedent(self.sites_config))
        self.obj = SitesConfig(self.read_path)
        mopen.assert_called_once_with(self.read_path, 'r')

    @patch('builtins.open')
    def test_sites_config_instantiation_invalid_configuration_file(self, mopen):
        sites_config = 'there, are, not, five, columns, here\n'
        mopen.return_value = StringIO(dedent(sites_config))
        msg = 'Number of columns in configuration file .* does not match with the expected number of columns .*'
        self.assertRaisesRegex(RuntimeError, msg, SitesConfig, self.read_path)

    def test_correct_sites_value(self):
        reference = [self.site1, self.site2]
        self.assertEqual(self.obj.sites, reference)

    def test_correct_coordinates_value(self):
        reference = [(self.longitude1, self.latitude1), (self.longitude2, self.latitude2)]
        self.assertEqual(self.obj.coordinates, reference)

    def test_correct_single_site_information_value(self):
        coordinate = [self.longitude1, self.latitude1]
        reference = self.site1
        self.assertEqual(self.obj.single_site_information(coordinate), reference)

    def test_single_site_information_with_unmatching_coordinate(self):
        coordinate = [self.longitude1, self.latitude2]
        self.assertIsNone(self.obj.single_site_information(coordinate))


class TestHybridHeightConfig(unittest.TestCase):
    """
    Tests for ``HybridHeightConfig`` in configuration.py.
    """

    def setUp(self):
        self.read_path = 'hybrid_height_levels.txt'
        self.model_level_numbers = [1, 2, 3]
        self.a_value = [20.0, 80.0, 180.0]
        self.a_lower_bound = [0.0, 50.0, 130.0]
        self.a_upper_bound = [50.0, 130.0, 250.0]
        self.b_value = [0.997716, 0.990882, 0.979543]
        self.b_lower_bound = [0.994296, 0.985204, 0.971644]
        self.b_upper_bound = [1.0, 0.994296, 0.985204]
        self.hybrid_height_config = (
            '{}, {}, {}, {}, {}, {}, {}\n'
            '{}, {}, {}, {}, {}, {}, {}\n'
            '{}, {}, {}, {}, {}, {}, {}\n'.format(
                self.model_level_numbers[0],
                self.a_value[0],
                self.a_lower_bound[0],
                self.a_upper_bound[0],
                self.b_value[0],
                self.b_lower_bound[0],
                self.b_upper_bound[0],
                self.model_level_numbers[1],
                self.a_value[1],
                self.a_lower_bound[1],
                self.a_upper_bound[1],
                self.b_value[1],
                self.b_lower_bound[1],
                self.b_upper_bound[1],
                self.model_level_numbers[2],
                self.a_value[2],
                self.a_lower_bound[2],
                self.a_upper_bound[2],
                self.b_value[2],
                self.b_lower_bound[2],
                self.b_upper_bound[2]
            )
        )
        self.obj = None
        self.test_hybrid_height_config_instantiation()

    @patch('builtins.open')
    def test_hybrid_height_config_instantiation(self, mopen):
        mopen.return_value = StringIO(dedent(self.hybrid_height_config))
        self.obj = HybridHeightConfig(self.read_path)
        mopen.assert_called_once_with(self.read_path, 'r')

    @patch('builtins.open')
    def test_hybrid_height_config_instantiation_invalid_configuration_file(self, mopen):
        hybrid_height_config = 'there, are, not, seven, columns, here\n'
        mopen.return_value = StringIO(dedent(hybrid_height_config))
        msg = 'Number of columns in configuration file .* does not match with the expected number of columns .*'
        self.assertRaisesRegex(RuntimeError, msg, HybridHeightConfig, self.read_path)

    def test_hybrid_height_information(self):
        attributes = ['model_level_numbers',
                      'a_value', 'a_lower_bound', 'a_upper_bound', 'a_bounds',
                      'b_value', 'b_lower_bound', 'b_upper_bound', 'b_bounds'
                      ]
        for attribute in attributes:
            if attribute == 'a_bounds':
                reference = list(zip(self.a_lower_bound, self.a_upper_bound))
            elif attribute == 'b_bounds':
                reference = list(zip(self.b_upper_bound, self.b_lower_bound))
            else:
                reference = getattr(self, attribute)
            output = getattr(self.obj, attribute)
            self.assertEqual(output, reference)


@patch('builtins.open')
class TestMappingConfig(unittest.TestCase):
    """
    Tests for ``MappingConfig`` in configuration.py.
    """

    def setUp(self):
        self.read_path = 'mapping_config'
        self.mapping_id = 'CMIP3 (A1c, wap)'
        self.row1 = (
            '| lagrangian_tendency_of_air_pressure |  | Pa s-1 |  '
            '| m01s12i201 |  | <= 4.7 | {mapping_id} |  |  |\n'.format(mapping_id=self.mapping_id))
        self.row2 = (
            '| lagrangian_tendency_of_air_pressure |  | Pa s-1 |  '
            '| m01s15i222 |  | <= 4.7 | {mapping_id} |  |  |\n'.format(mapping_id=self.mapping_id))
        self.row3 = (
            '| lagrangian_tendency_of_air_pressure |  | Pa s-1 |  '
            '| m01s15i222 |  | 4.8.1-4.9 | {mapping_id} |  |  |\n'.format(mapping_id=self.mapping_id))
        self.row4 = (
            '| lagrangian_tendency_of_air_pressure |  | Pa s-1 |  '
            '| m01s30i208/m01s30i301 |  | >= 5.0 | {mapping_id} |  |  |\n'.format(mapping_id=self.mapping_id))
        self.row5 = (
            '| lagrangian_tendency_of_air_pressure |  | Pa s-1 |  '
            '| m01s15i222 |  |  | {mapping_id} |  |  |\n'.format(mapping_id=self.mapping_id))

    def test_matched_row(self, mopen):
        # Exclude the duplicate.
        mapping_config = ''.join([self.row1, self.row3, self.row4, self.row5])
        mopen.return_value = StringIO(dedent(mapping_config))
        obj = MappingConfig(self.read_path)
        mopen.assert_called_once_with(self.read_path, 'r')
        matches = {'4.5.10': obj.parse_mapping_table_row(self.row1),
                   '4.8.09': obj.parse_mapping_table_row(self.row3),
                   '5.0': obj.parse_mapping_table_row(self.row4),
                   '10.12.1': obj.parse_mapping_table_row(self.row4),
                   '4.7.15': obj.parse_mapping_table_row(self.row5)
                   }
        for um_version, row in list(matches.items()):
            self.assertEqual(obj.matched_row(self.mapping_id, um_version), row)

    def test_no_rows_match_mapping_id(self, mopen):
        mapping_config = ''.join([self.row1, self.row2, self.row3, self.row4, self.row5])
        mopen.return_value = StringIO(dedent(mapping_config))
        obj = MappingConfig(self.read_path)
        mopen.assert_called_once_with(self.read_path, 'r')
        mapping_id = 'CMIP5 (A1a, tas)'
        um_version = '5.0'
        msg = 'No rows found in mapping table .* with mapping identifier .*'
        self.assertRaisesRegex(MatchError, msg, obj.matched_row, mapping_id, um_version)

    def test_rows_match_mapping_id_but_no_rows_match_um_version(self, mopen):
        # Exclude the empty version otherwise that row will be matched.
        mapping_config = ''.join([self.row1, self.row2, self.row3, self.row4])
        mopen.return_value = StringIO(dedent(mapping_config))
        obj = MappingConfig(self.read_path)
        mopen.assert_called_once_with(self.read_path, 'r')
        um_versions = ['4.7.1', '4.8', '4.9.5']
        msg = 'No rows found in mapping table .* with mapping identifier .*and UM version .*'
        for um_version in um_versions:
            self.assertRaisesRegex(MatchError, msg.format(um_version), obj.matched_row, self.mapping_id, um_version)

    def test_multiple_matched_rows(self, mopen):
        mapping_config = ''.join([self.row1, self.row2, self.row3, self.row4, self.row5])
        mopen.return_value = StringIO(dedent(mapping_config))
        obj = MappingConfig(self.read_path)
        mopen.assert_called_once_with(self.read_path, 'r')
        um_versions = ['4.7', '4.7.0']
        msg = 'Duplicate mapping for .*'
        for um_version in um_versions:
            self.assertRaisesRegex(MatchError, msg, obj.matched_row, self.mapping_id, um_version)

    def test_parse_mapping_table_row_missing_column(self, mopen):
        mapping_config = '| lagrangian_tendency_of_air_pressure | Pa s-1 |  | m01s15i222 |  |  | {mapping_id} |  |  |\n'
        mopen.return_value = StringIO(dedent(mapping_config))
        msg = 'Number of entries in row .* does not match the number of columns .*'
        self.assertRaisesRegex(ValidateConfigError, msg, MappingConfig, self.read_path)
        mopen.assert_called_once_with(self.read_path, 'r')


if __name__ == '__main__':
    unittest.main()
