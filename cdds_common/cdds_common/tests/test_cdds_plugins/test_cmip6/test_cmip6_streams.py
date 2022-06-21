# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from cdds_common.cdds_plugins.base.base_streams import StreamAttributes
from cdds_common.cdds_plugins.cmip6.cmip6_streams import Cmip6StreamStore, Cmip6StreamInfo

from datetime import datetime
from unittest import TestCase


class TestCmip6StreamInfoRetrieveStreamId(TestCase):

    def setUp(self):
        local_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        self.stream_info = Cmip6StreamInfo(config_path)

    def test_retrieve_stream_id_from_default(self):
        variable = 'tas'
        mip_table = 'Amon'
        stream, substream = self.stream_info.retrieve_stream_id(variable, mip_table)
        self.assertTupleEqual((stream, substream), ('ap5', None))

    def test_retrieve_stream_id_from_override(self):
        variable = 'tasmax'
        mip_table = 'Amon'
        stream, substream = self.stream_info.retrieve_stream_id(variable, mip_table)
        self.assertTupleEqual((stream, substream), ('ap6', None))

    def test_retrieve_stream_id_unknown(self):
        variable = 'tas'
        mip_table = 'Xmon'
        stream, substream = self.stream_info.retrieve_stream_id(variable, mip_table)
        self.assertEqual((stream, substream), ('unknown', None))

    def test_retrieve_stream_id_with_substream(self):
        variable = 'sos'
        mip_table = 'Oday'
        stream, substream = self.stream_info.retrieve_stream_id(variable, mip_table)
        self.assertEqual((stream, substream), ('ond', 'grid-T'))


class TestCmip6StreamInfoCalculateExpectedNumberOfFiles(TestCase):

    def setUp(self):
        local_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        self.stream_info = Cmip6StreamInfo(config_path)
        self.start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        self.end_date = datetime.strptime("2015-01-01", "%Y-%m-%d")

    def test_calculate_expected_number_of_files_in_ap4(self):
        stream_attributes = StreamAttributes('ap4', self.start_date, self.end_date)
        substreams = ["ap4"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 12, actual)

    def test_calculate_expected_number_of_files_in_onm(self):
        stream_attributes = StreamAttributes('onm', self.start_date, self.end_date)
        substreams = ["scalar", "grid-U", "grid-T", "grid-W", "grid-V"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 12 * 5, actual)

    def test_calculate_expected_number_of_files_in_inm(self):
        stream_attributes = StreamAttributes('inm', self.start_date, self.end_date)
        substreams = ["default"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 12, actual)


class TestCmip6StreamStore(TestCase):

    def tearDown(self):
        Cmip6StreamStore.clean_instance()

    def test_get_stream_info(self):
        store = Cmip6StreamStore.instance()
        stream_info = store.get()
        self.assertIsInstance(stream_info, Cmip6StreamInfo)

    def test_stream_store_is_singleton(self):
        Cmip6StreamStore.instance()
        self.assertRaises(Exception, Cmip6StreamStore())
