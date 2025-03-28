# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Tests of mip_convert_wrapper.file_management
"""
import unittest
import re

from metomi.isodatetime.data import TimePoint, Calendar

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.convert.constants import STREAMS_FILES_REGEX
from cdds.convert.mip_convert_wrapper.file_processors import (
    parse_atmos_monthly_filename, parse_atmos_submonthly_filename,
    parse_ocean_seaice_filename, parse_atmos_hourly_filename
)

ATMOS_MONTHLY_FILENAMES = [
    'aw310a.p41997apr.pp',
    'aw310a.p41997aug.pp',
    'aw310a.p41997dec.pp',
    'aw310a.p41997feb.pp',
    'aw310a.p41997jan.pp',
    'aw310a.p41997jul.pp',
    'aw310a.p41997jun.pp',
    'aw310a.p41997mar.pp',
    'aw310a.p41997may.pp',
    'aw310a.p41997nov.pp',
    'aw310a.p41997oct.pp',
    'aw310a.p41997sep.pp',
    'aw310a.p41996dec.pp',
    'aw310a.p41998jan.pp',
    'aw310a.p41998apr.pp',
    'aw310a.p41998aug.pp',
    'aw310a.p41998dec.pp',
    'aw310a.p41998feb.pp',
    'aw310a.p41998jul.pp',
    'aw310a.p41998jun.pp',
    'aw310a.p41998mar.pp',
    'aw310a.p41998may.pp',
    'aw310a.p41998nov.pp',
    'aw310a.p41998oct.pp',
    'aw310a.p41998sep.pp',
    'aw310a.p41996apr.pp',
    'aw310a.p41996aug.pp',
    'aw310a.p41996feb.pp',
    'aw310a.p41996jan.pp',
    'aw310a.p41996jul.pp',
    'aw310a.p41996jun.pp',
    'aw310a.p41996mar.pp',
    'aw310a.p41996may.pp',
    'aw310a.p41996nov.pp',
    'aw310a.p41996oct.pp',
    'aw310a.p41996sep.pp',
]

ATMOS_ENS_MONTHLY_FILENAMES = [
    'aw310-r001i1p00001a.p41997apr.pp',
    'aw310-r001i1p00001a.p41997aug.pp',
    'aw310-r001i1p00001a.p41997dec.pp',
    'aw310-r001i1p00001a.p41997feb.pp',
    'aw310-r001i1p00001a.p41997jan.pp',
    'aw310-r001i1p00001a.p41997jul.pp',
    'aw310-r001i1p00001a.p41997jun.pp',
    'aw310-r001i1p00001a.p41997mar.pp',
    'aw310-r001i1p00001a.p41997may.pp',
    'aw310-r001i1p00001a.p41997nov.pp',
    'aw310-r001i1p00001a.p41997oct.pp',
    'aw310-r001i1p00001a.p41997sep.pp',
    'aw310-r001i1p00001a.p41996dec.pp',
    'aw310-r001i1p00001a.p41998jan.pp',
    'aw310-r001i1p00001a.p41998apr.pp',
    'aw310-r001i1p00001a.p41998aug.pp',
    'aw310-r001i1p00001a.p41998dec.pp',
    'aw310-r001i1p00001a.p41998feb.pp',
    'aw310-r001i1p00001a.p41998jul.pp',
    'aw310-r001i1p00001a.p41998jun.pp',
    'aw310-r001i1p00001a.p41998mar.pp',
    'aw310-r001i1p00001a.p41998may.pp',
    'aw310-r001i1p00001a.p41998nov.pp',
    'aw310-r001i1p00001a.p41998oct.pp',
    'aw310-r001i1p00001a.p41998sep.pp',
    'aw310-r001i1p00001a.p41996apr.pp',
    'aw310-r001i1p00001a.p41996aug.pp',
    'aw310-r001i1p00001a.p41996feb.pp',
    'aw310-r001i1p00001a.p41996jan.pp',
    'aw310-r001i1p00001a.p41996jul.pp',
    'aw310-r001i1p00001a.p41996jun.pp',
    'aw310-r001i1p00001a.p41996mar.pp',
    'aw310-r001i1p00001a.p41996may.pp',
    'aw310-r001i1p00001a.p41996nov.pp',
    'aw310-r001i1p00001a.p41996oct.pp',
    'aw310-r001i1p00001a.p41996sep.pp',
]

ATMOS_SUBMONTHLY_FILENAMES = [
    'aw310a.p619970101.pp',
    'aw310a.p619970111.pp',
    'aw310a.p619970121.pp',
    'aw310a.p619970201.pp',
    'aw310a.p619970211.pp',
    'aw310a.p619970221.pp',
    'aw310a.p619970301.pp',
    'aw310a.p619970311.pp',
    'aw310a.p619970321.pp',
    'aw310a.p619970401.pp',
    'aw310a.p619970411.pp',
    'aw310a.p619970421.pp',
    'aw310a.p619970501.pp',
    'aw310a.p619970511.pp',
    'aw310a.p619970521.pp',
    'aw310a.p619970601.pp',
    'aw310a.p619970611.pp',
    'aw310a.p619970621.pp',
    'aw310a.p619970701.pp',
    'aw310a.p619970711.pp',
    'aw310a.p619970721.pp',
    'aw310a.p619970801.pp',
    'aw310a.p619970811.pp',
    'aw310a.p619970821.pp',
    'aw310a.p619970901.pp',
    'aw310a.p619970911.pp',
    'aw310a.p619970921.pp',
    'aw310a.p619971001.pp',
    'aw310a.p619971011.pp',
    'aw310a.p619971021.pp',
    'aw310a.p619971101.pp',
    'aw310a.p619971111.pp',
    'aw310a.p619971121.pp',
    'aw310a.p619971201.pp',
    'aw310a.p619971211.pp',
    'aw310a.p619971221.pp',
]

ATMOS_HOURLY_FILENAMES = [
    'aw310a.p619970101_00.pp',
    'aw310a.p619970101_01.pp',
    'aw310a.p619970101_02.pp',
    'aw310a.p619970101_03.pp',
    'aw310a.p619970101_04.pp',
    'aw310a.p619970101_05.pp',
    'aw310a.p619970101_06.pp',
    'aw310a.p619970101_07.pp',
    'aw310a.p619970101_08.pp',
    'aw310a.p619970101_09.pp',
    'aw310a.p619970101_10.pp',
    'aw310a.p619970101_11.pp',
    'aw310a.p619970101_12.pp',
    'aw310a.p619970101_13.pp',
    'aw310a.p619970101_14.pp',
    'aw310a.p619970101_15.pp',
    'aw310a.p619970101_16.pp',
    'aw310a.p619970101_17.pp',
    'aw310a.p619970101_18.pp',
    'aw310a.p619970101_19.pp',
    'aw310a.p619970101_20.pp',
    'aw310a.p619970101_21.pp',
    'aw310a.p619970101_22.pp',
    'aw310a.p619970101_23.pp',
]

OCEAN_FILENAMES = [
    'nemo_aw310o_1m_19970101-19970201_grid-T.nc',
    'nemo_aw310o_1m_19970201-19970301_grid-T.nc',
    'nemo_aw310o_1m_19970301-19970401_grid-T.nc',
    'nemo_aw310o_1m_19970401-19970501_grid-T.nc',
    'nemo_aw310o_1m_19970501-19970601_grid-T.nc',
    'nemo_aw310o_1m_19970601-19970701_grid-T.nc',
    'nemo_aw310o_1m_19970701-19970801_grid-T.nc',
    'nemo_aw310o_1m_19970801-19970901_grid-T.nc',
    'nemo_aw310o_1m_19970901-19971001_grid-T.nc',
    'nemo_aw310o_1m_19971001-19971101_grid-T.nc',
    'nemo_aw310o_1m_19971101-19971201_grid-T.nc',
    'nemo_aw310o_1m_19971201-19980101_grid-T.nc',
    'nemo_aw310o_1m_19980101-19980201_grid-T.nc',
    'nemo_aw310o_1m_19961101-19961201_grid-T.nc',
    'nemo_aw310o_1m_19961201-19970101_grid-T.nc',
    'nemo_aw310o_1m_19970101-19970201_grid-U.nc',
    'nemo_aw310o_1m_19970201-19970301_grid-U.nc',
    'nemo_aw310o_1m_19970301-19970401_grid-U.nc',
    'nemo_aw310o_1m_19970401-19970501_grid-U.nc',
    'nemo_aw310o_1m_19970501-19970601_grid-U.nc',
    'nemo_aw310o_1m_19970601-19970701_grid-U.nc',
    'nemo_aw310o_1m_19970701-19970801_grid-U.nc',
    'nemo_aw310o_1m_19970801-19970901_grid-U.nc',
    'nemo_aw310o_1m_19970901-19971001_grid-U.nc',
    'nemo_aw310o_1m_19971001-19971101_grid-U.nc',
    'nemo_aw310o_1m_19971101-19971201_grid-U.nc',
    'nemo_aw310o_1m_19971201-19980101_grid-U.nc',
    'nemo_aw310o_1m_19980101-19980201_grid-U.nc',
    'nemo_aw310o_1m_19961101-19961201_grid-U.nc',
    'nemo_aw310o_1m_19961201-19970101_grid-U.nc',
]


class TestProcessors(unittest.TestCase):

    def setUp(self):
        load_plugin()
        self.model_id = 'HadGEM3-GC31-LL'
        Calendar.default().set_mode('360_day')

    def test_parse_atmos_monthly_filename(self):
        stream = 'ap4'
        test_pattern = re.compile(STREAMS_FILES_REGEX['ap'])
        output_file_dict = parse_atmos_monthly_filename(
            ATMOS_MONTHLY_FILENAMES[0], test_pattern)
        expected_start = TimePoint(year=1997, month_of_year=4, day_of_month=1)
        expected_end = TimePoint(year=1997, month_of_year=5, day_of_month=1)
        expected_suite_id = 'aw310'
        self.assertEqual(output_file_dict['start'], expected_start)
        self.assertEqual(output_file_dict['end'], expected_end)
        self.assertEqual(output_file_dict['suite_id'], expected_suite_id)

    def test_parse_atmos_ens_monthly_filename(self):
        stream = 'ap4'
        test_pattern = re.compile(STREAMS_FILES_REGEX['ap'])
        output_file_dict = parse_atmos_monthly_filename(
            ATMOS_ENS_MONTHLY_FILENAMES[0], test_pattern)
        expected_start = TimePoint(year=1997, month_of_year=4, day_of_month=1)
        expected_end = TimePoint(year=1997, month_of_year=5, day_of_month=1)
        expected_suite_id = 'aw310'
        self.assertEqual(output_file_dict['start'], expected_start)
        self.assertEqual(output_file_dict['end'], expected_end)
        self.assertEqual(output_file_dict['suite_id'], expected_suite_id)

    def test_parse_atmos_submonthly_filename(self):
        stream = 'ap6'
        test_pattern = re.compile(STREAMS_FILES_REGEX['ap_submonthly'])
        output_file_dict = parse_atmos_submonthly_filename(
            ATMOS_SUBMONTHLY_FILENAMES[0], test_pattern)
        expected_start = TimePoint(year=1997, month_of_year=1, day_of_month=1)
        expected_end = TimePoint(year=1997, month_of_year=1, day_of_month=11)
        expected_suite_id = 'aw310'
        self.assertEqual(output_file_dict['start'], expected_start)
        self.assertEqual(output_file_dict['end'], expected_end)
        self.assertEqual(output_file_dict['suite_id'], expected_suite_id)

    def test_parse_ocean_seaice_filename(self):
        stream = 'onm'
        test_pattern = re.compile(STREAMS_FILES_REGEX['on'])
        output_file_dict = parse_ocean_seaice_filename(
            OCEAN_FILENAMES[0], test_pattern)
        expected_start = TimePoint(year=1997, month_of_year=1, day_of_month=1)
        expected_end = TimePoint(year=1997, month_of_year=2, day_of_month=1)
        expected_suite_id = 'aw310'
        self.assertEqual(output_file_dict['start'], expected_start)
        self.assertEqual(output_file_dict['end'], expected_end)
        self.assertEqual(output_file_dict['suite_id'], expected_suite_id)

    def test_parse_hourly_filename(self):
        test_pattern = re.compile(STREAMS_FILES_REGEX['ap_hourly'])
        output_file_dict = parse_atmos_hourly_filename(ATMOS_HOURLY_FILENAMES[0], test_pattern)
        expected_start = TimePoint(year=1997, month_of_year=1, day_of_month=1, hour_of_day=0)
        expected_end = TimePoint(year=1997, month_of_year=1, day_of_month=1, hour_of_day=1)
        expected_suite_id = 'aw310'
        self.assertEqual(output_file_dict['start'], expected_start)
        self.assertEqual(output_file_dict['end'], expected_end)
        self.assertEqual(output_file_dict['suite_id'], expected_suite_id)


if __name__ == '__main__':
    unittest.main()
