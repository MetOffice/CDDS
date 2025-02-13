# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.md for license details.
import os
import unittest

from cdds.common.plugins.cordex.cordex_streams import CordexStreamStore, CordexStreamInfo

from unittest import TestCase


class TestCordexStreamInfoRetrieveStreamId(TestCase):

    def setUp(self):
        local_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        self.stream_info = CordexStreamInfo(config_path)

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


class TestCmip6StreamStore(TestCase):

    def tearDown(self):
        CordexStreamStore.clean_instance()

    def test_get_stream_info(self):
        store = CordexStreamStore.instance()
        stream_info = store.get()
        self.assertIsInstance(stream_info, CordexStreamInfo)

    def test_stream_store_is_singleton(self):
        CordexStreamStore.instance()
        self.assertRaises(Exception, CordexStreamStore())


if __name__ == '__main__':
    unittest.main()
