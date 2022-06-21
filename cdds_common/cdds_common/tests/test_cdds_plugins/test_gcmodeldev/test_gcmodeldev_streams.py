# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from cdds_common.cdds_plugins.base.base_streams import StreamAttributes
from cdds_common.cdds_plugins.gcmodeldev.gcmodeldev_streams import GCModelDevStreamInfo, GCModelDevStreamStore

from datetime import datetime
from unittest import TestCase


class TestGCModelDevStreamInfoRetrieveStreamId(TestCase):

    def setUp(self):
        local_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        self.stream_info = GCModelDevStreamInfo(config_path)

    def test_retrieve_stream_id_from_default(self):
        variable = 'tas'
        mip_table = 'Amon'
        stream, substream = self.stream_info.retrieve_stream_id(variable, mip_table)
        self.assertTupleEqual((stream, substream), ('apm', None))

    def test_retrieve_stream_id_unknown(self):
        variable = 'tas'
        mip_table = 'Xmon'
        stream, substream = self.stream_info.retrieve_stream_id(variable, mip_table)
        self.assertEqual((stream, substream), ('unknown', None))


class TestGCModelDevStreamInfoCalculateExpectedNumberOfFiles(TestCase):

    def setUp(self):
        local_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        self.stream_info = GCModelDevStreamInfo(config_path)

    def test_calculate_expected_number_of_files_in_ap4(self):
        start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("2015-01-01", "%Y-%m-%d")
        stream_attributes = StreamAttributes('ap4', start_date, end_date)
        substreams = ["ap4"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 12, actual)

    def test_calculate_expected_number_of_files_in_onm(self):
        start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("2015-01-01", "%Y-%m-%d")
        stream_attributes = StreamAttributes('onm', start_date, end_date)
        substreams = ["scalar", "grid-U", "grid-T", "grid-W", "grid-V"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 12 * 5, actual)

    def test_calculate_expected_number_of_files_in_inm(self):
        start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("2015-01-01", "%Y-%m-%d")
        stream_attributes = StreamAttributes('inm', start_date, end_date)
        substreams = ["default"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 12, actual)


class TestGCModelDevStreamStore(TestCase):

    def tearDown(self):
        GCModelDevStreamStore.clean_instance()

    def test_get_stream_info(self):
        store = GCModelDevStreamStore.instance()
        stream_info = store.get()
        self.assertIsInstance(stream_info, GCModelDevStreamInfo)

    def test_stream_store_is_singleton(self):
        GCModelDevStreamStore.instance()
        self.assertRaises(Exception, GCModelDevStreamStore())
