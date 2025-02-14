# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import os

from cdds.common.plugins.cmip6.cmip6_streams import Cmip6StreamStore, Cmip6StreamInfo

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
